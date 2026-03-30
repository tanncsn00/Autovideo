"""Pre-made prompt templates for AI script generation.

Users select a prompt style → LLM generates script in that style.
"""

from dataclasses import dataclass


@dataclass
class PromptTemplate:
    id: str
    name: str
    description: str
    category: str  # hook, storytelling, educational, marketing, viral
    prompt_prefix: str  # Added BEFORE the user's topic
    prompt_suffix: str  # Added AFTER the user's topic
    language: str  # "en", "vi", "any"
    example: str  # Example output


# Built-in prompt templates
PROMPT_TEMPLATES = [
    # === HOOKS (Attention grabbers) ===
    PromptTemplate(
        id="hook-controversial",
        name="Controversial Hook",
        description="Start with a bold, controversial statement to grab attention",
        category="hook",
        prompt_prefix="""Write a video script that starts with a BOLD, CONTROVERSIAL hook statement that makes viewers stop scrolling.
The hook should challenge common beliefs or present a surprising fact.
Structure: [Hook - 1 sentence] → [Explain why - 2-3 sentences] → [Evidence/Story - 3-4 sentences] → [Call to action - 1 sentence]""",
        prompt_suffix="Make the hook irresistible. The first sentence MUST make people say 'Wait, what?!'",
        language="any",
        example="Most people think waking up at 5am makes you successful. They're wrong..."
    ),
    PromptTemplate(
        id="hook-question",
        name="Question Hook",
        description="Start with a compelling question that viewers NEED answered",
        category="hook",
        prompt_prefix="""Write a video script that opens with a COMPELLING QUESTION the viewer desperately wants answered.
Structure: [Question hook] → [Tease the answer] → [Build tension] → [Reveal the answer] → [Key takeaway]""",
        prompt_suffix="The question must be specific and intriguing, not generic.",
        language="any",
        example="What if I told you there's a FREE tool that can replace 90% of your video editing workflow?"
    ),
    PromptTemplate(
        id="hook-story",
        name="Story Hook",
        description="Start with 'I was...' or 'Last week...' — personal story format",
        category="hook",
        prompt_prefix="""Write a video script using the STORY HOOK format.
Start with a personal or relatable story that draws the viewer in emotionally.
Structure: [Story opening - set the scene] → [The problem/conflict] → [The turning point] → [The lesson/solution] → [Call to action]
Use conversational, first-person language.""",
        prompt_suffix="Make it feel authentic and relatable. Short sentences. Emotional.",
        language="any",
        example="Last month, I lost $5,000 because of one stupid mistake..."
    ),
    PromptTemplate(
        id="hook-number",
        name="Number/List Hook",
        description="'5 things...', '3 reasons...' — list format that performs well",
        category="hook",
        prompt_prefix="""Write a video script in LIST FORMAT (numbered items).
Start with a hook like '5 things nobody tells you about...' or '3 reasons why...'
Each point should be concise, surprising, and valuable.
Structure: [Hook with number] → [Point 1 + brief explanation] → [Point 2] → ... → [Strongest point last] → [Summary]""",
        prompt_suffix="Each point should be 1-2 sentences max. Fast-paced. Punchy.",
        language="any",
        example="7 websites that will make you smarter than 99% of people..."
    ),

    # === STORYTELLING ===
    PromptTemplate(
        id="story-dramatic",
        name="Dramatic Narrative",
        description="Cinematic storytelling with tension, conflict, and resolution",
        category="storytelling",
        prompt_prefix="""Write a DRAMATIC narrative script for a video. Use cinematic language.
Build tension throughout. Create vivid imagery with words.
Structure: [Opening scene] → [Rising tension] → [Climax] → [Resolution] → [Reflection]
Use present tense for immediacy. Short, punchy sentences for impact.""",
        prompt_suffix="Make it feel like a movie trailer. Every sentence should create a visual image.",
        language="any",
        example="The year is 2025. A small team of engineers is about to change everything..."
    ),
    PromptTemplate(
        id="story-emotional",
        name="Emotional Story",
        description="Touching, emotional narrative that connects with viewers",
        category="storytelling",
        prompt_prefix="""Write an EMOTIONAL story script that touches the viewer's heart.
Use vulnerability, authenticity, and universal human experiences.
Structure: [Emotional opening] → [The struggle] → [The moment of change] → [The transformation] → [Inspirational ending]""",
        prompt_suffix="Make viewers feel something. Use sensory details. Be genuine.",
        language="any",
        example="She was told she'd never walk again. But she had a different plan..."
    ),

    # === EDUCATIONAL ===
    PromptTemplate(
        id="edu-explainer",
        name="Simple Explainer",
        description="Explain complex topics simply — 'Explain like I'm 5'",
        category="educational",
        prompt_prefix="""Write an EXPLAINER script that makes a complex topic simple and engaging.
Use analogies, examples, and everyday language. No jargon.
Structure: [What is it? - simple definition] → [Why does it matter?] → [How does it work? - with analogy] → [Real-world example] → [Key takeaway]
Imagine explaining to a smart 15-year-old.""",
        prompt_suffix="Use at least one analogy. Keep it conversational, not academic.",
        language="any",
        example="Imagine your brain is a computer. AI is like teaching that computer to learn on its own..."
    ),
    PromptTemplate(
        id="edu-myth-busting",
        name="Myth Busting",
        description="'You've been told X. Here's the truth.' — debunking format",
        category="educational",
        prompt_prefix="""Write a MYTH-BUSTING script that challenges common misconceptions.
Format: Present the myth → Show why people believe it → Reveal the truth with evidence → Explain the real story.
Be respectful but firm. Use facts and logic.""",
        prompt_suffix="Start with: 'You've probably heard that...' or 'Everyone thinks...'",
        language="any",
        example="You've been told that breakfast is the most important meal of the day. Here's what science actually says..."
    ),

    # === MARKETING ===
    PromptTemplate(
        id="marketing-product",
        name="Product Showcase",
        description="Professional product demo/review script",
        category="marketing",
        prompt_prefix="""Write a PRODUCT SHOWCASE script that highlights benefits (not features).
Structure: [Problem the viewer has] → [Introduce the solution] → [3 key benefits with examples] → [Social proof / results] → [Call to action]
Focus on how it improves the viewer's life, not technical specs.""",
        prompt_suffix="Make the viewer feel the PAIN of the problem first, then the RELIEF of the solution.",
        language="any",
        example="Tired of spending hours editing videos? What if you could create professional content in 5 minutes?"
    ),
    PromptTemplate(
        id="marketing-testimonial",
        name="Testimonial Story",
        description="Customer success story format",
        category="marketing",
        prompt_prefix="""Write a TESTIMONIAL/SUCCESS STORY script.
Format: [Who is this person? - relatable background] → [Their problem/struggle] → [How they found the solution] → [Specific results with numbers] → [Their life now] → [Recommendation]
Make it feel authentic, not salesy.""",
        prompt_suffix="Include specific numbers and timeframes. Make the transformation believable.",
        language="any",
        example="Sarah was working 60 hours a week creating content. Then she discovered..."
    ),

    # === VIRAL / TIKTOK ===
    PromptTemplate(
        id="viral-facts",
        name="Mind-Blowing Facts",
        description="Rapid-fire surprising facts that make people share",
        category="viral",
        prompt_prefix="""Write a RAPID-FIRE FACTS script with mind-blowing, shareable facts.
Each fact should make the viewer say 'No way!' or 'I need to tell someone this!'
Structure: [Attention-grabbing opening fact] → [4-5 more incredible facts] → [The most mind-blowing fact saved for last]
Keep each fact to 1-2 sentences. Fast pace.""",
        prompt_suffix="Every fact must be TRUE and verifiable. Make them surprising, not obvious.",
        language="any",
        example="Your brain uses the same amount of power as a 10-watt light bulb..."
    ),
    PromptTemplate(
        id="viral-motivation",
        name="Motivation / Hustle",
        description="Motivational content — discipline, success, mindset",
        category="viral",
        prompt_prefix="""Write a MOTIVATIONAL script that fires people up.
Use powerful, direct language. Short sentences. Commanding tone.
Structure: [Bold statement] → [The harsh truth] → [What winners do differently] → [Actionable advice] → [Powerful closing statement]
Think Gary Vee meets David Goggins.""",
        prompt_suffix="Make every sentence quotable. No fluff. Raw truth.",
        language="any",
        example="While you're sleeping, someone else is working. While you're complaining, someone else is winning."
    ),

    # === VIETNAMESE SPECIFIC ===
    PromptTemplate(
        id="vi-sam-truyen",
        name="Sam Truyen (Vietnamese Storytelling)",
        description="Giong sam truyen Viet Nam — dramatic, emotional",
        category="storytelling",
        prompt_prefix="""Viet mot doan sam truyen bang tieng Viet, giong doc tram am, day cam xuc.
Su dung ngon ngu giau hinh anh, co nhip dieu nhu doc truyen dem khuya.
Cau truc: [Mo dau gay to mo] → [Dien bien kich tinh] → [Cao trao] → [Ket thuc sau lang]
Dung tu ngu goi cam, cau ngan dai xen ke, tao nhip tho.""",
        prompt_suffix="Viet nhu dang ke chuyen cho nguoi nghe luc 2 gio sang. Cham rai, sau lang, cuon hut.",
        language="vi",
        example="Co mot nguoi dan ong, suot 30 nam, ngay nao cung di ngang qua con hem nho ay..."
    ),
    PromptTemplate(
        id="vi-review",
        name="Review San Pham (Tieng Viet)",
        description="Review san pham kieu YouTuber Viet — tu nhien, vui",
        category="marketing",
        prompt_prefix="""Viet script review san pham bang tieng Viet, giong noi tu nhien nhu dang noi chuyen voi ban be.
Dung ngon ngu binh dan, co pha chut hai huoc.
Cau truc: [Gioi thieu van de] → [San pham la gi] → [Trai nghiem thuc te] → [Uu nhuoc diem] → [Ket luan]""",
        prompt_suffix="Viet tu nhien, khong salesy. Nhu dang noi chuyen voi ban than.",
        language="vi",
        example="Ey yo, hom nay minh se test thu cai nay xem no co xin nhu quang cao khong nha..."
    ),
]


