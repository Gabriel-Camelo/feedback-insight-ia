# Documentação do Sistema de Análise de Feedbacks com IA

## 1. Visão Geral

O **Sistema de Análise de Feedbacks com IA** é uma aplicação completa para coleta, processamento e visualização de feedbacks de clientes, com recursos avançados de análise de sentimentos e categorização automática utilizando modelos de IA.

### Principais Funcionalidades:
- **Coleta estruturada** de feedbacks vinculados a compras
- **Análise de sentimentos** automática (positivo, neutro, negativo)
- **Rotulagem inteligente** dos feedbacks por tópicos
- **Dashboard interativo** com visualizações avançadas
- **Armazenamento persistente** em banco de dados PostgreSQL
- **Processamento local** com modelos de IA

## 2. Arquitetura do Sistema

### Diagrama de Componentes

```
[Frontend: Streamlit] ←→ [Backend: FastAPI] ←→ [Banco: PostgreSQL]
       ↑
[Modelos de IA Locais]
```

### Tecnologias Utilizadas

| Componente       | Tecnologias                                                                 |
|------------------|-----------------------------------------------------------------------------|
| Backend          | FastAPI, Python 3.9, SQLAlchemy, Pydantic                                  |
| Frontend         | Streamlit, Plotly, WordCloud                                                |
| Banco de Dados   | PostgreSQL                                                                  |
| IA/NLP           | Transformers, Hugging Face Models (BERTweet, BART), TextBlob               |
| Infraestrutura   | Docker, Docker Compose                                                      |

## 3. Configuração e Instalação

### Pré-requisitos
- Docker 20.10+
- Docker Compose 1.29+
- 4GB de RAM disponível
- 5GB de espaço em disco

### Passos de Instalação

1. **Clonar o repositório**:
   ```bash
   git clone https://github.com/Gabriel-Camelo/feedback-insight-ia.git
   cd feedback-ai-project
   ```

2. **Construir e iniciar os containers**:
   ```bash
   docker compose build
   docker compose up -d
   ```

3. **Popular o banco de dados**:
   ```bash
   docker compose exec app python database_seed.py
   ```

4. **Acessar a aplicação**:
   - API: http://localhost:8000
   - Dashboard: http://localhost:8501
   - Banco de dados: `postgresql://postgres:postgres@localhost:5432/feedback_db`

## 4. Estrutura do Código

### Principais Módulos

| Módulo              | Descrição                                                                 |
|---------------------|---------------------------------------------------------------------------|
| `app/main.py`       | Ponto de entrada da API FastAPI                                          |
| `app/database.py`   | Configuração do banco de dados e sessões                                 |
| `app/models.py`     | Modelos SQLAlchemy para as tabelas do banco                              |
| `app/schemas.py`    | Modelos Pydantic para validação de dados                                 |
| `app/ai_processing.py` | Processamento de NLP e análise de sentimentos                          |
| `streamlit_app/dashboard.py` | Painel interativo de visualização de dados                          |

## 5. Endpoints da API

### Feedbacks

- `GET /feedbacks/` - Lista todos os feedbacks
- `POST /feedbacks/` - Cria um novo feedback
- `GET /feedbacks/{id}` - Obtém detalhes de um feedback específico

### Compras

- `GET /purchases/` - Lista todas as compras
- `POST /purchases/` - Registra uma nova compra

### Rótulos

- `GET /labels/` - Lista todos os rótulos disponíveis

## 6. Fluxo de Processamento

1. **Recebimento do Feedback**:
   - O feedback é recebido via API com o ID da compra associada
   - Os dados são validados pelos schemas Pydantic

2. **Análise de Sentimentos**:
   - O texto é processado pelo modelo BERTweet em português
   - São identificados: score (0-1) e label (positivo/neutro/negativo)

3. **Rotulagem Automática**:
   - O modelo BART-large-MNLI classifica o texto nos rótulos disponíveis
   - Se nenhum rótulo existente se aplicar, novos podem ser sugeridos

4. **Armazenamento**:
   - Os dados são persistidos no PostgreSQL com todas as relações

