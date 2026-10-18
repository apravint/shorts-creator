"""
Screenplay & Storyboarding Engine for Animated Films.
Generates structured multi-scene screenplays with cinematic visual prompts,
dramatic voiceover narration, camera choreography, and atmospheric FX.
Supports English and Tamil (தமிழ்).
"""

import os
import re
import json
import urllib.request
from typing import Dict, Any, List, Optional

ANIMATION_STYLES = {
    "anime_shinkai": {
        "name": "Makoto Shinkai Anime",
        "prompt_suffix": "masterpiece anime film screenshot, Makoto Shinkai style, breathtaking sky, cinematic volumetric lighting, hyperdetailed, 8k, emotional, vibrant colors"
    },
    "studio_ghibli": {
        "name": "Studio Ghibli Hand-Drawn",
        "prompt_suffix": "masterpiece anime movie, Studio Ghibli style, Hayao Miyazaki aesthetic, lush hand-painted environment, warm nostalgic watercolor feel, 8k"
    },
    "cyberpunk": {
        "name": "Neo Cyberpunk Anime",
        "prompt_suffix": "cinematic futuristic cyberpunk anime film still, neon rain, holographic reflections, Akira and Ghost in the Shell style, high contrast, cinematic 8k"
    },
    "pixar_3d": {
        "name": "3D Feature Animation (Pixar/Disney)",
        "prompt_suffix": "3D animated feature film still, Pixar Disney style, expressive characters, subsurface scattering, cinematic lighting, cute and epic, 8k render"
    },
    "dark_fantasy": {
        "name": "Dark Fantasy Anime",
        "prompt_suffix": "cinematic dark fantasy anime, Elden Ring and Berserk style, brooding atmosphere, ancient ruins, dramatic chiaroscuro lighting, epic concept art"
    },
    "tamil_epic": {
        "name": "Tamil Historical Epic (Chola/Pandya)",
        "prompt_suffix": "grand Indian historical anime film still, ancient Tamil Chola architecture, temple gopuram, majestic royal warriors, cinematic sunrise lighting, epic Baahubali aesthetic"
    }
}

