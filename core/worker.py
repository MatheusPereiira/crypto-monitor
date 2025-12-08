# core/worker.py

import json
import threading
from collections import defaultdict, deque

from PyQt6.QtCore import QObject, pyqtSignal, QMutex

from binance.spot import Spot
from websocket import WebSocketApp

from core.utils import POPULAR_NAMES


class BinanceWorker(QObject):
    data_updated = pyqtSignal(dict)
    data_state = defaultdict(dict)
    mutex = QMutex()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.client = Spot()   # REST sem autenticação
        self.ws = None
        self.keep_running = True
        self.thread = None

    # ----------------------------------------------------
    # REST → coleta inicial
    # ----------------------------------------------------

    def get_top_symbols(self):
        try:
            tickers = self.client.ticker_24hr()
            valid = list(POPULAR_NAMES.keys())

            usdt_pairs = [
                t for t in tickers
                if t["symbol"].endswith("USDT") and t["symbol"][:-4] in valid
            ]

            top = sorted(
                usdt_pairs,
                key=lambda x: float(x.get("quoteVolume", 0)),
                reverse=True
            )[:len(valid)]

            self.mutex.lock()
            for t in top:
                s = t["symbol"]

                self.data_state[s] = {
                    "price": float(t["lastPrice"]),
                    "open_price": float(t["openPrice"]),
                    "price_change_percent": float(t["priceChangePercent"]),
                    "high_price": float(t["highPrice"]),
                    "low_price": float(t["lowPrice"]),
                    "volume": float(t["volume"]),
                    "last_price": float(t["lastPrice"]),
                    "trend": "flat",
                    "history": deque(maxlen=200)
                }
            self.mutex.unlock()

            return [t["symbol"] for t in top]

        except Exception:
            return [f"{s}USDT" for s in POPULAR_NAMES.keys()]

    # ----------------------------------------------------
    # WebSocket — mensagem recebida
    # ----------------------------------------------------

    def _on_message(self, ws, msg):
        try:
            msg = json.loads(msg)
            data = msg.get("data", {})
            if "s" not in data:
                return

            symbol = data["s"]
            price = float(data["c"])

            self.mutex.lock()

            last = self.data_state[symbol].get("last_price", price)
            trend = "up" if price > last else "down" if price < last else "flat"

            if "history" not in self.data_state[symbol]:
                self.data_state[symbol]["history"] = deque(maxlen=200)

            self.data_state[symbol].update({
                "price": price,
                "open_price": float(data["o"]),
                "price_change_percent": float(data["P"]),
                "high_price": float(data["h"]),
                "low_price": float(data["l"]),
                "volume": float(data["v"]),
                "last_price": price,
                "trend": trend
            })

            self.data_state[symbol]["history"].append(price)

            self.mutex.unlock()

            self.data_updated.emit(self.data_state)

        except Exception:
            try:
                self.mutex.unlock()
            except:
                pass

    # ----------------------------------------------------
    # Iniciar WebSocket
    # ----------------------------------------------------

    def run(self):
        symbols = self.get_top_symbols()
        streams = "/".join([f"{s.lower()}@ticker" for s in symbols])

        url = f"wss://stream.binance.com:9443/stream?streams={streams}"

        self.ws = WebSocketApp(
            url,
            on_message=self._on_message
        )

        self.thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        self.thread.start()

    # ----------------------------------------------------
    # Parar de forma segura
    # ----------------------------------------------------

    def stop(self):
        self.keep_running = False
        try:
            if self.ws:
                self.ws.close()
        except:
            pass

        try:
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=1)
        except:
            pass
