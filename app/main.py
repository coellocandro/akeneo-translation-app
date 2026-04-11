# Akeneo sample apps: https://github.com/akeneo/sample-apps/tree/main
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from app.akeneo_client import AkeneoClient
from app.libretranslate_client import LibreTranslateClient

app = FastAPI()

def chunk_text(text: str, max_chars: int = 2000) -> list[str]:
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/product/{identifier}")
async def get_product(identifier: str) -> dict:
    client = AkeneoClient()
    return await client.get_product(identifier)

@app.get("/translate-product/{identifier}")
async def default_translation(
    identifier: str,
    fields: str = "name,description",
    scope: str = "ecommerce",
    source_locale: str = "en_US",
    target_locale: str = "de_DE",
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

        chunks = chunk_text(entry["data"])
        translated_chunks = []

        for chunk in chunks:
            translation = await libretranslate_client.translate_text(
                chunk, "en", target_locale.split("_")[0]
            )
            translated_text = translation.get("data", {}).get("translatedText", "")
            if translated_text:
                translated_chunks.append(translated_text)

        result["fields"][field] = {
            "found": True,
            "scope": entry.get("scope"),
            "text": entry["data"],
            "translation": " ".join(translated_chunks),
        }   

    return result

@app.post("/translate-products/save")
async def save_multiple_products(
    identifiers: str,  # comma-separated
    fields: str = "name,description",
    scope: str = "ecommerce",
    source_locale: str = "en_US",
    target_locale: str = "de_DE",
) -> dict:

    akeneo_client = AkeneoClient()
    libretranslate_client = LibreTranslateClient()

    ids = [i.strip() for i in identifiers.split(",")]
    results = []

    for identifier in ids:
        product = await akeneo_client.get_product_values(identifier)
        values = product["values"]
        fields_list = [f.strip() for f in fields.split(",")]

        def get_value(attribute: str):
            entries = values.get(attribute, [])

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

            return next(
                (
                    e for e in entries
                    if e.get("locale") == source_locale
                    and e.get("data")
                ),
                None,
            )

        target_values = {}

        for field in fields_list:
            entry = get_value(field)
            if not entry:
                continue

            chunks = chunk_text(entry["data"])
            translated_chunks = []

            for chunk in chunks:
                translated = await libretranslate_client.translate_text(
                    chunk, "en", target_locale.split("_")[0]
                )
                translated_text = translated.get("data", {}).get("translatedText", "")
                if translated_text:
                    translated_chunks.append(translated_text)

            if not translated_chunks:
                continue

            translated_text = " ".join(translated_chunks)

            target_values[field] = [
                {
                    "locale": target_locale,
                    "scope": entry.get("scope"),
                    "data": translated_text,
                }
            ]

        if not target_values:
            results.append({"identifier": identifier, "status": "skipped"})
            continue

        patch_response = await akeneo_client.patch_product_values(identifier, target_values)

        results.append({
            "identifier": identifier,
            "patched": target_values,
            "status_code": patch_response["status_code"] if target_values else None,
            "ok": patch_response["ok"] if target_values else False,
        })

    return {"results": results}