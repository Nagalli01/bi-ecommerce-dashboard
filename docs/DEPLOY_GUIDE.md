# Guia de Deploy - BI E-Commerce Dashboard

## Requisitos

- Conta gratuita em uma plataforma de hosting (Hugging Face Spaces, Render, Streamlit Cloud)
- Git instalado
- O projeto na sua maquina local

---

## Opcao 1: Hugging Face Spaces (RECOMENDADO)

**Vantagens:** Gratuito, CI integrado com GitHub, SSL incluso, sem limites de privacidade.

### Passo a passo

1. Acesse https://huggingface.co/spaces e clique em "Create new Space"

2. Configure:
   - **Space Name:** `bi-ecommerce-dashboard` (ou outro nome)
   - **License:** MIT
   - **SDK:** Streamlit
   - **Visibility:** Public (ou Private, se preferir)

3. Faca upload dos arquivos da pasta `deploy/`:
   ```
   app.py
   requirements.txt
   bi_ecommerce.db
   ```
   Voce pode fazer upload pelo navegador (arrastar arquivos) ou via git:
   ```bash
   git clone https://huggingface.co/spaces/SEU_USUARIO/bi-ecommerce-dashboard
   cp deploy/* bi-ecommerce-dashboard/
   cd bi-ecommerce-dashboard
   git add . && git commit -m "Initial commit"
   git push
   ```

4. O Hugging Face Spaces fara o build automaticamente. Em 2-3 minutos o dashboard estara no ar.

5. Pronto! URL: `https://SEU_USUARIO-bi-ecommerce-dashboard.hf.space`

---

## Opcao 2: Render

**Vantagens:** Facil, gratis, CI via GitHub.

1. Crie repositorio no GitHub com:
   - `app.py` (da pasta `deploy/`)
   - `requirements.txt`
   - `bi_ecommerce.db`

2. Acesse https://dashboard.render.com, New + Web Service

3. Conecte seu repositorio GitHub

4. Config:
   - **Name:** bi-ecommerce
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port $PORT`

5. **Variavel de ambiente:** `PORT = 10000`

6. Deploy. Apos build, URL: `https://bi-ecommerce.onrender.com`

---

## Opcao 3: Streamlit Community Cloud

**Vantagens:** Feito para Streamlit, gratuito, integracao nativa.

1. Crie repositorio no GitHub com `app.py`, `requirements.txt`, `bi_ecommerce.db`

2. Acesse https://share.streamlit.io, "Deploy an app"

3. Conecte repositorio, branch, caminho do app (`app.py`)

4. Deploy. URL: `https://SEU_USUARIO-bi-ecommerce-dashboard.streamlit.app`

---

## Estrutura do Deploy

```
bi-ecommerce-dashboard/
├── app.py              # Dashboard Streamlit (autocontido)
├── requirements.txt    # Dependencias Python
├── bi_ecommerce.db     # Banco SQLite (732 KB)
└── README.md           # (opcional) Descricao do projeto
```

## Notas

- O banco SQLite ja contem todos os dados. Nao precisa de MySQL.
- Para atualizar os dados, rode `python src/run_pipeline.py` no projeto local e reexporte com `python src/export_sqlite.py`.
- Para atualizar o deploy, substitua o arquivo `bi_ecommerce.db` e faça novo deploy.
- Nao inclua dados sensiveis nos repositorios publicos (senhas, chaves de API).
