@echo off
chcp 65001 >nul
title YggDex - Assistant d'Installation Rapide
color 0B

echo ======================================================================
echo           🏴‍☠️ YggDex - Assistant d'Installation Rapide
echo ======================================================================
echo.

:: 1. Vérification de Python
echo [1/4] Vérification de l'environnement Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Python n'est pas détecté sur votre système !
    echo Veuillez installer Python depuis https://www.python.org/downloads/
    echo Assurez-vous de cocher la case "Add Python to PATH" lors de l'installation.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version') do echo [OK] %%v détecté.
echo.

:: 2. Vérification de la base de données
echo [2/4] Vérification de la base de données (ygg_torrents.db)...
if exist "%~dp0ygg_torrents.db" (
    echo [OK] Base de données locale trouvée.
) else (
    echo [!] Le fichier 'ygg_torrents.db' est absent dans ce dossier.
    echo.
    echo Vous devez télécharger la base de données depuis les Releases GitHub.
    echo Placez 'ygg_torrents.db' dans : %~dp0
    echo.
    set /p DL="Voulez-vous ouvrir la page des Releases GitHub maintenant ? (O/N) : "
    if /i "%DL%"=="O" (
        start https://github.com/
    )
)
echo.

:: 3. Création du raccourci sur le Bureau
echo [3/4] Création du raccourci sur le Bureau...
set SCRIPT_DIR=%~dp0
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'YggDex.lnk')); $s.TargetPath = '%SCRIPT_DIR%Lancer_YggDex.bat'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Description = 'Moteur de Recherche YggDex'; $s.Save()" >nul 2>&1
if exist "%USERPROFILE%\Desktop\YggDex.lnk" (
    echo [OK] Raccourci 'YggDex' créé sur votre Bureau.
) else (
    echo [INFO] Raccourci bureau optionnel non créé.
)
echo.

:: 4. Lancement
echo [4/4] Installation terminée avec succès !
echo.
set /p LAUNCH="Voulez-vous lancer YggDex dès maintenant ? (O/N, défaut O) : "
if /i "%LAUNCH%"=="N" (
    echo.
    echo Vous pourrez lancer YggDex à tout moment via le raccourci Bureau ou 'Lancer_YggDex.bat'.
    pause
    exit /b 0
)

call "%~dp0Lancer_YggDex.bat"
