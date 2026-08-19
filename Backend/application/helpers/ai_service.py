import json
import base64
import logging
from functools import lru_cache
from groq import AsyncGroq
from application.helpers.config import Config
import re

logger = logging.getLogger(__name__)

MODEL = Config.GROQ_MODEL


@lru_cache(maxsize=1)
def _get_client():
    return AsyncGroq(api_key=Config.GROQ_API_KEY)


def _parse_json_response(text: str) -> dict | None:
    text = text.strip()
    
    text = re.sub(r"<think>.*?(</think>|$)", "", text, flags=re.DOTALL).strip()
    
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
                pass
    return None


async def detect_spam(title: str, description: str) -> dict | None:
    try:
        client = _get_client()

        system_prompt = """You are a strict quality-control filter for an Indian municipal civic complaint platform called CivicResolve.

Your job: classify whether a citizen's complaint is GENUINE or SPAM.

CLASSIFICATION RULES:
- "bot": Repetitive/template text, lorem ipsum, random characters, keyboard mashing, auto-generated patterns
- "scam": Phishing links, money requests, personal info harvesting, redirect to external numbers/sites
- "spam": Advertisements, promotions, political propaganda, jokes, memes, off-topic rants with no civic issue
- "outdated": References events clearly years in the past with no current relevance
- "none": A real civic infrastructure issue (even if brief, poorly written, or emotional)

IMPORTANT GUIDELINES:
- Short complaints ARE valid if they describe a real issue (e.g., "pothole near bus stop" is valid)
- Emotional language alone does NOT make something spam — citizens can be frustrated
- Typos and grammatical errors do NOT indicate bot activity
- Complaints in any Indian language are valid
- If uncertain, lean towards "none" — it is better to let a borderline complaint through than to reject a genuine one

Respond ONLY with a valid JSON object matching this structure:
{
  "is_spam": true,
  "spam_type": "spam",
  "reason": "brief explanation in under 50 words"
}

CRITICAL INSTRUCTION: DO NOT OUTPUT ANY <think> TAGS. DO NOT OUTPUT ANY REASONING. OUTPUT EXACTLY ONE RAW JSON OBJECT AND NOTHING ELSE. NO MARKDOWN. NO CONVERSATION."""

        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Complaint Title: {title}\nComplaint Description: {description}"},
            ],
            temperature=0.0,
            max_completion_tokens=500,
            response_format={"type": "json_object"},
            extra_body={"reasoning_effort": "none"},
        )
        return _parse_json_response(response.choices[0].message.content)
    except Exception as e:
        logger.error("detect_spam failed: %s: %s", type(e).__name__, e)
        return None


async def translate_text(text: str, target_lang: str = "en") -> dict | None:
    if not text or not text.strip():
        return None
    try:
        client = _get_client()

        system_prompt = f"""You are a multilingual text translator for an Indian civic services platform.

TASK: Detect the language of the given text and translate it to {target_lang}.

RULES:
- If text is already in {target_lang}, return it unchanged
- Handle romanized Indian languages (Hinglish, Tanglish, etc.) — e.g., "sadak pe bahut bada pothole hai" should translate to "There is a very big pothole on the road"
- Preserve ALL proper nouns, location names, landmark names, and street names exactly as written
- Preserve numbers, measurements, and technical terms
- Do NOT add information that isn't in the original text
- For mixed-language text (e.g., English words in a Hindi sentence), translate the non-English parts and keep the English parts

Respond ONLY with valid JSON:
{{"translated_text": "the translated text here", "detected_language": "ISO 639-1 code (en, hi, ta, te, bn, mr, gu, kn, ml, pa, or)"}}

CRITICAL INSTRUCTION: DO NOT OUTPUT ANY <think> TAGS. DO NOT OUTPUT ANY REASONING. OUTPUT EXACTLY ONE RAW JSON OBJECT AND NOTHING ELSE. NO MARKDOWN. NO CONVERSATION."""

        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Text: {text}"},
            ],
            temperature=0.1,
            max_completion_tokens=1000,
            response_format={"type": "json_object"},
            extra_body={"reasoning_effort": "none"},
        )
        return _parse_json_response(response.choices[0].message.content)
    except Exception as e:
        logger.error("translate_text failed: %s: %s", type(e).__name__, e)
        return None


