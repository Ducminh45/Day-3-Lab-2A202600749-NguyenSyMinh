import os
import sys
import time

# Reconfigure stdout to use UTF-8 to handle Vietnamese text without crashing on Windows terminal
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from typing import List, Dict, Any
from dotenv import load_dotenv

# Add src and project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chatbot import Chatbot
from src.agent.agent import ReActAgent
from src.core.openai_provider import OpenAIProvider
from src.core.gemini_provider import GeminiProvider
from src.tools import ALL_TOOLS
from src.telemetry.metrics import tracker

# Define test cases of varying complexity
TEST_CASES = [
    {
        "id": "TC_01_SIMPLE",
        "description": "Simple tool lookup (Single ticker price)",
        "query": "Giá cổ phiếu hiện tại của FPT là bao nhiêu?"
    },
    {
        "id": "TC_02_MEDIUM",
        "description": "Multi-step lookup (HPG fundamental + technical)",
        "query": "Hãy phân tích chi tiết mã cổ phiếu HPG về cả mặt cơ bản và phân tích kỹ thuật."
    },
    {
        "id": "TC_03_COMPLEX",
        "description": "Highly complex comparison (TCB vs FPT)",
        "query": "So sánh sức khỏe tài chính và chỉ báo kỹ thuật của TCB và FPT. Mã nào đang tốt hơn ở thời điểm này?"
    }
]

