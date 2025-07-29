import os
from pymongo import MongoClient, ASCENDING
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timedelta, date, time
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv

from app.models import (
    Medico, AgendamentoDetalhado, ListaEspecialidades, 
    SlotsDisponiveis, Paciente, StatusConsulta
)

load_dotenv()

class DatabaseService:
    """
    Gerencia a conexão e expõe métodos como ferramentas para o agente de IA.
    """
    def __init__(self, db: Database):
        """
        Inicializa o serviço com uma conexão de banco de dados já estabelecida.

        Args:
            db (Database): Uma instância do objeto de banco de dados do Pymongo.
        """
        print("INFO:     Instância do DatabaseService criada com sucesso.")
        self.db = db

        self.medicos_collection = self.db.medico
        self.consultas_collection = self.db.consulta
        self.especialidades_collection = self.db.especialidade
        self.tipos_exame_collection = self.db.tipo_exame
        self.pacientes_collection = self.db.paciente

    # --- Métodos Privados / Helpers ---

    def _limpar_e_validar_cpf(self, cpf_bruto: str) -> str:
        """
        Limpa e valida uma string de CPF para conter 11 dígitos numéricos.

        Args:
            cpf_bruto (str): CPF no formato bruto, possivelmente com pontos e traços.

        Returns:
            str: CPF limpo contendo somente os 11 dígitos numéricos.

        Raises:
            ValueError: Se o CPF não for uma string ou não tiver 11 dígitos válidos.
        """
        if not isinstance(cpf_bruto, str):
            raise ValueError("CPF deve ser uma string.")
        cpf_limpo = cpf_bruto.replace(".", "").replace("-", "").strip()
        if not cpf_limpo.isdigit() or len(cpf_limpo) != 11:
            raise ValueError("Formato de CPF inválido. Deve conter 11 dígitos.")
        return cpf_limpo
    
    def _obter_ou_criar_paciente(self, nome_completo: str, cpf: str) -> Paciente:
        """
        Busca um paciente pelo CPF. Se não encontrar, cria um novo paciente.

        Args:
            nome_completo (str): Nome completo do paciente.
            cpf (str): CPF do paciente, pode estar em formato bruto.

        Returns:
            Paciente: Objeto Pydantic do paciente encontrado ou criado.
        """
        cpf_limpo = self._limpar_e_validar_cpf(cpf)
        paciente_doc = self.pacientes_collection.find_one({"cpf": cpf_limpo})

        if not paciente_doc:
            maior_id_doc = self.pacientes_collection.find_one(sort=[("_id", -1)])
            novo_id = (maior_id_doc["_id"] + 1) if maior_id_doc else 101
            novo_paciente_doc = {"_id": novo_id, "nome": nome_completo, "cpf": cpf_limpo}
            self.pacientes_collection.insert_one(novo_paciente_doc)
            paciente_doc = novo_paciente_doc
        
        return Paciente.model_validate(paciente_doc)

    def _enriquecer_e_validar_agendamento(self, doc_consulta: dict) -> AgendamentoDetalhado:
        """
        Enriquecer um documento de consulta com dados adicionais e validá-lo.

        Args:
            doc_consulta (dict): Documento de consulta obtido do banco.

        Returns:
            AgendamentoDetalhado | None: Modelo Pydantic da consulta enriquecida ou None se doc_consulta for None.
        """
        if not doc_consulta:
            return None
            
        medico_doc = self.medicos_collection.find_one({"_id": doc_consulta.get("medico_id")})
        exame_doc = self.tipos_exame_collection.find_one({"_id": doc_consulta.get("tipo_exame_id")})
        
        doc_consulta["nome_medico"] = medico_doc["nome"] if medico_doc else "N/A (Apenas Exame)"
        doc_consulta["descricao_exame"] = exame_doc["descricao"] if exame_doc else "Consulta de Rotina"
        
        return AgendamentoDetalhado.model_validate(doc_consulta)

    # --- Ferramentas Expostas ao Agente de IA ---

    def listar_especialidades_com_medicos(self) -> ListaEspecialidades:
        """
        Lista especialidades médicas que possuem pelo menos um médico cadastrado.

        Returns:
            ListaEspecialidades: Objeto contendo lista de nomes de especialidades.
        """
        ids_ativas = self.medicos_collection.distinct("especialidade_id")
        if not ids_ativas:
            return ListaEspecialidades(especialidades_disponiveis=[])
        
        cursor = self.especialidades_collection.find({"_id": {"$in": ids_ativas}}, {"nome": 1, "_id": 0})
        nomes = [esp["nome"] for esp in cursor]
        return ListaEspecialidades(especialidades_disponiveis=nomes)

    def procurar_medicos(self, especialidade: Optional[str] = None) -> List[Medico]:
        """
        Busca médicos, filtrando por especialidade opcional.

        Args:
            especialidade (Optional[str]): Nome ou parte da especialidade.

        Returns:
            List[Medico]: Lista de médicos encontrados, pode ser vazia.
        """
        query = {}
        if especialidade:
            termo_base = especialidade.lower()
            if termo_base.endswith("logista"):
                termo_base = termo_base[:-7]
            elif termo_base.endswith("logia"):
                termo_base = termo_base[:-5]
            
            esp_doc = self.especialidades_collection.find_one(
                {"nome": {"$regex": termo_base, "$options": "i"}}
            )
            if not esp_doc:
                return []
            query["especialidade_id"] = esp_doc["_id"]

        medicos_cursor = self.medicos_collection.find(query)
        medicos_encontrados = []
        for medico_data in medicos_cursor:
            esp_id = medico_data.get("especialidade_id")
            esp_info = self.especialidades_collection.find_one({"_id": esp_id})
            medico_data["nome_especialidade"] = esp_info["nome"] if esp_info else "N/A"
            medicos_encontrados.append(Medico.model_validate(medico_data))
            
        return medicos_encontrados

    def verificar_disponibilidade_medico(self, medico_id: int, data_str: str) -> SlotsDisponiveis:
        """
        Retorna os horários livres (slots de 30 minutos) para um médico em uma data.

        Args:
            medico_id (int): ID do médico.
            data_str (str): Data no formato 'YYYY-MM-DD'.

        Returns:
            SlotsDisponiveis: Objeto com lista de horários livres.
        
        Raises:
            ValueError: Se a data estiver em formato inválido.
        """
        try:
            data_consulta = datetime.strptime(data_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            raise ValueError("Formato da data é inválido. Use AAAA-MM-DD.")

        horario_inicio, horario_fim = time(8, 0), time(18, 0)
        duracao_slot = timedelta(minutes=30)
        
        consultas_agendadas = self.consultas_collection.find(
            {"medico_id": medico_id, "data": data_str, "status": StatusConsulta.AGENDADA.value}
        )
        
        horarios_ocupados = [
            (datetime.strptime(c["hora_inicio"], "%H:%M").time(), 
             (datetime.combine(data_consulta, datetime.strptime(c["hora_inicio"], "%H:%M").time()) + timedelta(minutes=c["duracao_minutos"])).time())
            for c in consultas_agendadas
        ]
        
        slots_livres = []
        slot_atual = datetime.combine(data_consulta, horario_inicio)
        while slot_atual.time() < horario_fim:
            inicio_slot = slot_atual.time()
            fim_slot = (slot_atual + duracao_slot).time()
            if not any(inicio_slot < fim and fim_slot > inicio for inicio, fim in horarios_ocupados):
                slots_livres.append({"hora_inicio": inicio_slot.strftime("%H:%M"), "hora_fim": fim_slot.strftime("%H:%M")})
            slot_atual += duracao_slot
            
        return SlotsDisponiveis(slots_livres=slots_livres)

    def obter_data_por_termo_relativo(self, termo_data: str) -> str:
        """
        Converte um termo de data relativo para data no formato 'YYYY-MM-DD'.

        Args:
            termo_data (str): Termo relativo como 'hoje', 'amanhã', 'próxima sexta'.

        Returns:
            str: Data correspondente no formato ISO 'YYYY-MM-DD'.
        """
        hoje = date.today()
        termo = termo_data.lower()

        if "hoje" in termo: return hoje.isoformat()
        if "amanha" in termo or "amanhã" in termo: return (hoje + timedelta(days=1)).isoformat()

        dias_semana = {"segunda": 0, "terca": 1, "terça": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sabado": 5, "sábado": 5, "domingo": 6}
        for nome_dia, num_dia in dias_semana.items():
            if nome_dia in termo:
                dias_a_frente = (num_dia - hoje.weekday() + 7) % 7
                if dias_a_frente == 0: dias_a_frente = 7
                return (hoje + timedelta(days=dias_a_frente)).isoformat()
        
        return hoje.isoformat()

    def agendar_exame_simples(self, nome_paciente: str, cpf_paciente: str, data_str: str, hora_inicio_str: str, nome_exame: str) -> AgendamentoDetalhado:
        """
        Agenda um exame simples (sem médico), ex: exame de sangue, raio-x.

        Args:
            nome_paciente (str): Nome completo do paciente.
            cpf_paciente (str): CPF do paciente.
            data_str (str): Data do exame no formato 'YYYY-MM-DD'.
            hora_inicio_str (str): Horário de início no formato 'HH:MM'.
            nome_exame (str): Nome do exame.

        Returns:
            AgendamentoDetalhado: Objeto detalhado do agendamento criado.

        Raises:
            ValueError: Se o exame não for considerado simples ou não existir.
        """
        EXAMES_SEM_ESPECIALISTA = ["exame de sangue", "raio-x"]
        if nome_exame.lower() not in EXAMES_SEM_ESPECIALISTA:
            raise ValueError(f"'{nome_exame}' não é um exame simples e requer um médico.")

        paciente = self._obter_ou_criar_paciente(nome_paciente, cpf_paciente)
        exame_doc = self.tipos_exame_collection.find_one({"descricao": {"$regex": f"^{nome_exame}$", "$options": "i"}})
        if not exame_doc:
            raise ValueError(f"O tipo de exame '{nome_exame}' não foi encontrado no sistema.")
        
        return self.agendar_consulta(
            paciente_id=paciente.id, data_str=data_str, hora_inicio_str=hora_inicio_str,
            tipo_exame_id=exame_doc["_id"], observacoes=f"Exame: {nome_exame}"
        )

    def agendar_consulta_com_medico(self, nome_paciente: str, cpf_paciente: str, data_str: str, hora_inicio_str: str, nome_medico: str, motivo_consulta: Optional[str] = "Consulta de rotina") -> AgendamentoDetalhado:
        """
        Agenda uma consulta médica com especialista.

        Args:
            nome_paciente (str): Nome completo do paciente.
            cpf_paciente (str): CPF do paciente.
            data_str (str): Data da consulta no formato 'YYYY-MM-DD'.
            hora_inicio_str (str): Horário de início no formato 'HH:MM'.
            nome_medico (str): Nome do médico especialista.
            motivo_consulta (Optional[str]): Motivo da consulta (ex: "Consulta de rotina").

        Returns:
            AgendamentoDetalhado: Objeto detalhado do agendamento criado.

        Raises:
            ValueError: Se o médico não for encontrado no sistema.
        """
        medico_doc = self.medicos_collection.find_one({"nome": {"$regex": nome_medico, "$options": "i"}})
        if not medico_doc:
            raise ValueError(f"O médico '{nome_medico}' não foi encontrado.")
        
        paciente = self._obter_ou_criar_paciente(nome_paciente, cpf_paciente)
        tipo_exame_id = None
        if motivo_consulta:
            exame_doc = self.tipos_exame_collection.find_one({"descricao": {"$regex": motivo_consulta, "$options": "i"}})
            if exame_doc: tipo_exame_id = exame_doc["_id"]
        
        return self.agendar_consulta(
            paciente_id=paciente.id, data_str=data_str, hora_inicio_str=hora_inicio_str,
            medico_id=medico_doc["_id"], tipo_exame_id=tipo_exame_id, observacoes=motivo_consulta
        )

    def agendar_consulta(self, paciente_id: int, data_str: str, hora_inicio_str: str, medico_id: Optional[int] = None, tipo_exame_id: Optional[int] = None, observacoes: Optional[str] = "") -> AgendamentoDetalhado:
        """
        Função interna que insere a consulta/exame no banco, verificando conflitos.

        Args:
            paciente_id (int): ID do paciente.
            data_str (str): Data da consulta/exame no formato 'YYYY-MM-DD'.
            hora_inicio_str (str): Horário de início no formato 'HH:MM'.
            medico_id (Optional[int]): ID do médico (se consulta).
            tipo_exame_id (Optional[int]): ID do exame (se exame).
            observacoes (Optional[str]): Observações adicionais.

        Returns:
            AgendamentoDetalhado: Objeto detalhado do agendamento criado.

        Raises:
            ValueError: Se houver conflito de horário.
        """
        maior_id_doc = self.consultas_collection.find_one(sort=[("_id", -1)])
        novo_id = (maior_id_doc["_id"] + 1) if maior_id_doc else 123

        nova_consulta = {
            "_id": novo_id, "paciente_id": paciente_id, "data": data_str, "hora_inicio": hora_inicio_str,
            "duracao_minutos": 30, "status": StatusConsulta.AGENDADA.value, "observacoes": observacoes,
            "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()
        }
        if medico_id: nova_consulta["medico_id"] = medico_id
        if tipo_exame_id: nova_consulta["tipo_exame_id"] = tipo_exame_id
        
        try:
            self.consultas_collection.insert_one(nova_consulta)
        except DuplicateKeyError:
            raise ValueError("Conflito de horário. Este médico já possui um agendamento neste exato horário.")

        consulta_criada = self.consultas_collection.find_one({"_id": novo_id})
        return self._enriquecer_e_validar_agendamento(consulta_criada)
    
    def ver_minhas_consultas(self, cpf_paciente: str) -> List[AgendamentoDetalhado]:
        """
        Busca consultas agendadas para um paciente pelo CPF.

        Args:
            cpf_paciente (str): CPF do paciente.

        Returns:
            List[AgendamentoDetalhado]: Lista de agendamentos futuros confirmados.

        Raises:
            ValueError: Se paciente não for encontrado.
        """
        paciente = self._obter_ou_criar_paciente("Busca", cpf_paciente)
        if isinstance(paciente, dict) and "erro" in paciente:
            raise ValueError(paciente["erro"])

        hoje_str = date.today().isoformat()
        consultas_cursor = self.consultas_collection.find({
            "paciente_id": paciente.id, "status": StatusConsulta.AGENDADA.value, "data": {"$gte": hoje_str}
        }).sort("data", ASCENDING)
        
        return [self._enriquecer_e_validar_agendamento(c) for c in consultas_cursor]
    
    def reagendar_consulta(self, consulta_id: int, nova_data_str: str, nova_hora_str: str) -> AgendamentoDetalhado:
        """
        Reagenda uma consulta existente, verificando conflitos.

        Args:
            consulta_id (int): ID da consulta a ser reagendada.
            nova_data_str (str): Nova data no formato 'YYYY-MM-DD'.
            nova_hora_str (str): Novo horário no formato 'HH:MM'.

        Returns:
            AgendamentoDetalhado: Objeto detalhado do agendamento atualizado.

        Raises:
            ValueError: Se consulta não existir ou houver conflito de horário.
        """
        consulta_original = self.consultas_collection.find_one({"_id": consulta_id})
        if not consulta_original:
            raise ValueError(f"Consulta com ID {consulta_id} não encontrada.")
            
        medico_id = consulta_original.get("medico_id")
        if medico_id:
            conflito = self.consultas_collection.find_one({
                "medico_id": medico_id, "data": nova_data_str, "hora_inicio": nova_hora_str, "_id": {"$ne": consulta_id}
            })
            if conflito:
                raise ValueError(f"Conflito de horário. O médico já tem uma consulta para {nova_data_str} às {nova_hora_str}.")

        resultado = self.consultas_collection.update_one(
            {"_id": consulta_id},
            {"$set": {"data": nova_data_str, "hora_inicio": nova_hora_str, "updated_at": datetime.utcnow()}}
        )

        if resultado.modified_count == 0:
            raise ValueError("Não foi possível reagendar. A data e hora podem já ser as mesmas.")

        consulta_atualizada = self.consultas_collection.find_one({"_id": consulta_id})
        return self._enriquecer_e_validar_agendamento(consulta_atualizada)

    def cancelar_consulta(self, consulta_id: int) -> AgendamentoDetalhado:
        """
        Cancela uma consulta existente.

        Args:
            consulta_id (int):
        Returns:
            AgendamentoDetalhado: Objeto detalhado da consulta cancelada.

        Raises:
            ValueError: Se consulta não existir ou já estiver cancelada.
        """
        resultado = self.consultas_collection.update_one(
            {"_id": consulta_id},
            {"$set": {"status": StatusConsulta.CANCELADA.value, "updated_at": datetime.utcnow()}}
        )
        if resultado.modified_count == 0:
            raise ValueError(f"Consulta com ID {consulta_id} não encontrada ou já estava cancelada.")

        consulta_cancelada = self.consultas_collection.find_one({"_id": consulta_id})
        return self._enriquecer_e_validar_agendamento(consulta_cancelada)
