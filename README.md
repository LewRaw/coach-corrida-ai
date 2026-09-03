# 🏃 Coach de Corrida AI (Running Coach & Analytics)

Aplicação web interativa desenvolvida em **Streamlit** para corredores de rua e maratonistas. Utiliza o modelo multimodal de última geração **Gemini 2.5 Flash** (via SDK oficial `google-genai`) com **Structured Outputs** (JSON Schema) para analisar capturas de tela de treinos (Garmin Connect, Strava, Polar), correlacionar com a percepção de esforço do atleta (RPE) e fornecer diagnósticos técnicos de consultoria em corrida de rua, persistindo o histórico automaticamente no **Google Sheets** via `gspread`.

---

## 🌟 Funcionalidades Principais

1. **Aba "🏃 Novo Treino"**:
   - Upload de capturas de tela de treinos de corrida (Garmin, Strava, Polar, Coros).
   - Coleta de Percepção Subjetiva de Esforço (RPE na escala de Borg 1 a 10) e relato/notas do atleta.
   - Extração automática e estruturada das métricas:
     - 📏 **Distância (km)**
     - ⏱️ **Pace Médio (mm:ss)**
     - ❤️ **Frequência Cardíaca Média (bpm)**
     - ⏳ **Tempo Total de Prova/Treino**
     - 🎯 **Zona Cardíaca Predominante**
   - Emissão de **Parecer Técnico de Consultoria**:
     - *Diagnóstico do Treino*: Análise da relação ritmo vs volume vs altimetria.
     - *Intensidade Cardíaca*: Avaliação do estresse fisiológico e zonas de frequência.
     - *Próximo Passo*: Prescrição prática para a sessão seguinte (ex: descanso ativo, rodagem Z2, treino de força).
   - Persistência automática das informações estruturadas na aba `Treinos` do Google Sheets.

2. **Aba "📅 Treino Atual & Cronograma"**:
   - **Hero Card do Próximo Treino**: Destaque para a próxima sessão agendada com distância, ritmo alvo, RPE e como executar.
   - **Check-in Interativo**: Botão `✅ Marcar como Feito / Concluído` que atualiza diretamente a linha da sessão na aba `Cronograma` do Google Sheets com timestamp de conclusão e animação comemorativa.
   - **Indicadores de Adesão**: Acompanhamento de metas com barra de progresso (treinos concluídos/totais e km completados).
   - **Tabela Geral do Cronograma**: Histórico de sessões prescritas com filtros (`Todos`, `Pendentes ⏳` e `Concluídos ✅`).

3. **Aba "📊 Histórico e Gráficos"**:
   - Leitura em tempo real dos treinos concluídos na aba `Treinos` do Google Sheets com tratamento de formatos numéricos.
   - Indicadores agregados (Volume Total, Total de Sessões, FC Média Geral, Volume Médio por Sessão).
   - Gráfico de barras temporais com a evolução do volume de rodagem (km).
   - Gráfico de linha com o monitoramento da frequência cardíaca ao longo dos treinos.
   - Tabela de dados interativa para visualização completa dos registros e pareceres.

4. **Aba "💬 Conversar com o Coach"**:
   - Interface de chat interativo (`st.chat_message` e `st.chat_input`) direto com o Treinador de Corrida.
   - **Consulta em Tempo Real ao Histórico**: O modelo acessa automaticamente os treinos, paces, frequências cardíacas e pareceres salvos na planilha para dar respostas hiper-personalizadas.
   - Botões de atalhos rápidos com dúvidas frequentes (evolução de pace, prontidão para meia maratona, recomendação para o próximo treino, eficiência cardíaca).

5. **Aba "📋 Montador de Treinos"**:
   - Gerador de periodização estruturada com o Gemini 2.5 Flash (`Pydantic Schema`).
   - Seleção de objetivos: Estreia em 21k, Sub 50 nos 10k, Recorde nos 5k, Maratona 42k ou Base Aeróbica Z2.
   - **Sincronização com o Google Sheets**: Botão para salvar automaticamente os 7 treinos na aba `Cronograma` para acompanhamento no app.
   - Exportação da planilha de treinos em formato Markdown (`.md`).

---

## 🛠️ Tecnologias Utilizadas

