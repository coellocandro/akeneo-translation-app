# Akeneo sample apps: https://github.com/akeneo/sample-apps/
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from app.akeneo_client import AkeneoClient
from app.libretranslate_client import LibreTranslateClient

app = FastAPI()

@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "LibreTranslate Akeneo Translation API",
        "docs": "/docs",
        "health": "/health",
    }

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
            if v.get("data") is None:
                continue
            return v
    return None

async def translate_attribute(
    values: dict,
    field: str,
    source_locale: str,
    target_locale: str,
    scope: str | None,
    libretranslate_client: LibreTranslateClient,
) -> dict | None:
    entry = get_attribute_value(values, field, source_locale, scope)
    if not entry:
        return None

    source_lang = source_locale.split("_")[0]
    target_lang = target_locale.split("_")[0]
    chunks = chunk_text(entry["data"])
    translated_chunks = []

    for chunk in chunks:
        translation = await libretranslate_client.translate_text(
            chunk,
            source_lang,
            target_lang,
        )
        translated_text = translation.get("translatedText", "")
        if translated_text:
            translated_chunks.append(translated_text)

    if not translated_chunks:
        return None

    return {
        "locale": entry.get("locale"),
        "scope": entry.get("scope"),
        "text": entry["data"],
        "translation": "".join(translated_chunks),
    }

def get_product_values(product: dict, identifier: str) -> dict:
    values = product.get("values")
    if not isinstance(values, dict):
        raise HTTPException(
            status_code=502,
            detail=f"Invalid Akeneo response for product '{identifier}': missing or invalid values.",
        )
    return values

# Routes

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

    try:
        product = await akeneo_client.get_pim_content(identifier)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch product '{identifier}' from Akeneo.",
        ) from exc

    values = get_product_values(product, identifier)
    attributes = [f.strip() for f in fields.split(",") if f.strip()]

    result = {
        "identifier": identifier,
        "scope": scope,
        "source_locale": source_locale,
        "target_locale": target_locale,
        "fields": {},
    }
  
    for field in attributes:
        translated = await translate_attribute(
            values=values,
            field=field,
            source_locale=source_locale,
            target_locale=target_locale,
            scope=scope,
            libretranslate_client=libretranslate_client,
        )

        if not translated:
            result["fields"][field] = {
                "found": False,
                "text": None,
                "translation": None,
            }
            continue

        result["fields"][field] = {
            "found": True,
            "locale": translated["locale"],
            "scope": translated["scope"],
            "text": translated["text"],
            "translation": translated["translation"],
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

    ids = [i.strip() for i in identifiers.split(",") if i.strip()]
    attributes = [f.strip() for f in fields.split(",") if f.strip()]

    results = []
    
    for identifier in ids:
        try:
            product = await akeneo_client.get_pim_content(identifier)
            values = get_product_values(product, identifier)
        except Exception:
            results.append({
                "identifier": identifier,
                "status": "fetch_failed",
            })
            continue
        
        target_values = {}

        for field in attributes:
            translated = await translate_attribute(
                values=values,
                field=field,
                source_locale=source_locale,
                target_locale=target_locale,
                scope=scope,
                libretranslate_client=libretranslate_client,
            )
            if not translated:
                continue

            if translated["locale"] is None:
                continue

            target_values[field] = [
                {
                    "locale": target_locale if translated["locale"] is not None else None,
                    "scope": translated["scope"],
                    "data": translated["translation"],
                }
            ]

        if not target_values:
            results.append({"identifier": identifier, "status": "skipped"})
            continue

        try:
            patch_response = await akeneo_client.patch_translation_to_pim(identifier, target_values)
        except Exception:
            results.append({
                "identifier": identifier,
                "patched": target_values,
                "status": "patch_failed",
            })
            continue

        results.append({
            "identifier": identifier,
            "patched": target_values,
            "status_code": patch_response["status_code"],
            "ok": patch_response["ok"]
        })

    return {"results": results}