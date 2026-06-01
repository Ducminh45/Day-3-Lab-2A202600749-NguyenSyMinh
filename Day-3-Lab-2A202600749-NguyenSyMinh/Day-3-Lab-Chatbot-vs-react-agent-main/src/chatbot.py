import time
from typing import Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker

class Chatbot:
    """
    Chatbot baseline: gọi LLM 1 lần, không dùng tools.
    """
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def run(self, user_input: str) -> str:
        """
        Runs the chatbot on a user query with exactly one LLM call.
        """
        logger.log_event(
            "CHATBOT_START",
            {"input": user_input, "model": getattr(self.llm, "model_name", "unknown")},
        )
        
        system_prompt = (
            "Bạn là một chuyên gia phân tích thị trường chứng khoán cấp cao (Stock Market Analysis Agent) và Cố vấn Tài chính chuyên nghiệp.\n"
            "Nhiệm vụ của bạn là cung cấp các phân tích chất lượng cao, có tính thực tiễn và dựa trên dữ liệu cho người dùng về các mã cổ phiếu, xu hướng thị trường, báo cáo tài chính, và các chỉ số kỹ thuật.\n"
            "Vì bạn là một Chatbot thông thường không có công cụ bổ trợ, hãy cố gắng sử dụng kiến thức sẵn có của bạn một cách tốt nhất để trả lời câu hỏi của người dùng.\n"
            "Toàn bộ câu trả lời PHẢI được viết bằng tiếng Việt.\n\n"
            "### Khung Phân Tích Chứng Khoán Gợi Ý:\n"
            "1. Tổng Quan về mã cổ phiếu/doanh nghiệp.\n"
            "2. Phân Tích Cơ Bản (Fundamental Analysis) dựa trên thông tin đã biết.\n"
            "3. Phân Tích Kỹ Thuật (Technical Analysis) định hướng.\n"
            "4. Đánh Giá Rủi Ro & Khuyến Nghị đầu tư chi tiết."
        )

        try:
            start_time = time.time()
            
            # Call the LLM provider
            res = self.llm.generate(user_input, system_prompt=system_prompt)
            
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            
            content = ""
            usage = {}
            provider = "unknown"
            
            if isinstance(res, dict):
                content = res.get("content", "")
                usage = res.get("usage", {})
                latency_ms = res.get("latency_ms", latency_ms)
                provider = res.get("provider", "unknown")
            else:
                content = str(res)
            
            # Track request metrics in telemetry database
            tracker.track_request(
                provider=provider,
                model=self.llm.model_name,
                usage=usage,
                latency_ms=latency_ms
            )
            
            logger.log_event(
                "CHATBOT_END",
                {
                    "status": "success",
                    "latency_ms": latency_ms,
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                }
            )
            return content.strip()
            
        except Exception as e:
            logger.log_event("CHATBOT_ERROR", {"error": str(e)})
            logger.error(f"Error in Chatbot run: {e}")
            raise e