import json
import os
from pathlib import Path


def _custom_file() -> Path:
    """Path to custom prompt templates JSON file"""
    try:
        from app.config.config_v2 import get_config_dir
        return get_config_dir() / "custom_prompts.json"
    except Exception:
        return Path("custom_prompts.json")


def _load_custom() -> list[PromptTemplate]:
    """Load user-created custom prompt templates"""
    path = _custom_file()
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [PromptTemplate(**t) for t in data]
    except Exception:
        return []


def _save_custom(templates: list[PromptTemplate]):
    """Save custom prompt templates to JSON"""
    path = _custom_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "id": t.id, "name": t.name, "description": t.description,
            "category": t.category, "prompt_prefix": t.prompt_prefix,
            "prompt_suffix": t.prompt_suffix, "language": t.language,
            "example": t.example,
        }
        for t in templates
    ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_all_templates() -> list[dict]:
    """Return all prompt templates (built-in + custom) as dicts"""
    all_templates = list(PROMPT_TEMPLATES) + _load_custom()
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "category": t.category,
            "language": t.language,
            "example": t.example,
            "prompt_prefix": t.prompt_prefix,
            "prompt_suffix": t.prompt_suffix,
            "builtin": t in PROMPT_TEMPLATES,
        }
        for t in all_templates
    ]