- **Frontend / Framework Web**: [Streamlit](https://streamlit.io/)
- **Inteligência Artificial Multimodal**: [Google GenAI SDK](https://github.com/googleapis/python-genai) (`google-genai`) com modelo `gemini-2.5-flash`
- **Modelagem de Dados Estruturados**: [Pydantic v2](https://docs.pydantic.dev/)
- **Persistência de Dados**: [gspread](https://docs.gspread.org/) e [Google Cloud Service Account](https://cloud.google.com/iam/docs/service-accounts)
- **Visualização de Dados**: [Plotly Express](https://plotly.com/python/) e [Pandas](https://pandas.pydata.org/)
- **Processamento de Imagem**: [Pillow](https://python-pillow.org/)

---

## 🚀 Como Executar Localmente

### 1. Pré-requisitos
- **Python 3.12+** instalado na máquina.
- Conta no **Google AI Studio** para obter a chave de API do Gemini.
- Projeto no **Google Cloud Platform (GCP)** com as APIs do Google Sheets e Google Drive ativadas.

### 2. Clonar o Repositório e Criar Ambiente Virtual

```bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/coach-corrida-ai.git
cd coach-corrida-ai

# Crie o ambiente virtual (venv)
python -m venv venv

# Ative o ambiente virtual
# No Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# No Windows (CMD):
.\venv\Scripts\activate.bat
# No Linux/macOS:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração dos Segredos (.streamlit/secrets.toml)

Copie o arquivo de exemplo para criar seu arquivo de segredos local:

```bash
# No Windows (PowerShell):
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml

# No Linux/macOS:
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edite o arquivo `.streamlit/secrets.toml`:

```toml
# 1. Chave da API Gemini (https://aistudio.google.com/)
GEMINI_API_KEY = "AIzaSy..."

# 2. URL completa da sua planilha Google Sheets
sheet_url = "https://docs.google.com/spreadsheets/d/SEU_ID_DA_PLANILHA/edit#gid=0"

# 3. Credenciais da Service Account do Google Cloud (GCP)
[gcp_service_account]
type = "service_account"
project_id = "seu-projeto-gcp"
private_key_id = "abcdef1234567890abcdef1234567890abcdef12"
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n"
client_email = "running-coach-service@seu-projeto-gcp.iam.gserviceaccount.com"
client_id = "123456789012345678901"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/running-coach-service%40seu-projeto-gcp.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

> ⚠️ **IMPORTANTE - Compartilhamento da Planilha:**  
> Abra sua planilha no Google Sheets, clique em **Compartilhar** e adicione o endereço de e-mail da sua Service Account (`client_email`, por exemplo `running-coach-service@seu-projeto-gcp.iam.gserviceaccount.com`) com permissão de **Editor**. Crie uma aba nomeada `Treinos` (a aplicação adicionará os cabeçalhos automaticamente se estiver vazia).

### 4. Executar a Aplicação

```bash
streamlit run app.py
```

Acesse no navegador: `http://localhost:8501`.

---

## ☁️ Guia de Deploy no Streamlit Community Cloud

1. Faça o fork ou envie o código para seu repositório pessoal no **GitHub**.
2. Acesse [share.streamlit.io](https://share.streamlit.io/) e entre com sua conta do GitHub.
3. Clique em **"New app"**:
   - **Repository**: Selecione seu repositório `coach-corrida-ai`.
   - **Branch**: `main`.
   - **Main file path**: `app.py`.
4. Em **"Advanced settings"** -> **"Secrets"**, cole o conteúdo completo do seu `.streamlit/secrets.toml` com suas credenciais reais.
5. Clique em **"Deploy!"**.
6. Pronto! A aplicação estará acessível globalmente em ambiente seguro com HTTPS.

---

## 📂 Estrutura do Repositório

```text
├── .gitignore                      # Proteção de segredos, venv e caches
├── .streamlit/
│   └── secrets.toml.example        # Template de credenciais e chaves
├── app.py                          # Aplicação Streamlit completa e modular
├── requirements.txt                # Dependências do projeto
└── README.md                       # Documentação técnica e guia de uso
```

---

## 🔒 Segurança e Boas Práticas
- O arquivo `.streamlit/secrets.toml` está incluído no `.gitignore` para prevenir vazamento acidental de chaves de API e credenciais privadas da Service Account.
- As chamadas ao Google GenAI utilizam tipagem estrita via Pydantic para garantir respostas previsíveis e livres de alucinações de formato.
