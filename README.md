# 🌍 GeoAI Mentor

- Chatbot com memória de sessão para orientar profissionais de **Geociências** (Geologia e Geofísica) na transição para **Ciência de Dados e Inteligência Artificial**.
- Construído com **LangChain**, **LM Studio** e **Gemma 3** rodando 100% localmente — sem enviar dados para nenhuma API externa.
---

## 🎯 Problema

- Profissionais de Geociências possuem habilidades valiosas em matemática, física e análise de dados, mas frequentemente não sabem por onde começar na transição para IA. O  - - GeoAI Mentor atua como um mentor de carreira especializado nessa ponte, mantendo o contexto da conversa para orientações cada vez mais personalizadas.
---

## 🏗️ Arquitetura
```
Pergunta do usuário
        ↓
ChatPromptTemplate
  ├── system: persona e comportamento do mentor
  ├── {historico}: histórico da sessão injetado automaticamente
  └── {query}: pergunta atual
        ↓
   Modelo LLM (Gemma 3 via LM Studio)
        ↓
   StrOutputParser
        ↓
   Resposta em texto
```
O `RunnableWithMessageHistory` envolve toda a cadeia e é responsável por:
- Recuperar o histórico da sessão antes de cada chamada
- Injetar esse histórico no placeholder `{historico}` do prompt
- Atualizar o histórico com a nova pergunta e resposta após cada turno

Isso transforma uma cadeia stateless em um assistente com memória persistente por sessão.
---

## ⚙️ Configuração do ambiente

### Pré-requisitos
- Python 3.10+
- [LM Studio](https://lmstudio.ai/) instalado e rodando localmente
- Modelo **Gemma 3** carregado no LM Studio
### Instalação
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/geoai-mentor.git
cd geoai-mentor
# Instale as dependências
pip install langchain langchain-openai python-dotenv
```
### Variáveis de ambiente
Copie o arquivo de exemplo e preencha com seus valores:

```bash
cp .env.example .env
```
Edite o `.env`:
```
LOCAL_MODEL=google/gemma-3n-e4b
BASE_URL=http://127.0.0.1:1234/v1
```
> ⚠️ O arquivo `.env` nunca deve ser commitado. Ele já está no `.gitignore`.

### Executando
Certifique-se de que o LM Studio está rodando com o modelo carregado, então:
```bash
python chat_mentor.py
```
---
## 💬 Exemplo de interação

### ❌ Sem memória (chamadas isoladas)
```
Usuário: Sou geofísico e quero aprender IA. O que estudar primeiro?
IA: Recomendo começar com Python e bibliotecas como NumPy e Pandas...

Usuário: E como aplico isso em dados sísmicos?
IA: Para trabalhar com dados sísmicos, você pode usar Python... 
# ← não conecta com a resposta anterior
```

### ✅ Com memória (sessão contínua)
```
Usuário: Sou geofísico e quero aprender IA. O que estudar primeiro?
IA: Recomendo começar com Python e bibliotecas como NumPy e Pandas...
    [Memória: 2 mensagens armazenadas]

Usuário: E como aplico isso em dados sísmicos?
IA: Ótima pergunta! Como mencionei antes, com Python e NumPy você pode 
    carregar arquivos SEG-Y, aplicar transformadas de Fourier para análise 
    espectral e usar bibliotecas como ObsPy para processamento sísmico...
    # ← conecta diretamente com o contexto anterior
    [Memória: 4 mensagens armazenadas]
```
---

## 📦 Estrutura do projeto
```
geoai-mentor/
├── chat_mentor.py     # Script principal
├── .env.example       # Modelo de variáveis de ambiente
├── .gitignore         # Exclui .env e arquivos temporários
└── README.md
```
---
## 🛠️ Tecnologias
| Tecnologia | Uso |
|---|---|
| [LangChain](https://python.langchain.com/) | Orquestração da cadeia e memória |
| [LM Studio](https://lmstudio.ai/) | Servidor local compatível com API OpenAI |
| [Gemma 3](https://ai.google.dev/gemma) | Modelo de linguagem rodando localmente |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Gerenciamento seguro de variáveis de ambiente |

---
## 📚 Aprendizados

- Como o `ChatPromptTemplate` estrutura a persona e o comportamento do assistente
- A diferença entre uma IA **sem estado** (cada chamada é isolada) e **com estado** (contexto acumulado)
- Como o `InMemoryChatMessageHistory` armazena e recupera o histórico por sessão
- Como o `RunnableWithMessageHistory` conecta memória e cadeia de forma transparente
- Boas práticas de segurança: variáveis sensíveis em `.env`, nunca no código

## Desafio Proposto pela Alura.
