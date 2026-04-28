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
    QApplication, QDialog, QFileDialog, QLineEdit, QMainWindow, QPushButton, QDockWidget, QTextBrowser, QToolBar,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QMessageBox, QGridLayout, QLabel, QLineEdit, QComboBox, QTableWidget, QAbstractItemView
)
from datetime import datetime
# TODO: Die Klasse EditADUserWindow muss in editaduser_TN.py vervollständigt werden.
from editaduser_TN import EditADUserWindow


#Einfügen Login FEnster
#Der Benutzer wählt „Anmelden“, woraufhin das Programm eine Verbindung zum Anmeldedialog herstellt.
class LoginDialog(QDialog): #этот блок для входа в систему и подключению базе данных
    def __init__(self, parent=None):  #Когда пользователь нажимает "Einloggen", программа создаёт LoginDialog.
        super().__init__(parent)      #После создания сразу выполняется __init__.
    
        self.setWindowTitle("Login")
        self.setModal(True)
    
    
        layout = QGridLayout() #Окно называется Login.
        self.setLayout(layout) #Пока оно открыто, пользователь не может работать с главным окном.
    
        #Username
        self.label_user = QLabel("Username")
        self.input_user = QLineEdit()
    
        #Password
        self.label_pass = QLabel("Password:")
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password) #Она скрывает пароль точками/звёздочками.
    
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
        self.btn_ok.clicked.connect(self.handle_login) #Если нажали OK self.handle_login
        self.btn_cancel.clicked.connect(self.reject) #Если нажали Abbrechen: self.reject

    #Liest Login-Daten aus den Eingabefeldern und schließt das Fenster mit OK.
    #Nach der Bestätigung mit OK wird handle_login() aufgerufen, liest die Daten, gibt eine Sprachausgabe aus und schließt das Fenster.
    def handle_login(self): # после ОК запускается handle_login() считать данные>speichern>закрыть окно
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
        
        self.accept() #закрыть окно как успешный вход
    

# Fenster für Validierungs-Report
#Falls beim CSV-Import fehlerhafte Zeilen aufgetreten sind, werden diese in der Datenbank gespeichert und in diesem Fenster angezeigt.
# если при CSV импорте были неправильные строки, они сохраняются в базу, а это окно показывает эти ошибки
class ImportReportWindow(QDialog): # окно для просмотра ошибок
    def __init__(self, db_connection, parent=None): #Получает подключение к базе- Чтобы окно могло сделать SQL-запрос и загрузить ошибки.
        super().__init__(parent)
          # Datenbankverbindung speichern
        # Сохраняем подключение к базе данных
        self.db_connection = db_connection
        # Fenstertitel setzen
        # Устанавливаем заголовок окна
        self.setWindowTitle("Validierungs-Report")
        # Fenstergröße setzen
        # Устанавливаем размер окна
        self.resize(900, 500)
        # Layout erstellen
        # Создаём layout
        layout = QVBoxLayout(self) #вертикальное расположение элементов.
        #vertikale Anordnung der Elemente.

        # Tabelle für Fehler erstellen
        # Создаём таблицу для ошибок
        self.table_errors = QTableWidget() #Она нужна, чтобы показать ошибки в виде строк и колонок.
        #Es ist erforderlich, Fehler in Form von Zeilen und Spalten anzuzeigen.

        # Anzahl der Spalten setzen
        # Устанавливаем количество колонок
        self.table_errors.setColumnCount(6)

        # Spaltenüberschriften setzen
        # Устанавливаем названия колонок
        self.table_errors.setHorizontalHeaderLabels([
            "Zeit",
            "Datei",
            "Zeile",
            "Feld",
            "Wert",
            "Grund"
        ])

        # Tabelle ins Layout einfügen
        # Добавляем таблицу в окно
        layout.addWidget(self.table_errors) #Без этой строки таблица была бы создана в памяти, но не отображалась бы в окне.
        #Ohne diese Zeile würde die Tabelle zwar im Speicher erstellt, aber nicht im Fenster angezeigt.
        
        # Fehlerdaten laden
        # Загружаем ошибки из базы
        self.load_errors()

    # эта функциязагружает ошибки из базы данных и показывает их в таблице окна Validierungs-Report
    #Diese Funktion lädt Fehler aus der Datenbank und zeigt sie in der Tabelle des Validierungsberichtsfensters an.
    def load_errors(self):

        cursor =self.db_connection.cursor()
         # Fehlerdaten aus DB holen
        # Получаем ошибки из базы
        cursor.execute("""
            SELECT import_time, file_name, line_number, field_name, rejected_value, reason
            FROM import_errors
            ORDER BY id_pk DESC
        """) #запрос к Мариа ДБ, возьми данные из таблицы import_errors (import_time)
        #Anfrage an MariaDB, Daten aus der Tabelle import_errors (import_time) abrufen

        #загружаем все строки 
        rows = cursor.fetchall()

        # Anzahl der Zeilen setzen
        # Устанавливаем количество строк
        self.table_errors.setRowCount(len(rows))

        # Tabelle füllen
        # Заполняем таблицу данными
        for row_index, row_data in enumerate(rows):
            for col_index, value in enumerate(row_data):
                self.table_errors.setItem(
                    row_index,
                    col_index,
                    QTableWidgetItem(str(value))
                )

        # Cursor schließen
        # Закрываем cursor
        cursor.close()
        
