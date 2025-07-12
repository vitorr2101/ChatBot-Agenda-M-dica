from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from enum import Enum

class StatusConsulta(str, Enum):
    """Enum para os status possíveis de uma consulta."""
    AGENDADA = "agendada"
    CANCELADA = "cancelada"
    CONCLUIDA = "concluida"

class Especialidade(BaseModel):
    """Modelo de dados para uma especialidade médica."""
    id: int = Field(alias="_id")
    nome: str

class Medico(BaseModel):
    """Modelo de dados para um médico."""
    id: int = Field(alias="_id")
    nome: str
    crm: str
    especialidade_id: int
    nome_especialidade: str

class Paciente(BaseModel):
    """Modelo de dados para um paciente."""
    id: int = Field(alias="_id")
    nome: str
    cpf: str

class AgendamentoDetalhado(BaseModel):
    """
    Modelo de dados completo para um agendamento, usado nos retornos das ferramentas.
    Contém informações enriquecidas para o usuário final.
    """
    id: int = Field(alias="_id")
    paciente_id: int
    data: str
    hora_inicio: str
    status: StatusConsulta
    observacoes: str
    medico_id: Optional[int] = None
    tipo_exame_id: Optional[int] = None
    nome_medico: str = "N/A (Apenas Exame)"
    descricao_exame: str = "Consulta de Rotina"

class ReagendamentoRequest(BaseModel):
    """Modelo para o corpo da requisição de um reagendamento."""
    nova_data_str: str
    nova_hora_str: str
    
class ListaEspecialidades(BaseModel):
    """Modelo para a resposta da ferramenta que lista especialidades."""
    especialidades_disponiveis: List[str]

class SlotsDisponiveis(BaseModel):
    """Modelo para a resposta da ferramenta de verificação de disponibilidade."""
    slots_livres: List[Dict[str, str]]