PREBUILT_MOVIES = {
    "cyberpunk": {
        "en": {
            "title": "Echoes of Neo Tokyo",
            "scenes": [
                {
                    "scene_num": 1,
                    "setting": "Rainy neon-drenched rooftop overlooking Neo-Tokyo skyscrapers at midnight",
                    "visual_prompt": "A lone female cyber-detective standing on a wet neon rooftop in futuristic Tokyo under rain, glowing cyan visor, towering holograms, cinematic anime movie screenshot, 8k",
                    "narration": "In the year 2099, memories were no longer human. They were currency, traded in the shadows of Neo Tokyo.",
                    "camera": "zoom_in",
                    "particles": "rain"
                },
                {
                    "scene_num": 2,
                    "setting": "A dimly lit high-tech alleyway with flickering holographic advertisements",
                    "visual_prompt": "Dark cyberpunk alley with flickering purple neon signs, a rogue mechanical android escaping down a wet street, steam rising from grates, anime film still, 8k",
                    "narration": "Deep within sector seven, a rogue prototype awakened with a stolen human soul.",
                    "camera": "pan_left",
                    "particles": "rain"
                },
                {
                    "scene_num": 3,
                    "setting": "Ancient server room hidden beneath a traditional Japanese temple",
                    "visual_prompt": "Ancient cyberpunk server vault glowing with golden fiber-optic cables beneath a traditional torii gate, mystical tech fusion, cinematic anime, 8k",
                    "narration": "The secret it carried was terrifying: Earth had not been abandoned. It was merely sleeping.",
                    "camera": "zoom_out",
                    "particles": "stars"
                },
                {
                    "scene_num": 4,
                    "setting": "Sunrise breaking over the cybernetic metropolis as the detective looks into the horizon",
                    "visual_prompt": "Female cyber detective standing against a breathtaking golden sunrise over futuristic Neo Tokyo, wind blowing her hair, hopeful cinematic ending, Makoto Shinkai style, 8k",
                    "narration": "Now, the revolution begins not with a weapon, but with the truth.",
                    "camera": "zoom_in",
                    "particles": "embers"
                }
            ]
        },
        "ta": {
            "title": "நியோ டோக்கியோவின் ரகசியம்",
            "scenes": [
                {
                    "scene_num": 1,
                    "setting": "மழையில் நனையும் நியோ-டோக்கியோ எதிர்கால நகரம்",
                    "visual_prompt": "A lone female cyber-detective standing on a wet neon rooftop in futuristic Tokyo under rain, glowing cyan visor, towering holograms, cinematic anime movie screenshot, 8k",
                    "narration": "வருடம் 2099. நியோ டோக்கியோவின் நள்ளிரவு வானத்தில் மனித நினைவுகள் நிழல் சந்தைகளில் விற்கப்பட்டன.",
                    "camera": "zoom_in",
                    "particles": "rain"
                },
                {
                    "scene_num": 2,
                    "setting": "இருண்ட தொழில்நுட்ப சந்து",
                    "visual_prompt": "Dark cyberpunk alley with flickering purple neon signs, a rogue mechanical android escaping down a wet street, steam rising from grates, anime film still, 8k",
                    "narration": "ஏழாவது மண்டலத்தின் ஆழத்தில், ஒரு விசித்திரமான ரோபோ மனித உணர்வுகளுடன் விழித்துக்கொண்டது.",
                    "camera": "pan_left",
                    "particles": "rain"
                },
                {
                    "scene_num": 3,
                    "setting": "பழங்கால தொழில்நுட்ப ரகசிய அறை",
                    "visual_prompt": "Ancient cyberpunk server vault glowing with golden fiber-optic cables beneath a traditional torii gate, mystical tech fusion, cinematic anime, 8k",
                    "narration": "அது மறைத்து வைத்திருந்த ரகசியம் ஒட்டுமொத்த மனிதகுலத்தின் தலையெழுத்தையே மாற்றக்கூடியது.",
                    "camera": "zoom_out",
                    "particles": "stars"
                },
                {
                    "scene_num": 4,
                    "setting": "எதிர்கால நகரத்தின் மீது விடியல் உதயமாகிறது",
                    "visual_prompt": "Female cyber detective standing against a breathtaking golden sunrise over futuristic Neo Tokyo, wind blowing her hair, hopeful cinematic ending, Makoto Shinkai style, 8k",
                    "narration": "இப்போது உண்மை வெளிச்சத்திற்கு வந்துவிட்டது. புதிய யுகம் தொடங்குகிறது.",
                    "camera": "zoom_in",
                    "particles": "embers"
                }
            ]
        }
    },
    "tamil_epic": {
        "en": {
            "title": "Wrath of the Ocean King",
            "scenes": [
                {
                    "scene_num": 1,
                    "setting": "Grand Thanjavur temple illuminated by golden sunset torches",
                    "visual_prompt": "Ancient majestic Thanjavur Brihadisvara temple carved from golden stone, hundreds of flickering oil lamps, royal banners fluttering, anime film still, 8k",
                    "narration": "A thousand years ago, the great Chola fleet commanded the boundless oceans of the East.",
                    "camera": "zoom_in",
                    "particles": "embers"
                },
                {
                    "scene_num": 2,
                    "setting": "Fleet of massive wooden war galleons cutting through stormy ocean waves",
                    "visual_prompt": "Armada of ancient Tamil royal warships with tiger flags sailing through dramatic stormy sea waves, lightning flashing, epic anime movie screenshot, 8k",
                    "narration": "Their ships feared no tempest, carrying the valor of the roaring Tiger banner across distant kingdoms.",
                    "camera": "pan_right",
                    "particles": "rain"
                },
                {
                    "scene_num": 3,
                    "setting": "The supreme warrior general raising a bronze spear towards the stormy sky",
                    "visual_prompt": "Chola warrior prince standing on the bow of a warship, bronze armor, traditional royal sword raised high, lightning striking behind him, epic anime, 8k",
                    "narration": "For every wave that crashed against their armor only fueled the fire in their warrior blood.",
                    "camera": "zoom_in",
                    "particles": "embers"
                },
                {
                    "scene_num": 4,
                    "setting": "Golden sunrise over the victorious empire and peaceful waters",
                    "visual_prompt": "Majestic coastal empire fortress with golden morning sunlight reflecting on calm blue ocean, royal ships returning victorious, Makoto Shinkai anime style, 8k",
                    "narration": "Their legacy was written not in sand, but etched forever in stone and glory.",
                    "camera": "zoom_out",
                    "particles": "stars"
                }
            ]
        },
        "ta": {
            "title": "கடல் வேந்தனின் கர்ஜனை",
            "scenes": [
                {
                    "scene_num": 1,
                    "setting": "தஞ்சை பெரிய கோயிலின் பிரம்மாண்ட பொன்னான மாலை நேரம்",
                    "visual_prompt": "Ancient majestic Thanjavur Brihadisvara temple carved from golden stone, hundreds of flickering oil lamps, royal banners fluttering, anime film still, 8k",
                    "narration": "ஆயிரம் ஆண்டுகளுக்கு முன்பு, மாமன்னர் சோழரின் கலம் பாயும் கடற்படை கீழ்த்திசை கடல்களை தன் ஆளுகையில் வைத்திருந்தது.",
                    "camera": "zoom_in",
                    "particles": "embers"
                },
                {
                    "scene_num": 2,
                    "setting": "புயல் காற்றில் சீறும் சோழர் போர்க்கப்பல்கள்",
                    "visual_prompt": "Armada of ancient Tamil royal warships with tiger flags sailing through dramatic stormy sea waves, lightning flashing, epic anime movie screenshot, 8k",
                    "narration": "புலிக்கொடி ஏந்திய அவர்களின் நாவாய்கள் எத்தகைய கடற் புயலையும் அஞ்சாமல் கிழித்துக்கொண்டு பாய்ந்தன.",
                    "camera": "pan_right",
                    "particles": "rain"
                },
                {
                    "scene_num": 3,
                    "setting": "போர்க்கப்பலின் முகப்பில் வாளேந்திய சோழ இளவரசன்",
                    "visual_prompt": "Chola warrior prince standing on the bow of a warship, bronze armor, traditional royal sword raised high, lightning striking behind him, epic anime, 8k",
                    "narration": "அவர்கள் நெஞ்சில் எரிந்த வீரம், அலைகளின் சீற்றத்தை விட பன்மடங்கு சக்தி வாய்ந்ததாக இருந்தது.",
                    "camera": "zoom_in",
                    "particles": "embers"
                },
                {
                    "scene_num": 4,
                    "setting": "வெற்றி வாகை சூடிய சோழ சாம்ராஜ்யத்தின் பொற்காலை",
                    "visual_prompt": "Majestic coastal empire fortress with golden morning sunlight reflecting on calm blue ocean, royal ships returning victorious, Makoto Shinkai anime style, 8k",
                    "narration": "அவர்களின் புகழ் வரலாற்றில் அழியாத வைரக் கல்வெட்டாய் இன்றும் கம்பீரமாய் வாழ்கிறது.",
                    "camera": "zoom_out",
                    "particles": "stars"
                }
            ]
        }
    },
    "studio_ghibli": {
        "en": {
            "title": "The Whispering Star Forest",
            "scenes": [
                {
                    "scene_num": 1,
                    "setting": "Lush mossy ancient forest with giant glowing spirit mushrooms",
                    "visual_prompt": "Magical ancient green forest, giant glowing mushrooms, mossy ancient trees, soft mystical sunbeams breaking through canopy, Studio Ghibli anime style, 8k",
                    "narration": "Deep within the emerald valley lay a forest that only woke up when humans closed their eyes.",
                    "camera": "zoom_in",
                    "particles": "stars"
                },
                {
                    "scene_num": 2,
                    "setting": "A young girl discovering a tiny glowing celestial fox sleeping inside a hollow tree",
                    "visual_prompt": "Young anime girl with backpack finding a tiny glowing celestial spirit fox inside a mossy tree trunk, warm magical watercolor aesthetic, Studio Ghibli, 8k",
                    "narration": "A young traveler named Hana discovered a creature made entirely of fallen starlight.",
                    "camera": "zoom_in",
                    "particles": "stars"
                },
                {
                    "scene_num": 3,
                    "setting": "The spirit fox floating up and illuminating the entire ancient woods into a galaxy of light",
                    "visual_prompt": "Magical glowing spirit creature floating above a crystalline forest pond, thousands of glowing butterflies rising into night sky, Hayao Miyazaki aesthetic, 8k",
                    "narration": "With a gentle leap, it awakened the slumbering magic of the forgotten world.",
                    "camera": "zoom_out",
                    "particles": "stars"
                },
                {
                    "scene_num": 4,
                    "setting": "Hana standing on a grassy hill under a magnificent starry sky filled with shooting stars",
                    "visual_prompt": "Anime girl standing on a lush green cliff looking up at a breathtaking galaxy of shooting stars, warm breeze, Makoto Shinkai and Ghibli hybrid, 8k",
                    "narration": "And in that quiet moment, she knew she would never feel alone again.",
                    "camera": "zoom_in",
                    "particles": "stars"
                }
            ]
        },
        "ta": {
            "title": "மந்திர விண்மீன் காடு",
            "scenes": [
                {
                    "scene_num": 1,
                    "setting": "மந்திர சக்தி நிறைந்த பசுமையான அடர்ந்த காடு",
                    "visual_prompt": "Magical ancient green forest, giant glowing mushrooms, mossy ancient trees, soft mystical sunbeams breaking through canopy, Studio Ghibli anime style, 8k",
                    "narration": "பசுமையான மலைகளுக்கு நடுவே, மனிதர்கள் உறங்கும்போது மட்டுமே விழித்தெழும் ஒரு மாயக் காடு இருந்தது.",
                    "camera": "zoom_in",
                    "particles": "stars"
                },
                {
                    "scene_num": 2,
                    "setting": "மரப்பொந்தில் மின்னும் குட்டி தேவ தேவதை நரி",
                    "visual_prompt": "Young anime girl with backpack finding a tiny glowing celestial spirit fox inside a mossy tree trunk, warm magical watercolor aesthetic, Studio Ghibli, 8k",
                    "narration": "அங்கு வந்த ஒரு சிறுமி, வானத்திலிருந்து உதிர்ந்த நட்சத்திரத்தால் உருவான ஒரு விசித்திர உயிரினத்தைக் கண்டாள்.",
                    "camera": "zoom_in",
                    "particles": "stars"
                },
                {
                    "scene_num": 3,
                    "setting": "காடெங்கும் ஒளிவெள்ளம் பாய்கிறது",
                    "visual_prompt": "Magical glowing spirit creature floating above a crystalline forest pond, thousands of glowing butterflies rising into night sky, Hayao Miyazaki aesthetic, 8k",
                    "narration": "அது காற்றில் மிதந்த நொடியில், காடு முழுவதும் ஆயிரம் மின்னும் வண்ணங்களால் ஒளிர்ந்தது.",
                    "camera": "zoom_out",
                    "particles": "stars"
                },
                {
                    "scene_num": 4,
                    "setting": "இரவு வானத்து விண்மீன்களைப் பார்த்து புன்னகைக்கும் சிறுமி",
                    "visual_prompt": "Anime girl standing on a lush green cliff looking up at a breathtaking galaxy of shooting stars, warm breeze, Makoto Shinkai and Ghibli hybrid, 8k",
                    "narration": "அந்த அமைதியான இரவில், இயற்கை அவளுக்கு புதிய வாழ்வின் ரகசியத்தை கற்றுக்கொடுத்தது.",
                    "camera": "zoom_in",
                    "particles": "stars"
                }
            ]
        }
    }
}


