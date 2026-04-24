# Parameter für Import-Ordner / Параметр для папки импорта
param(
    [string]$ImportFolder = "network_test",
    #Passwort sicher eingeben / Ввод пароля безопасно
    [Parameter(Mandatory=$true)]
    [securestring]$Password
)
# AD Modul laden / Загрузка модуля AD
Import-Module ActiveDirectory
#Testausgabe / Проверочный вывод
Write-Host "ImportToAD.ps1 wurde gestartet"
Write-Host  "Import-Ordner: $ImportFolder"
# JSON-Datei suchen / Ищем JSON файл
$transferFile = Get-ChildItem -Path $ImportFolder -Filter "transfer_ad_*.json" | Select-Object -First 1
Write-Host "Gefunde Datei: $transferFile"
# Prüfen, ob eine Datei gefunden wurde / Проверяем, найден ли файл
if ($null -eq $transferFile) {
    Write-Host "Keine Transfer-Datei gefunden/ Transfer-Datei nicht gefunden"
    exit
}
# JSON-Datei einlesen / Чтение JSON файла
$transferData = Get-Content -Path $transferFile.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
# Anzahl Benutzer sicher zählen / Надёжно считаем пользователей
Write-Host "Anzahl Benutzer:" @($transferData).Count
#Jeden Benutzer aus JSON verarbeiten/ Обрабатываем каждого пользователя из JSON
foreach ($user in $transferData) {
    #Benutzername anzeigen / Показываем имя пользователя
    Write-Host "Username:" $user.username
    # Login bereinigen / очищаем логин
    $login = $user.username.Trim().ToLower()
    $login = $login -replace "\u00E4","ae"
    $login = $login -replace "\u00F6","oe"
    $login = $login -replace "\u00FC","ue"
    $login = $login -replace "\u00DF","ss"
    $login = $login -replace '\s+',''
    $login = $login -replace '[^a-z0-9\.\-]',''
    $login = $login.Substring(0, [Math]::Min(20, $login.Length))
    #Benutzer in AD suchen / Ищем пользователя в AD
    $adUser = Get-ADUser -Filter  "SamAccountName -eq '$login'" -ErrorAction SilentlyContinue
    #Prüfen, ob Benutzer existiert / Проверяем, существует ли пользователь
    if ($adUser) {
        Write-Host "User existiert:" $login

        Set-ADUser `
            -Identity $login `
            -EmailAddress $user.email

    }
    
    else {
        Write-Host "User NICHT gefunden:" $login
        #Ziel-OU festlegen/ Указываем OU для создания пользователя
        $targetOU = "OU=OU,DC=m-zukunftsmotor,DC=local"
        try{ 
        #Benutzer erstellen / Создаём пользователя
        New-ADUser `
            -Name "$($user.firstname) $($user.lastname) ($login)" `
            -GivenName $user.firstname `
            -Surname $user.lastname `
            -SamAccountName $login `
            -UserPrincipalName "$($login)@m-zukunftsmotor.local" `
            -EmailAddress $user.email `
            -Path $targetOU `
            -AccountPassword $Password `
            -Enabled $true `
            -ChangePasswordAtLogon $true
        Write-Host "User erstellt:" $login
        }
        catch {
            Write-Host "Fehler beim Benutzer:" $login
            Write-Host $_.Exception.Message
        }
    }
}