# Pfade festlegen / Указываем пути
$scriptPath = "C:\Users\pth\Documents\k22\Yaroslav\Yaroslav_22.04_modul3-myadmincenter\ImportToAD.ps1"
$importFolder = "C:\Users\pth\Documents\k22\Yaroslav\Yaroslav_22.04_modul3-myadmincenter\network_test"

# Passwort sicher eingeben / Безопасный ввод пароля
$password = Read-Host "Passwort eingeben" -AsSecureString

# Import-Skript starten
& $scriptPath -ImportFolder $importFolder -Password $password

# Import-Skript starten / Запускаем импорт-скрипт
& $scriptPath -ImportFolder $importFolder -Password $password