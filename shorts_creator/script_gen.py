"""
Script Generator for YouTube Shorts.
Supports Gemini AI API, OpenAI API, custom user inputs, and procedural viral offline templates.
Full bilingual support: Tamil (தமிழ்) and English.
"""

import os
import re
import json
import urllib.request
from typing import Dict, Any, List, Optional
from shorts_creator.templates import VIRAL_TEMPLATES
from shorts_creator.text_match import has_term

# Shared by every language and provider; these are what a viewer feels in the first seconds
RETENTION_RULES = (
    "Hook rules: at most 10 spoken words, open a specific curiosity gap, and never begin with a greeting, "
    "'Did you know' or the topic name. "
    "Every line must add one new, concrete detail: a number, a name or a surprising turn. No filler and no 'in this video'. "
    "Accuracy: use only claims that are true and widely documented. Never invent facts, statistics or quotes, "
    "and do not promise anything the script does not deliver. "
    "The cta must not ask viewers to subscribe, like or comment. "
    "Also output: screen_hook (the on-screen version of the hook, at most 6 words, in the script's language) and "
    "visuals (an array of 5 English stock-footage search phrases, one each for the hook, the 3 points and the cta, "
    "each naming a concrete filmable subject, for example 'astronaut floating above earth'). "
)


def detect_language(text: str) -> str:
    """Detect if the input text contains Tamil Unicode characters."""
    # Tamil Unicode block: U+0B80 to U+0BFF
    if re.search(r'[\u0B80-\u0BFF]', text):
        return "ta"
    return "en"


def clean_script_text(text: str) -> str:
    """Strip emojis, markdown headers and clean punctuation for natural TTS delivery."""
    # Remove markdown asterisks, hashes
    text = re.sub(r'[*#_~`>]', '', text)
    # Remove emojis (keep Tamil and English alphanumeric characters and punctuation)
    text = re.sub(r'[^\w\s\u0B80-\u0BFF.,!?;:\'\"%$+-]', '', text)
    # Collapse multiple whitespaces and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def is_valid_script(data: Any) -> bool:
    """A model response is usable only if every part the pipeline reads is present."""
    return (
        isinstance(data, dict)
        and all(isinstance(data.get(k), str) and data[k].strip() for k in ("hook", "cta"))
        and isinstance(data.get("points"), list)
        and len(data["points"]) > 0
        and all(isinstance(p, str) and p.strip() for p in data["points"])
    )


