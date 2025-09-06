"""PySide6 GUI for Tako Georgian Ads Generator (with user-settable model and max_tokens)."""
from __future__ import annotations

import sys
import threading
import time
from pathlib import Path
from typing import List, Tuple

import pandas as pd
from PySide6.QtCore import Qt, Slot, QObject, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QDialog,
    QDialogButtonBox,
)

from config import api_keys, settings
from core import ad_generator, csv_handler
from prompts.tone_prompts import TONES
from utils.validation import row_is_complete

COLUMNS = ["name", "description", "ad"]
AVAILABLE_MODELS = [
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-4o-mini",
    "gpt-4o",
]


class _Worker(QObject):
    finished = Signal()
    progress = Signal(int, int)
    result_row = Signal(int, str)

    def __init__(
        self,
        pending_rows: List[Tuple[int, str, str]],
        *,
        tone: str,
        model: str,
        max_tokens: int,
        temperature: float,
    ):
        super().__init__()
        self._rows = pending_rows
        self._tone = tone
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature

    def run(self):
        batch_size = 5
        idx = 0
        total = len(self._rows)
        while idx < total:
            batch = self._rows[idx : idx + batch_size]
            try:
                results = ad_generator.generate_batch(
                    [(n, d) for (_, n, d) in batch],
                    self._tone,
                    max_tokens=self._max_tokens,
                    temperature=self._temperature,
                    model=self._model,
                    concurrency=3,
                )
            except Exception as exc:  # noqa: BLE001
                for row_idx, *_ in batch:
                    self.result_row.emit(row_idx, f"Error: {exc}")
                break
            else:
                for (row_idx, _n, _d), ad_text in zip(batch, results):
                    self.result_row.emit(row_idx, ad_text if not isinstance(ad_text, Exception) else f"Error: {ad_text}")
            idx += batch_size
            self.progress.emit(min(idx, total), total)
            time.sleep(1.0)
        self.finished.emit()


class ApiKeyDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("API Key")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter your OpenAI API key:"))
        self._edit = QLineEdit(self)
        self._edit.setPlaceholderText("sk-...")
        layout.addWidget(self._edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @property
    def key(self) -> str:
        return self._edit.text().strip()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(settings.APP_NAME)
        self.resize(1120, 720)

        cfg = settings.read_settings("openai")

        central = QWidget(self)
        self.setCentralWidget(central)
        vbox = QVBoxLayout(central)
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setSpacing(12)

        # Top bar
        top = QWidget()
        hbox = QHBoxLayout(top)
        hbox.setSpacing(8)
        vbox.addWidget(top)

        hbox.addWidget(QLabel("ტონი:"))
        self.tone_combo = QComboBox()
        self.tone_combo.addItems(list(TONES.keys()))
        hbox.addWidget(self.tone_combo)

        # Model dropdown
        hbox.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(AVAILABLE_MODELS)
        self.model_combo.setCurrentText(cfg.get("model", AVAILABLE_MODELS[0]))
        hbox.addWidget(self.model_combo)

        # Max-tokens spinbox
        hbox.addWidget(QLabel("Max tokens:"))
        self.tokens_spin = QSpinBox()
        self.tokens_spin.setRange(10, 4096)
        self.tokens_spin.setValue(int(cfg.get("max_tokens", 200)))
        hbox.addWidget(self.tokens_spin)

        # Temperature spinbox (optional, default 0.8)
        hbox.addWidget(QLabel("Temp:"))
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 1.0)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setDecimals(2)
        self.temp_spin.setValue(float(cfg.get("temperature", 0.8)))
        hbox.addWidget(self.temp_spin)

        self.generate_btn = QPushButton("Generate Ads")
        self.generate_btn.clicked.connect(self._on_generate)
        hbox.addWidget(self.generate_btn)

        imp_btn = QPushButton("Import CSV", clicked=self._on_import)
        hbox.addWidget(imp_btn)
        exp_btn = QPushButton("Export CSV", clicked=self._on_export)
        hbox.addWidget(exp_btn)
        api_btn = QPushButton("Enter API Key", clicked=self._on_api_key)
        hbox.addWidget(api_btn)
        hbox.addStretch()

        # Spreadsheet
        self.table = QTableWidget(50, 3)
        self.table.setHorizontalHeaderLabels(["Product Name", "Description", "Ad (output)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().hide()
        vbox.addWidget(self.table, 1)

        # Status bar
        self._status = QStatusBar(self)
        self.setStatusBar(self._status)
        self._status.showMessage("Ready")

        self._worker_thread: threading.Thread | None = None

    # ---------- CSV ----------
    @Slot()
    def _on_import(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Open CSV", filter="CSV files (*.csv)")
        if not fn:
            return
        try:
            df = csv_handler.import_csv(fn)
        except Exception as exc:  # noqa
            QMessageBox.critical(self, "Error", str(exc))
            return
        self.table.setRowCount(max(len(df), 1))
        for r, row in df.iterrows():
            for c, key in enumerate(COLUMNS):
                self.table.setItem(r, c, QTableWidgetItem(str(row.get(key, ""))))
        self._status.showMessage(f"Loaded {Path(fn).name}")

    @Slot()
    def _on_export(self):
        fn, _ = QFileDialog.getSaveFileName(self, "Save CSV", filter="CSV files (*.csv)")
        if not fn:
            return
        rows = [(
            self._cell_text(r, 0),
            self._cell_text(r, 1),
            self._cell_text(r, 2),
        ) for r in range(self.table.rowCount())]
        try:
            csv_handler.export_csv(pd.DataFrame(rows, columns=COLUMNS), fn)
            self._status.showMessage("CSV exported")
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    # ---------- API KEY ----------
    @Slot()
    def _on_api_key(self):
        dlg = ApiKeyDialog(self)
        if dlg.exec() == QDialog.Accepted and dlg.key:
            if api_keys.validate_api_key(dlg.key):
                api_keys.save_api_key(dlg.key)
                settings.write_settings({"api_saved": True}, section="openai")
                QMessageBox.information(self, "Saved", "API key saved")
            else:
                QMessageBox.warning(self, "Invalid", "Key invalid")

    # ---------- GENERATE ----------
    @Slot()
    def _on_generate(self):
        if not api_keys.load_api_key():
            QMessageBox.warning(self, "API", "Set API key first")
            return
        pending: List[Tuple[int, str, str]] = []
        for r in range(self.table.rowCount()):
            name = self._cell_text(r, 0)
            desc = self._cell_text(r, 1)
            ad = self._cell_text(r, 2)
            if row_is_complete(name, desc) and not ad:
                pending.append((r, name, desc))
        if not pending:
            QMessageBox.information(self, "Info", "No rows to generate")
            return

        self.generate_btn.setEnabled(False)
        self._status.showMessage("Generating…")

        worker = _Worker(
            pending,
            tone=self.tone_combo.currentText(),
            model=self.model_combo.currentText(),
            max_tokens=self.tokens_spin.value(),
            temperature=self.temp_spin.value(),
        )
        thread = threading.Thread(target=worker.run, daemon=True)
        self._worker_thread = thread
        worker.result_row.connect(self._on_result_row)
        worker.progress.connect(lambda p, t: self._status.showMessage(f"Processed {p}/{t}…"))
        worker.finished.connect(self._on_finished)
        thread.start()

    @Slot()
    def _on_finished(self):
        self.generate_btn.setEnabled(True)
        self._status.showMessage("Done ✔")
        settings.write_settings({
            "max_tokens": self.tokens_spin.value(),
            "temperature": self.temp_spin.value(),
            "model": self.model_combo.currentText(),
        }, section="openai")

    @Slot(int, str)
    def _on_result_row(self, row: int, text: str):
        self.table.setItem(row, 2, QTableWidgetItem(text))

    def closeEvent(self, event):  # noqa: N802
        # Ask user to save CSV and keep API key
        save_api = QMessageBox.question(self, "Exit", "Save API key before exit?", QMessageBox.Yes | QMessageBox.No)
        if save_api == QMessageBox.No:
            api_keys.save_api_key("")  # clear key
        save_csv = QMessageBox.question(self, "Exit", "Export spreadsheet before quit?", QMessageBox.Yes | QMessageBox.No)
        if save_csv == QMessageBox.Yes:
            self._on_export()
        event.accept()

    # ---------- helpers ----------
    def _cell_text(self, r: int, c: int) -> str:
        itm = self.table.item(r, c)
        return "" if itm is None else itm.text().strip()


def run_qt_app():
    app = QApplication(sys.argv)

    # App naming
    app.setApplicationName(settings.APP_NAME)
    app.setApplicationDisplayName(settings.APP_NAME)

    # Set application/window icon using project-relative path
    icon_path = Path(__file__).resolve().parents[1] / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))
    window.show()
    sys.exit(app.exec())