#Dies ist das Hauptfenster der Anwendung „myAdmin Center“.
class MainWindow(QMainWindow): #Это главное окно приложения myAdmin Center.

    def __init__(self):
        super().__init__() #запускает базовую логику QMainWindow.
        # Zentrale Konfiguration für Menüs und Toolbars 
        self.mainmenue = {1: "&Datei", 2: "&Active Directory", 4:"&Hilfe"} #Главное меню
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
        #К кнопке приклеивается ID
        self.toolbarbuttons = {13: "Einloggen", 11: "Import von CSV", 12: "Transfer nach AD", 0: "separator", 21: "Bearbeite AD-User", 42: "&Hilfe"}
        
        self.db_connection = None # Initial keine Verbindung 
        self.initUI()
        
    #initUI() — это функция, которая строит всё главное окно программы.   
    # #initUI() ist eine Funktion, die das gesamte Hauptfenster des Programms erstellt. 
    def initUI(self): 
        self.setWindowTitle("myAdmin Center") #название окна: myAdmin Center
        self.setWindowIcon(QIcon(".\\images\\logo-zm.png")) #иконку окна: images/logo-zm.png
        
        # Automatische Generierung der Menüleiste
        #topline Datei | Active Directory | Hilfe
        menubar = self.menuBar() #верхняя строка Datei | Active Directory | Hilfe
        #ruft diese Daten ab self.mainmenue = {1: "&Datei"...
        for menu_id, menu_title in self.mainmenue.items(): #берет эти данные self.mainmenue = {1: "&Datei"...
            # und erstellt das Menü Datei | Active Directory | Hilfe
            menu = menubar.addMenu(menu_title)# и создает меню  Datei | Active Directory | Hilfe
            # übernimmt alle Elemente aus dem Import von CSV usw.
            for action_id, action_title in self.menueoptions.items(): # берет все пункты Import von CSV и так далее
                if action_id == 0: #Если ID = 0, это не кнопка, а разделительная линия.
                    menu.addSeparator()
                elif action_id // 10 == menu_id: #// 10 — это деление без остатка.
                    #13 идёт в меню 1 → Datei
                    #21 идёт в меню 2 → Active Directory
                    #42 идёт в меню 4 → Hilfe
                    #Так программа автоматически раскладывает пункты по меню.

                    #Создаётся пункт меню.
                    action = QAction(action_title, self)
                    action.setProperty("command", (action_id, action_title)) #Программа запоминает: Einloggen = команда 13
                    action.triggered.connect(self.menue_clicked)# Подключение клика
                    menu.addAction(action) 

        # Toolbar Setup
        toolbar = QToolBar("Hauptwerkzeugleiste") #Создаётся панель кнопок под меню.
        self.addToolBar(toolbar)
        for command, caption in self.toolbarbuttons.items(): #Добавление кнопок 13,11,12 те, которые сверху
            if command == 0: #пишет вертикальную линию как разделитель
                toolbar.addSeparator()
            else:
                btn = QPushButton(caption)
                btn.setProperty("command", (command, caption))
                btn.clicked.connect(self.menue_clicked)
                toolbar.addWidget(btn)   
        
        self.statusBar().showMessage("Bereit - Bitte einloggen")
        
        # Zentrales Widget & Tabelle
        central_widget = QWidget(self) # центральная часть окна
        self.setCentralWidget(central_widget)
        central_layout = QVBoxLayout(central_widget)

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Benutzer suchen...") # подсказка 

        #Bei Texteingabe Tabelle filtern
        self.filter_input.textChanged.connect(self.filter_ad_users)
        # Filterfeld ins Layout einfügen
        central_layout.addWidget(self.filter_input)


        self.table_interessenten = QTableWidget()
        self.table_interessenten.setColumnCount(5) #Создаётся таблица с 5 колонками.
        self.table_interessenten.setHorizontalHeaderLabels([
            "ID",
            "Vorname",
            "Benutzername",
            "E-Mail",
            "Status"
        ])
        # Zeilennummern (linke Spalte) ausblenden
        self.table_interessenten.verticalHeader().setVisible(False) #Скрывает номера строк слева.
        # Auswahlverhalten gemäß US 3.1 
        self.table_interessenten.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows) #Выбирается вся строка.
        self.table_interessenten.setSelectionMode(QTableWidget.SelectionMode.SingleSelection) #Можно выбрать только одну строку
        self.table_interessenten.doubleClicked.connect(self.editaduser)  #Двойной клик открывает редактирование пользователя.
        self.table_interessenten.horizontalHeader().setStretchLastSection(True) # Letzte Spalte der Tabelle automatisch strecken
        self.table_interessenten.resizeColumnsToContents() # Spaltenbreite automatisch an Inhalt anpassen



        central_layout.addWidget(self.table_interessenten) #Без этой строки таблица не появилась бы в интерфейсе.
        # Hilfe-Dock vorbereiten
        self.help_dock = QDockWidget("Hilfe", self) #Окно помощи
        self.help_dock.setAllowedAreas( #Панель можно ставить:слева- справа- снизу
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea |
            Qt.DockWidgetArea.BottomDockWidgetArea
        )

        #Создаётся поле для HTML-текста помощи.
        self.help_browser = QTextBrowser()
        self.help_browser.setReadOnly(True)
        self.load_help_text()
        # Панель помощи появляется справа. 
        self.help_dock.setWidget(self.help_browser)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.help_dock)
        self.resize(1000, 600)
        self.show()

    def load_help_text(self): # вызывается тут self.load_help_text()
        try: #если получается  войи, то ок, если нет, то в except
            with open("help.html", "r", encoding="utf-8") as file:#открыть файл
                                                                  #после чтения автоматически закрыть
                html = file.read() #чтение содержимого
        
            self.help_browser.setHtml(html) #правая панель показывает текст как веб-страницу

        except:
            self.help_browser.setHtml("<h2>Hilfe</h2><p>Help-Datei nicht gefunden.</p>")
            #чтобы программа не упала, если help.html отсутствует




    # --- Platzhalter für die Teilnehmer-Logik ---

    def menue_clicked(self): #Это центральная функция обработки кликов.
        """Zentraler Slot für alle Aktionen. Teilnehmer müssen das match-case implementieren."""
        sender = self.sender() #какой объект меня вызвал?
        command_id = sender.property("command")[0]
        
        
        # Beispielhafter Einstieg::
        if command_id == 13: self.db_login()  # Menüpunkt: Login zur Datenbank
        elif command_id == 11: self.csv_import_with_validation() # Menüpunkt: CSV-Datei importieren und in DB speichern
        elif command_id == 12: self.transfer_to_ad() # Menüpunkt: Daten für AD-Transfer vorbereiten
        elif command_id == 21: self.editaduser()  # Menüpunkt: ausgewählten Benutzer bearbeiten
        elif command_id == 22: self.delete_ad_user() # Menüpunkt: ausgewählten Benutzer löschen
        elif command_id ==23: self.deactivate_ad_user() # Menüpunkt: ausgewählten AD-Benutzer deaktivieren
        elif command_id == 24: self.show_import_report() # Menüpunkt: Validierungs-Report
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
    def db_login(self): #Это функция входа в базу данных.
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

            except Exception as e: #если логин неправильный / база недоступна:
                QMessageBox.critical(self, "Fehler", str(e))

        else:
            print("Login abgebrochen") #Если нажали Abbrechen:


    def load_ad_users(self): #После логина вызывается
        #мы открыли канал общения с БД
        cursor = self.db_connection.cursor() #Es wird ein "Werkzeug" zur Arbeit mit der Datenbank erstellt.
        #возьми все данные из view_aduser_details #view_aduser_details объединяет их в один удобный вид.

        cursor.execute("SELECT * FROM view_aduser_details") #Es wird eine Anfrage an die Datenbank gesendet.
        #забрать все строки результата
        rows = cursor.fetchall() #Alle Daten aus der Datenbank in Python abrufen

        headers = [description[0] for description in cursor.description] #Ich verwende Spaltennamen (zum Beispiel: Name, E-Mail usw.).

        #таблица получает 5 колонок.
        self.table_interessenten.setColumnCount(len(headers)) #wie viele Spalten
        #ставит заголовки: id | vorname | username | email | status
        self.table_interessenten.setHorizontalHeaderLabels(headers) #Spaltennamen (Überschriften).
        #Количество строк
        self.table_interessenten.setRowCount(len(rows)) #Wie viele Zeilen wird es geben
 
        for row_index, row_data in enumerate(rows): #jede Zeile aus der Datenbank. 0>(1, Max, max.stermann)
            for col_index, value in enumerate(row_data): #für jede Zelle innerhalb der Zeile.
                self.table_interessenten.setItem(
                    row_index,
                    col_index,
                    QTableWidgetItem(str(value)) #Wert in eine bestimmte Tabellenzelle einfügen.
                )
        self.table_interessenten.resizeColumnsToContents() #ширина колонок подстраивается под текст автоматически.
        cursor.close()
    #self.filter_input = QLineEdit() und self.filter_input.textChanged.connect(self.filter_ad_users)
    def filter_ad_users(self): #эта функция связанн с поиском пользователя  по поиску
        filter_text = self.filter_input.text().lower().strip() #для одинакового результата при 
        #разном стиле написания имени МАКС, макс, МаКс...
        
        for row in range(self.table_interessenten.rowCount()): # проверка каждого пользователя
            row_matches = False

            for col in range(self.table_interessenten.columnCount()): #например 
                item = self.table_interessenten.item(row, col)
                if item is not  None and filter_text in item.text().lower():
                    row_matches = True
                    break
            
            self.table_interessenten.setRowHidden(row, not row_matches)


    # Eine CSV-Zeile auslesen und die Felder für weitere Verarbeitung vorbereiten   
    #Она очищает данные и приводит их к нормальному виду.
    def process_csv_row(self, row, line_number, source_file): #получает  row, line_number, source_file
        firstname = (row.get("firstname") or "").strip()
        lastname = (row.get("lastname") or "").strip()
        phone = (row.get("phone") or "").strip()
        ou = (row.get("ou") or "").strip()
        street = (row.get("street") or "").strip()
        city = (row.get("city") or "").strip()
        city_code = (row.get("city_code") or "").strip()
        postalcode = (row.get("postalcode") or "").strip()
        kurs = (row.get("kurs") or "").strip()
        status_id_fk = (row.get("status_id_fk") or "").strip()

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
            "source_file": source_file #ошибка в файле kunden.csv
        }
    
    def validate_row(self, row): #Метод `validate_row` проверяет наличие обязательных полей в строке CSV-файла.
        errors = [] #создаём пустой список ошибок.
        
        if row["firstname"] == "": #проверяем, пустое ли поле firstname.
            errors.append({ #если ошибка есть, добавляем её в список.
                "field": "firstname",
                "value": row["firstname"],
                "reason": "Vorname fehlt"
            })

        if row["lastname"] == "":
            errors.append({
                "field": "lastname",
                 "value": row["lastname"],
                 "reason": "Nachname fehlt"
            })
        
        return errors #возвращаем список ошибок назад в CSV-Import.
    
      # Speichert einen Importfehler in der Datenbank
    # Сохраняет ошибку импорта в базу данных
    def log_import_error(self, source_file, line_number, error):

        # Cursor für SQL-Abfrage erstellen
        # Создаем cursor для SQL-запроса
        cursor = self.db_connection.cursor() #SQL-инструмент, через него будем писать в MariaDB

        # Fehler in Tabelle import_errors speichern
        # Сохраняем ошибку в таблицу import_errors
        #вставить новую запись в таблицу import_errors
        #NOW() = текущее время базы.
        cursor.execute("""
            INSERT INTO import_errors 
            (import_time, file_name, line_number, field_name, rejected_value, reason)
            VALUES (NOW(), %s, %s, %s, %s, %s)
        """, (
            source_file,         # Dateiname / имя файла
            line_number,         # Zeilennummer / номер строки
            error["field"],      # Feldname / имя поля
            error["value"],      # Falscher Wert / неправильное значение
            error["reason"]      # Fehlergrund / причина ошибки
        ))

        # Änderungen speichern
        # Сохраняем изменения
        self.db_connection.commit()

        # Cursor schließen
        # Закрываем cursor
        cursor.close()

    # Username aus Vorname und Nachname generieren (Format: firstname.lastname)
    def generate_username(self,firstname, lastname): #Она нужна, чтобы из имени и фамилии сделать логин пользователя.
        # Leerzeichen entfernen und alles in Kleinbuchstaben umwandeln
        firstname = firstname.strip().lower()
        lastname = lastname.strip().lower()

        username = f"{firstname}.{lastname}"
        # Username auf maximale Länge kürzen
        username = username[:20]
        return username
        
     # E-Mail aus Vorname, Nachname und Standort generieren   
    def generate_email(self, firstname, lastname, location): #Это функция автоматического создания email
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
    def user_exists(self, username): #Это функция проверки: есть ли уже такой пользователь в MARIA DB
        # Datenbankabfrage zur Überprüfung, ob Username bereits existiert
        cursor = self.db_connection.cursor()
        cursor.execute(
            "SELECT username FROM aduser WHERE username = %s", #найди такого пользователя
            (username,)
        )
        result = cursor.fetchone()
        cursor.close()
        # True zurückgeben, wenn Benutzer gefunden wurde, sonst False
        return result is not None

    # Neuen Benutzer in die Datenbank einfügen
    def insert_user(self, data): #Это функция сохранения нового пользователя в базу данных.
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
    def update_user(self, data): #Это функция обновления существующего пользователя в базе.
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
                           
                           


    #Она связывает сразу несколько методов
    # process_csv_row()
    #validate_row()
    #log_import_error()
    #generate_username()
    #generate_email()
    #user_exists()
    #insert_user()
    #update_user()
    #load_ad_users()
    def csv_import_with_validation(self):
        """
        TODO: CSV einlesen, Daten validieren (US 7) und in DB schreiben.
        Fehlerhafte Zeilen müssen in die Tabelle 'import_errors'.
        """
        if self.db_connection is None: #Если нет подключения к базе, импорт запрещён Einloggen
            QMessageBox.warning(self, "Fehler", "Bitte zuerst einloggen")
            return
            #Пользователь выбирает CSV
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
            with open(file_path, newline='', encoding='utf-8-sig') as csvfile: #utf-8-sig нужен, чтобы корректно читать CSV с немецкими
                reader = csv.DictReader(csvfile, delimiter=";") #CSV читается построчно, и каждая строка становится словарём
                
                print("CSV-Spalten:", reader.fieldnames)

                rows = list(reader)  #Все строки CSV сохраняются в список.
              
                

                

                print("Anzahl Zeigen:", len(rows))
                #Zähler für neue und bereits vorhandene Datensätze vorbereiten
                new_count = 0
                existing_count = 0
                rejected_count = 0 # Abgelehnte Zeilen zählen / Отклонённые строки считать

                for index, row in enumerate(rows, start=1):
                    processed_row = self.process_csv_row(row, index, file_path) #Здесь убираются пробелы
                    errors = self.validate_row(processed_row) #проверяем строку. firstname/ lastname
                    

                    if errors: #если список ошибок не пустой.
                        print("Fehler in Zeile:", index, errors) #показываем ошибку в терминале.
                        
                        
                        for error in errors:
                           self.log_import_error(file_path, index, error) # каждую отдельную ошибку сохранить в базу данных

                        rejected_count += 1 # Eine fehlerhafte Zeile zählen / Посчитать одну ошибочную строку
                        continue #пропускаем эту CSV-строку и переходим к следующей.

                    # Username für jeden Datensatz generieren
                    username = self.generate_username( #Если ошибок нет — генерируем username Max + Mustermann
                        processed_row["firstname"],
                        processed_row["lastname"]
                    )

                    # Username dem Datensatz hinzufügen
                    processed_row["username"] = username # такой ключ "username": "max.mustermann"

                    # E-Mail für jeden Datensatz generieren
                    email = self.generate_email(
                        processed_row["firstname"],
                        processed_row["lastname"],
                        processed_row["city"]
                    )
                    # E-Mail dem Datensatz hinzufügen
                    processed_row["email"] = email #Теперь данные готовы для базы.
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
                QMessageBox.information( #Сообщение пользователю
                    self,
                    "Import erfolgreich",
                    f"Neu importiert: {new_count}\nAktualisiert: {existing_count}\nAbgelehnt: {rejected_count}"
                )



        except Exception as e: #Если что-то сломалось, пользователь видит окно ошибки.
            QMessageBox.critical(self, "Fehler", str(e))

        print(file_path)

    #Это функция открытия окна редактирования пользователя.
    # Она только находит выбранного пользователя и открывает окно редактирования.
    def editaduser(self):  #Это метод MainWindow
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
    #Это функция полного удаления пользователя из базы данных.
    def delete_ad_user(self):
        # Prüfen, ob ein Benutzer ausgewählt ist
        selection = self.table_interessenten.selectedItems() #Берём выделенную строку.
        if not selection:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie einen User aus!")
            return
        
        #ID aus erster Spalte holen
        row = selection[0].row()
        userid = self.table_interessenten.item(row, 0).text()        

        #Sicherhetsabfrage
        antwort = QMessageBox.question( #Benutzer wirklich löschen?
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
                    "DELETE FROM aduser WHERE id_pk = %s", #удалить пользователя с этим ID?
                    (int(userid),) 
                )

                self.db_connection.commit()
                cursor.close()

                QMessageBox.information(self, "Erfolg", "Benutzer gelöscht")

                #Tabelle neu Laden

                self.load_ad_users()

            except Exception as e:
                QMessageBox.critical(self, "Fehler", str(e))


    def deactivate_ad_user(self): #Это функция деактивации пользователя.
        """Deaktiviert den ausgewöhlten Benutzer (Status ändern)."""
        #Prüfen, ob ein Benutzer ausgewählt ist
        selection = self.table_interessenten.selectedItems() #Берём выбранную строку.
        if not selection:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie einen User aus!")
            return
        #ID aus der ersten Spalte holen
        row = selection[0].row()
        userid = self.table_interessenten.item (row, 0).text()

        #Sicherheitsabfrage
        antwort = QMessageBox.question( #показывает  Benutzer wirklich deaktivieren?
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

    # Öffnet das Fenster mit dem Validierungs-Report
    # Открывает окно с отчётом ошибок валидации
    def show_import_report(self):
        # Prüfen, ob Datenbankverbindung besteht
        # Проверяем, есть ли подключение к базе данных
        if self.db_connection is None:
            QMessageBox.warning(self, "Fehler", "Bitte zuerst einloggen")
            return
        # Report-Fenster erstellen
        # Создаём окно отчёта
        self.report_window = ImportReportWindow(self.db_connection, self)
        # Report-Fenster anzeigen
        # Показываем окно отчёта
        self.report_window.show()

    def transfer_to_ad(self): # создает transfer_ad_20260427_115704.json
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

        
        
    #эта функция достаёт пользователей из базы и подготавливает их для JSON.
    def get_all_ad_users_for_transfer(self): #Вот это мост между базой данных и JSON-файлом.
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
            

#Это точка запуска всей Python-программы.
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()