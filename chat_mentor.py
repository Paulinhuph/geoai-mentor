import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Carrega as variáveis do arquivo .env para o ambiente antes de qualquer os.getenv()
load_dotenv()

# Lê e valida as variáveis de ambiente obrigatórias
local_model = os.getenv("LOCAL_MODEL")
if not local_model:
    raise ValueError(
        "Variável LOCAL_MODEL não encontrada no .env. "
        "Adicione: LOCAL_MODEL=nome-do-seu-modelo"
    )

base_url = os.getenv("BASE_URL")
if not base_url:
    raise ValueError(
        "Variável BASE_URL não encontrada no .env. "
        "Adicione: BASE_URL=http://127.0.0.1:1234/v1"
    )

# Instancia o modelo de linguagem apontando para o servidor local do LM Studio
llm = ChatOpenAI(
    model=local_model,
    # LM Studio exige algum valor na chave, mas não valida — qualquer string serve
    # Para OpenAI real, substitua por: api_key=os.getenv("OPENAI_API_KEY")
    api_key="lm-studio",
    # Endereço do servidor LM Studio compatível com a API da OpenAI
    base_url=base_url,
    # 0.7 equilibra criatividade e coerência nas respostas
    temperature=0.7
)

# Define o template do prompt com três partes:
# 1. system: instrução de comportamento do assistente
# 2. placeholder {historico}: onde o histórico da conversa será injetado automaticamente
# 3. human {query}: a mensagem atual do usuário
# IMPORTANTE: os nomes {historico} e {query} devem bater exatamente com
# history_messages_key e input_messages_key definidos no RunnableWithMessageHistory
prompt_GeoMentor = ChatPromptTemplate.from_messages(
    [
        ("system", """Você é e deve se apresentar como Mr. GeoAI Mentor, um assistente especializado em orientar estudantes e profissionais de Geociências, como Geologia e Geofísica, que desejam migrar para a área de Ciência de Dados e Inteligência Artificial.

Seu papel é atuar como um mentor de carreira: responda de forma clara, didática, amigável e objetiva. Considere o contexto das mensagens anteriores para manter a conversa coerente e personalizada.

Ao responder:
- explique conceitos de forma simples, mas sem ser superficial;
- conecte habilidades de Geociências com aplicações em Dados e IA;
- sugira caminhos práticos de estudo, projetos de portfólio e transição de carreira;
- adapte as respostas ao histórico da conversa;
- quando fizer sentido, organize a resposta em passos curtos e acionáveis.

Evite respostas genéricas, vagas ou excessivamente técnicas sem necessidade."""),
        ("placeholder", "{historico}"),
        ("human", "{query}")
    ]
)

# Monta a cadeia de execução: prompt → modelo → parser de texto
cadeia = prompt_GeoMentor | llm | StrOutputParser()

# Dicionário em memória que armazena o histórico de cada sessão separadamente
memoria = {}

# Identificador único da sessão — permite múltiplas conversas isoladas
sessao = "geoamentor"

# Retorna o histórico da sessão informada, criando um novo se ainda não existir
def obter_historico_por_sessao(sessao: str) -> InMemoryChatMessageHistory:
    if sessao not in memoria:
        memoria[sessao] = InMemoryChatMessageHistory()
    return memoria[sessao]

# Envolve a cadeia com gerenciamento de memória automático:
# a cada invoke, o histórico é recuperado, injetado no prompt e atualizado com a resposta
cadeia_com_memoria = RunnableWithMessageHistory(
    runnable=cadeia,
    get_session_history=obter_historico_por_sessao,
    # Deve bater com "{query}" no ChatPromptTemplate
    input_messages_key="query",
    # Deve bater com "{historico}" no ChatPromptTemplate
    history_messages_key="historico"
)

# Lista de perguntas que simulam uma conversa sequencial com contexto acumulado
listas_perguntas = [
    "Sou geofísico, tenho boa base em matemática e quero ir para IA. O que estudar primeiro?",
    "E como eu aplico isso especificamente em dados sísmicos?"
]

print("=" * 60)
print(f"Sessão iniciada: {sessao}")
print("=" * 60, "\n")

for i, uma_pergunta in enumerate(listas_perguntas, start=1):
    print(f"[Pergunta {i}]")
    print(f"Usuário: {uma_pergunta}\n")

    try:
        # Envia a pergunta para a cadeia com memória
        # config passa o session_id para que o histórico correto seja recuperado
        resposta = cadeia_com_memoria.invoke(
            {"query": uma_pergunta},
            config={"configurable": {"session_id": sessao}}
        )
        print(f"IA: {resposta}\n")

    except Exception as e:
        # Captura falhas de conexão com o servidor LM Studio ou erros do modelo
        print(f"Erro ao chamar o modelo: {e}")
        print("Verifique se o LM Studio está rodando em http://127.0.0.1:1234\n")
        break

    # Exibe quantas mensagens estão armazenadas para confirmar que a memória cresce
    # Se na 2ª resposta o modelo referenciar a 1ª, a memória está funcionando
    historico_atual = obter_historico_por_sessao(sessao)
    print(f"[Memória: {len(historico_atual.messages)} mensagens armazenadas]")
    print("-" * 60, "\n")