import sys
import os
from tkinter import dialog
import mysql.connector 

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (
    QApplication, QDialog, QLineEdit, QMainWindow, QPushButton, QDockWidget, QToolBar,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QMessageBox, QGridLayout, QLabel, QLineEdit, QComboBox
)
# TODO: Die Klasse EditADUserWindow muss in editaduser_TN.py vervollständigt werden.
from editaduser_TN import EditADUserWindow

DB_CONFIGS = {
    "Test": {
        "host": "localhost",
        "database": "AD"
    },
    "Produktion": {
        "host": "localhost",
        "database": "AD"
    }
}
#Einfügen Login FEnster
class LoginDialog(QDialog):
    def __init__(self, db_configs, parent=None):
        super().__init__(parent)
    
        self.setWindowTitle("Login")
        self.setModal(True)
    
        self.db_configs = db_configs
    
        layout = QGridLayout()
        self.setLayout(layout)
    
        #Username
        self.label_user = QLabel("Username")
        self.input_user = QLineEdit()
    
        #Password
        self.label_pass = QLabel("Password:")
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
    
        #Datbase ComboBox
        self.label_db = QLabel("Datenbank:")
        self.combo_db = QComboBox()
        self.combo_db.addItems(self.db_configs.keys())
    
        #Buttons
        self.btn_ok = QPushButton("OK")
        self.btn_cancel = QPushButton("Abbrechen")
    
        #Buttons
        self.btn_ok = QPushButton("OK")
        self.btn_cancel = QPushButton("Abbrechen")
    
        #Layout
        layout.addWidget(self.label_user, 0, 0)
        layout.addWidget(self.input_user, 0, 1)
    
        layout.addWidget(self.label_pass, 1, 0)
        layout.addWidget(self.input_pass, 1, 1)
    
        layout.addWidget(self.label_db, 2, 0)
        layout.addWidget(self.combo_db, 2, 1)
    
        layout.addWidget(self.btn_ok, 3, 0)
        layout.addWidget(self.btn_cancel, 3, 1)
    
        # Buttons logic
        self.btn_ok.clicked.connect(self.handle_login)
        self.btn_cancel.clicked.connect(self.reject)

    #Liest Login-Daten aus den Eingabefeldern und schließt das Fenster mit OK.
    def handle_login(self):
        username = self.input_user.text()
        password = self.input_pass.text()
        db_name = self.combo_db.currentText()
        #Dieser Block speichert die Benutzereingaben im Anmeldefensterobjekt.
        self.login_data ={
            "username": username,
            "password": password,
            "database": db_name
        }
        
        self.accept()
    
        

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
        elif command_id == 14: self.db_logout()

    def db_logout(self): #Diese Methode schließt die Verbindung zur Datenbank und setzt self.db_connection auf None zurück.
        if self.db_connection is not None:
            self.db_connection.close()
            self.db_connection = None

        self.table_interessenten.clear()
        self.table_interessenten.setRowCount(0)
        self.table_interessenten.setColumnCount(0)

        QMessageBox.information(self, "Info", "Ausgeloggt")

#Einlogen zeigt
    def db_login(self):
        dialog = LoginDialog(DB_CONFIGS, self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            login_data = dialog.login_data

            try:
                self.db_connection = mysql.connector.connect(
                host="10.5.0.35",
                user=login_data["username"],
                password=login_data["password"],
                database="AD",
                port=3306
            )

                QMessageBox.information(self, "Erfolg", "Verbindung erfolgreich")
                self.load_ad_users() #Der Benutzer meldet sich an und die Tabelle wird automatisch ausgefüllt.

            except Exception as e:
                QMessageBox.critical(self, "Fehler", str(e))

        else:
            print("Login abgebrochen")


    def load_ad_users(self):
        cursor = self.db_connection.cursor() #Es wird ein "Werkzeug" zur Arbeit mit der Datenbank erstellt.
        cursor.execute("SELECT * FROM view_aduser_details") #Es wird eine Anfrage an die Datenbank gesendet.
        rows = cursor.fetchall() #Alle Daten aus der Datenbank in Python abrufen

        headers = [description[0] for description in cursor.description] #Ich verwende Spaltennamen (zum Beispiel: Name, E-Mail usw.).

        self.table_interessenten.setColumnCount(len(headers)) #wie viele Spalten
        self.table_interessenten.setHorizontalHeaderLabels(headers) #Spaltennamen (Überschriften).
        self.table_interessenten.setRowCount(len(rows)) #Wie viele Zeilen wird es geben
 
        for row_index, row_data in enumerate(rows): #jede Zeile aus der Datenbank.
            for col_index, value in enumerate(row_data): #für jede Zelle innerhalb der Zeile.
                self.table_interessenten-setItem(
                    row_index,
                    col_index,
                    QTableWidgetItem(str(value)) #Wert in eine bestimmte Tabellenzelle einfügen.
                )
        cursor.close()

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