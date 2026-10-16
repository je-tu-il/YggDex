@echo off
title Moteur de Recherche Local YGG
color 0B
echo ========================================================
echo        LANCEMENT DU MOTEUR DE RECHERCHE YGG
echo ========================================================
echo.
echo Initialisation du serveur local sur http://localhost:7777 ...
echo Ouverture automatique de votre navigateur...
echo.
python "%~dp0server.py"
pause
