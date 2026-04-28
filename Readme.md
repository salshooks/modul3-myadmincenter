Installationsanleitung – myAdmin Center

1. Voraussetzungen installieren

Folgende Software muss installiert sein:

- Python 3.x
- MariaDB
- PyQt6
- mysql-connector-python
- RSAT / Active Directory Modul für PowerShell

Python-Module installieren:

pip install PyQt6
pip install mysql-connector-python

2. Datenbank vorbereiten

In MariaDB muss die Datenbank erstellt werden.

Benötigte Tabellen:

- aduser
- aduser_status
- import_errors

Zusätzlich muss die View erstellt werden:

- view_aduser_details

3. Projektdateien kopieren

Projektordner auf den Rechner kopieren.

Wichtige Dateien:

- mainapplication.py
- editaduser_TN.py
- help.html
- ImportToAD.ps1
- Run-ImportToAD.ps1

Ordner:

- images/
- exports/
- network_test/

4. Anwendung starten

Python-Anwendung starten:

python mainapplication.py

Danach erscheint das Fenster „myAdmin Center“.

5. Datenbankverbindung herstellen

Über „Einloggen“ folgende Daten eingeben:

- Host
- Datenbankname
- Benutzername
- Passwort

Nach erfolgreichem Login werden die Benutzerdaten geladen.

6. CSV importieren

Über „Import von CSV“ eine CSV-Datei auswählen.

Die Daten werden:

- validiert
- in MariaDB gespeichert
- Fehler werden in import_errors protokolliert

7. Transfer nach Active Directory

Über „Transfer nach AD“ wird eine JSON-Datei erzeugt.

Diese Datei wird in den Import-Ordner kopiert.

8. PowerShell Import

PowerShell-Skript starten:

.\Run-ImportToAD.ps1

Das Skript:

- liest die JSON-Datei
- prüft vorhandene Benutzer
- aktualisiert bestehende Benutzer
- erstellt neue Benutzer in Active Directory

9. Automatischer Import (optional)

Über Windows Aufgabenplanung kann Run-ImportToAD.ps1 automatisch alle 5 Minuten gestartet werden.