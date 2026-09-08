@echo off
:: Script de inicialização automatizada para sistemas Windows.
chcp 65001 > nul

:: Garante que o diretório de trabalho do terminal seja sempre a raiz do script
set DIR_RAIZ=%~dp0
cd /d "%DIR_RAIZ%"

echo =========================================================
echo 🛸 Iniciando o Ambiente do App Neutron Star...
echo =========================================================

:: 1. Verifica se o ambiente virtual existe fisicamente na raiz
if not exist ".venv" (
    echo ❌ Erro: O ambiente virtual '.venv' não foi encontrado na raiz.
    echo Por favor, crie-o primeiro rodando:
    echo    python -m venv .venv
    echo    .venv\Scripts\activate
    echo    pip install -r Atoms\requirements.txt
    echo.
    pause
    exit /b 1
)

:: 2. Ativa o ambiente virtual isolado no Windows
echo 📦 Ativando ambiente virtual (.venv)...
call .venv\Scripts\activate.bat

:: 3. Navega para a subpasta Atoms onde o main.py está localizado
cd Atoms

:: 4. Executa a aplicação Flask com debugger ativo
set FLASK_DEBUG=1
python main.py

:: Mantém o terminal aberto se ocorrer erro de crash no servidor
if %errorlevel% neq 0 (
    echo.
    echo ❌ O servidor Neutron Star encerrou com falhas.
    pause
)
