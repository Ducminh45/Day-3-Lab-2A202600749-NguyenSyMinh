# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Sỹ Minh
- **Student ID**: 2A202600749
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

In this lab, I was responsible for implementing the core execution loop and tool parsing/execution mechanisms of the **ReAct Agent** system. The objective was to build a robust, production-friendly agent that can reason step-by-step and leverage specialized stock analysis tools.

### 1. Modules Implemented

- **`src/agent/agent.py`**: Designed and developed the standard ReAct loop.
  - Formulated the System Prompt that structures the model's thinking (`Thought`), action-selection (`Action: tool_name(arguments)`), observation handling (`Observation`), and final answering (`Final Answer:`).
  - Built resilient regex patterns (`ACTION_RE` and `FINAL_RE`) to parse the LLM outputs.
  - Implemented an advanced argument parsing module (`_parse_tool_args`) to handle diverse payload formats (JSON objects, Python positional/keyword arguments, single literal values, or raw strings).
  - Designed the fallback mechanism when `max_steps` is exceeded to synthesize historical reasoning into a high-quality response.
- **`src/tools/`**: Integrated the Vietnamese Stock Market tools (prices, fundamental metrics, technical indicators, and news) to ensure clean, consistent data formatting (JSON) as Observations for the LLM.

### 2. Code Highlights

Here is the core logic of the ReAct execution loop inside `src/agent/agent.py` that manages the thought-action-observation cycle and parses tool outputs cleanly:

```python
# Extract from src/agent/agent.py - ReAct Agent Core Loop
def run(self, user_input: str) -> str:
    logger.log_event(
        "AGENT_START",
        {"input": user_input, "model": getattr(self.llm, "model_name", "unknown")},
    )

    self.history = []
    scratchpad = ""
    last_response = ""

    for step in range(1, self.max_steps + 1):
        prompt = self._build_prompt(user_input=user_input, scratchpad=scratchpad)
        response = self._generate(prompt)
        last_response = response.strip()
        self.history.append({"role": "assistant", "content": last_response})

        logger.log_event("AGENT_STEP", {"step": step, "response": last_response})

        # Check for Final Answer
        final_answer = self._parse_final_answer(last_response)
        if final_answer is not None:
            logger.log_event("AGENT_END", {"steps": step, "status": "final_answer"})
            return final_answer.strip()

        # Parse and execute action
        action = self._parse_action(last_response)
        if action is None:
            observation = (
                "No valid Action or Final Answer was found. "
                "Use either `Action: tool_name(arguments)` or `Final Answer: ...`."
            )
        else:
            tool_name, raw_args = action
            observation = self._execute_tool(tool_name, raw_args)

        self.history.append({"role": "observation", "content": observation})
        scratchpad += f"\n{last_response}\nObservation: {observation}\n"

    logger.log_event("AGENT_END", {"steps": self.max_steps, "status": "max_steps"})
    
    # Best-effort fallback when step limit is reached
    fallback_prompt = self._build_prompt(
        user_input=user_input,
        scratchpad=scratchpad + "\nYou reached the step limit. Provide the best possible final answer now.",
    )
    fallback_response = self._generate(fallback_prompt).strip()
    final_answer = self._parse_final_answer(fallback_response)
    return (final_answer or fallback_response or last_response).strip()
```

### 3. Documentation & System Prompt Alignment

The agent interacts with the ReAct loop via a tailored system prompt. The loop behaves as follows:
1. **Thought**: The LLM determines what information is missing to resolve the query.
2. **Action**: The LLM outputs an action in the format `Action: tool_name(arguments)`.
3. **Execution**: The Python interpreter intercepts the action, runs the corresponding tool from the registry, and returns the result as an `Observation`.
4. **Final Answer**: When the scratchpad contains sufficient data, the LLM outputs `Final Answer: [Detailed analysis]`.

---

## II. Debugging Case Study (10 Points)

### 1. Problem Description

During testing of the standard LLM Chatbot baseline on the query: **"Giá cổ phiếu hiện tại của FPT là bao nhiêu?"**, the application threw a runtime exception and failed to answer. The system log captured a `CHATBOT_ERROR` with a `402 Payment Required` status from the API provider gateway (OpenRouter).

### 2. Log Source

The issue was captured in `logs/2026-06-01.log` (lines 77-79):

