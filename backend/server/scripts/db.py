from pymongo import MongoClient, ASCENDING
from datetime import datetime
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv(".env")
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME")

def criar_conexao():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db

def criar_collections(db):
    # Criação de índices para as coleções
    db.especialidade.create_index("nome", unique=True)
    db.medico.create_index("crm", unique=True)
    db.medico.create_index("especialidade_id")
    db.tipo_exame.create_index("descricao", unique=True)
    db.consulta.create_index([("medico_id", ASCENDING), ("data", ASCENDING)])
    db.consulta.create_index("status")
    db.paciente.create_index("cpf", unique=True)  # <- Índice único para paciente
    print("Índices criados com sucesso.")

def inserir_exemplos(db):
    # Especialidades
    especialidades = [{"_id": 1, "nome": "Cardiologia"}, {"_id": 2, "nome": "Ortopedia"}]
    try:
        db.especialidade.insert_many(especialidades, ordered=False)
    except Exception:
        pass

    # Médicos
    medicos = [
        {
            "_id": 42,
            "nome": "Dr. João Silva",
            "crm": "12345",
            "especialidade_id": 1,
            "email": "joao@clinica.com",
            "telefone": "555-1234",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 58,
            "nome": "Dra. Maria Souza",
            "crm": "67890",
            "especialidade_id": 2,
            "email": "maria@clinica.com",
            "telefone": "555-5678",
            "senha_hash": "hashdummy"
        }
    ]
    try:
        db.medico.insert_many(medicos, ordered=False)
    except Exception:
        pass

    # Tipos de exame
    tipos_exame = [{"_id": 1, "descricao": "Exame de Sangue"}, {"_id": 2, "descricao": "Raio-X"}]
    try:
        db.tipo_exame.insert_many(tipos_exame, ordered=False)
    except Exception:
        pass

    # Pacientes
    pacientes = [
        {
            "_id": 101,
            "nome": "Carlos Silva",
            "cpf": "11122233344",
            "email": "carlos@email.com",
            "telefone": "99999-9999"
        },
        {
            "_id": 102,
            "nome": "Ana Pereira",
            "cpf": "55566677788",
            "email": "ana@email.com",
            "telefone": "88888-7777"
        }
    ]
    try:
        db.paciente.insert_many(pacientes, ordered=False)
    except Exception:
        pass

    # Consulta
    consulta = {
        "_id": 123,
        "medico_id": 42,
        "paciente_id": 101,  # Agora com referência ao paciente
        "tipo_exame_id": 1,
        "data": "2025-06-10",
        "hora_inicio": "14:00",
        "duracao_minutos": 30,
        "status": "agendada",
        "observacoes": "Primeira consulta",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    try:
        db.consulta.insert_one(consulta)
    except Exception:
        pass

    print("Documentos de exemplo inseridos (ou já existiam).")

def main():
    if not MONGO_URI or not DB_NAME:
        print("Erro: variáveis de ambiente MONGODB_URI e MONGODB_DB_NAME não definidas.")
        return
    db = criar_conexao()
    criar_collections(db)
    inserir_exemplos(db)

if __name__ == "__main__":
    main()
