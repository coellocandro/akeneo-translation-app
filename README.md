<p align="center">
  <img src="https://raw.githubusercontent.com/LibreTranslate/LibreTranslate/refs/heads/main/libretranslate/static/favicon.ico" width="75"/>
  <img src="https://static.helpjuice.com/helpjuice_production/uploads/upload/image/13819/3005028/akeneo.png" width="80"/>
</p>
<h1 align="center"> LibreTranslate App</h1>
<p align="center">Akeneo PIM translation app that automates safe, structured translation of product content across locales
</p>

## 🌟 Highlights
- Translates Akeneo product content attributes into preferred language & locale
- Supports multiple products, attributes and large content translation using Chunking to stay within API limits
- Intelligent Locale & Channel (Scope) fallback logic to select best content sources & skip non-localized attributes
- Lightweight, reproducible, real-world setup using <u>free</u> PIM & API tools

## Requirements
- WSL (Recommended for Docker compatibility, if using Windows OS)
- Docker 19+ & docker-compose
- Python 3.12+

## ⬇️ Installation & Setup
- Clone this repo, navigate to its root, and run `docker compose up -d` to start local services:
[**Akeneo PIM**](https://github.com/akeneo/pim-community-standard) will be available on http://localhost:8080 and [**LibreTranslate API**](https://docs.libretranslate.com/) on http://localhost:5000
> ##### Note: First time initialization of these containers will take 5-10 minutes. Also, first time Docker users may need to enable Hardware Virtualization in BIOS

- Log into Akeneo using admin/admin to create & connect a custom app and obtain its credentials by following these steps: https://api.akeneo.com/apps/create-custom-app.html#step-2-create-an-app-get-credentials 

- Navigate to `app/` to rename `.env.example` to `.env` and then update it using the credentials obtained above.  After saving, run the block below to create a virtual environment & start FastAPI
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
FastAPI is now available at http://127.0.0.1:8000 with Swagger docs at http://127.0.0.1:8000/docs

- Verify setup: Since **Akeneo PIM** comes pre-loaded with sample data, you can quickly preview a product translation in your terminal using:\
```curl "http://127.0.0.1:8000/translate-product/127469?target_locale=fr_FR"```\
![Terminal Response Preview](assets/product_127469_response_preview.jpg)
And then deliver the translated content to Akeneo using:\
```curl -X POST "http://127.0.0.1:8000/translate-product/delivery?identifiers=127469&target_locale=fr_FR"```\
Updating the previously empty Description (fr-FR) attribute as shown below:\
![Description (fr_FR) Update](assets/product_127469_edit_history.jpg)\
\
Alternatively, you can build your translation request and preview the response via FastAPI at http://127.0.0.1:8000/docs
![FastAPI Browser Preview](assets/product_127469_fastapi_preview_alternative.jpg)