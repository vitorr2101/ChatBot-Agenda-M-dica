#!/bin/bash

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

cleanup() {
    echo -e "\n${YELLOW}Encerrando todos os serviços...${NC}"
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    sleep 2
    
    pkill -f "next dev" 2>/dev/null || true
    pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
    
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    
    echo -e "${GREEN}Todos os serviços foram encerrados.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

echo -e "${BLUE}=== Iniciando Ambiente de Desenvolvimento ===${NC}"
echo -e "${BLUE}ChatBot Agenda Médica - Todos os Serviços${NC}"
echo ""

if [ ! -d "backend/agent/.venv" ]; then
    echo -e "${RED}Erro: Ambiente virtual do backend não encontrado.${NC}"
    echo -e "${YELLOW}Execute: ./setup.sh${NC}"
    exit 1
fi

if [ ! -d "backend/server/.venv" ]; then
    echo -e "${RED}Erro: Ambiente virtual do servidor MCP não encontrado.${NC}"
    echo -e "${YELLOW}Execute: ./setup.sh${NC}"
    exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
    echo -e "${RED}Erro: Dependências do frontend não instaladas.${NC}"
    echo -e "${YELLOW}Execute: ./setup.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Verificações de ambiente concluídas${NC}"
echo ""

echo -e "${BLUE}Verificando processos existentes...${NC}"
if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
    echo -e "${YELLOW}Encerrando processos backend existentes...${NC}"
    pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
    sleep 2
fi

if pgrep -f "next dev" > /dev/null; then
    echo -e "${YELLOW}Encerrando processos frontend existentes...${NC}"
    pkill -f "next dev" 2>/dev/null || true
    sleep 2
fi

if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${YELLOW}Porta 8000 em uso, liberando...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

if lsof -ti:3000 > /dev/null 2>&1; then
    echo -e "${YELLOW}Porta 3000 em uso, liberando...${NC}"
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo -e "${GREEN}✓ Portas liberadas${NC}"
echo ""

mkdir -p logs

echo -e "${BLUE}Iniciando Backend (Agent)...${NC}"
cd backend/agent
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ../..
echo -e "${GREEN}✓ Backend iniciado (PID: $BACKEND_PID)${NC}"

sleep 3

echo -e "${BLUE}Iniciando Frontend...${NC}"
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✓ Frontend iniciado (PID: $FRONTEND_PID)${NC}"

echo ""
echo -e "${GREEN}=== Todos os serviços iniciados com sucesso! ===${NC}"
echo ""
echo -e "${BLUE}URLs dos serviços:${NC}"
echo -e "  Frontend:     http://localhost:3000"
echo -e "  Backend API:  http://localhost:8000"
echo -e "  API Docs:     http://localhost:8000/docs"
echo ""
echo -e "${BLUE}Logs em tempo real:${NC}"
echo -e "  Backend:      tail -f logs/backend.log"
echo -e "  Frontend:     tail -f logs/frontend.log"
echo ""
echo -e "${YELLOW}Pressione Ctrl+C para encerrar todos os serviços${NC}"

wait
