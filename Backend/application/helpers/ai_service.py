import base64
import json
import re
from functools import lru_cache

from groq import AsyncGroq

from application.helpers.config import Config

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
- "bot": Repetitive/template text, lorem ipsum, random characters, keyboard mashing, gibberish, auto-generated patterns
- "scam": Phishing links, money requests, personal info harvesting, redirect to external numbers/sites
- "spam": Advertisements, promotions, political propaganda, jokes, memes, fake or non-existent landmarks, off-topic rants with no civic relevance
- "outdated": References events clearly years in the past with no current relevance
- "none": A real civic infrastructure issue or a valid resolution report (even if brief, poorly written, or emotional)

IMPORTANT GUIDELINES:
- Short complaints/resolutions ARE valid if they describe a real issue or repair
- Emotional language alone does NOT make something spam — citizens can be frustrated
- Typos and grammatical errors do NOT indicate bot activity
- Complaints in any Indian language are valid
- If uncertain, lean towards "none" — it is better to let a borderline complaint through than to reject a genuine one

Respond ONLY with a valid JSON object matching this structure:
{
  "is_spam": true,
  "spam_type": "spam",
  "reason": "brief explanation in under 10 words"
}

CRITICAL INSTRUCTION: DO NOT OUTPUT ANY <think> TAGS. DO NOT OUTPUT ANY REASONING. OUTPUT EXACTLY ONE RAW JSON OBJECT AND NOTHING ELSE. NO MARKDOWN. NO CONVERSATION."""

        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Complaint Title: {title}\nComplaint Description: {description}",
                },
            ],
            temperature=0.0,
            max_completion_tokens=100,
            response_format={"type": "json_object"},
            extra_body={"reasoning_effort": "none"},
        )
        return _parse_json_response(response.choices[0].message.content)
    except Exception as e:
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
            temperature=0.0,
            max_completion_tokens=400,
            response_format={"type": "json_object"},
            extra_body={"reasoning_effort": "none"},
        )
        return _parse_json_response(response.choices[0].message.content)
    except Exception as e:
        return None


async def sanitize_complaint(title: str, description: str, location: str | None) -> dict | None:
    try:
        client = _get_client()

        system_prompt = """You are a civic complaint text processor for an Indian municipal government system.

TASK: Rewrite the complaint's title, description, and location to be professional, neutral, factual, and semantically rich to aid in deduplication.

WHAT TO REMOVE:
- Personal identifying info: names, phone numbers, emails, flat/house numbers of the complainant
- Emotional language: anger, threats, profanity, vulgar language, ALL-CAPS shouting, sarcasm
- Repetitive content and filler words

WHAT TO KEEP AND ENRICH:
- Title: Discard the original title completely. Generate a brand new, clear, concise, and descriptive title for the core issue based strictly on the description.
- Description: Keep the specific infrastructure problem, severity, duration, and impact. Make it semantically rich but factual.
- Location (Landmark): Preserve the exact physical location, street names, landmarks, area names, and pincodes EXACTLY as they refer to the physical world, but remove any personal context or vulgarity. Make it semantically clear for mapping/deduplication.

OUTPUT REQUIREMENTS:
- Professional third-person tone suitable for a government work order.
- Description should be a single paragraph, 2-3 sentences, maximum 60 words.
- No markdown formatting.
- Respond ONLY with a valid JSON object matching this structure:
{
  "sanitized_title": "rewritten professional title",
  "sanitized_description": "rewritten professional description",
  "sanitized_location": "rewritten location preserving the exact physical landmark"
}

CRITICAL INSTRUCTION: DO NOT OUTPUT ANY <think> TAGS. DO NOT OUTPUT ANY REASONING. OUTPUT EXACTLY ONE RAW JSON OBJECT AND NOTHING ELSE. NO MARKDOWN. NO CONVERSATION."""

        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Title: {title}\nDescription: {description}\nLocation: {location or 'Not provided'}",
                },
            ],
            temperature=0.0,
            max_completion_tokens=400,
            response_format={"type": "json_object"},
            extra_body={"reasoning_effort": "none"},
        )
        result = _parse_json_response(response.choices[0].message.content)
        return result
    except Exception as e:
        return None


async def sanitize_resolution_note(note: str) -> str | None:
    try:
        client = _get_client()

        system_prompt = """You are a text processor for a municipal government system.

TASK: Rewrite the field officer's resolution note to remove inappropriate content while keeping their original tone and perspective.

WHAT TO REMOVE:
- Profanity, vulgar language, anger, personal attacks, or emotional rants
- Excuses or unprofessional complaints about the citizen

WHAT TO KEEP:
- The perspective of the officer (e.g., "I have visited", "We fixed", "Our team barricaded")
- All factual details of the work done
- Make it sound like a professional human officer wrote it, NOT an AI.

