"""
Script Generator for YouTube Shorts.
Supports Gemini AI API, OpenAI API, custom user inputs, and procedural viral offline templates.
Full bilingual support: Tamil (தமிழ்) and English.
"""

import os
import re
import json
import urllib.request
from typing import Dict, Any, Optional
from shorts_creator.templates import VIRAL_TEMPLATES


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
    text = re.sub(r'[^\w\s\u0B80-\u0BFF.,!?;:\'\"-]', '', text)
    # Collapse multiple whitespaces and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def generate_with_gemini(topic: str, lang: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Generate viral short script using Google Gemini API with model fallbacks."""
    models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"]
    
    if lang == "ta":
        system_instruction = (
            "You are an expert YouTube Shorts creator for Tamil audience. "
            "Write a highly engaging 30-45 second viral script entirely in Tamil (தமிழ்). "
            "Structure: "
            "1. A powerful 3-second hook that creates curiosity. "
            "2. Three fascinating, rapid-fire points or facts. "
            "3. A call-to-action asking viewers to comment and subscribe. "
            "Output JSON with keys: title, hook, points (array of 3 strings), cta, tags (array of 5 hashtags)."
        )
    else:
        system_instruction = (
            "You are an expert YouTube Shorts creator. "
            "Write a high-retention 30-45 second viral script in English. "
            "Structure: "
            "1. A powerful 3-second hook that creates curiosity. "
            "2. Three punchy, fast-paced points or facts. "
            "3. A call-to-action asking viewers to comment and subscribe. "
            "Output JSON with keys: title, hook, points (array of 3 strings), cta, tags (array of 5 hashtags)."
        )

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_instruction}\nTopic: {topic}\nRespond ONLY with valid JSON."}
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
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                candidate = res_data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(candidate)
        except Exception:
            continue
    return None


def generate_with_groq(topic: str, lang: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Generate viral short script using ultra-fast Groq Llama 3 API."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    if lang == "ta":
        sys_msg = (
            "You are an expert YouTube Shorts creator for Tamil audience. "
            "Write a highly engaging 30-second viral script entirely in Tamil (தமிழ்). "
            "Respond ONLY with a JSON object containing keys: title, hook, points (list of 3 strings), cta, tags (list of 5 hashtags)."
        )
    else:
        sys_msg = (
            "You are an expert YouTube Shorts creator. "
            "Write a high-retention 30-second viral script in English. "
            "Respond ONLY with a JSON object containing keys: title, hook, points (list of 3 strings), cta, tags (list of 5 hashtags)."
        )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_msg},
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
            return json.loads(content)
    except Exception as e:
        print(f"[Warning] Groq API request failed: {e}")
        return None


def get_procedural_template(topic: str, lang: str) -> Dict[str, Any]:
    """Find the best matching template or return a general high-retention script."""
    topic_lower = topic.lower()
    
    category = "space"
    if any(k in topic_lower for k in ["tamil", "தமிழ்", "language", "மொழி", "செம்மொழி", "தமிழன்", "இலக்கியம்", "சிறப்பு"]):
        category = "tamil"
    elif any(k in topic_lower for k in ["space", "universe", "planet", "black hole", "galaxy", "விண்வெளி", "கிரகம்", "நிலவு", "சூரியன்"]):
        category = "space"
    elif any(k in topic_lower for k in ["psychology", "brain", "mind", "human", "behavior", "உளவியல்", "மனசு", "மூளை", "பயம்"]):
        category = "psychology"
    elif any(k in topic_lower for k in ["history", "ancient", "temple", "pyramid", "war", "வரலாறு", "கோயில்", "சோழர்", "பழமை"]):
        category = "history"
    elif any(k in topic_lower for k in ["tech", "ai", "robot", "computer", "future", "ஏஐ", "தொழில்நுட்பம்", "ரோபோ", "கணினி"]):
        category = "technology"
    elif any(k in topic_lower for k in ["money", "rich", "wealth", "business", "habit", "பணம்", "கோடீஸ்வரன்", "வெற்றி", "முதலீடு"]):
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
    gemini_key = os.environ.get("GEMINI_API_KEY")
    data = None

    if groq_key:
        data = generate_with_groq(active_topic, lang, groq_key)
    if not data and gemini_key:
        data = generate_with_gemini(active_topic, lang, gemini_key)

    if not data:
        data = get_procedural_template(active_topic, lang)

    # Assemble sentences with rhythmic flow
    all_sentences = [data["hook"]]
    for pt in data["points"]:
        all_sentences.append(pt)
    all_sentences.append(data["cta"])

    full_text = " ".join(all_sentences)
    full_text_cleaned = clean_script_text(full_text)

    return {
        "title": data.get("title", active_topic),
        "full_text": full_text_cleaned,
        "sentences": all_sentences,
        "tags": data.get("tags", ["#shorts", "#viral"]),
        "language": lang
    }
