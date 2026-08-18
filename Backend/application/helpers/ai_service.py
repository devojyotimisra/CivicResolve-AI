import json
import asyncio
from functools import lru_cache
from google import genai
from google.genai import types
from application.helpers.config import Config


MODEL = Config.GEMINI_MODEL


@lru_cache(maxsize=1)
def _get_client():
    return genai.Client(api_key=Config.GEMINI_API_KEY)


def _parse_json_response(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                return None
    return None


async def detect_spam(title: str, description: str) -> dict | None:
    try:
        client = _get_client()
        prompt = f"""You are a strict municipal complaint quality filter for an Indian civic services platform.

Analyze the following civic complaint and determine if it is:
- **bot-generated**: Repetitive patterns, nonsensical text, lorem ipsum, random characters, template-like submissions
- **scam**: Attempts to phish, extract money, or redirect to external links/numbers
- **spam**: Irrelevant content, advertisements, promotional material, political propaganda, jokes
- **outdated**: References events clearly in the distant past (years ago) with no current relevance

A REAL civic complaint describes a REAL infrastructure problem (potholes, water leaks, broken lights, garbage, sewage, etc.) with a specific location. Be strict but fair — short complaints are fine if they describe a real issue.

Complaint Title: {title}
Complaint Description: {description}

Respond ONLY with valid JSON:
{"is_spam": true/false, "spam_type": "bot"/"scam"/"spam"/"outdated"/"none", "reason": "brief explanation"} """

        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=1000,
            ),
        )
        return _parse_json_response(response.text)
    except Exception:
        return None


async def translate_text(text: str, target_lang: str = "en") -> dict | None:
    if not text or not text.strip():
        return None
    try:
        client = _get_client()
        prompt = f"""Detect the language of the following text and translate it to {target_lang}.

If the text is already in {target_lang}, return it as-is.

Text: {text}

Respond ONLY with valid JSON:
{"translated_text": "the translated text here", "detected_language": "two-letter ISO 639-1 code like en, hi, bn, ta, te, mr, gu, kn, ml"} """

        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1000,
            ),
        )
        return _parse_json_response(response.text)
    except Exception:
        return None


async def sanitize_complaint(description: str) -> dict | None:
    try:
        client = _get_client()
        prompt = f"""You are a civic complaint text processor. Your job is to rewrite the following complaint description to:

1. **Remove ALL personal identifying information**: names, phone numbers, email addresses, flat/house numbers, personal addresses of the complainant
2. **Remove ALL emotional language**: anger, frustration, threats, caps-lock shouting, profanity, sarcasm
3. **Keep ONLY actionable facts**: What is the issue? Where exactly is it? How long has it been present? How severe is it? What is the impact?
4. **Write in professional, neutral, third-person tone** suitable for a government report

Original complaint:
{description}

Respond ONLY with valid JSON:
{"sanitized_text": "the rewritten professional description here", "summary": "one-line factual summary under 100 characters"} """

        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=800,
            ),
        )
        return _parse_json_response(response.text)
    except Exception:
        return None


async def auto_route_complaint(
    title: str,
    description: str,
    photo_bytes: bytes | None,
    department_names: list[str],
) -> dict | None:
    try:
        client = _get_client()
        dept_list = ", ".join(f'"{d}"' for d in department_names)

        prompt = f"""You are an expert municipal complaint routing system for an Indian city.

Given a civic complaint, determine which department should handle it.

Available departments: [{dept_list}]

Complaint Title: {title}
Complaint Description: {description}

Rules:
- You MUST pick exactly one department from the list above
- If a photo is attached, use visual cues (road damage, water, garbage, broken lights, etc.) to help decide
- confidence should be a float between 0.0 and 1.0

Respond ONLY with valid JSON:
{"department": "exact department name from list", "confidence": 0.0-1.0, "reasoning": "brief explanation"} """

        contents = [prompt]
        if photo_bytes:
            contents = [
                types.Part.from_text(prompt),
                types.Part.from_bytes(data=photo_bytes, mime_type="image/jpeg"),
            ]

        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1024,
            ),
        )
        result = _parse_json_response(response.text)
        if result and result.get("department") not in department_names:
            dept_lower = {d.lower(): d for d in department_names}
            matched = dept_lower.get(result["department"].lower())
            if matched:
                result["department"] = matched
            else:
                return None
        return result
    except Exception:
        return None


async def find_duplicate_complaints(
    new_complaint: dict,
    existing_complaints: list[dict],
) -> dict | None:
    if not existing_complaints:
        return {"is_duplicate": False}
    try:
        client = _get_client()
        existing_json = json.dumps(existing_complaints[:20], ensure_ascii=False)

        prompt = f"""You are a duplicate complaint detector for a municipal civic services system.

Determine if the NEW complaint below describes the SAME physical infrastructure issue at the SAME location as any of the EXISTING complaints.

Two complaints are duplicates ONLY if ALL of these are true:
1. They describe the SAME physical issue (e.g., both about a burst water pipe, both about the same pothole)
2. They refer to the SAME location (use semantic matching — "near Anna Nagar tower" and "Anna Nagar Tower Park area" are the same place)
3. They are clearly about the same real-world incident, not just similar categories

Do NOT mark as duplicate if:
- They are in the same category but at different locations
- They describe different issues at the same location
- The descriptions are vaguely similar but clearly about different incidents

NEW COMPLAINT:
Title: {new_complaint.get('title', '')}
Description: {new_complaint.get('description', '')}
Location: {new_complaint.get('location', '')}

EXISTING OPEN COMPLAINTS:
{existing_json}

Respond ONLY with valid JSON. If duplicate found, use the FIRST matching complaint:
{{ "is_duplicate": true, "master_id": <id of matching complaint>, "master_token": "<token of matching complaint>", "reason": "brief explanation"}} 
OR
{{ "is_duplicate": false}} """

        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1024,
            ),
        )
        return _parse_json_response(response.text)
    except Exception as e:
        print(f"Exception in find_duplicate_complaints: {e}")
        return None
