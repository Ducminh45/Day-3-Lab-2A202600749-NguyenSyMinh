def search_market_news(ticker: str) -> str:
    """Tìm kiếm tin tức và sự kiện nóng gần đây về doanh nghiệp."""
    ticker = ticker.upper().strip()
    mock_news = {
        "FPT": "- FPT ky ket hop dong xuat khau phan mem tri gia 100 trieu USD voi doi tac My.\n- Doanh nghiep du kien chia co tuc tien mat 20% trong quy toi.\n- Xu huong tich cuc tu lan song AI va ban dan.",
        "TCB": "- Techcombank len ke hoach phat hanh co phieu thuong ty le 100%.\n- Ket qua kinh doanh quy 1 vuot 15% so voi ky vong cua cac cong ty chung khoan.\n- Lai suat huy dong co xu huong nhich nhe.",
        "VCB": "- Vietcombank duoc chap thuan tang von dieu le len hon 55,000 ty VND.\n- Giu vung vi the ngan hang co loi nhuan cao nhat he thong.",
        "HPG": "- Hoa Phat khoi dong lai lo cao so 3 tai Dung Quat giup gia tang cong suat.\n- Gia thep the gioi phuc hoi nhe ho tro bien loi nhuan gop.\n- Chi phi nguyen lieu dau vao (quang sat, than coc) dang di ngang.",
    }
    return mock_news.get(ticker, f"Tin tuc gan day ve {ticker}: Cong ty dang hoat dong on dinh, chua ghi nhan tin tuc vi mo hay su kiem bat thuong nao moi (Du lieu gia lap).")