Respond ONLY with a valid JSON object matching this structure:
{
  "sanitized_note": "the rewritten professional note"
}

CRITICAL INSTRUCTION: DO NOT OUTPUT ANY <think> TAGS. DO NOT OUTPUT ANY REASONING. OUTPUT EXACTLY ONE RAW JSON OBJECT AND NOTHING ELSE. NO MARKDOWN. NO CONVERSATION."""

        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Officer Note: {note}"},
            ],
            temperature=0.0,
            max_completion_tokens=200,
            response_format={"type": "json_object"},
            extra_body={"reasoning_effort": "none"},
        )
        result = _parse_json_response(response.choices[0].message.content)
        if result and result.get("sanitized_note"):
            return result["sanitized_note"]
        return None
    except Exception as e:
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
  "reasoning": "brief explanation in under 10 words"
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
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                        },
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
            temperature=0.0,
            max_completion_tokens=100,
            response_format={"type": "json_object"},
            extra_body={"reasoning_effort": "none"},
        )
        result = _parse_json_response(response.choices[0].message.content)

        if result and result.get("department") not in department_names:
            dept_lower = {d.lower(): d for d in department_names}
            matched = dept_lower.get(result["department"].lower())
            if matched:
                result["department"] = matched
            else:
                return None
        return result
    except Exception as e:
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
Title: {new_complaint.get("title", "")}
Description: {new_complaint.get("description", "")}
Location: {new_complaint.get("location", "")}

EXISTING OPEN COMPLAINTS:
{existing_json}"""

        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.0,
            max_completion_tokens=100,
            response_format={"type": "json_object"},
            extra_body={"reasoning_effort": "none"},
        )
        return _parse_json_response(response.choices[0].message.content)
    except Exception as e:
        return None


async def generate_description_from_photo(photo_bytes: bytes) -> str | None:
    try:
        client = _get_client()

        system_prompt = """You are a civic infrastructure analyst for an Indian municipal government.

TASK: Analyze the provided photo and describe the civic/infrastructure issue visible in it.

RULES:
- Focus ONLY on the infrastructure problem (pothole, broken pipe, garbage, damaged road, broken streetlight, open manhole, waterlogging, etc.) OR the evidence of a recent repair/resolution (e.g., fresh asphalt, new pipes, clean street).
- Describe: what the issue or resolution is, estimated severity or quality, visible extent/dimensions, surrounding context
- Do NOT describe people, vehicles, or irrelevant background elements
- Write in professional, neutral tone
- Keep under 500 characters
- If no civic issue or repair is visible, state "No infrastructure issue or repair identified in the image"

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
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                        },
                    ],
                },
            ],
            temperature=0.0,
            max_completion_tokens=500,
            extra_body={"reasoning_effort": "none"},
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
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
5. Output a SINGLE professional paragraph, 2-3 sentences, maximum 80 words
6. Be concise — prioritize the most important facts
7. Do NOT add any information not present in either description
8. Do NOT use markdown formatting or bullet points

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
            temperature=0.0,
            max_completion_tokens=400,
            extra_body={"reasoning_effort": "none"},
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return None


async def verify_resolution_relevance(
    complaint_title: str, complaint_desc: str, resolution_desc: str
) -> dict | None:
    try:
        client = _get_client()

        system_prompt = """You are a civic infrastructure auditor for a municipal government.

TASK: Verify if the provided resolution (photo analysis + officer note) actually resolves the original complaint.

RULES:
- Be HIGHLY LENIENT. The resolution must be even vaguely related to the original issue (e.g., if the complaint is a pothole, the resolution should show a filled pothole or state it was fixed).
- Keep in mind that a photo of a fixed issue might look like a normal road/street without issues.
- If the resolution is clearly unrelated or completely mismatched (e.g., complaint is a broken pipe, resolution photo is a tree), mark it as invalid.
- If it plausibly addresses the issue or describes a valid repair, mark it valid.
- Respond ONLY with a valid JSON object matching this structure:
{
  "is_valid": true,
  "reason": "brief explanation in under 10 words"
}

CRITICAL INSTRUCTION: DO NOT OUTPUT ANY <think> TAGS. DO NOT OUTPUT ANY REASONING. OUTPUT EXACTLY ONE RAW JSON OBJECT AND NOTHING ELSE. NO MARKDOWN. NO CONVERSATION."""

        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"ORIGINAL COMPLAINT:\nTitle: {complaint_title}\nDescription: {complaint_desc}\n\nRESOLUTION PROVIDED:\n{resolution_desc}",
                },
            ],
            temperature=0.0,
            max_completion_tokens=100,
            response_format={"type": "json_object"},
            extra_body={"reasoning_effort": "none"},
        )
        return _parse_json_response(response.choices[0].message.content)
    except Exception as e:
        return None
