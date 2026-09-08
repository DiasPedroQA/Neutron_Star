#!/bin/bash
# -*- coding: utf-8 -*-
# Script de inicialização automatizada para sistemas Linux/macOS.

# Garante que o diretório de trabalho seja sempre a raiz do repositório
DIR_RAIZ="$( cd "$( dirname "${BASH_SOURCE}" )" && pwd )"
cd "$DIR_RAIZ"

echo "========================================================="
echo "🛸 Iniciando o Ambiente do App Neutron Star..."
echo "========================================================="

# 1. Verifica se o ambiente virtual existe fisicamente na raiz
if [ ! -d ".venv" ]; then
    echo "❌ Erro: O ambiente virtual '.venv' não foi encontrado na raiz."
    echo "Por favor, crie-o primeiro rodando:"
    echo "   python3 -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r Atoms/requirements.txt"
    echo ""
    read -p "Pressione [Enter] para sair..."
    exit 1
fi

# 2. Ativa o ambiente virtual isolado
echo "📦 Ativando ambiente virtual (.venv)..."
source .venv/bin/activate

# 3. Navega para a subpasta Atoms onde o entrypoint principal está
cd Atoms

# 4. Executa a aplicação Flask com suporte a debugger seguro
export FLASK_DEBUG=1
python3 main.py

# Desativa o ambiente virtual ao encerrar o servidor
deactivate