def get_template(template_id: str) -> PromptTemplate | None:
    """Get a specific template by ID (checks both built-in and custom)"""
    for t in PROMPT_TEMPLATES:
        if t.id == template_id:
            return t
    for t in _load_custom():
        if t.id == template_id:
            return t
    return None


def save_custom_template(data: dict) -> str:
    """Save a new custom prompt template"""
    customs = _load_custom()
    template = PromptTemplate(
        id=data.get("id", f"custom-{len(customs) + 1}"),
        name=data.get("name", "Custom Template"),
        description=data.get("description", ""),
        category=data.get("category", "custom"),
        prompt_prefix=data.get("prompt_prefix", ""),
        prompt_suffix=data.get("prompt_suffix", ""),
        language=data.get("language", "any"),
        example=data.get("example", ""),
    )
    # Update if exists, else append
    found = False
    for i, t in enumerate(customs):
        if t.id == template.id:
            customs[i] = template
            found = True
            break
    if not found:
        customs.append(template)
    _save_custom(customs)
    return template.id


def delete_custom_template(template_id: str) -> bool:
    """Delete a custom prompt template (cannot delete built-in)"""
    for t in PROMPT_TEMPLATES:
        if t.id == template_id:
            return False  # Cannot delete built-in
    customs = _load_custom()
    new_customs = [t for t in customs if t.id != template_id]
    if len(new_customs) == len(customs):
        return False  # Not found
    _save_custom(new_customs)
    return True


def get_categories() -> list[str]:
    """Get all unique categories"""
    all_templates = list(PROMPT_TEMPLATES) + _load_custom()
    return sorted(set(t.category for t in all_templates))


def apply_prompt_template(template_id: str, topic: str, language: str = "") -> str:
    """Apply a prompt template to a topic, returning the full prompt for the LLM"""
    template = get_template(template_id)
    if not template:
        return ""

    prompt = f"""{template.prompt_prefix}

# Video Topic:
{topic}

{template.prompt_suffix}"""

    if language:
        prompt += f"\n\nIMPORTANT: Write the script in {language}."

    return prompt
