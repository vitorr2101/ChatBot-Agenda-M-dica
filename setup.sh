#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 não está instalado. Por favor, instale o Python 3.8+ antes de continuar."
        exit 1
    fi
    print_success "Python $(python3 --version) encontrado"
}

check_node() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js não está instalado. Por favor, instale o Node.js 16+ antes de continuar."
        exit 1
    fi
    print_success "Node.js $(node --version) encontrado"
}

setup_backend() {
    print_step "Configurando o serviço de backend..."
    
    if [ ! -f "backend/agent/requirements.txt" ]; then
        print_warning "Arquivo backend/agent/requirements.txt não encontrado. Pulando configuração do backend."
        return
    fi
    
    cd backend/agent
    
    if [ ! -d ".venv" ]; then
        print_step "Criando ambiente virtual para o backend..."
        python3 -m venv .venv
        print_success "Ambiente virtual criado em backend/agent/.venv"
    else
        print_success "Ambiente virtual já existe em backend/agent/.venv"
        if [ ! -f ".venv/bin/python" ] || ! .venv/bin/python -m pip --version &>/dev/null; then
            print_step "Recriando ambiente virtual (pip não encontrado)..."
            rm -rf .venv
            python3 -m venv .venv
            print_success "Ambiente virtual recriado em backend/agent/.venv"
        fi
    fi
    
    print_step "Instalando dependências do backend..."
    .venv/bin/python -m pip install --upgrade pip
    .venv/bin/python -m pip install -r requirements.txt
    
    print_success "Backend configurado com sucesso!"
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_warning "IMPORTANTE: Arquivo .env não encontrado no backend!"
            print_warning "Copie o arquivo .env.example para .env e configure as variáveis:"
            print_warning "  cp backend/agent/.env.example backend/agent/.env"
            print_warning "  Edite backend/agent/.env com suas configurações (API keys, etc.)"
        else
            print_warning "Arquivo .env não encontrado no backend. Certifique-se de criar um com as configurações necessárias."
        fi
    fi
    
    cd ../..
}

setup_mcp_server() {
    print_step "Configurando o servidor MCP..."
    
    if [ ! -f "backend/server/requirements.txt" ]; then
        print_warning "Arquivo backend/server/requirements.txt não encontrado. Pulando configuração do servidor MCP."
        return
    fi
    
    cd backend/server
    
    if [ ! -d ".venv" ]; then
        print_step "Criando ambiente virtual para o servidor MCP..."
        python3 -m venv .venv
        print_success "Ambiente virtual criado em backend/server/.venv"
    else
        print_success "Ambiente virtual já existe em backend/server/.venv"
        if [ ! -f ".venv/bin/python" ] || ! .venv/bin/python -m pip --version &>/dev/null; then
            print_step "Recriando ambiente virtual (pip não encontrado)..."
            rm -rf .venv
            python3 -m venv .venv
            print_success "Ambiente virtual recriado em backend/server/.venv"
        fi
    fi
    
    print_step "Instalando dependências do servidor MCP..."
    .venv/bin/python -m pip install --upgrade pip
    .venv/bin/python -m pip install -r requirements.txt
    
    print_success "Servidor MCP configurado com sucesso!"
    
    cd ../..
}

setup_frontend() {
    print_step "Configurando o frontend..."
    
    if [ ! -f "frontend/package.json" ]; then
        print_warning "Arquivo frontend/package.json não encontrado. Pulando configuração do frontend."
        return
    fi
    
    cd frontend
    
    print_step "Instalando dependências do frontend..."
    npm install
    
    print_success "Frontend configurado com sucesso!"
    
    cd ..
}

final_checks() {
    print_step "Realizando verificações finais..."
    
    if [ ! -f "package.json" ]; then
        print_warning "Arquivo package.json não encontrado na raiz do projeto."
        print_warning "Considere criar um para orquestrar todos os serviços."
    fi
    
    print_success "Configuração completa!"
    echo ""
    echo -e "${BLUE}=== PRÓXIMOS PASSOS ===${NC}"
    echo "1. Configure os arquivos .env conforme os avisos acima"
    echo "2. Para desenvolvimento, use os comandos:"
    echo "   - Frontend: cd frontend && npm run dev"
    echo "   - Backend: cd backend/agent && source .venv/bin/activate && python -m uvicorn app.main:app --reload"
    echo ""
    echo "3. Ou use o script de desenvolvimento conjunto (recomendado): ./dev-start.sh"
    echo ""
}

main() {
    echo -e "${BLUE}=== CONFIGURAÇÃO AUTOMÁTICA DO PROJETO DE IA ===${NC}"
    echo "Chatbot Agenda Médica - Sistema Multi-serviços"
    echo ""
    
    check_python
    check_node
    echo ""
    
    setup_backend
    echo ""
    setup_mcp_server
    echo ""
    setup_frontend
    echo ""
    
    final_checks
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