```json
{"timestamp": "2026-06-01T09:55:09.408432", "event": "CHATBOT_START", "data": {"input": "Giá cổ phiếu hiện tại của FPT là bao nhiêu?", "model": "gpt-4o-mini"}}
{"timestamp": "2026-06-01T09:55:11.080189", "event": "CHATBOT_ERROR", "data": {"error": "Error code: 402 - {'error': {'message': 'This request requires more credits, or fewer max_tokens. You requested up to 16384 tokens, but can only afford 10692. To increase, visit https://openrouter.ai/settings/credits and upgrade to a paid account', 'code': 402, 'metadata': {'provider_name': None, 'previous_errors': [{'code': 402, 'message': 'This request requires more credits, or fewer max_tokens. You requested up to 16384 tokens, but can only afford 10692. To increase, visit https://openrouter.ai/settings/credits and upgrade to a paid account'}]}}, 'user_id': 'user_33r35cfPArUCagwexSCkhJuvIR3'}"}}
```

### 3. Diagnosis

- **Root Cause**: The API client did not specify a concrete `max_tokens` value, or configured it in a way that prompted the SDK/OpenRouter to request the model's absolute maximum output size (16,384 tokens for `gpt-4o-mini`).
- **Credit Pre-allocation**: OpenRouter's gateway preemptively calculates the cost of the *maximum possible* tokens for a request. If the user's account credit balance is insufficient to cover this peak scenario (even if the actual generated response only takes 100 tokens), the gateway terminates the call and returns an **HTTP 402** error.

### 4. Solution

We resolved this by modifying `src/core/openai_provider.py` to enforce a tight and deterministic upper limit on generation length:

```python
# Modified OpenAIProvider inside src/core/openai_provider.py
response = self.client.chat.completions.create(
    model=self.model_name,
    messages=messages,
    max_tokens=2048,  # Constrained max_tokens to prevent preemptive credit blocks
)
```

Setting `max_tokens=2048` dramatically reduced the credit reservation requirement, allowing queries to pass through successfully even with low account balances, without affecting quality since stock analyses rarely exceed 1,500 tokens.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning Capability**: 
   The `Thought` block acts as a cognitive draft space (Scratchpad). Instead of immediately jumping to an answer, the model reasons: *"I need the price of FPT first, then I must evaluate its P/E, and finally check the technical indicators."* This prevents the agent from making premature assumptions and leads to highly structured, logical, and complete financial reports.
   
2. **Reliability and Hallucinations**:
   - **Chatbot Baseline**: Extremely vulnerable to hallucination. When asked for real-time stock prices or latest financial statements, the Chatbot outputs outdated static training data, invents fictitious numbers, or politely declines the request.
   - **ReAct Agent**: Highly reliable because its conclusions are grounded in the data fetched dynamically in the `Observation` block. However, the ReAct Agent can perform *worse* than the Chatbot if:
     - The tools fail or return empty/malformed structures.
     - The agent enters a loop (e.g., repeatedly calling a tool with different casing).
     - The system prompt is too restrictive, causing parsing errors or formatting recovery loops.
     
3. **Environment Feedback**:
   Observations serve as direct environmental feedback. For example, in a comparison scenario (TCB vs FPT), the agent calls `get_financial_metrics('TCB')`, reads the observation containing a P/E of 9.5 and EPS of 5,100, and immediately synthesizes: *"Since TCB's P/E is 9.5 and EPS is 5,100, I now need to fetch FPT's metrics to perform the comparison."* It dynamically adjusts its next tool selection based on the data returned in previous steps.

---

## IV. Future Improvements (5 Points)

To scale this Vietnamese Stock Market Analyst system to production, I propose the following enhancements:

- **Scalability**: Implement **Asynchronous Tool Execution** using `asyncio` or `Celery`. When an agent decides to fetch multiple metrics (e.g., prices for FPT, HPG, TCB simultaneously), it should execute these tool calls in parallel rather than sequentially, reducing latency from 15s to under 3s.
- **Safety & Guardrails**: Add an independent **Guardrail Layer** (such as Llama Guard or NeMo Guardrails) to sanitize user inputs (preventing prompt injection and tool argument injection) and audit tool arguments (ensuring only approved ticker symbols are queried). Enforce strict circuit breakers on the ReAct loop (e.g., max budget per session, hard limits on loop repetitions).
- **Performance**: Implement a **Caching Layer** (Redis) for slow tools (`search_market_news`, `get_financial_metrics`) since stock fundamentals and daily news do not change second-by-second. Use **Vector DB embeddings** to index market research, enabling semantic search and selective RAG injection into the system prompt.

---

> [!NOTE]
> This individual report documents Nguyễn Sỹ Minh's implementation and personal reflections for Lab 3.
