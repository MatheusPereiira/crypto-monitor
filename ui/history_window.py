# ui/history_window.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
except Exception:
    Figure = None
    FigureCanvas = None
import json, os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PRICE_HISTORY_FILE = os.path.join(BASE_DIR, 'resources', 'price_history.json')

class HistoryDialog(QDialog):
    def __init__(self, parent=None, symbol=None):
        super().__init__(parent)
        self.setWindowTitle(f'Histórico - {symbol}')
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout(self)

        if Figure is None or FigureCanvas is None:
            layout.addWidget(QLabel('matplotlib não está instalado. Instale matplotlib para visualizar gráficos.'))
            return

        # load price history
        try:
            with open(PRICE_HISTORY_FILE, 'r', encoding='utf-8') as f:
                p = json.load(f)
        except Exception:
            p = {}

        series = p.get(symbol, [])
        if not series:
            layout.addWidget(QLabel('Sem histórico para este símbolo.'))
            return

        fig = Figure(figsize=(6,4))
        ax = fig.add_subplot(111)
        ax.plot(series)
        ax.set_title(symbol)
        ax.set_ylabel('Preço (USDT)')
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
