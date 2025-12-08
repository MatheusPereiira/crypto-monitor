# ui/main_window.py
import json
import os
from collections import deque

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout,
    QDialog, QSizePolicy, QAbstractItemView
)
from PyQt6.QtCore import Qt, QTimer, QVariant, QThread
from PyQt6.QtGui import QColor, QBrush

from core.worker import BinanceWorker
from core.alerts import AlertManager
from core.utils import POPULAR_NAMES, format_volume
from ui.alert_window import AlertConfigWindow
from ui.graph_window import GraphWindow
from ui.style import STYLE_DARK


class CryptoMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitor de Criptomoedas - Binance (Tempo Real) v1.1")
        self.setGeometry(80, 40, 1200, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.alert_manager = AlertManager()
        self.worker = None
        self.worker_thread = None

        self.setup_ui()
        self.apply_style()

        # THREAD DO WORKER
        self.worker_thread = QThread()
        self.worker = BinanceWorker()
        self.worker.moveToThread(self.worker_thread)
        self.worker.data_updated.connect(self.update_table)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

        # TIMER PARA VERIFICAR ALERTAS
        self.alert_timer = QTimer(self)
        self.alert_timer.timeout.connect(self._check_alerts)
        self.alert_timer.start(1000)

    # ================================================================
    # INTERFACE PRINCIPAL
    # ================================================================
    def setup_ui(self):
        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget)
        control_layout.setContentsMargins(0, 0, 0, 0)

        # Pesquisa
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Pesquisar moeda (ex: BTC, Ethereum...)")
        self.filter_input.textChanged.connect(self.filter_table)
        self.filter_input.setMaximumHeight(32)
        control_layout.addWidget(self.filter_input, 1)

        # -------------------------------------------------------------
        # ORDEM DOS BOTÕES: FAVORITOS → GRÁFICO → ALERTA → LIMPAR
        # -------------------------------------------------------------
        self.fav_button = QPushButton("Favoritos ⭐")
        control_layout.addWidget(self.fav_button)

        self.graph_button = QPushButton("Mostrar Gráfico")
        self.graph_button.clicked.connect(self.open_graph)
        control_layout.addWidget(self.graph_button)

        self.alert_button = QPushButton("Configurar Alerta")
        self.alert_button.clicked.connect(self.open_alert_config)
        control_layout.addWidget(self.alert_button)

        self.clear_alerts_button = QPushButton("Limpar Alertas")
        self.clear_alerts_button.clicked.connect(self.clear_all_alerts)
        control_layout.addWidget(self.clear_alerts_button)

        self.layout.addWidget(control_widget)

        # ======================================================
        # TABELA PRINCIPAL
        # ======================================================
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Nome", "Símbolo", "Preço Atual (USDT)", "Variação % (24h)",
            "Volume (24h)", "Preço Máx (24h)", "Preço Mín (24h)"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        # Seleção estilo dark
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #444 !important;
                color: white !important;
            }
        """)

        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.layout.addWidget(self.table, 1)

        # ======================================================
        # PAINEL DE ALERTAS
        # ======================================================
        self.alert_panel = QLabel()
        self.alert_panel.setWordWrap(True)
        self.alert_panel.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.alert_panel.setStyleSheet("""
            background-color: #2e2e2e;
            color: #eaeaea;
            border: 1px solid #444;
            padding: 12px;
            margin-top: 12px;
            font-size: 12pt;
            border-radius: 6px;
        """)
        self.layout.addWidget(self.alert_panel)
        self.update_alert_panel()

        self._symbol_to_row = {}

    # ================================================================
    # ALERTAS
    # ================================================================
    def update_alert_panel(self):
        active = getattr(self.alert_manager, "active_alerts", [])
        if not active:
            self.alert_panel.setText("<b>Alertas Ativos:</b><br>Nenhum alerta ativo.")
            return

        alert_text = "<b>Alertas Ativos:</b><br>"
        for alert in active:
            s = alert.get('symbol', '').replace('USDT', '')
            cond = alert.get('condition', '')
            val = alert.get('value', 0)
            color = "#1fff53" if "Acima" in cond else "#ff3c3c"
            formatted = f"{val:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')
            alert_text += f"<span style='color:{color};'>• {s}</span> | {cond} <b>{formatted}</b><br>"

        self.alert_panel.setText(alert_text)

    # ================================================================
    # FILTRO
    # ================================================================
    def filter_table(self, text: str):
        text = text.lower().strip()
        for r in range(self.table.rowCount()):
            name = self.table.item(r, 0)
            sym = self.table.item(r, 1)
            visible = (text in name.text().lower()) or (text in sym.text().lower())
            self.table.setRowHidden(r, not visible)

    # ================================================================
    # CONFIGURAR ALERTA
    # ================================================================
    def open_alert_config(self):
        if not self.worker or not getattr(self.worker, "data_state", None):
            QMessageBox.warning(self, "Erro", "Aguarde o carregamento dos dados.")
            return

        dialog = AlertConfigWindow(self, symbols=sorted(self.worker.data_state.keys()))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            alert_data = dialog.get_alert_data()
            self.alert_manager.active_alerts.append(alert_data)
            self.alert_manager.save_alerts()
            self.update_alert_panel()

    # ================================================================
    # LIMPAR ALERTAS
    # ================================================================
    def clear_all_alerts(self):
        self.alert_manager.active_alerts = []
        self.alert_manager.save_alerts()
        self.update_alert_panel()
        QMessageBox.information(self, "OK", "Todos os alertas foram removidos.")

    # ================================================================
    # CHECAR ALERTAS
    # ================================================================
    def _check_alerts(self):
        try:
            self.alert_manager.check_alerts(self, self.worker.data_state)
        except:
            pass
        self.update_alert_panel()

    # ================================================================
    # APLICAR STYLE DARK
    # ================================================================
    def apply_style(self):
        self.setStyleSheet(STYLE_DARK)

    # ================================================================
    # ATUALIZA TABELA
    # ================================================================
    def update_table(self, data_state: dict):
        try:
            self.table.setSortingEnabled(False)
            symbols = sorted(data_state.keys())
            self.table.setRowCount(len(symbols))
            self._symbol_to_row.clear()

            for row, symbol in enumerate(symbols):
                d = data_state[symbol]
                base = symbol.replace("USDT", "")
                name = POPULAR_NAMES.get(base, base)

                # Nome
                item = QTableWidgetItem(name)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 0, item)

                # Símbolo
                item = QTableWidgetItem(base)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 1, item)

                # Preço
                price = d.get("price", 0.0)
                s = f"{price:,.4f}" if price < 10 else f"{price:,.2f}"
                s = s.replace('.', '#').replace(',', '.').replace('#', ',')
                item = QTableWidgetItem(s)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 2, item)

                # Variação %
                perc = d.get("price_change_percent", 0.0)
                ps = f"{perc:.2f}%".replace('.', ',')
                item = QTableWidgetItem(ps)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QBrush(QColor("#1fff53") if perc >= 0 else QColor("#ff3c3c")))
                self.table.setItem(row, 3, item)

                # Volume
                vol = d.get("volume", 0.0)
                item = QTableWidgetItem(format_volume(vol))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 4, item)

                # High
                hv = d.get("high_price", 0.0)
                s = f"{hv:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')
                item = QTableWidgetItem(s)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 5, item)

                # Low
                lv = d.get("low_price", 0.0)
                s = f"{lv:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')
                item = QTableWidgetItem(s)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 6, item)

                self._symbol_to_row[symbol] = row

            self.table.setSortingEnabled(True)

        except Exception as e:
            print("Erro update_table:", e)

    # ================================================================
    # ABRE JANELA DO GRÁFICO
    # ================================================================
    def open_graph(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erro", "Selecione uma criptomoeda.")
            return

        symbol_item = self.table.item(row, 1)
        if not symbol_item:
            QMessageBox.warning(self, "Erro", "Erro ao obter símbolo.")
            return

        symbol = symbol_item.text().upper() + "USDT"

        window = GraphWindow(symbol)
        window.exec()

    # ================================================================
    # FECHAR PROGRAMA
    # ================================================================
    def closeEvent(self, event):
        try:
            self.alert_manager.save_alerts()
        except:
            pass

        try:
            if self.worker:
                self.worker.stop()
        except:
            pass

        try:
            if self.worker_thread:
                self.worker_thread.quit()
                self.worker_thread.wait(2000)
        except:
            pass

        event.accept()
