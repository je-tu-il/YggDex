@echo off
title YggDex - Acces Distant Securise (zrok)
color 0B

echo ======================================================================
echo          YGGDEX - ACCES DISTANT SECURISE VIA ZROK TUNNEL
echo ======================================================================
echo.

REM 1. Verification de l'executable zrok
where zrok >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "ZROK_CMD=zrok"
) else (
    if exist "E:\App\Pc\Installer\Cmd\Path\zrok.exe" (
        set "ZROK_CMD=E:\App\Pc\Installer\Cmd\Path\zrok.exe"
    ) else (
        echo [ERREUR] zrok.exe est introuvable sur le systeme.
        echo Telechargez zrok depuis https://zrok.io
        pause
        exit /b 1
    )
)

REM 2. Verification de l'activation zrok
"%ZROK_CMD%" status > "%TEMP%\zrok_status.tmp" 2>&1
findstr /i "zrok enable" "%TEMP%\zrok_status.tmp" >nul
if %ERRORLEVEL% EQU 0 (
    del "%TEMP%\zrok_status.tmp" >nul 2>&1
    goto :ACTIVATE_ZROK
)
del "%TEMP%\zrok_status.tmp" >nul 2>&1
goto :CHECK_SERVER

:ACTIVATE_ZROK
echo [!] Votre environnement zrok n'est pas encore active sur cet ordinateur.
echo.
echo   [1] J'ai deja un token zrok (lancer 'zrok enable')
echo   [2] Je n'ai pas de compte zrok (creer un compte gratuit avec 'zrok invite')
echo   [3] Quitter
echo.
set /p CHOIX="Votre choix [1/2/3] : "

if "%CHOIX%"=="1" (
    echo.
    set /p ZTOKEN="Collez votre token zrok ici : "
    if "%ZTOKEN%"=="" (
        echo [!] Token vide. Operation annulee.
        pause
        exit /b 1
    )
    echo.
    echo [+] Activation de l'environnement zrok...
    "%ZROK_CMD%" enable %ZTOKEN%
    if %ERRORLEVEL% NEQ 0 (
        echo [ERREUR] Impossible d'activer le token zrok.
        pause
        exit /b 1
    )
    echo [OK] zrok est maintenant active !
    echo.
    goto :CHECK_SERVER
)

if "%CHOIX%"=="2" (
    echo.
    echo [+] Lancement de la procedure d'invitation zrok :
    "%ZROK_CMD%" invite
    echo.
    echo ------------------------------------------------------------------
    echo Consultez vos emails pour valider votre compte et obtenir votre token.
    echo Une fois votre token recu, relancez ce script et choisissez [1].
    echo ------------------------------------------------------------------
    pause
    exit /b 0
)

exit /b 0

:CHECK_SERVER
REM 3. Verification du serveur YggDex
netstat -ano | findstr /R ":7777 " >nul
if %ERRORLEVEL% NEQ 0 (
    echo [+] Demarrage du serveur YggDex local (1 218 387 torrents)...
    start "Serveur YggDex Local" /min python "%~dp0server.py" --no-browser
    timeout /t 3 /nobreak >nul
) else (
    echo [OK] Serveur local YggDex actif sur le port 7777.
)

REM 4. Mode de tunnel zrok
echo.
echo ======================================================================
echo Choisissez le mode de partage distant :
echo   [1] Acces Public Direct (URL HTTPS securisee accessible partout)
echo   [2] Acces Public Protege par Mot de Passe (Basic Auth)
echo ======================================================================
echo.
set /p MODE="Votre choix [1/2] (defaut: 1) : "

if "%MODE%"=="2" (
    echo.
    set /p AUTH_USER="Nom d'utilisateur distant : "
    set /p AUTH_PASS="Mot de passe distant : "
    echo.
    echo ======================================================================
    echo  TUNNEL EN COURS...
    echo  Authentification requise : %AUTH_USER% / ****
    echo  Appuyez sur Ctrl+C dans cette console pour arreter le tunnel.
    echo ======================================================================
    echo.
    "%ZROK_CMD%" share public http://localhost:7777 --backend-mode proxy --basic-auth %AUTH_USER%:%AUTH_PASS%
) else (
    echo.
    echo ======================================================================
    echo  TUNNEL EN COURS...
    echo  L'URL publique HTTPS generee ci-dessous est accessible depuis
    echo  votre smartphone, tablette ou PC distant (4G/5G/WiFi).
    echo  Appuyez sur Ctrl+C dans cette console pour arreter le tunnel.
    echo ======================================================================
    echo.
    "%ZROK_CMD%" share public http://localhost:7777 --backend-mode proxy
)

echo.
echo Tunnel zrok arrete.
pause
