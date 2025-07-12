import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from pymongo import MongoClient
from typing import Optional, List

from fastapi import HTTPException
from mcp.server.fastmcp import FastMCP

from app.services import DatabaseService
from app.models import (
    Medico, AgendamentoDetalhado, ListaEspecialidades, 
    SlotsDisponiveis, ReagendamentoRequest
)

# --- Gerenciador de Ciclo de Vida (Lifespan) ---
class AppContext:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Gerencia a inicialização e o desligamento dos recursos do servidor."""
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME")
    
    mongo_client = MongoClient(mongo_uri)
    db = mongo_client[db_name]
    db_service_instance = DatabaseService(db)
    
    try:
        yield AppContext(db_service=db_service_instance)
    finally:
        mongo_client.close()

# --- Instância do Servidor FastMCP ---
mcp = FastMCP(
    title="Clínica Proativa - API de Ferramentas",
    description="API de ferramentas para agendamento de consultas e exames.",
    version="1.0.0",
    lifespan=app_lifespan
)

# --- Definição das Ferramentas com Documentação Completa ---

@mcp.tool()
def listar_especialidades_com_medicos() -> ListaEspecialidades:
    """
    Lista apenas as especialidades médicas que possuem pelo menos um médico cadastrado.
    É a forma mais útil de responder quando um usuário pergunta sobre as especialidades disponíveis.

    Returns:
        ListaEspecialidades: Um objeto contendo a lista de nomes de especialidades.
    """
    ctx = mcp.get_context()
    db_service: DatabaseService = ctx.request_context.lifespan_context.db_service
    return db_service.listar_especialidades_com_medicos()

@mcp.tool()
def procurar_medicos(especialidade: Optional[str] = None) -> List[Medico]:
    """
    Procura por médicos, com busca flexível por especialidade. Se nenhuma especialidade for 
    fornecida, lista todos os médicos disponíveis.

    Args:
        especialidade (Optional[str]): O nome da especialidade (ex: "Cardiologia") ou do especialista (ex: "cardiologista").

    Returns:
        List[Medico]: Uma lista de objetos Medico, que pode estar vazia se nenhum for encontrado.
    """
    ctx = mcp.get_context()
    db_service: DatabaseService = ctx.request_context.lifespan_context.db_service
    return db_service.procurar_medicos(especialidade)

@mcp.tool()
def verificar_disponibilidade_medico(medico_id: int, data_str: str) -> SlotsDisponiveis:
    """
    Retorna os horários livres de um médico para uma data específica.

    Args:
        medico_id (int): O ID numérico do médico, obtido previamente pela ferramenta 'procurar_medicos'.
        data_str (str): A data para a verificação, no formato 'YYYY-MM-DD'.

    Returns:
        SlotsDisponiveis: Um objeto contendo a lista de horários livres.
    """
    ctx = mcp.get_context()
    db_service: DatabaseService = ctx.request_context.lifespan_context.db_service
    try:
        return db_service.verificar_disponibilidade_medico(medico_id, data_str)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@mcp.tool()
def agendar_exame_simples(nome_paciente: str, cpf_paciente: str, data_str: str, hora_inicio_str: str, nome_exame: str) -> AgendamentoDetalhado:
    """
    [USAR PARA EXAMES SEM MÉDICO] Agenda um exame simples que não requer um especialista, como 'Exame de Sangue' ou 'Raio-X'.

    Args:
        nome_paciente (str): O nome completo do paciente.
        cpf_paciente (str): O CPF do paciente (obrigatório, pode estar formatado).
        data_str (str): A data exata do agendamento (ex: '2025-07-15').
        hora_inicio_str (str): A hora exata do agendamento (ex: '14:00').
        nome_exame (str): O nome do exame simples a ser realizado (ex: "Exame de Sangue").

    Returns:
        AgendamentoDetalhado: O objeto completo do agendamento realizado.
    """
    ctx = mcp.get_context()
    db_service: DatabaseService = ctx.request_context.lifespan_context.db_service
    try:
        return db_service.agendar_exame_simples(nome_paciente, cpf_paciente, data_str, hora_inicio_str, nome_exame)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@mcp.tool()
def agendar_consulta_com_medico(nome_paciente: str, cpf_paciente: str, data_str: str, hora_inicio_str: str, nome_medico: str, motivo_consulta: Optional[str] = "Consulta de rotina") -> AgendamentoDetalhado:
    """
    [USAR PARA CONSULTAS COM MÉDICO] Agenda uma consulta que requer um médico especialista.

    Args:
        nome_paciente (str): O nome completo do paciente.
        cpf_paciente (str): O CPF do paciente (obrigatório, pode estar formatado).
        data_str (str): A data exata do agendamento (ex: '2025-07-15').
        hora_inicio_str (str): A hora exata do agendamento (ex: '14:00').
        nome_medico (str): O nome do médico especialista para a consulta.
        motivo_consulta (Optional[str]): Opcional. O motivo da consulta ou exame associado.

    Returns:
        AgendamentoDetalhado: O objeto completo do agendamento realizado.
    """
    ctx = mcp.get_context()
    db_service: DatabaseService = ctx.request_context.lifespan_context.db_service
    try:
        return db_service.agendar_consulta_com_medico(nome_paciente, cpf_paciente, data_str, hora_inicio_str, nome_medico, motivo_consulta)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@mcp.tool()
def ver_minhas_consultas(cpf_paciente: str) -> List[AgendamentoDetalhado]:
    """
    [BUSCA DE CONSULTAS] Use quando um usuário cadastrado pedir para 'ver' ou 'encontrar' seus agendamentos.

    Args:
        cpf_paciente (str): O CPF do paciente para buscar as consultas.

    Returns:
        List[AgendamentoDetalhado]: Uma lista com os agendamentos futuros do paciente.
    """
    ctx = mcp.get_context()
    db_service: DatabaseService = ctx.request_context.lifespan_context.db_service
    try:
        return db_service.ver_minhas_consultas(cpf_paciente)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@mcp.tool()
def obter_data_por_termo_relativo(termo_data: str) -> str:
    """
    [FERRAMENTA DE AUXÍLIO] Converte um termo de data relativo (como 'hoje', 'amanhã' 
    ou 'próxima sexta-feira') para uma data específica no formato 'YYYY-MM-DD'.
    Use esta função para traduzir o pedido de data do usuário antes de usar outras ferramentas.

    Args:
        termo_data (str): A expressão de data relativa (ex: 'amanhã', 'próxima terça').

    Returns:
        str: A data correspondente no formato 'YYYY-MM-DD'.
    """
    ctx = mcp.get_context()
    db_service: DatabaseService = ctx.request_context.lifespan_context.db_service
    # A lógica real está segura dentro do nosso serviço
    return db_service.obter_data_por_termo_relativo(termo_data)

@mcp.tool()
def reagendar_consulta(consulta_id: int, request: ReagendamentoRequest) -> AgendamentoDetalhado:
    """
    [GERENCIAMENTO] Reagenda uma consulta existente para uma nova data e hora.
    Esta função deve ser usada após o usuário confirmar qual consulta deseja alterar.

    Args:
        consulta_id (int): O ID numérico da consulta a ser reagendada.
        request (ReagendamentoRequest): Um objeto contendo a nova data e hora desejada.

    Returns:
        AgendamentoDetalhado: Os detalhes completos da consulta após o reagendamento.
    """
    try:
        ctx = mcp.get_context()
        db_service: DatabaseService = ctx.request_context.lifespan_context.db_service
        return db_service.reagendar_consulta(
            consulta_id, request.nova_data_str, request.nova_hora_str
        )
    except ValueError as e:
        # Erros de lógica (ex: conflito de horário, consulta não encontrada)
        raise HTTPException(status_code=400, detail=str(e))

@mcp.tool()
def cancelar_consulta(consulta_id: int) -> AgendamentoDetalhado:
    """
    [GERENCIAMENTO] Cancela uma consulta existente.
    Use esta função após o usuário confirmar qual consulta deseja cancelar.

    Args:
        consulta_id (int): O ID numérico da consulta a ser cancelada.

    Returns:
        AgendamentoDetalhado: Os detalhes da consulta que foi marcada como 'cancelada'.
    """
    try:
        ctx = mcp.get_context()
        db_service: DatabaseService = ctx.request_context.lifespan_context.db_service
        return db_service.cancelar_consulta(consulta_id)
    except ValueError as e:
        # Erro se a consulta não for encontrada
        raise HTTPException(status_code=404, detail=str(e))
    
if __name__ == "__main__":
    # Para rodar em modo desenvolvedor use: mcp dev server.py
    # Para modo API Web: python server.py
    print("Iniciando servidor MCP em modo de API Web (HTTP)...")

    mcp.run(transport="streamable-http")