# ui/alert_window.py
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QComboBox, QDoubleSpinBox,
    QSpinBox, QPushButton, QMessageBox
)
from core.utils import POPULAR_NAMES


class AlertConfigWindow(QDialog):
    def __init__(self, parent=None, symbols=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Alerta")
        self.setMinimumWidth(320)

        # Layout principal
        layout = QFormLayout(self)

        ########################################################################
        # SELEÇÃO DE SÍMBOLOS (melhor visual + nome popular)
        ########################################################################
        self.symbol_combo = QComboBox()

        # Mostrar "Bitcoin (BTC)" em vez de só "BTCUSDT"
        display_list = []
        for s in symbols:
            base = s.replace("USDT", "")
            name = POPULAR_NAMES.get(base, base)
            display_list.append(f"{name} ({base})")

        self.symbol_map = {f"{POPULAR_NAMES.get(s.replace('USDT',''), s)} ({s.replace('USDT','')})": s for s in symbols}

        self.symbol_combo.addItems(display_list)
        layout.addRow("Criptomoeda:", self.symbol_combo)

        ########################################################################
        # CONDIÇÕES DO ALERTA
        ########################################################################
        self.condition_combo = QComboBox()
        self.condition_combo.addItems([
            "Preço Acima de",
            "Preço Abaixo de",
            "Variação % Acima de",
            "Variação % Abaixo de",
        ])
        layout.addRow("Condição:", self.condition_combo)

        ########################################################################
        # VALOR DO ALERTA
        ########################################################################
        self.value_spin = QDoubleSpinBox()
        self.value_spin.setRange(-999999999, 999999999)
        self.value_spin.setDecimals(4)
        self.value_spin.setValue(0.0)
        layout.addRow("Valor:", self.value_spin)

        ########################################################################
        # DEFINIR DECIMAIS
        ########################################################################
        self.decimal_spin = QSpinBox()
        self.decimal_spin.setRange(0, 10)
        self.decimal_spin.setValue(2)
        self.decimal_spin.valueChanged.connect(
            lambda v: self.value_spin.setDecimals(v)
        )
        layout.addRow("Precisão:", self.decimal_spin)

        ########################################################################
        # BOTÃO SALVAR
        ########################################################################
        save_btn = QPushButton("Salvar Alerta")
        save_btn.clicked.connect(self.validate_and_accept)
        layout.addWidget(save_btn)

    ########################################################################
    # VALIDAR E SALVAR ALERTA
    ########################################################################
    def validate_and_accept(self):
        selected = self.symbol_combo.currentText()
        value = self.value_spin.value()

        if selected == "" or selected is None:
            QMessageBox.warning(self, "Erro", "Selecione uma criptomoeda válida.")
            return

        if value == 0:
            QMessageBox.warning(self, "Valor inválido",
                                "O valor do alerta não pode ser zero.\n"
                                "Escolha um valor maior ou menor.")
            return

        self.accept()

    ########################################################################
    # RETORNO DO ALERTA ESCOLHIDO
    ########################################################################
    def get_alert_data(self):
        display_text = self.symbol_combo.currentText()
        symbol = self.symbol_map[display_text]  # converte novamente para "BTCUSDT"

        return {
            "symbol": symbol,
            "condition": self.condition_combo.currentText(),
            "value": self.value_spin.value()
        }
