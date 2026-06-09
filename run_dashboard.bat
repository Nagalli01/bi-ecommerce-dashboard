@echo off
title Nexus Dashboard
cd /d "%~dp0.."
echo ========================================
echo   NEXUS - DASHBOARD WEB
echo ========================================
echo.
echo 1. Dashboard Local (http://localhost:8501)
echo 2. Dashboard Publico (Ngrok - link compartilhavel)
echo.
set /p opcao="Escolha (1 ou 2): "

if "%opcao%"=="2" (
    echo.
    echo Iniciando Streamlit + Ngrok...
    echo Gerando link publico... (aguarde alguns segundos)
    python src\launch_web.py
) else (
    echo.
    echo Iniciando servidor local...
    echo Abra http://localhost:8501
    python -m streamlit run src\dashboard_app.py --server.port 8501
)

pause
