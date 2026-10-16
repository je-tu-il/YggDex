@echo off
title YggDex - Moteur de Recherche Local
color 0B
echo ========================================================
echo        LANCEMENT DE YGGDEX (MOTEUR DE RECHERCHE LOCAL)
echo ========================================================
echo.
echo Initialisation du serveur local sur http://localhost:7777 ...
echo Ouverture automatique de votre navigateur...
echo.
python "%~dp0server.py"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERREUR] Le serveur s'est arrêté de façon inattendue.
    pause
)
