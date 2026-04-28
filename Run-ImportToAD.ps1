# Pfade festlegen
$scriptPath = ".\ImportToAD.ps1"
$importFolder = ".\network_test"

# Passwort sicher eingeben
$password = Read-Host "Passwort eingeben" -AsSecureString

# Import-Skript starten
& $scriptPath -ImportFolder $importFolder -Password $password