5. **Visualização**:
   - O dashboard Streamlit consome a API para mostrar insights

## 7. Modelos de IA

### Análise de Sentimentos
- **Modelo**: `lxyuan/distilbert-base-multilingual-cased-sentiments-student`
- **Linguagem**: Português
- **Saída**:
  - `score`: Confiança da predição (0-1)
  - `label`: POS (positivo), NEU (neutro), NEG (negativo)

### Rotulagem de Tópicos
- **Modelo**: `facebook/bart-large-mnli`
- **Abordagem**: Zero-shot classification
- **Capacidade**: Até 200 rótulos simultâneos

## 8. Dashboard Streamlit

### Seções Principais

1. **Visão Geral**:
   - Métricas chave (total feedbacks, média sentimentos)
   - Distribuição de sentimentos (gráfico de pizza)
   - Evolução temporal (gráfico de linhas)

2. **Análise Detalhada**:
   - Rótulos mais frequentes (top 10)
   - Nuvem de palavras dos tópicos
   - Correlação entre produtos e sentimentos

3. **Feedbacks Completos**:
   - Tabela interativa com filtros
   - Visualização raw dos dados

## 9. Banco de Dados

### Diagrama ER

```
+-------------+       +-------------+       +-------+
|  Purchase   |       |  Feedback   |       | Label |
+-------------+       +-------------+       +-------+
| id (PK)     |<------| purchase_id |       | id(PK)|
| customer_id |       | id (PK)     |---+   | name  |
| product_id  |       | comment     |   |   +-------+
| product_name|       | sentiment_  |   |
| amount      |       |   score     |   |
| purchase_   |       | sentiment_  |   |
|   date      |       |   label     |   |
+-------------+       | created_at  |   |
                      +-------------+   |
                                        |
+-------------------+                   |
| FeedbackLabel     |<------------------+
+-------------------+
| id (PK)          |
| feedback_id (FK) |
| label_id (FK)    |
+-------------------+
```

## 10. Operação em Produção

### Variáveis de Ambiente Críticas

| Variável          | Descrição                              | Exemplo                           |
|-------------------|----------------------------------------|-----------------------------------|
| `DATABASE_URL`    | URL de conexão com o PostgreSQL        | `postgresql://postgres:postgres@localhost:5432/feedback_db` |
| `API_URL`         | URL base da API FastAPI                | `http://localhost:8000`           |

### Escalabilidade

1. **Horizontal**:
   - Adicionar mais réplicas do serviço `app`
   - Usar um load balancer

2. **Vertical**:
   - Aumentar recursos para containers (CPU/Memória)
   - Especialmente para processamento de IA

## 11. Monitoramento e Manutenção

### Métricas Recomendadas
- Tempo médio de resposta da API
- Uso de CPU/Memória durante análise
- Acertos/misses do cache de modelos

### Rotinas de Manutenção
1. **Backup diário** do volume PostgreSQL
2. **Limpeza semanal** do cache de modelos não utilizados
3. **Atualização mensal** dos modelos de IA

## 12. Troubleshooting

### Problemas Comuns e Soluções

| Problema                          | Solução                                                                 |
|-----------------------------------|-------------------------------------------------------------------------|
| Conexão com DB falha              | Checar se o serviço `feedback_db` está saudável (`docker ps`)            |
| Dashboard não atualiza            | Limpar cache do Streamlit (`Ctrl+R` no navegador)                       |
| Alta latência na análise          | Aumentar recursos para o container ou reduzir concorrência              |

## 13. Roadmap e Melhorias Futuras

1. **Próximas Versões**:
   - Integração com APIs de e-commerce
   - Alertas automáticos para feedbacks negativos
   - Análise comparativa entre produtos

2. **Melhorias de Performance**:
   - Cache de resultados de análise
   - Modelos de IA otimizados

3. **Novos Recursos**:
   - Extração de palavras-chave
   - Detecção de urgência em reclamações
   - Integração com sistemas de CRM

## 14. Referências e Dependências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Hugging Face Models](https://huggingface.co/models)
- [SQLAlchemy ORM](https://www.sqlalchemy.org/)
