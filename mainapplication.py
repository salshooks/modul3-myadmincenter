from fileinput import filename
import sys
import os
from tkinter import dialog
import mysql.connector 
import csv
import json
import shutil #Datei kopieren

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (
    QApplication, QDialog, QFileDialog, QLineEdit, QMainWindow, QPushButton, QDockWidget, QToolBar,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QMessageBox, QGridLayout, QLabel, QLineEdit, QComboBox, QTableWidget, QAbstractItemView
)
from datetime import datetime
# TODO: Die Klasse EditADUserWindow muss in editaduser_TN.py vervollständigt werden.
from editaduser_TN import EditADUserWindow


#Einfügen Login FEnster
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
    
        self.setWindowTitle("Login")
        self.setModal(True)
    
    
        layout = QGridLayout()
        self.setLayout(layout)
    
        #Username
        self.label_user = QLabel("Username")
        self.input_user = QLineEdit()
    
        #Password
        self.label_pass = QLabel("Password:")
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
    
        #Host
        self.label_host = QLabel("Host:")
        self.input_host = QLineEdit()

        #Database
        self.label_db = QLabel("Database:")
        self.input_db = QLineEdit()

    
        #Buttons
        self.btn_ok = QPushButton("OK")
        self.btn_cancel = QPushButton("Abbrechen")
    
        
    
        #Layout
        layout.addWidget(self.label_host, 0, 0)
        layout.addWidget(self.input_host, 0, 1)
    
        layout.addWidget(self.label_db, 1, 0)
        layout.addWidget(self.input_db, 1, 1)
    
        layout.addWidget(self.label_user, 2, 0)
        layout.addWidget(self.input_user, 2, 1)
    
        layout.addWidget(self.label_pass, 3, 0)
        layout.addWidget(self.input_pass, 3, 1)

        layout.addWidget(self.btn_ok, 4, 0)
        layout.addWidget(self.btn_cancel, 4, 1)
    
        # Buttons logic
        self.btn_ok.clicked.connect(self.handle_login)
        self.btn_cancel.clicked.connect(self.reject)

    #Liest Login-Daten aus den Eingabefeldern und schließt das Fenster mit OK.
    def handle_login(self):
        host = self.input_host.text()
        database = self.input_db.text()
        username = self.input_user.text()
        password = self.input_pass.text()
        
        #Dieser Block speichert die Benutzereingaben im Anmeldefensterobjekt.
        self.login_data ={
            "host": host,
            "database": database,
            "username": username,
            "password": password,
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

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Benutzer suchen...")

        #Bei Texteingabe Tabelle filtern
        self.filter_input.textChanged.connect(self.filter_ad_users)
        # Filterfeld ins Layout einfügen
        central_layout.addWidget(self.filter_input)


        self.table_interessenten = QTableWidget()
        self.table_interessenten.setColumnCount(5)
        self.table_interessenten.setHorizontalHeaderLabels([
            "ID",
            "Vorname",
            "Benutzername",
            "E-Mail",
            "Status"
        ])
        # Zeilennummern (linke Spalte) ausblenden
        self.table_interessenten.verticalHeader().setVisible(False)
        # Auswahlverhalten gemäß US 3.1 
        self.table_interessenten.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_interessenten.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table_interessenten.doubleClicked.connect(self.editaduser) 
        self.table_interessenten.horizontalHeader().setStretchLastSection(True) # Letzte Spalte der Tabelle automatisch strecken
        self.table_interessenten.resizeColumnsToContents() # Spaltenbreite automatisch an Inhalt anpassen



        central_layout.addWidget(self.table_interessenten)
        self.resize(1000, 600)
        self.show()

    # --- Platzhalter für die Teilnehmer-Logik ---

    def menue_clicked(self):
        """Zentraler Slot für alle Aktionen. Teilnehmer müssen das match-case implementieren."""
        sender = self.sender()
        command_id = sender.property("command")[0]
        
        
        # Beispielhafter Einstieg::
        if command_id == 13: self.db_login()  # Menüpunkt: Login zur Datenbank
        elif command_id == 11: self.csv_import_with_validation() # Menüpunkt: CSV-Datei importieren und in DB speichern
        elif command_id == 12: self.transfer_to_ad() # Menüpunkt: Daten für AD-Transfer vorbereiten
        elif command_id == 21: self.editaduser()  # Menüpunkt: ausgewählten Benutzer bearbeiten
        elif command_id == 22: self.delete_ad_user() # Menüpunkt: ausgewählten Benutzer löschen
        elif command_id ==23: self.deactivate_ad_user() # Menüpunkt: ausgewählten AD-Benutzer deaktivieren
        elif command_id == 14: self.db_logout() # Menüpunkt: Logout (Verbindung schließen)

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
        dialog = LoginDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            login_data = dialog.login_data

            try:
                self.db_connection = mysql.connector.connect(
                host=login_data["host"],
                user=login_data["username"],
                password=login_data["password"],
                database=login_data["database"],
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
                self.table_interessenten.setItem(
                    row_index,
                    col_index,
                    QTableWidgetItem(str(value)) #Wert in eine bestimmte Tabellenzelle einfügen.
                )
        self.table_interessenten.resizeColumnsToContents()
        cursor.close()

    def filter_ad_users(self):
        filter_text = self.filter_input.text().lower().strip()
        
        for row in range(self.table_interessenten.rowCount()):
            row_matches = False

            for col in range(self.table_interessenten.columnCount()):
                item = self.table_interessenten.item(row, col)
                if item is not  None and filter_text in item.text().lower():
                    row_matches = True
                    break
            
            self.table_interessenten.setRowHidden(row, not row_matches)


    # Eine CSV-Zeile auslesen und die Felder für weitere Verarbeitung vorbereiten   
    def process_csv_row(self, row, line_number, source_file):
        firstname = row.get("firstname", "").strip()
        lastname = row.get("lastname", "").strip()
        phone = row.get("phone", "").strip()
        ou = row.get("ou", "").strip()
        street = row.get("street", "").strip()
        city = row.get("city", "").strip()
        city_code = row.get("city_code", "").strip()
        postalcode = row.get("postalcode", "").strip()
        kurs = row.get("kurs", "").strip()
        status_id_fk = row.get("status_id_fk", "").strip()

        return {
            "firstname": firstname,
            "lastname": lastname,
            "phone": phone,
            "ou": ou,
            "street": street,
            "city": city,
            "city_code": city_code,
            "postalcode": postalcode,
            "kurs": kurs,
            "status_id_fk": status_id_fk,
            "line_number": line_number,
            "source_file": source_file
        }
    # Username aus Vorname und Nachname generieren (Format: firstname.lastname)
    def generate_username(self,firstname, lastname):
        # Leerzeichen entfernen und alles in Kleinbuchstaben umwandeln
        firstname = firstname.strip().lower()
        lastname = lastname.strip().lower()

        username = f"{firstname}.{lastname}"
        # Username auf maximale Länge kürzen
        username = username[:20]
        return username
        
     # E-Mail aus Vorname, Nachname und Standort generieren   
    def generate_email(self, firstname, lastname, location):
        # Leerzeichen entfernen und alles in Kleinbuchstaben umwandeln
        firstname = firstname.strip().lower()
        lastname = lastname.strip().lower()
        location = location.strip().lower()
        # Lokalen Teil der E-Mail erstellen (vorname.nachname)
        local_part = f"{firstname}.{lastname}"
        # Domain abhängig vom Standort festlegen
        if location == "berlin":
            domain = "@company-berlin.de"
        else:
            domain = "@company.de"
        # Vollständige E-Mail zurückgeben
        return local_part + domain
    
    #Prüfen, ob Benutzer bereits in der Datenbank existiert
    def user_exists(self, username):
        # Datenbankabfrage zur Überprüfung, ob Username bereits existiert
        cursor = self.db_connection.cursor()
        cursor.execute(
            "SELECT username FROM aduser WHERE username = %s",
            (username,)
        )
        result = cursor.fetchone()
        cursor.close()
        # True zurückgeben, wenn Benutzer gefunden wurde, sonst False
        return result is not None

    # Neuen Benutzer in die Datenbank einfügen
    def insert_user(self, data):
        cursor = self.db_connection.cursor()
        # SQL-Insert-Befehl zum Speichern eines neuen Benutzers
        cursor.execute("""
            INSERT INTO aduser 
            (username, firstname, lastname, email, phone, ou, street, city, postalcode)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data["username"][:20],
            data["firstname"][:20],
            data["lastname"][:20],
            data["email"][:50],
            data["phone"][:20],
            data["ou"][:20],
            data["street"][:50],
            data["city"][:30],
            data["postalcode"][:10]
        ))
        # Änderungen in der Datenbank speichern (commit)
        self.db_connection.commit()
        cursor.close()

        # Vorhandenen Benutzer in der Datenbank aktualisieren
    def update_user(self, data):
        cursor = self.db_connection.cursor()

        # SQL-Update-Befehl zum Aktualisieren eines vorhandenen Benutzers
        cursor.execute("""
            UPDATE aduser
            SET firstname = %s,
            lastname = %s,
            email = %s,
            phone = %s,
            ou = %s,
            street = %s,
            city = %s,
            postalcode = %s
            WHERE username = %s
        """, (
            data["firstname"][:20],
            data["lastname"][:20],
            data["email"][:50],
            data["phone"][:20],
            data["ou"][:20],
            data["street"][:50],
            data["city"][:30],
            data["postalcode"][:10],
            data["username"][:20]
        ))

        # Änderungen in der Datenbank speichern (commit)
        self.db_connection.commit()
        cursor.close()
                           
                           



    def csv_import_with_validation(self):
        """
        TODO: CSV einlesen, Daten validieren (US 7) und in DB schreiben.
        Fehlerhafte Zeilen müssen in die Tabelle 'import_errors'.
        """
        if self.db_connection is None:
            QMessageBox.warning(self, "Fehler", "Bitte zuerst einloggen")
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "CSV-Datei auswählen",
            "",
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        # CSV-Datei einlesen und Zeilen als Dictionaries für weitere Verarbeitung speichern
        try:
            with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=";")

                rows = list(reader)  

                

                print("Anzahl Zeigen:", len(rows))
                #Zähler für neue und bereits vorhandene Datensätze vorbereiten
                new_count = 0
                existing_count = 0

                for index, row in enumerate(rows, start=1):
                    processed_row = self.process_csv_row(row, index, file_path)
                    # Username für jeden Datensatz generieren
                    username = self.generate_username(
                        processed_row["firstname"],
                        processed_row["lastname"]
                    )

                    # Username dem Datensatz hinzufügen
                    processed_row["username"] = username

                    # E-Mail für jeden Datensatz generieren
                    email = self.generate_email(
                        processed_row["firstname"],
                        processed_row["lastname"],
                        processed_row["city"]
                    )
                    # E-Mail dem Datensatz hinzufügen
                    processed_row["email"] = email
                    # Prüfen, ob der Benutzer bereits in der Datenbank existiert
                    if self.user_exists(processed_row["username"]):
                        processed_row["db_action"] = "update"
                        existing_count +=1
                        self.update_user(processed_row) # Vorhandenen Benutzer aktualisieren
                    else:
                        processed_row["db_action"] = "insert"
                        new_count +=1
                        # Neuen Benutzer in die Datenbank einfügen
                        self.insert_user(processed_row)


                    # Ergebnis zur Kontrolle ausgeben
                    print(processed_row)

                print("Neue Datensätze:", new_count)
                print("Vorhandene Datensätze:", existing_count)
                self.load_ad_users()
                QMessageBox.information(
                    self,
                    "Import erfolgreich",
                    f"Neu importiert: {new_count}\nAktualisiert: {existing_count} "
                )



        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))

        print(file_path)


    def editaduser(self): 
        """Ruft das Bearbeitungsfenster auf """ 
        selection = self.table_interessenten.selectedItems() # Ausgewählte Zeile ermitteln
        # Prüfen, ob eine Zeile ausgewählt ist
        if selection:
            row = selection[0].row()
            # Benutzer-ID aus der ersten Spalte holen
            userid = self.table_interessenten.item(row, 0).text()
            
            # Bearbeitungsfenster öffnen
            self.edit_win = EditADUserWindow("Benutzer bearbeiten", userid, self.db_connection, self)
            self.edit_win.show()
        else:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie einen User aus!")

    #Löscht den ausgewählten Benutzer aus der Datenbank
    def delete_ad_user(self):
        # Prüfen, ob ein Benutzer ausgewählt ist
        selection = self.table_interessenten.selectedItems()
        if not selection:
            QMessageBox.warning(self, "Fehler", "Bitte wöhlen Sie einen User aus!")
            return
        
        #ID aus erster Spalte holen
        row = selection[0].row()
        userid = self.table_interessenten.item(row, 0).text()        

        #Sicherhetsabfrage
        antwort = QMessageBox.question(
            self,
            "Bestätigung",
            "Benutzer wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        #Wenn bestätigt> löschen
        if antwort == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.db_connection.cursor()

                #WICHTIG: id_pk verwenden
                cursor.execute(
                    "DELETE FROM aduser WHERE id_pk = %s",
                    (int(userid),)
                )

                self.db_connection.commit()
                cursor.close()

                QMessageBox.information(self, "Erfolg", "Benutzer gelöscht")

                #Tabelle neu Laden

                self.load_ad_users()

            except Exception as e:
                QMessageBox.critical(self, "Fehler", str(e))


    def deactivate_ad_user(self):
        """Deaktiviert den ausgewöhlten Benutzer (Status ändern)."""
        #Prüfen, ob ein Benutzer ausgewählt ist
        selection = self.table_interessenten.selectedItems()
        if not selection:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie einen User aus!")
            return
        #ID aus der ersten Spalte holen
        row = selection[0].row()
        userid = self.table_interessenten.item (row, 0).text()

        #Sicherheitsabfrage
        antwort = QMessageBox.question(
            self,
            "Bestätigung",
            "Benutzer wirklich deaktivieren?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if antwort == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.db_connection.cursor()


                #Status auf "inaktiv" setzen (status_id_fk = 0)
                cursor.execute(
                    "UPDATE aduser SET status_id_fk = 2 WHERE id_pk = %s",
                    (int(userid),)
                )
                
                self.db_connection.commit()
                cursor.close()

                QMessageBox.information(self, "Erfolg", "Benutzer deaktiviert")

                #Tabelle neu laden
                self.load_ad_users()

            except Exception as e:
                QMessageBox.critical(self, "Fehler", str(e))

    def transfer_to_ad(self):
        """Startet den Transfer zur AD"""
        # Prüfen, ob Verbindung zur Datenbank besteht
        if self.db_connection is None:
            QMessageBox.warning(self, "Fehler", "Bitte zuerst einloggen")
            return
        
        #Benutzer für Transfer laden
        users = self.get_all_ad_users_for_transfer()

        #Prüfen, ob Benutzer vorhanden sind
        if not users:
            QMessageBox.warning(self, "Fehler", "Keine Benutzer für den Tansfer gefunden")
            return
        
        #Expoer-Ordner festlegen/ определяем папку для экспорта
        export_folder = "exports"
        #Export-Ordner erstellem, falls er nicht existiert/ создаем папку если ее нет
        os.makedirs(export_folder, exist_ok=True)

        #Dateiname mit Zeitstemperl erstellen / Создаем имя файла
        filename = f"transfer_ad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        #Vollstädigen Dateipfad erstellen / полный путь к файлу
        local_file = os.path.join(export_folder, filename)
        

        #Daten in JSON-Datei schreiben/ запись в джейсон в папку експортс
        with open(local_file, "w", encoding="utf-8") as file:
            json.dump(users, file, ensure_ascii=False, indent=4)

        network_folder = "network_test" #Netzwerkpfad (Test)/ тестовая папка
        os.makedirs(network_folder, exist_ok=True)  # Ordner erstellen / создать папку
        network_file = os.path.join(network_folder, filename) #Zielpfad
        shutil.copy2(local_file, network_file) # Datei kopiert    
    
        #Erfolgsmeldung anzeigen
        QMessageBox.information(
            self,
            "Erfolg",
            f"{len(users)} Benutzer exportiert.\nDatei erstellt:\n{local_file}\nKopiert nach:\n{network_file}"
        )

        
        

    def get_all_ad_users_for_transfer(self):
        """Ladt alle Benutzer für den AD-Transfer aus der DB"""

        try:
            cursor = self.db_connection.cursor()
            #Benötige Felder für PowerShell-Transfer laden
            cursor.execute("""
                SELECT
                    username,
                    firstname,
                    lastname,
                    street,
                    postalcode,
                    city,
                    phone,
                    email,
                    ou
                FROM aduser
            """)
            rows = cursor.fetchall()

            users = []

            for row in rows:
                user = {
                    "username": row[0],
                    "firstname": row[1],
                    "lastname": row[2],
                    "street": row[3],
                    "postalcode": row[4],
                    "city": row[5],
                    "phone": row[6],
                    "email": row[7],
                    "ou": row[8],
                }
                users.append(user)

            cursor.close()

            return users
        
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim der Transferdaten:\n{e}")
            return []
            


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()