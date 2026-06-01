def get_stock_price(ticker: str) -> str:
    """Lấy giá cổ phiếu hiện tại của một doanh nghiệp."""
    ticker = ticker.upper().strip()
    mock_prices = {
        "FPT": "135,200 VND (Tang 1.5% so voi hom qua)",
        "TCB": "48,500 VND (Giam 0.8% so voi hom qua)",
        "VCB": "92,000 VND (Khong doi)",
        "HPG": "29,100 VND (Tang 2.1% so voi hom qua)",
        "VNM": "68,400 VND (Giam 0.5% so voi hom qua)",
    }
    return mock_prices.get(ticker, f"Gia hien tai cua co phieu {ticker} la 50,000 VND (Du lieu gia lap).")
