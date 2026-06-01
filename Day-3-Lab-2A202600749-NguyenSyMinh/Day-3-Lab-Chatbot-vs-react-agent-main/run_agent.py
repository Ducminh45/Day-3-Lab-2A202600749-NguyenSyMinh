import os
import sys
from dotenv import load_dotenv

# Đảm bảo thư mục hiện tại nằm trong đường dẫn hệ thống
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agent.agent import ReActAgent
from src.core.openai_provider import OpenAIProvider
from src.core.gemini_provider import GeminiProvider

from src.tools import ALL_TOOLS

# ==========================================
# 2. CHƯƠNG TRÌNH CHÍNH (MAIN ENTRYPOINT)
# ==========================================

def main():
    # Tải biến môi trường từ .env
    load_dotenv()
    
    # Lấy thông số từ .env
    provider_name = os.getenv("DEFAULT_PROVIDER", "google").lower()
    
    print("=" * 60)
    print("*** CHUONG TRINH CHAY THU STOCK MARKET ANALYSIS AGENT ***")
    print("=" * 60)
    
    # Sử dụng các công cụ được nhập từ thư mục src/tools
    tools = ALL_TOOLS
    
    # Khởi tạo LLM Provider phù hợp
    if provider_name == "google":
        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")
        print(f"[INFO] Dang su dung Provider: Google Gemini ({model})")
        if not api_key:
            print("[WARNING] Loi: Khong tim thay GEMINI_API_KEY trong file .env.")
            return
        provider = GeminiProvider(model_name=model, api_key=api_key)
    elif provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("DEFAULT_MODEL", "gpt-4o")
        print(f"[INFO] Dang su dung Provider: OpenAI ({model})")
        if not api_key or "your_openai" in api_key:
            print("[WARNING] Loi: Khong tim thay hoac chua thay the OPENAI_API_KEY hop le trong file .env.")
            print("[TIP] Meo: Ban co the doi sang 'google' lam DEFAULT_PROVIDER trong file .env vi ban da co san khoa Gemini.")
            return
        provider = OpenAIProvider(model_name=model, api_key=api_key)
    else:
        print(f"[WARNING] Provider {provider_name} chua duoc ho tro hoan chinh trong script chay thu nay.")
        return

    # Khởi tạo ReAct Agent
    agent = ReActAgent(llm=provider, tools=tools, max_steps=8)
    
    print("\nAgent phan tich da san sang! Mot so goi y cau hoi phan tich:")
    print("1. 'Hay phan tich co phieu FPT va dua ra khuyen nghi dau tu.'")
    print("2. 'Xem xet va danh gia ca mat co ban lan ky thuat cua co phieu HPG.'")
    print("3. 'So sanh co phieu TCB va FPT, ma nao dang tot hon?'")
    print("-" * 60)
    
    while True:
        try:
            # Dung ky tu tieu chuan de khong bi loi tren cmd/powershell Windows
            user_query = input("\n[USER] Nhap yeu cau phan tich cua ban (hoac go 'exit' de thoat): ")
            if user_query.strip().lower() == "exit":
                print("[BYE] Tam biet!")
                break
            if not user_query.strip():
                continue
                
            print("\n[AGENT] Agent dang thuc hien suy luan ReAct va goi cac cong cu lien quan...")
            print("-" * 40)
            
            # Chạy Agent
            result = agent.run(user_query)
            
            print("\n" + "=" * 60)
            print("[RESULT] KET QUA PHAN TICH CUOI CUNG TU AGENT (STOCK MARKET REPORT):")
            print("=" * 60)
            print(result)
            print("=" * 60)
            
        except KeyboardInterrupt:
            print("\n[BYE] Da dung chuong trinh.")
            break
        except Exception as e:
            print(f"\n[ERROR] Co loi xay ra trong qua trinh chay: {e}")

if __name__ == "__main__":
    main()
