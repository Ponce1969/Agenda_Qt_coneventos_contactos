import sys
from PyQt6.QtWidgets import QApplication
from app import AgendaApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = AgendaApp()
    ventana.show()
    sys.exit(app.exec())