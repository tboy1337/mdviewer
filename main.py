#!/usr/bin/env python3
import sys
from PyQt6.QtWidgets import QApplication
from mdviewer.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MDViewer")
    app.setOrganizationName("MDViewer")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 