import json
import os
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QStandardPaths

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
ALERT_FILE = os.path.join(RESOURCES_DIR, "alerts.json")
HISTORY_FILE = os.path.join(RESOURCES_DIR, "alerts_history.json")
PRICE_HISTORY_FILE = os.path.join(RESOURCES_DIR, "price_history.json")

# Auto-alert thresholds
AUTO_PERCENT_THRESHOLD = 3.0  # percent change to auto-trigger
AUTO_ENABLE = True

def notify_user(title, message):
    """Try to notify using plyer if available, else fallback to QMessageBox."""
    try:
        from plyer import notification
        notification.notify(title=title, message=message)
    except Exception:
        # fallback will be handled by caller via QMessageBox
        print("Notification (fallback):", title, message)

class AlertManager:
    def __init__(self):
        self.active_alerts = []
        os.makedirs(RESOURCES_DIR, exist_ok=True)
        self.load_alerts()
        # ensure history files exist
        if not os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
        if not os.path.exists(PRICE_HISTORY_FILE):
            with open(PRICE_HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def save_alerts(self):
        try:
            with open(ALERT_FILE, "w", encoding="utf-8") as f:
                json.dump(self.active_alerts, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print("Erro ao salvar alerts.json:", e)

    def load_alerts(self):
        if os.path.exists(ALERT_FILE):
            try:
                with open(ALERT_FILE, "r", encoding="utf-8") as f:
                    self.active_alerts = json.load(f)
            except Exception as e:
                print("Erro ao carregar alerts.json:", e)
                self.active_alerts = []
        else:
            self.active_alerts = []

    def _log_alert_trigger(self, symbol, condition, value, current):
        entry = {
            "symbol": symbol,
            "condition": condition,
            "value": value,
            "current": current
        }
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []
        data.append(entry)
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print("Erro ao salvar histórico de alertas:", e)

    def _save_price_snapshot(self, data_state):
        # store last price per symbol to PRICE_HISTORY_FILE (keeps limited history)
        try:
            try:
                with open(PRICE_HISTORY_FILE, "r", encoding="utf-8") as f:
                    p = json.load(f)
            except Exception:
                p = {}
            for sym, metrics in data_state.items():
                history = p.get(sym, [])
                price = metrics.get("price")
                if price is None:
                    continue
                # keep last 200 values
                history.append(price)
                p[sym] = history[-200:]
            with open(PRICE_HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(p, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print("Erro ao salvar price history:", e)

    def check_alerts(self, window, data_state):
        # always persist a snapshot of prices for history features
        try:
            self._save_price_snapshot(data_state)
        except Exception:
            pass

        # Auto alerts (simple rule-based)
        if AUTO_ENABLE:
            for sym, metrics in data_state.items():
                try:
                    pct = float(metrics.get("price_change_percent", 0))
                    # if absolute percent exceeds threshold, create a transient notification
                    if abs(pct) >= AUTO_PERCENT_THRESHOLD:
                        msg = f"{sym} variação {pct:.2f}% — verifique rapidamente."
                        try:
                            notify_user("Alerta Automático", msg)
                        except Exception:
                            pass
                        # log but do not create persistent alert unless user wants
                        self._log_alert_trigger(sym, "AutoDetecção", pct, metrics.get("price"))
                except Exception:
                    continue

        if not self.active_alerts:
            return

        to_remove = []

        for i, alert in enumerate(list(self.active_alerts)):
            try:
                symbol = alert.get("symbol")
                cond = alert.get("condition", "")
                value = alert.get("value")
                # robust convert
                try:
                    value = float(value)
                except Exception:
                    continue

                if not symbol or symbol not in data_state:
                    continue

                if "Preço" in cond:
                    cur = data_state[symbol].get("price")
                else:
                    cur = data_state[symbol].get("price_change_percent")

                if cur is None:
                    continue

                hit = (
                    ("Acima" in cond and cur > value) or
                    ("Abaixo" in cond and cur < value)
                )

                if hit:
                    # try system notification first
                    try:
                        notify_user("ALERTA ACIONADO", f"{symbol} atingiu {cond}: {cur}")
                    except Exception:
                        pass

                    # fallback message box
                    try:
                        QMessageBox.critical(
                            window,
                            "ALERTA ACIONADO",
                            f"{symbol} atingiu {cond}: {cur}"
                        )
                    except Exception:
                        print(f"Alerta: {symbol} atingiu {cond}: {cur}")

                    to_remove.append(i)
                    # log trigger
                    self._log_alert_trigger(symbol, cond, value, cur)
            except Exception as e:
                print("Erro ao processar alerta:", e)
                continue

        if to_remove:
            self.active_alerts = [
                a for idx, a in enumerate(self.active_alerts)
                if idx not in to_remove
            ]
            self.save_alerts()
