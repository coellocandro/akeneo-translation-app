# Akeneo sample apps: https://github.com/akeneo/sample-apps/tree/main
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from app.akeneo_client import AkeneoClient
from app.libretranslate_client import LibreTranslateClient

app = FastAPI()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/akeneo-test")
async def akeneo_test() -> dict:
    client = AkeneoClient()
    return await client.ping()

@app.get("/products-test")
async def products_test() -> dict:
    client = AkeneoClient()
    return await client.get_products()

@app.get("/auth-test")
async def auth_test() -> dict:
    client = AkeneoClient()
    return await client.get_access_token()

@app.get("/products-auth-test")
async def products_auth_test() -> dict:
    client = AkeneoClient()
    return await client.get_products_authenticated()

@app.get("/product/{identifier}")
async def get_product(identifier: str) -> dict:
    client = AkeneoClient()
    return await client.get_product(identifier)

@app.get("/translate-test")
async def translate_test() -> dict:
    client = LibreTranslateClient()
    return await client.translate_text("Hello world!", "en", "es")


@app.get("/translate-product/{identifier}")
async def default_translation(
    identifier: str,
    fields: str = "name,description",
    scope: str = "ecommerce",
    source_locale: str = "en_US",
    target_locale: str = "es_ES",
) -> dict:
    akeneo_client = AkeneoClient()
    libretranslate_client = LibreTranslateClient()

    product = await akeneo_client.get_product_values(identifier)
    values = product["values"]

    fields_list = [f.strip() for f in fields.split(",")]

    def get_value(attribute: str) -> dict | None:
        entries = values.get(attribute, [])

        # default to Ecommerce channel/scope & en_US locale
        scoped = next(
            (
                e for e in entries
                if e.get("locale") == source_locale
                and e.get("scope") == scope
                and e.get("data")
            ),
            None,
        )
        if scoped:
            return scoped

        # fallback: locale only
        return next(
            (
                e for e in entries
                if e.get("locale") == source_locale
                and e.get("data")
            ),
            None,
        )

    result = {
        "identifier": identifier,
        "scope": scope,
        "source_locale": source_locale,
        "target_locale": target_locale,
        "fields": {},
    }

    for field in fields_list:
        entry = get_value(field)

        if not entry:
            result["fields"][field] = {
                "found": False,
                "text": None,
                "translation": None,
            }
            continue

        translation = await libretranslate_client.translate_text(
            entry["data"], "en", target_locale.split("_")[0]
        )

        result["fields"][field] = {
            "found": True,
            "scope": entry.get("scope"),
            "text": entry["data"],
            "translation": translation,
        }

    return result