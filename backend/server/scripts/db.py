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
    especialidades = [
        {"_id": 1, "nome": "Cardiologia"},
        {"_id": 2, "nome": "Ortopedia"},
        {"_id": 3, "nome": "Dermatologia"},
        {"_id": 4, "nome": "Ginecologia"},
        {"_id": 5, "nome": "Neurologia"},
        {"_id": 6, "nome": "Pediatria"},
        {"_id": 7, "nome": "Psiquiatria"},
        {"_id": 8, "nome": "Oftalmologia"},
        {"_id": 9, "nome": "Otorrinolaringologia"},
        {"_id": 10, "nome": "Urologia"},
        {"_id": 11, "nome": "Endocrinologia"},
        {"_id": 12, "nome": "Gastroenterologia"},
        {"_id": 13, "nome": "Pneumologia"},
        {"_id": 14, "nome": "Reumatologia"},
        {"_id": 15, "nome": "Oncologia"},
        {"_id": 16, "nome": "Anestesiologia"},
        {"_id": 17, "nome": "Radiologia"},
        {"_id": 18, "nome": "Medicina do Trabalho"},
        {"_id": 19, "nome": "Medicina de Família"},
        {"_id": 20, "nome": "Cirurgia Geral"},
        {"_id": 21, "nome": "Cirurgia Plástica"},
        {"_id": 22, "nome": "Cirurgia Vascular"},
        {"_id": 23, "nome": "Proctologia"},
        {"_id": 24, "nome": "Nefrologia"},
        {"_id": 25, "nome": "Hematologia"},
        {"_id": 26, "nome": "Infectologia"},
        {"_id": 27, "nome": "Geriatria"},
        {"_id": 28, "nome": "Patologia"},
        {"_id": 29, "nome": "Medicina Intensiva"},
        {"_id": 30, "nome": "Nutrologia"},
        {"_id": 31, "nome": "Acupuntura"},
        {"_id": 32, "nome": "Homeopatia"},
        {"_id": 33, "nome": "Medicina Esportiva"},
        {"_id": 34, "nome": "Genética Médica"},
        {"_id": 35, "nome": "Cirurgia Torácica"},
        {"_id": 36, "nome": "Neurocirurgia"},
        {"_id": 37, "nome": "Cirurgia Pediátrica"},
        {"_id": 38, "nome": "Mastologia"},
        {"_id": 39, "nome": "Medicina Legal"},
        {"_id": 40, "nome": "Alergia e Imunologia"},
        {"_id": 41, "nome": "Clínica Médica"},
        {"_id": 42, "nome": "Medicina Preventiva"},
        {"_id": 43, "nome": "Medicina Física e Reabilitação"}
    ]
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
        },
        {
            "_id": 59,
            "nome": "Dr. Carlos Mendes",
            "crm": "11111",
            "especialidade_id": 3,
            "email": "carlos@clinica.com",
            "telefone": "555-1111",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 60,
            "nome": "Dra. Ana Paula",
            "crm": "22222",
            "especialidade_id": 4,
            "email": "ana@clinica.com",
            "telefone": "555-2222",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 61,
            "nome": "Dr. Roberto Lima",
            "crm": "33333",
            "especialidade_id": 5,
            "email": "roberto@clinica.com",
            "telefone": "555-3333",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 62,
            "nome": "Dra. Julia Santos",
            "crm": "44444",
            "especialidade_id": 6,
            "email": "julia@clinica.com",
            "telefone": "555-4444",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 63,
            "nome": "Dr. Fernando Costa",
            "crm": "55555",
            "especialidade_id": 8,
            "email": "fernando@clinica.com",
            "telefone": "555-5555",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 64,
            "nome": "Dra. Patricia Alves",
            "crm": "66666",
            "especialidade_id": 11,
            "email": "patricia@clinica.com",
            "telefone": "555-6666",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 65,
            "nome": "Dr. Marcos Pereira",
            "crm": "77777",
            "especialidade_id": 7,
            "email": "marcos@clinica.com",
            "telefone": "555-7777",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 66,
            "nome": "Dra. Beatriz Cunha",
            "crm": "88888",
            "especialidade_id": 9,
            "email": "beatriz@clinica.com",
            "telefone": "555-8888",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 67,
            "nome": "Dr. Eduardo Rocha",
            "crm": "99999",
            "especialidade_id": 10,
            "email": "eduardo@clinica.com",
            "telefone": "555-9999",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 68,
            "nome": "Dra. Fernanda Martins",
            "crm": "10101",
            "especialidade_id": 12,
            "email": "fernanda@clinica.com",
            "telefone": "555-0101",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 69,
            "nome": "Dr. Ricardo Barbosa",
            "crm": "20202",
            "especialidade_id": 13,
            "email": "ricardo@clinica.com",
            "telefone": "555-0202",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 70,
            "nome": "Dra. Camila Nascimento",
            "crm": "30303",
            "especialidade_id": 14,
            "email": "camila@clinica.com",
            "telefone": "555-0303",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 71,
            "nome": "Dr. Gustavo Melo",
            "crm": "40404",
            "especialidade_id": 15,
            "email": "gustavo@clinica.com",
            "telefone": "555-0404",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 72,
            "nome": "Dra. Larissa Teixeira",
            "crm": "50505",
            "especialidade_id": 16,
            "email": "larissa@clinica.com",
            "telefone": "555-0505",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 73,
            "nome": "Dr. André Gomes",
            "crm": "60606",
            "especialidade_id": 17,
            "email": "andre@clinica.com",
            "telefone": "555-0606",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 74,
            "nome": "Dra. Isabela Cardoso",
            "crm": "70707",
            "especialidade_id": 19,
            "email": "isabela@clinica.com",
            "telefone": "555-0707",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 75,
            "nome": "Dr. Felipe Araújo",
            "crm": "80808",
            "especialidade_id": 20,
            "email": "felipe@clinica.com",
            "telefone": "555-0808",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 76,
            "nome": "Dra. Vanessa Reis",
            "crm": "90909",
            "especialidade_id": 21,
            "email": "vanessa@clinica.com",
            "telefone": "555-0909",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 77,
            "nome": "Dr. Bruno Carvalho",
            "crm": "12121",
            "especialidade_id": 22,
            "email": "bruno@clinica.com",
            "telefone": "555-1212",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 78,
            "nome": "Dra. Renata Ferreira",
            "crm": "13131",
            "especialidade_id": 24,
            "email": "renata@clinica.com",
            "telefone": "555-1313",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 79,
            "nome": "Dr. Thiago Moreira",
            "crm": "14141",
            "especialidade_id": 25,
            "email": "thiago@clinica.com",
            "telefone": "555-1414",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 80,
            "nome": "Dra. Priscila Viana",
            "crm": "15151",
            "especialidade_id": 27,
            "email": "priscila@clinica.com",
            "telefone": "555-1515",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 81,
            "nome": "Dr. Rodrigo Santana",
            "crm": "16161",
            "especialidade_id": 36,
            "email": "rodrigo@clinica.com",
            "telefone": "555-1616",
            "senha_hash": "hashdummy"
        },
        {
            "_id": 82,
            "nome": "Dra. Carolina Dias",
            "crm": "17171",
            "especialidade_id": 38,
            "email": "carolina@clinica.com",
            "telefone": "555-1717",
            "senha_hash": "hashdummy"
        }
    ]
    try:
        db.medico.insert_many(medicos, ordered=False)
    except Exception:
        pass

    # Tipos de exame
    tipos_exame = [
        {"_id": 1, "descricao": "Exame de Sangue"},
        {"_id": 2, "descricao": "Raio-X"},
        {"_id": 3, "descricao": "Tomografia Computadorizada"},
        {"_id": 4, "descricao": "Ressonância Magnética"},
        {"_id": 5, "descricao": "Ultrassonografia"},
        {"_id": 6, "descricao": "Eletrocardiograma"},
        {"_id": 7, "descricao": "Ecocardiograma"},
        {"_id": 8, "descricao": "Endoscopia"},
        {"_id": 9, "descricao": "Colonoscopia"},
        {"_id": 10, "descricao": "Mamografia"},
        {"_id": 11, "descricao": "Papanicolau"},
        {"_id": 12, "descricao": "Biopsia"},
        {"_id": 13, "descricao": "Eletroencefalograma"},
        {"_id": 14, "descricao": "Teste Ergométrico"},
        {"_id": 15, "descricao": "Densitometria Óssea"},
        {"_id": 16, "descricao": "Audiometria"},
        {"_id": 17, "descricao": "Campimetria"},
        {"_id": 18, "descricao": "Espirometria"},
        {"_id": 19, "descricao": "Holter 24h"},
        {"_id": 20, "descricao": "MAPA - Monitorização Ambulatorial da Pressão Arterial"},
        {"_id": 21, "descricao": "Exame de Urina"},
        {"_id": 22, "descricao": "Exame de Fezes"},
        {"_id": 23, "descricao": "Cultura de Urina"},
        {"_id": 24, "descricao": "Hemograma Completo"},
        {"_id": 25, "descricao": "Glicemia"},
        {"_id": 26, "descricao": "Colesterol Total e Frações"},
        {"_id": 27, "descricao": "Triglicerídeos"},
        {"_id": 28, "descricao": "Creatinina"},
        {"_id": 29, "descricao": "Ureia"},
        {"_id": 30, "descricao": "TGO/TGP (Transaminases)"},
        {"_id": 31, "descricao": "TSH - Hormônio da Tireoide"},
        {"_id": 32, "descricao": "T3 e T4 Livre"},
        {"_id": 33, "descricao": "PSA - Antígeno Prostático"},
        {"_id": 34, "descricao": "Beta HCG"},
        {"_id": 35, "descricao": "Vitamina D"},
        {"_id": 36, "descricao": "Vitamina B12"},
        {"_id": 37, "descricao": "Ácido Fólico"},
        {"_id": 38, "descricao": "Ferritina"},
        {"_id": 39, "descricao": "PCR - Proteína C Reativa"},
        {"_id": 40, "descricao": "VHS - Velocidade de Hemossedimentação"},
        {"_id": 41, "descricao": "Eletromielografia"},
        {"_id": 42, "descricao": "Polissonografia"},
        {"_id": 43, "descricao": "Cintilografia"},
        {"_id": 44, "descricao": "Angiotomografia"},
        {"_id": 45, "descricao": "Angioressonância"},
        {"_id": 46, "descricao": "Ultrassom Doppler"},
        {"_id": 47, "descricao": "Ecodopplercardiograma"},
        {"_id": 48, "descricao": "Cateterismo Cardíaco"},
        {"_id": 49, "descricao": "Artroscopia"},
        {"_id": 50, "descricao": "Laparoscopia"},
        {"_id": 51, "descricao": "Histeroscopia"},
        {"_id": 52, "descricao": "Cistoscopia"},
        {"_id": 53, "descricao": "Broncoscopia"},
        {"_id": 54, "descricao": "Retossigmoidoscopia"},
        {"_id": 55, "descricao": "Mielograma"},
        {"_id": 56, "descricao": "Punção Lombar"},
        {"_id": 57, "descricao": "Teste de Esforço"},
        {"_id": 58, "descricao": "MIBG Cintilografia"},
        {"_id": 59, "descricao": "PET-CT"},
        {"_id": 60, "descricao": "Elastografia Hepática"}
    ]
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
        },
        {
            "_id": 103,
            "nome": "João Santos",
            "cpf": "12345678901",
            "email": "joao.santos@email.com",
            "telefone": "11111-2222"
        },
        {
            "_id": 104,
            "nome": "Maria Oliveira",
            "cpf": "98765432109",
            "email": "maria.oliveira@email.com",
            "telefone": "33333-4444"
        },
        {
            "_id": 105,
            "nome": "Pedro Costa",
            "cpf": "45678912345",
            "email": "pedro.costa@email.com",
            "telefone": "55555-6666"
        },
        {
            "_id": 106,
            "nome": "Lucia Fernandes",
            "cpf": "78912345678",
            "email": "lucia.fernandes@email.com",
            "telefone": "77777-8888"
        },
        {
            "_id": 107,
            "nome": "Roberto Almeida",
            "cpf": "32165498712",
            "email": "roberto.almeida@email.com",
            "telefone": "99999-0000"
        },
        {
            "_id": 108,
            "nome": "Sandra Lima",
            "cpf": "65498732165",
            "email": "sandra.lima@email.com",
            "telefone": "11111-3333"
        },
        {
            "_id": 109,
            "nome": "Ricardo Moura",
            "cpf": "14725836901",
            "email": "ricardo.moura@email.com",
            "telefone": "22222-4444"
        },
        {
            "_id": 110,
            "nome": "Fernanda Ramos",
            "cpf": "36925814702",
            "email": "fernanda.ramos@email.com",
            "telefone": "66666-5555"
        },
        {
            "_id": 111,
            "nome": "Gustavo Nunes",
            "cpf": "75315948620",
            "email": "gustavo.nunes@email.com",
            "telefone": "44444-7777"
        },
        {
            "_id": 112,
            "nome": "Juliana Macedo",
            "cpf": "95135748260",
            "email": "juliana.macedo@email.com",
            "telefone": "88888-1111"
        },
        {
            "_id": 113,
            "nome": "Bruno Carvalho",
            "cpf": "15935748260",
            "email": "bruno.carvalho@email.com",
            "telefone": "33333-9999"
        },
        {
            "_id": 114,
            "nome": "Camila Torres",
            "cpf": "75395148620",
            "email": "camila.torres@email.com",
            "telefone": "77777-2222"
        },
        {
            "_id": 115,
            "nome": "Diego Mendes",
            "cpf": "35715948260",
            "email": "diego.mendes@email.com",
            "telefone": "55555-8888"
        },
        {
            "_id": 116,
            "nome": "Isabela Rocha",
            "cpf": "85296374100",
            "email": "isabela.rocha@email.com",
            "telefone": "99999-3333"
        },
        {
            "_id": 117,
            "nome": "Leonardo Pinto",
            "cpf": "75395142860",
            "email": "leonardo.pinto@email.com",
            "telefone": "11111-6666"
        },
        {
            "_id": 118,
            "nome": "Mariana Souza",
            "cpf": "95175348620",
            "email": "mariana.souza@email.com",
            "telefone": "44444-5555"
        },
        {
            "_id": 119,
            "nome": "Thiago Barbosa",
            "cpf": "35795148260",
            "email": "thiago.barbosa@email.com",
            "telefone": "66666-7777"
        },
        {
            "_id": 120,
            "nome": "Vanessa Castro",
            "cpf": "15975348260",
            "email": "vanessa.castro@email.com",
            "telefone": "22222-8888"
        },
        {
            "_id": 121,
            "nome": "André Gomes",
            "cpf": "85395174620",
            "email": "andre.gomes@email.com",
            "telefone": "77777-1111"
        },
        {
            "_id": 122,
            "nome": "Beatriz Silva",
            "cpf": "95175364820",
            "email": "beatriz.silva@email.com",
            "telefone": "33333-2222"
        },
        {
            "_id": 123,
            "nome": "Felipe Santos",
            "cpf": "75315942860",
            "email": "felipe.santos@email.com",
            "telefone": "88888-4444"
        },
        {
            "_id": 124,
            "nome": "Larissa Costa",
            "cpf": "35715948620",
            "email": "larissa.costa@email.com",
            "telefone": "55555-9999"
        },
        {
            "_id": 125,
            "nome": "Rodrigo Lima",
            "cpf": "95375148620",
            "email": "rodrigo.lima@email.com",
            "telefone": "11111-7777"
        }
    ]
    try:
        db.paciente.insert_many(pacientes, ordered=False)
    except Exception:
        pass

    # Consultas de exemplo
    consultas = [
        {
            "_id": 123,
            "medico_id": 42,  # Dr. João Silva - Cardiologia
            "paciente_id": 101,  # Carlos Silva
            "tipo_exame_id": 1,  # Exame de Sangue
            "data": "2025-08-15",
            "hora_inicio": "14:00",
            "duracao_minutos": 30,
            "status": "agendada",
            "observacoes": "Primeira consulta - Check-up cardiovascular",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": 124,
            "medico_id": 58,  # Dra. Maria Souza - Ortopedia
            "paciente_id": 102,  # Ana Pereira
            "tipo_exame_id": 2,  # Raio-X
            "data": "2025-08-16",
            "hora_inicio": "09:30",
            "duracao_minutos": 45,
            "status": "agendada",
            "observacoes": "Dor no joelho direito",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": 125,
            "medico_id": 59,  # Dr. Carlos Mendes - Dermatologia
            "paciente_id": 103,  # João Santos
            "tipo_exame_id": 12,  # Biopsia
            "data": "2025-08-17",
            "hora_inicio": "11:00",
            "duracao_minutos": 60,
            "status": "realizada",
            "observacoes": "Exame de lesão na pele",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": 126,
            "medico_id": 60,  # Dra. Ana Paula - Ginecologia
            "paciente_id": 104,  # Maria Oliveira
            "tipo_exame_id": 11,  # Papanicolau
            "data": "2025-08-18",
            "hora_inicio": "15:30",
            "duracao_minutos": 30,
            "status": "agendada",
            "observacoes": "Exame preventivo anual",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": 127,
            "medico_id": 61,  # Dr. Roberto Lima - Neurologia
            "paciente_id": 105,  # Pedro Costa
            "tipo_exame_id": 13,  # Eletroencefalograma
            "data": "2025-08-19",
            "hora_inicio": "08:00",
            "duracao_minutos": 90,
            "status": "agendada",
            "observacoes": "Investigação de episódios convulsivos",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": 128,
            "medico_id": 62,  # Dra. Julia Santos - Pediatria
            "paciente_id": 106,  # Lucia Fernandes
            "tipo_exame_id": 24,  # Hemograma Completo
            "data": "2025-08-20",
            "hora_inicio": "10:15",
            "duracao_minutos": 30,
            "status": "realizada",
            "observacoes": "Consulta de rotina pediátrica",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": 129,
            "medico_id": 63,  # Dr. Fernando Costa - Oftalmologia
            "paciente_id": 107,  # Roberto Almeida
            "tipo_exame_id": 17,  # Campimetria
            "data": "2025-08-21",
            "hora_inicio": "13:45",
            "duracao_minutos": 45,
            "status": "cancelada",
            "observacoes": "Paciente solicitou cancelamento",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": 130,
            "medico_id": 64,  # Dra. Patricia Alves - Endocrinologia
            "paciente_id": 108,  # Sandra Lima
            "tipo_exame_id": 31,  # TSH
            "data": "2025-08-22",
            "hora_inicio": "16:00",
            "duracao_minutos": 30,
            "status": "agendada",
            "observacoes": "Acompanhamento de hipotireoidismo",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": 131,
            "medico_id": 65,  # Dr. Marcos Pereira - Psiquiatria
            "paciente_id": 109,  # Ricardo Moura
            "tipo_exame_id": 1,  # Exame de Sangue
            "data": "2025-08-23",
            "hora_inicio": "14:30",
            "duracao_minutos": 60,
            "status": "agendada",
            "observacoes": "Acompanhamento psiquiátrico - ajuste medicação",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": 132,
            "medico_id": 42,  # Dr. João Silva - Cardiologia
            "paciente_id": 110,  # Fernanda Ramos
            "tipo_exame_id": 6,  # Eletrocardiograma
            "data": "2025-08-24",
            "hora_inicio": "09:00",
            "duracao_minutos": 30,
            "status": "realizada",
            "observacoes": "Palpitações frequentes",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": 133,
            "medico_id": 66,  # Dra. Beatriz Cunha - Otorrinolaringologia
            "paciente_id": 111,  # Gustavo Nunes
            "tipo_exame_id": 16,  # Audiometria
            "data": "2025-08-25",
            "hora_inicio": "11:30",
            "duracao_minutos": 45,
            "status": "agendada",
            "observacoes": "Perda auditiva progressiva",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": 134,
            "medico_id": 67,  # Dr. Eduardo Rocha - Urologia
            "paciente_id": 112,  # Juliana Macedo
            "tipo_exame_id": 33,  # PSA
            "data": "2025-08-26",
            "hora_inicio": "15:15",
            "duracao_minutos": 30,
            "status": "agendada",
            "observacoes": "Exame preventivo",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": 135,
            "medico_id": 68,  # Dra. Fernanda Martins - Gastroenterologia
            "paciente_id": 113,  # Bruno Carvalho
            "tipo_exame_id": 8,  # Endoscopia
            "data": "2025-08-27",
            "hora_inicio": "07:30",
            "duracao_minutos": 60,
            "status": "agendada",
            "observacoes": "Investigação de dor abdominal",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": 136,
            "medico_id": 69,  # Dr. Ricardo Barbosa - Pneumologia
            "paciente_id": 114,  # Camila Torres
            "tipo_exame_id": 18,  # Espirometria
            "data": "2025-08-28",
            "hora_inicio": "10:45",
            "duracao_minutos": 45,
            "status": "realizada",
            "observacoes": "Avaliação função pulmonar",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": 137,
            "medico_id": 70,  # Dra. Camila Nascimento - Reumatologia
            "paciente_id": 115,  # Diego Mendes
            "tipo_exame_id": 39,  # PCR
            "data": "2025-08-29",
            "hora_inicio": "13:00",
            "duracao_minutos": 30,
            "status": "agendada",
            "observacoes": "Suspeita de artrite reumatoide",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    try:
        db.consulta.insert_many(consultas, ordered=False)
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
