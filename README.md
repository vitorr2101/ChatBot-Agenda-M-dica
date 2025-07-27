# ChatBot Agenda Médica

Sistema inteligente de agendamento médico baseado em IA que utiliza Model Context Protocol (MCP) para gerenciar consultas especializadas e exames médicos de forma automatizada e conversacional.

## Visão Geral

O projeto implementa uma arquitetura moderna distribuída em três componentes principais que trabalham em conjunto para fornecer uma experiência completa de agendamento médico assistido por inteligência artificial.

### Arquitetura do Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend Agent  │    │  MCP Server     │
│   (Next.js)     │◄──►│   (FastAPI)      │◄──►│  (Database)     │
│                 │    │                  │    │                 │
│ • Interface Web │    │ • LLM Client     │    │ • MongoDB       │
│ • Chat UI       │    │ • Orchestrator   │    │ • Tool Provider │
│ • File Upload   │    │ • MCP Client     │    │ • Data Services │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Componentes Técnicos

### 1. Frontend (Next.js + TypeScript)

Interface web moderna desenvolvida com Next.js que oferece:

- **Chat Interface**: Sistema de conversação em tempo real com o assistente de IA
- **Multimodal Input**: Suporte para texto e upload de imagens/documentos médicos
- **Responsive Design**: Interface adaptável para desktop e dispositivos móveis
- **Real-time Updates**: Feedback instantâneo durante as operações de agendamento

**Tecnologias**: Next.js 14, TypeScript, Tailwind CSS, React Hooks

**Localização**: `frontend/`

### 2. Backend Agent (FastAPI + Python)

Serviço principal que orquestra a inteligência artificial e gerencia as interações:

- **LLM Integration**: Integração com Google Gemini para processamento de linguagem natural
- **Chat Orchestrator**: Gerenciamento de sessões de conversa e contexto
- **MCP Client**: Cliente para comunicação com o servidor de ferramentas MCP
- **Session Management**: Controle de sessões de usuário e estado da conversa
- **File Processing**: Processamento de imagens e documentos médicos enviados

**Tecnologias**: FastAPI, Google Gemini AI, MCP Protocol, Python 3.13

**Localização**: `backend/agent/`

### 3. MCP Server (Database + Tools)

Servidor que implementa o Model Context Protocol fornecendo ferramentas especializadas:

- **Database Service**: Camada de abstração para operações no MongoDB
- **Medical Tools**: Conjunto de ferramentas especializadas para agendamento médico
- **Data Models**: Schemas estruturados para pacientes, médicos, consultas e exames
- **Business Logic**: Regras de negócio para validação e processamento de agendamentos

**Tecnologias**: Python 3.13, MongoDB, PyMongo, MCP Framework

**Localização**: `backend/server/`

## Funcionalidades Principais

### Agendamento Inteligente

O sistema oferece múltiplas formas de agendamento:

1. **Análise de Pedidos Médicos**: Upload de imagens de prescrições médicas com OCR automático
2. **Agendamento por Conversa**: Diálogo natural para agendar consultas e exames
3. **Gestão de Agendamentos**: Visualização, reagendamento e cancelamento de consultas existentes
4. **Busca por Especialidade**: Localização de médicos por especialidade ou nome

### Tipos de Serviços Suportados

- **Consultas Médicas**: Agendamento com médicos especialistas
- **Exames Simples**: Agendamento de exames que não requerem médico específico
- **Verificação de Disponibilidade**: Consulta em tempo real de horários disponíveis
- **Informações da Clínica**: Dados sobre especialidades, convênios e horários

### Sistema de IA Avançado

- **Processamento de Linguagem Natural**: Compreensão de solicitações em português
- **Análise de Imagens**: Extração de informações de documentos médicos
- **Fluxos Estruturados**: Procedimentos padronizados para diferentes tipos de agendamento
- **Validação Inteligente**: Verificação automática de dados e disponibilidade

## Estrutura do Projeto

