"""Test script for Antenna Calculator Module"""

import sys
from PySide6.QtWidgets import QApplication
from modules.antenna_calculator import AntennaCalculatorDialog

def main():
    app = QApplication(sys.argv)

    # Create and show antenna calculator
    calculator = AntennaCalculatorDialog()
    calculator.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
