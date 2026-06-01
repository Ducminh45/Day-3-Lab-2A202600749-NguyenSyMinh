from .stock_prices import get_stock_price
from .financial_metrics import get_financial_metrics
from .market_news import search_market_news
from .technical_indicators import get_technical_indicators

ALL_TOOLS = [
    {
        "name": "get_stock_price",
        "description": "Lay gia co phieu hien tai cua mot doanh nghiep. Dau vao la ma co phieu (vi du: 'FPT', 'TCB').",
        "function": get_stock_price,
    },
    {
        "name": "get_financial_metrics",
        "description": "Lay cac chi so tai chinh co ban nhu P/E, EPS, doanh thu, loi nhuan rong cua ma co phieu dau vao.",
        "function": get_financial_metrics,
    },
    {
        "name": "search_market_news",
        "description": "Tim kiem cac tin tuc thi truong, su kien noi bat gan day lien quan den doanh nghiep.",
        "function": search_market_news,
    },
    {
        "name": "get_technical_indicators",
        "description": "Lay cac chi chi bao ky thuat quan trong nhu RSI, duong MA20/MA50, MACD cua ma co phieu dau vao.",
        "function": get_technical_indicators,
    }
]
