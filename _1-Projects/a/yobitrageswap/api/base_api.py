class BaseAPI:
    def __init__(self, name: str):
        self.name = name

    def connect(self):
        raise NotImplementedError("connect() must be implemented")

    def fetch_orderbook(self, symbol: str):
        """Return dict with keys: bids, asks. Each: list[(price, qty)]."""
        raise NotImplementedError("fetch_orderbook() must be implemented")

    def place_order(self, symbol: str, side: str, qty: float, price: float | None = None):
        """side in {'buy','sell'}; price optional for market orders."""
        raise NotImplementedError("place_order() must be implemented")