def generate_with_gemini(topic: str, lang: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Generate viral short script using Google Gemini API with model fallbacks."""
    models = [m for m in [os.environ.get("GEMINI_MODEL")] if m] + [
        "gemini-3.8-flash",
        "gemini-flash-latest",
        "gemini-3.7-flash",
        "gemini-3.5-flash",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]
    
    if lang == "ta":
        system_instruction = (
            "You are an elite YouTube Shorts creator for Tamil audience. "
            "Write a high-retention 30-second viral script entirely in natural, conversational spoken Tamil (பேச்சுத் தமிழ்). "
            "STRICT RULES: "
            "1. Do NOT use stiff textbook/literary Tamil (e.g. use 'தோணுதா', 'செஞ்சிருக்காங்க', 'பாருங்க', 'உங்ககிட்ட' instead of 'தோன்றுகிறதா', 'செய்யப்பட்டுள்ளது'). "
            "2. Structure: "
            "   - Hook: A magnetic 3-second opening hook that sparks curiosity. "
            "   - Points: 3 punchy, rapid-fire sentences with high emotional momentum. "
            "   - CTA / Loop Outro: An INFINITE LOOP bridge sentence that seamlessly and grammatically flows right back into the opening hook without saying generic 'subscribe' slogans. "
            "Output JSON with keys: title, hook, points (array of 3 strings), cta, tags (array of 5 hashtags)."
        )
    else:
        system_instruction = (
            "You are an elite YouTube Shorts creator. "
            "Write a high-retention 30-second viral script in natural, conversational English. "
            "STRICT RULES: "
            "1. Punchy, rapid-paced delivery suitable for 1-2 word kinetic captions. "
            "2. Structure: "
            "   - Hook: A magnetic 3-second opening question or statement. "
            "   - Points: 3 rapid-fire, high-retention sentences. "
            "   - CTA / Loop Outro: An INFINITE LOOP bridge sentence that seamlessly and grammatically flows right back into the opening hook (creating an endless looping video). "
            "Output JSON with keys: title, hook, points (array of 3 strings), cta, tags (array of 5 hashtags)."
        )

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_instruction}\n{RETENTION_RULES}\nTopic: {topic}\nRespond ONLY with valid JSON."}
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.7
            }
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "x-goog-api-key": api_key}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                candidate = res_data["candidates"][0]["content"]["parts"][0]["text"]
                data = json.loads(candidate)
                if is_valid_script(data):
                    return data
        except Exception:
            continue
    return None


def generate_with_groq(topic: str, lang: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Generate viral short script using ultra-fast Groq Llama 3 API."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    if lang == "ta":
        sys_msg = (
            "You are an elite YouTube Shorts creator for Tamil audience. "
            "Write a high-retention 30-second viral script in natural conversational spoken Tamil (பேச்சுத் தமிழ், no stiff textbook grammar). "
            "The final 'cta' MUST be an infinite loop bridge sentence flowing back into the opening hook. "
            "Respond ONLY with a JSON object containing keys: title, hook, points (list of 3 strings), cta, tags (list of 5 hashtags)."
        )
    else:
        sys_msg = (
            "You are an elite YouTube Shorts creator. "
            "Write a high-retention 30-second viral script in natural, kinetic conversational English. "
            "The final 'cta' MUST be an infinite loop bridge sentence flowing back into the opening hook. "
            "Respond ONLY with a JSON object containing keys: title, hook, points (list of 3 strings), cta, tags (list of 5 hashtags)."
        )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": f"{sys_msg} {RETENTION_RULES}"},
            {"role": "user", "content": f"Topic: {topic}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            content = res_data["choices"][0]["message"]["content"]
            data = json.loads(content)
            return data if is_valid_script(data) else None
    except Exception as e:
        print(f"[Warning] Groq API request failed: {e}")
        return None


def get_procedural_template(topic: str, lang: str) -> Dict[str, Any]:
    """Find the best matching template or return a general high-retention script."""
    category = "space"
    if has_term(topic, ["motivation", "motivational", "mindset", "success", "discipline", "வெற்றி", "முயற்சி", "விடாமுயற்சி", "உழைப்பு", "தோல்வி", "நம்பிக்கை", "சிகரம்"]):
        category = "motivation"
    elif has_term(topic, ["tamil", "தமிழ்", "language", "மொழி", "செம்மொழி", "தமிழன்", "இலக்கியம்", "சிறப்பு"]):
        category = "tamil"
    elif has_term(topic, ["space", "universe", "planet", "black hole", "galaxy", "விண்வெளி", "கிரகம்", "நிலவு", "சூரியன்"]):
        category = "space"
    elif has_term(topic, ["psychology", "brain", "mind", "human", "behavior", "உளவியல்", "மனசு", "மூளை", "பயம்"]):
        category = "psychology"
    elif has_term(topic, ["history", "ancient", "temple", "pyramid", "war", "வரலாறு", "கோயில்", "சோழர்", "பழமை"]):
        category = "history"
    elif has_term(topic, ["tech", "ai", "robot", "computer", "future", "ஏஐ", "தொழில்நுட்பம்", "ரோபோ", "கணினி"]):
        category = "technology"
    elif has_term(topic, ["money", "rich", "wealth", "business", "habit", "பணம்", "கோடீஸ்வரன்", "முதலீடு"]):
        category = "wealth"
        
    template = VIRAL_TEMPLATES.get(category, VIRAL_TEMPLATES["space"])[lang]
    return {
        "title": template["title"],
        "hook": template["hook"],
        "points": template["points"],
        "cta": template["cta"],
        "tags": template["tags"]
    }


def split_into_rhythmic_sentences(text: str) -> List[str]:
    """Splits text into impactful sentence beats, merging tiny fragments so each beat has sufficient duration."""
    raw = [s.strip() for s in re.split(r'[.!?\n]+', text) if s.strip()]
    merged = []
    curr = ""
    for s in raw:
        if curr:
            curr = f"{curr} {s}"
        else:
            curr = s
        if len(curr.split()) >= 4:
            merged.append(curr.strip())
            curr = ""
    if curr:
        if merged:
            merged[-1] = f"{merged[-1]} {curr}"
        else:
            merged.append(curr)
    return merged or [text.strip()]


def prepare_script(
    topic: Optional[str] = None,
    custom_script: Optional[str] = None,
    script_file: Optional[str] = None,
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Prepare complete script package for TTS and video assembly.
    Returns:
        dict with title, full_text, sentences, tags, language
    """
    # 1. Custom Script from File or Argument
    if script_file and os.path.isfile(script_file):
        with open(script_file, "r", encoding="utf-8") as f:
            raw_text = f.read().strip()
        detected = detect_language(raw_text)
        cleaned = clean_script_text(raw_text)
        sentences = split_into_rhythmic_sentences(cleaned)
        return {
            "title": topic or ("Tamil Short" if detected == "ta" else "Viral Short"),
            "full_text": cleaned,
            "sentences": sentences,
            "tags": ["#shorts", "#viral", "#tamil" if detected == "ta" else "#english"],
            "language": detected
        }

    if custom_script:
        detected = detect_language(custom_script)
        cleaned = clean_script_text(custom_script)
        sentences = split_into_rhythmic_sentences(cleaned)
        return {
            "title": topic or ("Tamil Short" if detected == "ta" else "Viral Short"),
            "full_text": cleaned,
            "sentences": sentences,
            "tags": ["#shorts", "#viral", "#tamil" if detected == "ta" else "#english"],
            "language": detected
        }

    # 2. Automated Generation via Topic
    active_topic = topic or ("5 Mind-Blowing Facts" if lang == "en" else "வியக்கவைக்கும் 5 விசித்திர உண்மைகள்")
    if not lang:
        lang = detect_language(active_topic)

    groq_key = os.environ.get("GROQ_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    data = None

    if groq_key:
        data = generate_with_groq(active_topic, lang, groq_key)
    if not data and gemini_key:
        data = generate_with_gemini(active_topic, lang, gemini_key)

    if not data:
        print(
            f"[Warning] No AI script available (set GEMINI_API_KEY or GROQ_API_KEY). "
            f"Using a stock template that may not match the topic: {active_topic}"
        )
        data = get_procedural_template(active_topic, lang)

    # Assemble sentences with rhythmic flow
    all_sentences = [clean_script_text(s) for s in [data["hook"], *data["points"], data["cta"]]]
    title = data.get("title", active_topic)
    visuals = data.get("visuals")

    return {
        "title": title,
        "full_text": " ".join(all_sentences),
        "sentences": all_sentences,
        "tags": data.get("tags", ["#shorts", "#viral"]),
        "language": lang,
        "screen_hook": clean_script_text(data.get("screen_hook") or title),
        "visuals": visuals if isinstance(visuals, list) and all(isinstance(v, str) for v in visuals) else None
    }
