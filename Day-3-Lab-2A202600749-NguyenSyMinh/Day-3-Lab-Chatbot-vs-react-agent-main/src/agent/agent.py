import ast
import inspect
import json
import re
from typing import List, Dict, Any, Optional, Tuple, Callable

from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker


class ReActAgent:
    """
    A small, production-friendly ReAct-style agent.

    The agent repeatedly asks the LLM what to do next, parses an optional
    `Action: tool_name(arguments)` line, executes the matching tool, appends the
    resulting `Observation`, and stops when the model emits `Final Answer:`.

    Expected tool format:
        {
            "name": "search_hotel_info",
            "description": "Search official resort information",
            "function": callable,        # also accepts: "func", "callable"
        }

    Tool arguments are flexible:
    - Action: tool_name("text")
    - Action: tool_name(query="text", top_k=3)
    - Action: tool_name({"query": "text", "top_k": 3})
    - Action: tool_name(text without quotes)
    """

    ACTION_RE = re.compile(
        r"^\s*Action\s*:\s*([a-zA-Z_][\w\-]*)\s*\((.*)\)\s*$",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    FINAL_RE = re.compile(r"Final\s*Answer\s*:\s*(.*)", re.IGNORECASE | re.DOTALL)

    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools or []
        self.max_steps = max_steps
        self.history: List[Dict[str, str]] = []
        self._tool_map = {tool.get("name"): tool for tool in self.tools if tool.get("name")}

    def get_system_prompt(self) -> str:
        """
        Build the ReAct instruction prompt tailored for stock market analysis with available tools.
        """
        if self.tools:
            tool_descriptions = "\n".join(
                f"- {tool.get('name')}: {tool.get('description', 'No description provided.')}"
                for tool in self.tools
            )
        else:
            tool_descriptions = "- Không có công cụ nào. Hãy trả lời trực tiếp."

        return f"""Bạn là một chuyên gia phân tích thị trường chứng khoán cấp cao (Stock Market Analysis Agent) và Cố vấn Tài chính chuyên nghiệp.
Nhiệm vụ của bạn là cung cấp các phân tích chất lượng cao, có tính thực tiễn và dựa trên dữ liệu cho người dùng về các mã cổ phiếu, xu hướng thị trường, báo cáo tài chính, và các chỉ số kỹ thuật.

Bạn có thể sử dụng các công cụ sau:
{tool_descriptions}

### Quy trình ReAct (Thought - Action - Observation - Final Answer):
Khi cần tìm kiếm thông tin bằng công cụ, hãy tuân thủ chính xác định dạng sau:
Thought: Suy nghĩ của bạn về những gì cần phân tích tiếp theo (ví dụ: cần tìm giá cổ phiếu, xem báo cáo tài chính, chỉ số MA/RSI hoặc phân tích tin tức gần đây).
Action: tool_name(arguments)

Sau khi nhận được kết quả (Observation) từ công cụ, bạn tiếp tục phân tích hoặc kết thúc quy trình nếu đã có đủ thông tin.
Khi đã có đầy đủ thông tin để kết luận, bạn PHẢI đưa ra câu trả lời cuối cùng với định dạng chính xác sau:
Final Answer: [Câu trả lời chi tiết bằng tiếng Việt]

### Khung Phân Tích Chứng Khoán (Dành cho Final Answer):
Hãy cố gắng cấu trúc câu trả lời trong phần `Final Answer` một cách chuyên nghiệp gồm các nội dung sau:
1. **Tổng Quan**: Sơ lược về công ty/mã cổ phiếu và bối cảnh phân tích.
2. **Phân Tích Cơ Bản (Fundamental Analysis)**: Doanh thu, lợi nhuận, P/E, EPS, biên lợi nhuận, đòn bẩy tài chính hoặc các điểm nhấn từ báo cáo tài chính mới nhất.
3. **Phân Tích Kỹ Thuật (Technical Analysis)**: Xu hướng giá, các vùng hỗ trợ/kháng cự quan trọng, các chỉ báo chính (MA, RSI, MACD, v.v.) dựa trên dữ liệu lịch sử giá.
4. **Tin Tức & Tâm Lý Thị Trường**: Các sự kiện doanh nghiệp gần đây, tin tức vĩ mô hoặc tâm lý chung của nhà đầu tư đối với mã cổ phiếu này.
5. **Đánh Giá Rủi Ro**: Các rủi ro tiềm ẩn đối với doanh nghiệp/ngành nghề hoặc biến động thị trường.
6. **Khuyến Nghị Đầu Tư**: Đưa ra khuyến nghị rõ ràng (Mua/Bán/Nắm giữ) kèm theo mức giá mục tiêu (nếu có thể) và luận điểm đầu tư chi tiết.

### Quy tắc quan trọng:
- Toàn bộ nội dung suy nghĩ (Thought) và câu trả lời cuối cùng (Final Answer) PHẢI được viết bằng tiếng Việt.
- Chỉ sử dụng chính xác tên các công cụ được liệt kê ở trên. Không tự tạo ra công cụ mới.
- Chỉ sử dụng tối đa một Action trong mỗi phản hồi.
- Không tự bịa đặt hay giả lập số liệu (Observation). Hãy dựa vào kết quả thực tế từ công cụ hoặc nêu rõ nếu dữ liệu không tồn tại.
- Nếu không cần sử dụng bất kỳ công cụ nào, hãy trả lời trực tiếp ngay lập tức dưới dạng `Final Answer: [Nội dung trả lời]`.
"""

    def run(self, user_input: str) -> str:
        """
        Execute the ReAct loop until `Final Answer` or `max_steps` is reached.
        """
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

            final_answer = self._parse_final_answer(last_response)
            if final_answer is not None:
                logger.log_event("AGENT_END", {"steps": step, "status": "final_answer"})
                return final_answer.strip()

            action = self._parse_action(last_response)
            if action is None:
                # Give the model one explicit chance to recover formatting.
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

        # Best-effort fallback: ask once for a concise final answer from the accumulated context.
        fallback_prompt = self._build_prompt(
            user_input=user_input,
            scratchpad=scratchpad
            + "\nYou reached the step limit. Provide the best possible final answer now.",
        )
        fallback_response = self._generate(fallback_prompt).strip()
        final_answer = self._parse_final_answer(fallback_response)
        return (final_answer or fallback_response or last_response).strip()

    def _build_prompt(self, user_input: str, scratchpad: str) -> str:
        return f"""User request:
{user_input}

Previous reasoning, actions, and observations:
{scratchpad.strip() if scratchpad.strip() else "None yet."}

Continue the ReAct process."""

    def _generate(self, prompt: str) -> str:
        """
        Call the configured LLMProvider while staying compatible with common
        wrapper signatures used in student projects.
        """
        system_prompt = self.get_system_prompt()

        def extract_and_track(res):
            if isinstance(res, dict):
                content = res.get("content", "")
                usage = res.get("usage", {})
                latency_ms = res.get("latency_ms", 0)
                provider = res.get("provider", "unknown")
                
                # Track request in performance telemetry
                tracker.track_request(
                    provider=provider,
                    model=self.llm.model_name,
                    usage=usage,
                    latency_ms=latency_ms
                )
                return content
            return str(res)

        try:
            res = self.llm.generate(prompt, system_prompt=system_prompt)
            return extract_and_track(res)
        except TypeError:
            try:
                res = self.llm.generate(prompt, system_prompt)
                return extract_and_track(res)
            except TypeError:
                res = self.llm.generate(prompt)
                return extract_and_track(res)


    def _parse_final_answer(self, text: str) -> Optional[str]:
        match = self.FINAL_RE.search(text)
        if not match:
            return None
        return match.group(1).strip()

    def _parse_action(self, text: str) -> Optional[Tuple[str, str]]:
        match = self.ACTION_RE.search(text)
        if not match:
            return None
        tool_name = match.group(1).strip()
        raw_args = match.group(2).strip()
        return tool_name, raw_args

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Execute a registered tool by name and return a string Observation.
        """
        tool = self._tool_map.get(tool_name)
        if not tool:
            available = ", ".join(self._tool_map.keys()) or "none"
            return f"Tool `{tool_name}` not found. Available tools: {available}."

        func = self._get_tool_callable(tool)
        if func is None:
            return f"Tool `{tool_name}` has no callable function."

        try:
            parsed_args, parsed_kwargs = self._parse_tool_args(args)
            result = func(*parsed_args, **parsed_kwargs)
            return self._stringify_observation(result)
        except Exception as exc:  # Keep the agent loop alive after tool failures.
            logger.log_event(
                "AGENT_TOOL_ERROR",
                {"tool": tool_name, "args": args, "error": str(exc)},
            )
            return f"Error while executing `{tool_name}`: {exc}"

    def _get_tool_callable(self, tool: Dict[str, Any]) -> Optional[Callable[..., Any]]:
        for key in ("function", "func", "callable"):
            candidate = tool.get(key)
            if callable(candidate):
                return candidate
        return None

    def _parse_tool_args(self, raw_args: str) -> Tuple[List[Any], Dict[str, Any]]:
        """
        Convert the text inside Action parentheses into Python args/kwargs.
        Falls back to passing the raw string when parsing is not possible.
        """
        raw_args = raw_args.strip()
        if not raw_args:
            return [], {}

        # JSON object: Action: tool({"query": "hello"})
        if raw_args.startswith("{") and raw_args.endswith("}"):
            try:
                value = json.loads(raw_args)
                if isinstance(value, dict):
                    return [], value
                return [value], {}
            except json.JSONDecodeError:
                pass

        # Python literal single argument: "hello", [1, 2], {"a": 1}
        try:
            value = ast.literal_eval(raw_args)
            if isinstance(value, dict):
                return [], value
            return [value], {}
        except Exception:
            pass

        # Python-like call arguments: query="hello", top_k=3
        try:
            fake_call = ast.parse(f"_tool_call({raw_args})", mode="eval")
            call = fake_call.body
            if isinstance(call, ast.Call):
                args = [ast.literal_eval(arg) for arg in call.args]
                kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords if kw.arg}
                return args, kwargs
        except Exception:
            pass

        # Last resort: treat as one plain string argument.
        return [raw_args], {}

    def _stringify_observation(self, result: Any) -> str:
        if result is None:
            return "Tool returned no result."
        if isinstance(result, str):
            return result
        try:
            return json.dumps(result, ensure_ascii=False, indent=2)
        except TypeError:
            return str(result)
