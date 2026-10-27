"""Translation and regional language support module for Hindi and English."""
import re
import logging

logger = logging.getLogger(__name__)

# Regex to detect Devanagari script (Hindi, Marathi, etc.)
DEVANAGARI_REGEX = re.compile(r"[\u0900-\u097F]")


def contains_hindi(text: str) -> bool:
    """Checks if the string contains Devanagari characters."""
    if not text:
        return False
    return bool(DEVANAGARI_REGEX.search(text))


def detect_language(text: str) -> str:
    """
    Detects whether the text is primarily Hindi (Devanagari) or English.
    Returns 'hi' or 'en'.
    """
    if not text:
        return "en"
    hindi_chars = len(DEVANAGARI_REGEX.findall(text))
    # If more than 5 Devanagari characters or >10% of characters are Devanagari
    if hindi_chars >= 5 or (len(text) > 0 and (hindi_chars / len(text)) > 0.10):
        return "hi"
    return "en"


def translate_to_english(text: str, source_lang: str = "hi"):
    """
    Translates text to English using available translation providers.
    
    Processing Pipeline:
      1. Attempt MyMemoryTranslator (deep-translator) with 500-char chunks if needed.
      2. Fallback to GoogleTranslator (deep-translator).
      3. If all network translators fail, return clear error message.
      
    Returns a dict with:
      - success (bool)
      - translated_text (str)
      - original_text (str)
      - was_translated (bool)
      - error (str or None)
      - provider (str)
    """
    if not text or not text.strip():
        return {
            "success": False,
            "translated_text": "",
            "original_text": text,
            "was_translated": False,
            "error": "Input text is empty.",
            "provider": None
        }

    # If already English, return as-is
    if not contains_hindi(text) and source_lang == "en":
        return {
            "success": True,
            "translated_text": text,
            "original_text": text,
            "was_translated": False,
            "error": None,
            "provider": "direct_english"
        }

    cleaned_input = text.strip()
    
    # Provider 1: MyMemoryTranslator
    try:
        from deep_translator import MyMemoryTranslator
        # Split text into chunks of <= 450 characters to stay within MyMemory single-query limits
        chunks = [cleaned_input[i:i + 450] for i in range(0, len(cleaned_input), 450)]
        translated_chunks = []
        translator = MyMemoryTranslator(source="hi-IN", target="en-GB")
        for chunk in chunks:
            translated_chunks.append(translator.translate(chunk))
        translated_text = " ".join(translated_chunks)
        if translated_text and translated_text.strip():
            return {
                "success": True,
                "translated_text": translated_text.strip(),
                "original_text": cleaned_input,
                "was_translated": True,
                "error": None,
                "provider": "MyMemoryTranslator"
            }
    except Exception as e1:
        logger.warning("MyMemoryTranslator failed: %s; trying GoogleTranslator fallback.", e1)

    # Provider 2: GoogleTranslator
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source="hi", target="en")
        translated_text = translator.translate(cleaned_input[:4000])
        if translated_text and translated_text.strip():
            return {
                "success": True,
                "translated_text": translated_text.strip(),
                "original_text": cleaned_input,
                "was_translated": True,
                "error": None,
                "provider": "GoogleTranslator"
            }
    except Exception as e2:
        logger.warning("GoogleTranslator failed: %s", e2)

    return {
        "success": False,
        "translated_text": "",
        "original_text": cleaned_input,
        "was_translated": False,
        "error": (
            "Hindi translation service is currently unavailable or rate-limited. "
            "Because the existing model was trained exclusively on English vocabulary, "
            "untranslated Hindi text cannot be evaluated reliably. "
            "Please check your internet connection or paste the English translation directly."
        ),
        "provider": None
    }
