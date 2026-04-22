import sys
import os
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QDockWidget, QToolBar,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QMessageBox
)
# TODO: Die Klasse EditADUserWindow muss in editaduser_TN.py vervollständigt werden.
from editaduser_TN import EditADUserWindow

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # Zentrale Konfiguration für Menüs und Toolbars 
        self.mainmenue = {1: "&Datei", 2: "&Active Directory", 4:"&Hilfe"}
        self.menueoptions = {
            11: "Import von CSV", 
            12: "Transfer nach AD",  
            13: "Einloggen", 
            14: "Ausloggen", 
            0: "separator", 
            19: "&Beenden", 
            21: "Bearbeite AD-User", 
            22: "Lösche AD-User",  
            23: "Inaktiv AD-User",
            24: "Validierungs-Report", # NEU: US 7.4
            41: "&Über", 
            42: "&Hilfe"
        }
        self.toolbarbuttons = {13: "Einloggen", 11: "Import von CSV", 12: "Transfer nach AD", 0: "separator", 21: "Bearbeite AD-User", 42: "&Hilfe"}
        
        self.db_connection = None # Initial keine Verbindung 
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("myAdmin Center")
        self.setWindowIcon(QIcon(".\\images\\logo-zm.png"))
        
        # Automatische Generierung der Menüleiste
        menubar = self.menuBar()
        for menu_id, menu_title in self.mainmenue.items():
            menu = menubar.addMenu(menu_title)
            for action_id, action_title in self.menueoptions.items():
                if action_id == 0:
                    menu.addSeparator()
                elif action_id // 10 == menu_id:
                    action = QAction(action_title, self)
                    action.setProperty("command", (action_id, action_title))
                    action.triggered.connect(self.menue_clicked)
                    menu.addAction(action)

        # Toolbar Setup
        toolbar = QToolBar("Hauptwerkzeugleiste")
        self.addToolBar(toolbar)
        for command, caption in self.toolbarbuttons.items():
            if command == 0:
                toolbar.addSeparator()
            else:
                btn = QPushButton(caption)
                btn.setProperty("command", (command, caption))
                btn.clicked.connect(self.menue_clicked)
                toolbar.addWidget(btn)   
        
        self.statusBar().showMessage("Bereit - Bitte einloggen")
        
        # Zentrales Widget & Tabelle
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_layout = QVBoxLayout(central_widget)

        self.table_interessenten = QTableWidget()
        # Auswahlverhalten gemäß US 3.1 
        self.table_interessenten.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_interessenten.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table_interessenten.doubleClicked.connect(self.editaduser) # [cite: 49]
        
        central_layout.addWidget(self.table_interessenten)
        self.resize(1000, 600)
        self.show()

    # --- Platzhalter für die Teilnehmer-Logik ---

    def menue_clicked(self):
        """Zentraler Slot für alle Aktionen. Teilnehmer müssen das match-case implementieren."""
        sender = self.sender()
        command_id = sender.property("command")[0]
        
        # Beispielhafter Einstieg::
        if command_id == 13: self.db_login() 
        elif command_id == 11: self.csv_import_with_validation() 
        elif command_id == 21: self.editaduser() 

    def db_login(self):
        """TODO: Implementierung eines modalen Login-Dialogs """
        pass

    def csv_import_with_validation(self):
        """
        TODO: CSV einlesen, Daten validieren (US 7) und in DB schreiben.
        Fehlerhafte Zeilen müssen in die Tabelle 'import_errors'.
        """
        pass

    def editaduser(self):
        """Ruft das Bearbeitungsfenster auf """
        selection = self.table_interessenten.selectedItems()
        if selection:
            row = selection[0].row()
            userid = self.table_interessenten.item(row, 0).text()
            # EditADUserWindow muss in editaduser_TN.py definiert werden.
            self.edit_win = EditADUserWindow("Benutzer bearbeiten", userid)
            self.edit_win.show()
        else:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie einen User aus!")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()