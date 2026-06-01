def get_financial_metrics(ticker: str) -> str:
    """Lấy các chỉ số tài chính cơ bản của một doanh nghiệp (P/E, EPS, Doanh thu, Lợi nhuận)."""
    ticker = ticker.upper().strip()
    mock_metrics = {
        "FPT": "P/E: 22.4, EPS: 6,035 VND, Tang truong doanh thu: 19.6%, Loi nhuan sau thue nam qua: 7,796 ty VND, Bien loi nhuan gop: 38%.",
        "TCB": "P/E: 9.5, EPS: 5,100 VND, Loi nhuan truoc thue nam qua: 22,900 ty VND, Ty le no xau (NPL): 1.1%, CAR: 14%.",
        "VCB": "P/E: 15.2, EPS: 6,050 VND, Loi nhuan sau thue nam qua: 33,000 ty VND, Ty le no xau (NPL): 0.9%.",
        "HPG": "P/E: 16.8, EPS: 1,732 VND, San luong thep tieu thu tang 15% so voi cung ky, Loi nhuan sau thue nam qua: 6,800 ty VND.",
    }
    return mock_metrics.get(ticker, f"Chi so tai chinh cua {ticker}: P/E: 12.5, EPS: 4,000 VND, Tang truong doanh thu: 10% (Du lieu gia lap).")
