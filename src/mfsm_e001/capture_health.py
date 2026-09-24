"""Source-specific capture diagnostics; monotonic IDs aren't proof of completeness."""


class FeedError(ValueError):
    pass


class FeedMonitor:
    def __init__(self, source, topics):
        self.source = source
        self.topics = topics
        self.books = {}
        self.binance_id = None
        self.ticker_snapshot = False

    def validate_scope(self, message):
        """Reject out-of-scope observations before writing any payload to disk."""
        if not isinstance(message, dict):
            raise FeedError("non-object message")
        if self.source == "binance_spot":
            stream = message.get("stream")
            if stream not in self.topics:
                raise FeedError("unexpected Binance stream")
            data = message["data"]
            if data.get("s") != "BTCUSDT":
                raise FeedError("non-BTC symbol rejected")
            return
        topic = message.get("topic")
        if topic is None:
            if "data" in message:
                raise FeedError("unexpected unscoped Bybit observations")
            return
        if topic not in self.topics:
            raise FeedError("unexpected Bybit topic")
        data = message["data"]
        rows = data if isinstance(data, list) else [data]
        if any(row.get("s", row.get("symbol")) != "BTCUSDT" for row in rows):
            raise FeedError("non-BTC symbol rejected")

    def inspect(self, message):
        """Return diagnostics; fail on broken ordering without modifying raw data."""
        self.validate_scope(message)
        if self.source == "binance_spot":
            data = message["data"]
            if data.get("e") == "depthUpdate":
                first, last = int(data["U"]), int(data["u"])
                if first > last:
                    raise FeedError("invalid depth update range")
                if self.binance_id is not None:
                    if last <= self.binance_id:
                        return [{"kind": "duplicate_or_old_depth", "last_id": last}]
                    if first > self.binance_id + 1:
                        raise FeedError("Binance depth sequence gap")
                self.binance_id = last
            return []
        topic = message.get("topic")
        if topic is None:
            if message.get("success") is False:
                raise FeedError("Bybit rejected request")
            return []  # Subscription/heartbeat envelopes have no market observations.
        data = message["data"]
        if topic.startswith("orderbook."):
            current = int(data["u"]), int(data["seq"])
            if message["type"] == "snapshot":
                self.books[topic] = current
                return [{"kind": "book_snapshot_reset", "topic": topic,
                         "update_id": current[0], "sequence": current[1]}]
            if message["type"] != "delta" or topic not in self.books:
                raise FeedError("book delta without snapshot")
            previous = self.books[topic]
            if current[0] <= previous[0] or current[1] <= previous[1]:
                raise FeedError("Bybit book ID regression or unexpected duplicate delta")
            # Bybit does not document a +1 guarantee for these streams.
            self.books[topic] = current
        elif topic.startswith("tickers."):
            if message["type"] == "snapshot":
                self.ticker_snapshot = True
            elif message["type"] != "delta" or not self.ticker_snapshot:
                raise FeedError("ticker delta without snapshot")
        return []