```
ChatBot-Agenda-Médica/
├── frontend/                    # Interface web (Next.js)
│   ├── app/                     # Páginas e layouts da aplicação
│   ├── components/              # Componentes React reutilizáveis
│   ├── lib/                     # Utilitários e configurações
│   └── public/                  # Recursos estáticos
├── backend/
│   ├── agent/                   # Serviço principal de IA
│   │   ├── app/
│   │   │   ├── configs/         # Configurações e settings
│   │   │   ├── prompts/         # Instruções para o modelo de IA
│   │   │   ├── routers/         # Endpoints da API
│   │   │   ├── schemas/         # Schemas de validação
│   │   │   ├── services/        # Lógica de negócio
│   │   │   └── utils/           # Utilitários auxiliares
│   │   ├── requirements.txt
│   │   └── pyproject.toml
│   └── server/                  # Servidor MCP
│       ├── app/
│       │   ├── models.py        # Modelos de dados
│       │   └── services.py      # Serviços de banco de dados
│       ├── scripts/
│       │   └── db.py           # Scripts de inicialização do banco
│       ├── requirements.txt
│       └── server.py           # Servidor principal MCP
├── logs/                       # Logs dos serviços
├── setup.sh                   # Script de configuração automática
├── dev-start.sh               # Script para desenvolvimento
├── package.json               # Orquestração dos serviços
├── .gitignore                 # Arquivos ignorados pelo Git
└── LICENSE                    # Licença MIT
```

## Configuração e Instalação

### Pré-requisitos

- **Python**: Versão 3.8 ou superior
- **Node.js**: Versão 16 ou superior
- **MongoDB**: Instância local ou remota
- **Google Gemini API Key**: Para o serviço de IA

### Instalação Automática

Execute o script de configuração para setup completo:

**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows (PowerShell):**
```powershell
.\setup.sh
```

**Windows (CMD):**
```cmd
bash setup.sh
```

O script realizará automaticamente:

- Criação de ambientes virtuais Python isolados
- Instalação de todas as dependências
- Verificação de pré-requisitos
- Configuração de estrutura de logs

### Configuração Manual

#### 1. Backend Agent

**Linux/macOS:**
```bash
cd backend/agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```cmd
cd backend\agent
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. MCP Server

**Linux/macOS:**
```bash
cd backend/server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```cmd
cd backend\server
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Frontend

```bash
cd frontend
npm install
```

### Configuração de Ambiente

#### Arquivo .env

Crie o arquivo `backend/agent/.env` (compartilhado pelos dois serviços backend):

```env
GEMINI_API_KEY=your_gemini_api_key_here
DEFAULT_MODEL=gemini-1.5-flash
DEBUG=true
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
SESSION_SECRET_KEY=your_session_secret_here
CORS_ORIGINS=["http://localhost:3000"]
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=clinica_agenda
```

### Inicialização do Banco de Dados

Execute o script de inicialização para criar as coleções e dados de exemplo:

**Linux/macOS:**
```bash
cd backend/server
source .venv/bin/activate
python scripts/db.py
```

**Windows:**
```cmd
cd backend\server
.venv\Scripts\activate
python scripts\db.py
```

## Execução

### Desenvolvimento - Todos os Serviços

Para iniciar todos os serviços simultaneamente:

**Linux/macOS:**
```bash
npm run dev
```

ou diretamente:
```bash
./dev-start.sh
```

**Windows (PowerShell/CMD):**
```cmd
npm run dev
```

**Nota para Windows:** O script `dev-start.sh` requer um ambiente bash. Use apenas o comando `npm run dev` no Windows.

### Serviços Individuais

#### Frontend
```bash
npm run dev:frontend
```

#### Backend Agent
```bash
npm run dev:backend
```

#### MCP Server
```bash
npm run dev:mcp-server
```

### URLs de Acesso

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação da API**: http://localhost:8000/docs
- **Logs**: Arquivos em `logs/`

## Scripts Disponíveis

### Desenvolvimento
- `npm run dev`: Inicia todos os serviços em modo desenvolvimento
- `npm run dev:frontend`: Apenas o frontend
- `npm run dev:backend`: Apenas o backend agent
- `npm run dev:mcp-server`: Apenas o servidor MCP

### Utilitários
- `npm run setup`: Executa configuração automática
- `npm run status`: Verifica status dos serviços em execução
- `npm run clean`: Remove arquivos temporários e dependências
- `npm run logs:backend`: Visualiza logs do backend em tempo real
- `npm run logs:mcp-server`: Visualiza logs do servidor MCP

