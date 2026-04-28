# Parameter für Import-Ordner / Параметр для папки импорта
param(
    [Parameter(Mandatory=$true)]
    [string]$ImportFolder,

    # Passwort sicher eingeben / Ввод пароля безопасно
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
    # Feste Ziel-OU / Фиксированная OU для создания
    $targetOU = "OU=OU,DC=m-zukunftsmotor,DC=local"

    # Prüfen, ob Ziel-OU existiert / Проверяем, существует ли целевая OU
    try {
        $ouExists = Get-ADOrganizationalUnit -Identity $targetOU -ErrorAction Stop #попробовать найти OU в Active Directory
    }
    catch {
        Write-Host "OU nicht gefunden, Benutzer wird abgelehnt:" $targetOU
        continue
    }   
    #Benutzer in AD suchen / Ищем пользователя в AD
    $adUser = Get-ADUser -Filter  "SamAccountName -eq '$login'" -ErrorAction SilentlyContinue
    #Prüfen, ob Benutzer existiert / Проверяем, существует ли пользователь
    if ($adUser) {
        Write-Host "User existiert:" $login

        
        # Benutzerdaten aktualisieren / Обновляем данные пользователя
        Set-ADUser `
            -Identity $login `
            -EmailAddress $user.email `
            -StreetAddress $user.street `
            -PostalCode $user.postalcode `
            -City $user.city `
            -OfficePhone $user.phone
        
        #если поле ou в JSON не пустое — записать его в Department
        # Department nur aktualisieren, wenn OU im JSON nicht leer ist / Department обновляем только если OU в JSON не пустая
        if (-not [string]::IsNullOrWhiteSpace($user.ou)) {
            Set-ADUser `
                    -Identity $login `
                    -Department $user.ou
        }

        # Prüfen, ob Benutzer in der richtigen OU liegt / Проверяем, находится ли пользователь в правильной OU
        if ($adUser.DistinguishedName -notlike "*$targetOU") {
            # Benutzer in die Ziel-OU verschieben / Перемещаем пользователя в целевую OU
            Move-ADObject -Identity $adUser.DistinguishedName -TargetPath $targetOU #Move-ADObject перемещает AD-объект в целевую OU.
            Write-Host "User wurde in die Ziel-OU verschoben:" $login
        }

    }
    
    else {
        Write-Host "User NICHT gefunden:" $login #если пользователя нет в AD — дальше будет New-ADUser
        #Если пользователя нет в AD, скрипт создаёт нового пользователя с данными из JSON, помещает его в нужную OU, задаёт стартовый пароль, включает аккаунт и требует смену пароля при первом входе.
        try{ 
        #Benutzer erstellen / Создаём пользователя
        New-ADUser `
            -Name "$($user.firstname) $($user.lastname) ($login)" `
            -GivenName $user.firstname `
            -Surname $user.lastname `
            -SamAccountName $login `
            -UserPrincipalName "$($login)@m-zukunftsmotor.local" `
            -EmailAddress $user.email `
            -StreetAddress $user.street `
            -PostalCode $user.postalcode `
            -City $user.city `
            -OfficePhone $user.phone `
            -Department $user.ou `
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