def generate_screenplay_ai(
    prompt: str,
    lang: str = "en",
    style_key: str = "anime_shinkai",
    num_scenes: int = 4
) -> Optional[Dict[str, Any]]:
    """Generate dynamic multi-scene screenplay using Groq or Gemini."""
    groq_key = os.environ.get("GROQ_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    style_info = ANIMATION_STYLES.get(style_key, ANIMATION_STYLES["anime_shinkai"])

    system_msg = (
        f"You are a master anime film director and cinematic screenwriter. "
        f"Create an unforgettable animated movie screenplay with exactly {num_scenes} continuous storytelling scenes based on the user's prompt. "
        f"Language requirement: {'Tamil (தமிழ்) script ONLY' if lang == 'ta' else 'English ONLY'}. "
        f"Animation visual style: {style_info['name']}. "
        f"Output JSON with:\n"
        f"- 'title': Movie title\n"
        f"- 'genre': Movie genre\n"
        f"- 'scenes': Array of {num_scenes} objects, each with:\n"
        f"   - 'scene_num': integer\n"
        f"   - 'setting': concise setting description\n"
        f"   - 'visual_prompt': Highly descriptive English text-to-image prompt tailored for {style_info['name']} (describe subjects, lighting, colors, emotions, cinematic angle)\n"
        f"   - 'narration': 1-2 sentence dramatic cinematic narration for the scene ({'in Tamil' if lang == 'ta' else 'in English'})\n"
        f"   - 'camera': 'zoom_in' | 'zoom_out' | 'pan_left' | 'pan_right'\n"
        f"   - 'particles': 'rain' | 'embers' | 'stars' | 'none'\n"
        f"Respond ONLY with valid JSON."
    )

    # 1. Try Groq
    if groq_key:
        try:
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=json.dumps({
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": f"Movie Prompt: {prompt}"}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.75
                }).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception:
            pass

    # 2. Try Gemini
    if gemini_key:
        for model in ["gemini-3.8-flash", "gemini-flash-latest", "gemini-3.7-flash", "gemini-3.5-flash", "gemini-2.5-flash", "gemini-1.5-flash"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
                req = urllib.request.Request(
                    url,
                    data=json.dumps({
                        "contents": [{"parts": [{"text": f"{system_msg}\nPrompt: {prompt}"}]}],
                        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7}
                    }).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=14) as resp:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    cand = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(cand)
            except Exception:
                continue

    return None


def get_screenplay(
    prompt: Optional[str] = None,
    lang: str = "en",
    style_key: str = "anime_shinkai",
    num_scenes: int = 4
) -> Dict[str, Any]:
    """
    Get screenplay: via AI generation if keys exist or prompt given,
    falling back to curated prebuilt cinematic screenplays.
    """
    if prompt:
        ai_data = generate_screenplay_ai(prompt, lang=lang, style_key=style_key, num_scenes=num_scenes)
        if ai_data and "scenes" in ai_data and len(ai_data["scenes"]) > 0:
            return ai_data

    # Match prebuilt by keywords or style
    prompt_lower = (prompt or "").lower()
    if any(k in prompt_lower for k in ["tamil", "தமிழ்", "chola", "சோழர்", "warrior", "temple", "கோயில்", "கடல்"]):
        cat = "tamil_epic"
    elif any(k in prompt_lower for k in ["forest", "magic", "ghibli", "nature", "காடு", "மந்திரம்", "விலங்கு"]):
        cat = "studio_ghibli"
    else:
        cat = "cyberpunk"

    prebuilt = PREBUILT_MOVIES.get(cat, PREBUILT_MOVIES["cyberpunk"]).get(lang, PREBUILT_MOVIES["cyberpunk"]["en"])
    return {
        "title": prebuilt["title"],
        "genre": cat,
        "scenes": prebuilt["scenes"][:num_scenes]
    }