async def sanitize_complaint(description: str) -> dict | None:
    try:
        client = _get_client()

        system_prompt = """You are a civic complaint text processor for an Indian municipal government system.

TASK: Rewrite the complaint into a professional, neutral, factual report.

WHAT TO REMOVE:
- Personal identifying info: names, phone numbers, emails, flat/house numbers of the complainant
- Emotional language: anger, threats, profanity, ALL-CAPS shouting, sarcasm
- Repetitive content and filler words

WHAT TO KEEP:
- The specific infrastructure problem (what is broken/damaged/missing)
- Exact location details (street names, landmarks, area names, pincodes)
- Duration/timeline of the issue
- Severity indicators (dimensions, extent of damage, safety hazards)
- Impact on citizens (traffic disruption, health hazard, safety risk)

OUTPUT REQUIREMENTS:
- Professional third-person tone suitable for a government work order
- Single paragraph, 50-200 words
- No markdown formatting

Respond ONLY with valid JSON:
{"sanitized_text": "rewritten professional description", "summary": "one-line factual summary under 100 characters"}

CRITICAL INSTRUCTION: DO NOT OUTPUT ANY <think> TAGS. DO NOT OUTPUT ANY REASONING. OUTPUT EXACTLY ONE RAW JSON OBJECT AND NOTHING ELSE. NO MARKDOWN. NO CONVERSATION."""

        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Original complaint:\n{description}"},
            ],
            temperature=0.2,
            max_completion_tokens=1500,
            response_format={"type": "json_object"},
            extra_body={"reasoning_effort": "none"},
        )
        logger.debug("[sanitize] Raw response: %s", response.choices[0].message.content[:200])
        result = _parse_json_response(response.choices[0].message.content)
        logger.debug("[sanitize] Parsed result: %s", result)
        return result
    except Exception as e:
        logger.error("sanitize_complaint failed: %s: %s", type(e).__name__, e)
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

        system_prompt = f"""You are an expert municipal complaint routing system for an Indian city government.

TASK: Based on the complaint details (and optional photo), determine which department should handle this complaint.

AVAILABLE DEPARTMENTS: [{dept_list}]

ROUTING GUIDELINES:
- Analyze the primary issue described in the complaint
- If a photo is provided, use visual evidence to support your decision (e.g., broken pipes → Water Supply, potholes → Roads, garbage → Sanitation)
- Choose the SINGLE most appropriate department from the list above — do NOT invent department names
- If the complaint spans multiple departments, choose the one responsible for the PRIMARY issue
- If no department is a clear match, choose the closest one and set confidence below 0.5

CONFIDENCE SCORING:
- 0.9-1.0: Clear, unambiguous match
- 0.7-0.89: Strong match with minor ambiguity
- 0.5-0.69: Reasonable match but could belong elsewhere
- Below 0.5: Uncertain, may need manual review

Respond ONLY with a valid JSON object matching this structure:
{{
  "department": "exact name from the list above",
  "confidence": 0.85,
  "reasoning": "brief explanation in under 30 words"
}}

CRITICAL INSTRUCTION: DO NOT OUTPUT ANY <think> TAGS. DO NOT OUTPUT ANY REASONING. OUTPUT EXACTLY ONE RAW JSON OBJECT AND NOTHING ELSE. NO MARKDOWN. NO CONVERSATION."""

        user_content = f"Complaint Title: {title}\nComplaint Description: {description}"

        if photo_bytes:
            b64 = base64.b64encode(photo_bytes).decode("utf-8")
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_content},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                    ],
                },
            ]
        else:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ]

        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.1,
            max_completion_tokens=1024,
            response_format={"type": "json_object"},
            extra_body={"reasoning_effort": "none"},
        )
        logger.debug("[auto_route] Raw response: %s", response.choices[0].message.content[:200])
        result = _parse_json_response(response.choices[0].message.content)
        logger.debug("[auto_route] Parsed result: %s", result)

        if result and result.get("department") not in department_names:
            logger.debug("[auto_route] Department '%s' NOT in %s, trying case-insensitive match",
                         result.get("department"), department_names)
            dept_lower = {d.lower(): d for d in department_names}
            matched = dept_lower.get(result["department"].lower())
            if matched:
                result["department"] = matched
            else:
                logger.debug("[auto_route] No match found, returning None")
                return None
        return result
    except Exception as e:
        logger.error("auto_route_complaint failed: %s: %s", type(e).__name__, e)
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

        system_prompt = """You are a duplicate complaint detector for a municipal civic services system.

TASK: Determine if the NEW complaint describes the SAME real-world infrastructure issue as any EXISTING complaint.

DUPLICATE CRITERIA — ALL must be true:
1. SAME type of physical issue (e.g., both about a burst water pipe, both about a pothole)
2. SAME location (use semantic matching — "near Anna Nagar tower" ≈ "Anna Nagar Tower Park area")
3. SAME real-world incident, not just similar categories

NOT DUPLICATES:
- Same category but different locations (e.g., potholes on different streets)
- Different issues at the same location (e.g., pothole vs. broken light on same road)
- Similar descriptions but clearly different incidents
- Complaints where location info is too vague to confirm a match

If a duplicate is found, return the FIRST matching complaint from the existing list.

Respond ONLY with a valid JSON object matching one of these two structures:

If a duplicate is found:
{
  "is_duplicate": true,
  "master_id": 123,
  "master_token": "ABC123XYZ",
  "reason": "brief explanation"
}

If no duplicate is found:
{
  "is_duplicate": false
}

CRITICAL INSTRUCTION: DO NOT OUTPUT ANY <think> TAGS. DO NOT OUTPUT ANY REASONING. OUTPUT EXACTLY ONE RAW JSON OBJECT AND NOTHING ELSE. NO MARKDOWN. NO CONVERSATION."""

        user_content = f"""NEW COMPLAINT:
Title: {new_complaint.get('title', '')}
Description: {new_complaint.get('description', '')}
Location: {new_complaint.get('location', '')}

EXISTING OPEN COMPLAINTS:
{existing_json}"""

        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.1,
            max_completion_tokens=1024,
            response_format={"type": "json_object"},
            extra_body={"reasoning_effort": "none"},
        )
        print(response.choices[0].message.content)
        return _parse_json_response(response.choices[0].message.content)
    except Exception as e:
        logger.error("find_duplicate_complaints failed: %s: %s", type(e).__name__, e)
        return None


