# ui/graph_window.py
import requests
import datetime
from PyQt6.QtWidgets import QDialog, QVBoxLayout
from PyQt6.QtCore import Qt
import pyqtgraph as pg


class GraphWindow(QDialog):
    def __init__(self, parent=None, symbol="BTCUSDT"):
        super().__init__(parent)

        self.symbol = symbol
        self.setWindowTitle(f"Gráfico - {symbol}")
        self.setMinimumSize(900, 500)

        layout = QVBoxLayout(self)

        # Criação do widget de gráfico
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setBackground('#1e1e1e')
        self.plot_widget.getAxis("left").setTextPen("white")
        self.plot_widget.getAxis("bottom").setTextPen("white")

        layout.addWidget(self.plot_widget)

        # Carregar dados
        self.load_graph()

    def load_graph(self):
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {
                "symbol": self.symbol,
                "interval": "1m",
                "limit": 120
            }
            response = requests.get(url, params=params)
            data = response.json()

            # Se a API retornar erro
            if isinstance(data, dict) and "code" in data:
                print("Erro Binance API:", data)
                return

            timestamps = []
            prices = []

            for candle in data:
                open_time = candle[0] / 1000
                price = float(candle[4])  # preço de fechamento
                timestamps.append(datetime.datetime.fromtimestamp(open_time))
                prices.append(price)

            # Limpar gráfico
            self.plot_widget.clear()

            # Plotar
            self.plot_widget.plot(
                list(range(len(prices))),
                prices,
                pen=pg.mkPen('#00ff80', width=2)
            )

        except Exception as e:
            print("Erro ao gerar gráfico:", e)
