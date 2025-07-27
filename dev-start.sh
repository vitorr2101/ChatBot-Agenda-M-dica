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
        kill $FRONTEND_PID 2>/dev/null
    fi
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$MCP_PID" ]; then
        kill $MCP_PID 2>/dev/null
    fi
    
    pkill -f "next dev" 2>/dev/null
    pkill -f "uvicorn.*app.main:app" 2>/dev/null
    pkill -f "python.*server.py" 2>/dev/null
    
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

echo -e "${BLUE}Iniciando Backend (Agent)...${NC}"
cd backend/agent
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ../..
echo -e "${GREEN}✓ Backend iniciado (PID: $BACKEND_PID)${NC}"

sleep 2

echo -e "${BLUE}Iniciando Servidor MCP...${NC}"
cd backend/server
.venv/bin/python server.py > ../../logs/mcp-server.log 2>&1 &
MCP_PID=$!
cd ../..
echo -e "${GREEN}✓ Servidor MCP iniciado (PID: $MCP_PID)${NC}"

sleep 2

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
echo -e "  MCP Server:   tail -f logs/mcp-server.log"
echo -e "  Frontend:     tail -f logs/frontend.log"
echo ""
echo -e "${YELLOW}Pressione Ctrl+C para encerrar todos os serviços${NC}"

mkdir -p logs

wait