async def generate_description_from_photo(photo_bytes: bytes) -> str | None:
    try:
        client = _get_client()

        system_prompt = """You are a civic infrastructure analyst for an Indian municipal government.

TASK: Analyze the provided photo and describe the civic/infrastructure issue visible in it.

RULES:
- Focus ONLY on the infrastructure problem (pothole, broken pipe, garbage, damaged road, broken streetlight, open manhole, waterlogging, etc.)
- Describe: what the issue is, estimated severity, visible extent/dimensions, surrounding context
- Do NOT describe people, vehicles, or irrelevant background elements
- Write in professional, neutral tone
- Keep under 500 characters
- If no civic issue is visible, state "No infrastructure issue identified in the image"

CRITICAL INSTRUCTION: DO NOT OUTPUT ANY <think> TAGS. DO NOT OUTPUT ANY REASONING. OUTPUT ONLY THE RAW TEXT DESCRIPTION AND NOTHING ELSE. NO MARKDOWN. NO CONVERSATION."""

        b64 = base64.b64encode(photo_bytes).decode("utf-8")

        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe the civic issue shown in this image."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                    ],
                },
            ],
            temperature=0.2,
            max_completion_tokens=500,
            extra_body={"reasoning_effort": "none"},
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error("generate_description_from_photo failed: %s: %s", type(e).__name__, e)
        return None


async def merge_duplicate_descriptions(master_desc: str, new_desc: str) -> str | None:
    try:
        client = _get_client()

        system_prompt = """You are a civic complaint text processor for a municipal government system.

TASK: Merge two complaint descriptions about the SAME issue into one cohesive professional paragraph.

RULES:
1. Preserve ALL factual details from BOTH descriptions: dimensions, exact locations, duration, severity, impact
2. If both mention the same fact differently, combine logically (e.g., "200 cm" + "large" → "a large pothole measuring approximately 200 cm")
3. If one provides details the other doesn't, include both
4. Remove any emotional language, personal info, or redundant content
5. Output a SINGLE professional paragraph, 50-250 words
6. Do NOT add any information not present in either description
7. Do NOT use markdown formatting or bullet points

CRITICAL INSTRUCTION: DO NOT OUTPUT ANY <think> TAGS. DO NOT OUTPUT ANY REASONING. OUTPUT ONLY THE MERGED TEXT AND NOTHING ELSE. NO MARKDOWN. NO CONVERSATION."""

        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"MASTER COMPLAINT DESCRIPTION:\n{master_desc}\n\nNEW COMPLAINT DESCRIPTION:\n{new_desc}",
                },
            ],
            temperature=0.2,
            max_completion_tokens=800,
            extra_body={"reasoning_effort": "none"},
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error("merge_duplicate_descriptions failed: %s: %s", type(e).__name__, e)
        return None
