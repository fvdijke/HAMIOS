"""Full integration test - Antenna Calculator in simulated HAMIOS context"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from modules.antenna_calculator import AntennaCalculatorDialog

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HAMIOS - Antenna Calculator Test")
        self.setGeometry(100, 100, 600, 400)

        widget = QWidget()
        layout = QVBoxLayout(widget)

        btn_calc = QPushButton("Open Antenna Calculator")
        btn_calc.clicked.connect(self._open_calculator)
        layout.addWidget(btn_calc)

        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(self.close)
        layout.addWidget(btn_exit)

        layout.addStretch()
        self.setCentralWidget(widget)

    def _open_calculator(self):
        calc = AntennaCalculatorDialog(self)
        calc.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
