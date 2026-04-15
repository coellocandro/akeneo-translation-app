# Akeneo sample apps: https://github.com/akeneo/sample-apps/
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.akeneo_client import AkeneoClient
from app.libretranslate_client import LibreTranslateClient

app = FastAPI()

def chunk_text(text: str, max_chars: int = 2000) -> list[str]:
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]

def get_attribute_value(values: dict, attribute: str, source_locale: str, scope: str | None) -> dict | None:
    values_list = values.get(attribute, [])

    default_priority = [
        (source_locale, scope),
        (source_locale, None),
        (None, None)       
    ]

    for locale, channel in default_priority:
        for v in values_list:
            if v.get("locale") != locale:
                continue
            if channel is not None and v.get("scope") != channel:
                continue
            if not v.get("data"):
                continue
            return v
    return None

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/translate-product/{identifier}")
async def translate_product(
    identifier: str,
    fields: str = "name,description",
    scope: str = "ecommerce",
    source_locale: str = "en_US",
    target_locale: str = "de_DE",
) -> dict:
    
    akeneo_client = AkeneoClient()
    libretranslate_client = LibreTranslateClient()

    product = await akeneo_client.get_content_to_translate(identifier)
    values = product["values"]
    attributes = [f.strip() for f in fields.split(",")]
    source_lang = source_locale.split("_")[0]
    target_lang = target_locale.split("_")[0] 

    result = {
        "identifier": identifier,
        "scope": scope,
        "source_locale": source_locale,
        "target_locale": target_locale,
        "fields": {},
    }
  
    for field in attributes:
        entry = get_attribute_value(values, field, source_locale, scope)
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
                chunk, source_lang, target_lang
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

@app.post("/translate-product/delivery")
async def deliver_translation(
    identifiers: str,
    fields: str = "name,description",
    scope: str = "ecommerce",
    source_locale: str = "en_US",
    target_locale: str = "de_DE",
) -> dict:

    akeneo_client = AkeneoClient()
    libretranslate_client = LibreTranslateClient()

    ids = [i.strip() for i in identifiers.split(",")]
    attributes = [f.strip() for f in fields.split(",")]
    source_lang = source_locale.split("_")[0]
    target_lang = target_locale.split("_")[0] 
    results = []
    
    for identifier in ids:
        product = await akeneo_client.get_content_to_translate(identifier)
        values = product["values"]
        target_values = {}

        for field in attributes:
            entry = get_attribute_value(values, field, source_locale, scope)
            if not entry:
                continue

            if entry.get("locale") is None:
                continue

            chunks = chunk_text(entry["data"])
            translated_chunks = []

            for chunk in chunks:
                translated = await libretranslate_client.translate_text(
                    chunk, source_lang, target_lang
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

        patch_response = await akeneo_client.patch_translation_to_pim(identifier, target_values)

        results.append({
            "identifier": identifier,
            "patched": target_values,
            "status_code": patch_response["status_code"],
            "ok": patch_response["ok"]
        })

    return {"results": results}