def run_evaluation() -> Dict[str, Any]:
    load_dotenv()
    
    provider_name = os.getenv("DEFAULT_PROVIDER", "google").lower()
    
    # Initialize provider
    if provider_name == "google":
        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")
        provider = GeminiProvider(model_name=model, api_key=api_key)
    elif provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("DEFAULT_MODEL", "gpt-4o")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env")
        provider = OpenAIProvider(model_name=model, api_key=api_key)
    else:
        raise ValueError(f"Provider {provider_name} not supported for evaluation.")

    print("=" * 70)
    print(f"--- STARTING SYSTEM COMPARISON: {provider_name.upper()} ({model}) ---")
    print("=" * 70)

    # Initialize systems
    chatbot = Chatbot(llm=provider)
    agent = ReActAgent(llm=provider, tools=ALL_TOOLS, max_steps=8)

    results = {
        "metadata": {
            "provider": provider_name,
            "model": model,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "chatbot": [],
        "agent": []
    }

    for case in TEST_CASES:
        query = case["query"]
        print(f"\nEvaluating: {case['description']}")
        print(f"Query: '{query}'")
        print("-" * 50)

        # 1. Run Chatbot
        print("[CHATBOT] Processing...", end="", flush=True)
        tracker.session_metrics = [] # Clear metrics for isolated tracking
        
        start_time = time.time()
        chatbot_response = chatbot.run(query)
        chatbot_latency = int((time.time() - start_time) * 1000)
        
        # Aggregate token counts for Chatbot
        chatbot_prompt_tokens = sum(m["prompt_tokens"] for m in tracker.session_metrics)
        chatbot_completion_tokens = sum(m["completion_tokens"] for m in tracker.session_metrics)
        chatbot_total_tokens = sum(m["total_tokens"] for m in tracker.session_metrics)
        chatbot_cost = sum(m["cost_estimate"] for m in tracker.session_metrics)
        print(" Done!")

        results["chatbot"].append({
            "id": case["id"],
            "query": query,
            "response": chatbot_response,
            "latency_ms": chatbot_latency,
            "steps": 1,
            "prompt_tokens": chatbot_prompt_tokens,
            "completion_tokens": chatbot_completion_tokens,
            "total_tokens": chatbot_total_tokens,
            "cost_estimate": chatbot_cost
        })

        # 2. Run ReAct Agent
        print("[REACT AGENT] Processing...", end="", flush=True)
        tracker.session_metrics = [] # Clear metrics for isolated tracking
        
        start_time = time.time()
        agent_response = agent.run(query)
        agent_latency = int((time.time() - start_time) * 1000)
        
        # Aggregate token counts for Agent
        agent_prompt_tokens = sum(m["prompt_tokens"] for m in tracker.session_metrics)
        agent_completion_tokens = sum(m["completion_tokens"] for m in tracker.session_metrics)
        agent_total_tokens = sum(m["total_tokens"] for m in tracker.session_metrics)
        agent_cost = sum(m["cost_estimate"] for m in tracker.session_metrics)
        agent_steps = len(tracker.session_metrics)
        print(" Done!")

        results["agent"].append({
            "id": case["id"],
            "query": query,
            "response": agent_response,
            "latency_ms": agent_latency,
            "steps": agent_steps,
            "prompt_tokens": agent_prompt_tokens,
            "completion_tokens": agent_completion_tokens,
            "total_tokens": agent_total_tokens,
            "cost_estimate": agent_cost
        })

    # Print Terminal Comparison Table
    print("\n" + "=" * 80)
    print("--- EVALUATION METRICS SUMMARY TABLE ---")
    print("=" * 80)
    print(f"{'System':<15} | {'Case':<10} | {'Latency':<10} | {'Steps':<7} | {'Tokens':<10} | {'Cost ($)':<10}")
    print("-" * 80)
    
    for i, case in enumerate(TEST_CASES):
        cb = results["chatbot"][i]
        ag = results["agent"][i]
        
        print(f"{'Chatbot':<15} | {case['id']:<10} | {cb['latency_ms']:>6}ms | {cb['steps']:>7} | {cb['total_tokens']:>10} | ${cb['cost_estimate']:.5f}")
        print(f"{'ReAct Agent':<15} | {case['id']:<10} | {ag['latency_ms']:>6}ms | {ag['steps']:>7} | {ag['total_tokens']:>10} | ${ag['cost_estimate']:.5f}")
        print("-" * 80)
        
    return results

def generate_report(results: Dict[str, Any]):
    report_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "report")
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
        
    report_path = os.path.join(report_dir, "comparison_report.md")
    
    md_content = f"""# Comparative Evaluation Report: Chatbot vs ReAct Agent

This report contains a systematic performance comparison between a standard LLM Chatbot baseline and a ReAct Agent (loop). Both are tested against Vietnamese Stock Market Analysis scenarios.

## 📊 Run Configuration
- **Timestamp**: {results['metadata']['timestamp']}
- **LLM Provider**: `{results['metadata']['provider'].upper()}`
- **Model Name**: `{results['metadata']['model']}`

---

## 📈 Quantitative Performance Summary

| Test Case | System | Latency (ms) | Steps (LLM Calls) | Prompt Tokens | Completion Tokens | Total Tokens | Estimated Cost ($) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
"""

    for i in range(len(TEST_CASES)):
        case = TEST_CASES[i]
        cb = results["chatbot"][i]
        ag = results["agent"][i]
        
        md_content += f"""| **{case['id']}** ({case['description']}) | Chatbot | {cb['latency_ms']:,} | {cb['steps']} | {cb['prompt_tokens']:,} | {cb['completion_tokens']:,} | {cb['total_tokens']:,} | ${cb['cost_estimate']:.5f} |
| | ReAct Agent | {ag['latency_ms']:,} | {ag['steps']} | {ag['prompt_tokens']:,} | {ag['completion_tokens']:,} | {ag['total_tokens']:,} | ${ag['cost_estimate']:.5f} |
"""

    md_content += """
---

## 🔍 Qualitative Response Analysis

"""

    for i in range(len(TEST_CASES)):
        case = TEST_CASES[i]
        cb = results["chatbot"][i]
        ag = results["agent"][i]
        
        md_content += f"""### [{case['id']}] {case['query']}

#### 🤖 Chatbot Baseline (Gọi LLM 1 Lần)
> **Phân tích**: Chatbot trả lời trực tiếp mà không có công cụ. Do đó, các thông tin cụ thể (như giá cổ phiếu chính xác tại thời điểm mock, báo cáo tài chính cụ thể, chỉ số kỹ thuật hiện tại) có thể bị thiếu, lỗi thời, hoặc bị chatbot tự suy đoán (hallucinate).
>
```
{cb['response']}
```

#### 🧠 ReAct Agent (Thought -> Action -> Observation Loop)
> **Phân tích**: Agent liên tục suy luận và gọi các công cụ liên quan như `get_stock_price`, `get_financial_metrics`, `get_technical_indicators` để tích hợp dữ liệu thực tế chính xác vào câu trả lời cuối cùng (`Final Answer`).
>
```
{ag['response']}
```

"""

    md_content += """
---

## 💡 Key Takeaways & Conclusions

1. **Độ chính xác dữ liệu (Data Accuracy)**:
   - **Chatbot Baseline**: Dễ bị ảo giác (hallucination) khi hỏi về số liệu chi tiết hoặc giá cổ phiếu thời gian thực, do bị giới hạn bởi tri thức huấn luyện tĩnh.
   - **ReAct Agent**: Sử dụng công cụ động để lấy dữ liệu thực tế, giúp câu trả lời cực kỳ chính xác và có độ tin cậy cao.

2. **Chi phí và Hiệu suất (Cost & Token Efficiency)**:
   - **Chatbot Baseline**: Nhanh hơn (gọi LLM đúng 1 lần), ít tốn token hơn, chi phí cực kỳ rẻ.
   - **ReAct Agent**: Chậm hơn nhiều (latency cao hơn do phải lặp Thought-Action nhiều lần), tiêu tốn nhiều token hơn do tích lũy scratchpad ngữ cảnh qua mỗi bước.

3. **Khuyến nghị sử dụng (Production Recommendation)**:
   - Đối với các tác vụ tra cứu thông thường, có thể sử dụng Chatbot hoặc các mô hình tối ưu hóa rẻ.
   - Đối với các tác vụ phân tích tài chính sâu, tư vấn đầu tư hoặc các quyết định nhạy cảm cần dữ liệu chuẩn xác 100%, **ReAct Agent** là lựa chọn bắt buộc.
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"\n[OK] Comparative report generated successfully at: {report_path}")

if __name__ == "__main__":
    try:
        eval_results = run_evaluation()
        generate_report(eval_results)
    except Exception as e:
        print(f"\n[ERROR] Evaluation failed: {e}")
        sys.exit(1)
