from PyQt6.QtWidgets import (
    QWidget, QMessageBox, QGridLayout, QLabel, QLineEdit, QPushButton
)

class EditADUserWindow(QWidget):

    def __init__(self, caption, userid, db_connection, main_window=None):
        super().__init__()

        # Fenstertitel setzen
        self.setWindowTitle(caption)

        # Daten speichern
        self.userid = userid
        self.db_connection = db_connection
        self.main_window = main_window

        # Layout erstellen
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Feld: Vorname
        self.label_firstname = QLabel("Vorname:")
        self.input_firstname = QLineEdit()

        # Feld: Nachname
        self.label_lastname = QLabel("Nachname:")
        self.input_lastname = QLineEdit()

        # Feld: E-Mail
        self.label_email = QLabel("E-Mail:")
        self.input_email = QLineEdit()

        # Feld: Telefon
        self.label_phone = QLabel("Telefon:")
        self.input_phone = QLineEdit()

        # Buttons
        self.btn_ok = QPushButton("OK")
        self.btn_cancel = QPushButton("Abbrechen")

        # Widgets ins Layout einfügen
        self.layout.addWidget(self.label_firstname, 0, 0)
        self.layout.addWidget(self.input_firstname, 0, 1)

        self.layout.addWidget(self.label_lastname, 1, 0)
        self.layout.addWidget(self.input_lastname, 1, 1)

        self.layout.addWidget(self.label_email, 2, 0)
        self.layout.addWidget(self.input_email, 2, 1)

        self.layout.addWidget(self.label_phone, 3, 0)
        self.layout.addWidget(self.input_phone, 3, 1)

        self.layout.addWidget(self.btn_ok, 4, 0)
        self.layout.addWidget(self.btn_cancel, 4, 1)

        # Signale verbinden
        self.btn_ok.clicked.connect(self.save_user)
        self.btn_cancel.clicked.connect(self.close)

        # Benutzerdaten laden
        self.load_user_data()

    def load_user_data(self):
        """Lädt die Benutzerdaten aus der Datenbank."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT firstname, lastname, email, phone
                FROM aduser
                WHERE id_pk = %s
            """, (self.userid,))
            row = cursor.fetchone()
            cursor.close()

            if row is None:
                QMessageBox.warning(self, "Fehler", "Benutzer nicht gefunden.")
                self.close()
                return

            # Felder mit DB-Daten füllen
            self.input_firstname.setText("" if row[0] is None else str(row[0]))
            self.input_lastname.setText("" if row[1] is None else str(row[1]))
            self.input_email.setText("" if row[2] is None else str(row[2]))
            self.input_phone.setText("" if row[3] is None else str(row[3]))

        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden:\n{e}")
            self.close()

    def save_user(self):
        """Speichert die geänderten Benutzerdaten in der Datenbank."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE aduser
                SET firstname = %s,
                    lastname = %s,
                    email = %s,
                    phone = %s,
                    modified = NOW()
                WHERE id_pk = %s
            """, (
                self.input_firstname.text(),
                self.input_lastname.text(),
                self.input_email.text(),
                self.input_phone.text(),
                self.userid
            ))
            self.db_connection.commit()
            cursor.close()

            QMessageBox.information(self, "Erfolg", "Benutzer erfolgreich aktualisiert.")

            # Haupttabelle neu laden
            if self.main_window is not None:
                self.main_window.load_ad_users()

            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern:\n{e}")