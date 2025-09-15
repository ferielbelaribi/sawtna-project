from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from groq import Groq
import re
from typing import Optional
from ..database import get_db
from .auth import get_current_user
from .. import schemas

router = APIRouter(prefix="/generate", tags=["text_generation"])

# Groq client
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# Request body schema
class TextRequest(BaseModel):
    text: str

# Sensitive words dictionaries
SENSITIVE_ARABIC_WORDS = {
    "الإبادة الجماعية": "الإبـ ـادة الجمـ ـاعية",
    "إسرائيل": "إسـ ـرائيل",
    "إسرائيلية": "إسـ ـرائيلية",
    "إسرائيلي": "إسـ ـرائيلي",
    "صهيوني": "صهـ ـيوني",
    "صهيونية": "صهـ ـيونية",
    "احتلال": "احتـ ـلال",
    "مجزرة": "مـ ـجزرة",
    "قوات الاحتلال": "قـ ـوات الاحتـ ـلال",
    "الجيش الإسرائيلي": "الجـ ـيش الإسـ ـرائيلي",
    "جرائم الحرب": "جرـ ـائم الحرب",
    "التطهير العرقي": "التطهـ ـير العرقي"
}

SENSITIVE_ENGLISH_WORDS = {
    "genocide": "ɢęиσƈιđę",
    "Israel": "Įşŕǻęł",
    "Israeli": "Įşŕǻęłı",
    "Zionist": "Źıøиıŝŧ",
    "Zionism": "Źıøиıŝŧıƈ",
    "occupation": "Øƈƈųƥǻŧıøи",
    "massacre": "Mǻššǻƈŕę",
    "war crimes": "Ŵǻř ƈŕıɱęš",
    "ethnic cleansing": "ęŧħиıƈ ƈłęǻиšıиɠ",
    "apartheid": "ǻƥǻřŧħęıđ",
    "settlers": "šęŧŧłęřš",
    "colonization": "ƈøłøиıżǻŧıøи"
}

# Language detection function
def detect_language(text: str) -> str:
    clean_text = re.sub(r'[^\w\s]', '', text)
    clean_text = re.sub(r'\d+', '', clean_text)
    if not clean_text.strip():
        return "en"

    arabic_chars = re.findall(r'[\u0600-\u06FF]', clean_text)
    arabic_ratio = len(arabic_chars) / len(clean_text) if clean_text else 0

    arabic_words = ["ال", "في", "من", "على", "أن", "إن", "إلى", "هذا", "هذه", "كان", "يكون"]
    arabic_word_count = sum(1 for word in arabic_words if word in clean_text)

    english_words = ["the", "and", "of", "to", "a", "in", "is", "it", "you", "that", "for"]
    english_word_count = sum(1 for word in english_words if word.lower() in clean_text.lower())

    if arabic_ratio > 0.3 or arabic_word_count > 2:
        return "ar"
    elif english_word_count > 2 and arabic_ratio == 0:
        return "en"
    else:
        return "en"

# Function to find a working model
def find_working_model():
    model_priority = [
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "llama3-8b-8192",
        "llama3-70b-8192"
    ]
    for model in model_priority:
        try:
            client.models.retrieve(model)
            return model
        except:
            continue
    return "llama-3.1-8b-instant"

# Prompt helpers
def create_arabic_prompt(input_text: str) -> str:
    return f"""أنت مساعد ذكي ومحايد. أعد صياغة النص التالي ليصبح مناسبًا للتواصل الاجتماعي:

المتطلبات:
1. حافظ على المعنى الأساسي ولكن بلغة محايدة وموضوعية
2. استخدم لغة دبلوماسية ومهنية
3. تجنب أي لغة عاطفية أو تحريضية
4. اكتب النص المعاد صياغته فقط بدون أي تعليقات إضافية
5. استخدم جملة أو جملتين كحد أقصى

النص الأصلي:
{input_text}

النص المعاد صياغته:"""

def create_english_prompt(input_text: str) -> str:
    return f"""You are an intelligent and neutral assistant. Rewrite the following text to make it suitable for social media:

Requirements:
1. Focus on maintain the core meaning but use neutral and objective language
2. Use diplomatic and professional language
3. Avoid any emotional or inflammatory language
4. Write only the rewritten text without any additional comments
5. Use 1-2 sentences maximum

Original text:
{input_text}

Rewritten text:"""

# Sanitize helper
def sanitize_text_groq(input_text: str) -> str:
    lang = detect_language(input_text)
    model_name = find_working_model()
    prompt = create_arabic_prompt(input_text) if lang == "ar" else create_english_prompt(input_text)

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3,
            top_p=0.9
        )
        generated_text = completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq generation failed: {e}")

    # Clean output
    cleaned_text = generated_text.strip()
    prefixes_to_remove = [
        "النص المعاد صياغته:", "النص الجديد:", "هذا النص المعاد صياغته:",
        "إليك النص المعاد صياغته:", "Rewritten text:", "New text:",
        "Here is the rewritten text:", "The rewritten text is:"
    ]
    for prefix in prefixes_to_remove:
        if cleaned_text.startswith(prefix):
            cleaned_text = cleaned_text[len(prefix):].strip()

    result = cleaned_text

    if lang == "ar":
        if result and len(result) > 10:
            for word, masked in SENSITIVE_ARABIC_WORDS.items():
                result = result.replace(word, masked)
        else:
            result = input_text
            for word, masked in SENSITIVE_ARABIC_WORDS.items():
                result = result.replace(word, masked)
    else:
        for word, masked in SENSITIVE_ENGLISH_WORDS.items():
            result = result.replace(word, masked)

    return result

# Route
@router.post("/neutralize")
def neutralize_text(
    request: TextRequest,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    sanitized_text = sanitize_text_groq(request.text)

    content_data = schemas.ContentCreate(
        user_id=current_user.id,
        content_type="text",  # hardcoded since we removed it from request
        title="Generated Text",
        text=sanitized_text,
        content_metadata={
            "original_text": request.text,
            "type": "neutralized"
        }
    )

    from .. import crud
    db_content = crud.create_content(db, content_data)

    if not db_content:
        raise HTTPException(
            status_code=400,
            detail="Error saving generated content"
        )

    return {"result": sanitized_text, "content_id": db_content.id}
