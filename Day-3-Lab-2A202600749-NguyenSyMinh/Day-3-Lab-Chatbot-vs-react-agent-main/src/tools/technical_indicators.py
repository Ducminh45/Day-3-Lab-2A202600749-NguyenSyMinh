def get_technical_indicators(ticker: str) -> str:
    """Lấy các chỉ báo phân tích kỹ thuật quan trọng (RSI, MA20, MA50, MACD)."""
    ticker = ticker.upper().strip()
    mock_tech = {
        "FPT": "RSI: 62 (Xu huong tang khoe, chua qua mua), MA20: 132,000 VND, MA50: 128,000 VND (Gia nam tren cac duong MA lon the hien xu huong tang dai han ro ret), MACD: Cat len duong tin hieu cho tin hieu MUA tiep tuc.",
        "TCB": "RSI: 48 (Trung tinh, dang tich luy di ngang), MA20: 49,000 VND, MA50: 47,800 VND (Gia dang kiem dinh duong MA20), MACD: Dang hoi tu quanh moc 0.",
        "VCB": "RSI: 55 (Xu huong tang nhe), MA20: 91,500 VND, MA50: 90,800 VND, MACD: Cho tin hieu tich luy tich cuc.",
        "HPG": "RSI: 68 (Sap tiem can vung qua mua, luc mua manh), MA20: 28,200 VND, MA50: 27,500 VND, MACD: Cat len manh me, dong tien vao cai thien ro ret.",
    }
    return mock_tech.get(ticker, f"Chi bao ky thuat cua {ticker}: RSI: 50 (Trung tinh), MA20 dang di ngang, xu huong tich luy (Du lieu gia lap).")