### Produção
- `npm run build`: Build de produção do frontend
- `npm run start`: Inicia todos os serviços em modo produção

## Tecnologias Principais

- **FastAPI**: Framework web moderno para APIs Python
- **Google Gemini SDK**: Modelo de linguagem para processamento de texto e imagens
- **MCP (Model Context Protocol)**: Protocolo para integração de ferramentas com IA
- **Next.js**: Framework React para aplicações web
- **TypeScript**: Superset tipado do JavaScript
- **Tailwind CSS**: Framework CSS utilitário
- **Framer Motion**: Biblioteca de animações React
- **MongoDB**: Banco de dados NoSQL para armazenamento
- **PyMongo**: Driver Python para MongoDB

## Ferramentas MCP Disponíveis

O servidor MCP expõe as seguintes ferramentas para o agente de IA:

### Consulta de Informações
- `listar_especialidades_com_medicos()`: Lista especialidades disponíveis
- `procurar_medicos(especialidade)`: Busca médicos por especialidade
- `verificar_disponibilidade_medico(medico_id, data)`: Verifica horários livres

### Agendamento
- `agendar_consulta_com_medico()`: Agenda consulta com especialista
- `agendar_exame_simples()`: Agenda exame sem médico específico

### Gestão de Agendamentos
- `ver_minhas_consultas(cpf)`: Lista agendamentos do paciente
- `reagendar_consulta(id, nova_data, nova_hora)`: Reagenda consulta existente
- `cancelar_consulta(id)`: Cancela agendamento

### Utilitários
- `obter_data_por_termo_relativo(termo)`: Converte termos como "amanhã" para data

## Monitoramento e Logs

### Sistema de Logs
- **Backend**: `logs/backend.log`
- **MCP Server**: `logs/mcp-server.log`
- **Frontend**: `logs/frontend.log`

### Monitoramento em Tempo Real

**Linux/macOS:**
```bash
# Logs do backend
tail -f logs/backend.log

# Logs do servidor MCP
tail -f logs/mcp-server.log

# Status dos serviços
npm run status
```

**Windows (PowerShell):**
```powershell
# Logs do backend
Get-Content logs/backend.log -Wait -Tail 50

# Logs do servidor MCP
Get-Content logs/mcp-server.log -Wait -Tail 50

# Status dos serviços
npm run status
```

**Windows (CMD):**
```cmd
rem Para monitoramento contínuo use PowerShell
rem Visualização única dos logs:
type logs\backend.log
type logs\mcp-server.log

rem Status dos serviços
npm run status
```

## Contribuição

### Estrutura de Desenvolvimento

1. **Fork** o repositório
2. **Clone** localmente
3. **Execute** setup:
   - Linux/macOS: `./setup.sh`
   - Windows: `npm run setup` (recomendado) ou execute o script via PowerShell/CMD com bash disponível
4. **Desenvolva** as funcionalidades
5. **Teste** com `npm run dev`
6. **Submeta** pull request

### Padrões de Código

- **Python**: Siga PEP 8 e use type hints
- **TypeScript**: Use ESLint e Prettier para formatação
- **Commits**: Use conventional commits para mensagens

### Testing

Execute os testes e linting:

```bash
# Linting
npm run lint
```

## Segurança

### Boas Práticas Implementadas

- **Isolamento de Ambientes**: Ambientes virtuais separados para cada serviço
- **Validação de Dados**: Schemas Pydantic para validação de entrada
- **Sanitização**: Limpeza de dados de entrada, especialmente CPF
- **Session Management**: Gerenciamento seguro de sessões de usuário
- **CORS**: Configuração adequada para requests cross-origin

### Variáveis Sensíveis

Mantenha sempre em arquivos `.env` (não versionados):
- API Keys (Gemini)
- Strings de conexão de banco de dados
- Chaves de sessão
- Configurações de produção

## Licença

Este projeto está licenciado sob a **MIT License**. Consulte o arquivo `LICENSE` para detalhes completos.

## Suporte

Para suporte técnico ou dúvidas sobre implementação:

1. **Issues**: Use o sistema de issues do GitHub
2. **Documentação**: Consulte os comentários no código
3. **Logs**: Verifique os arquivos de log para diagnóstico
4. **Configuração**: Execute `./setup.sh` para resolver problemas de ambiente
