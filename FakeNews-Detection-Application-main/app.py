"""Flask application for AI-Powered Fake News Detection."""
import os
import io
import tempfile
from datetime import datetime, timezone
import joblib
from flask import Flask, render_template, request, jsonify, send_file, Response
from werkzeug.utils import secure_filename

import warnings
from sklearn.exceptions import InconsistentVersionWarning
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

from src.config import (
    MODEL_PATH,
    UNCERTAINTY_THRESHOLD,
    MAX_ARTICLE_CHARS,
    MAX_UPLOAD_SIZE_BYTES
)
from src.preprocess import clean_text
from src.explainer import explain_prediction
from src.translator import detect_language, translate_to_english, contains_hindi
from src.url_fetcher import fetch_article_from_url
from src.ocr_reader import extract_text_from_image, is_ocr_available
from src.fact_checker import search_fact_checks
from src.database import init_db, save_feedback
from src.report_generator import generate_text_report, generate_html_report

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE_BYTES

# Initialize database schema
init_db()

# -----------------------------
# Load Model
# -----------------------------
model = None
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"[FakeNews AI] Model loaded successfully from {MODEL_PATH}")
    else:
        print(f"[FakeNews AI] Warning: Model file not found at {MODEL_PATH}")
except Exception as e:
    print(f"[FakeNews AI] Error loading model: {e}")
    model = None


# -----------------------------
# Home & Static Favicon Routes
# -----------------------------
@app.route("/favicon.ico")
def favicon():
    return send_file(os.path.join(app.root_path, "static", "images", "logo.png"), mimetype="image/png")


@app.route("/")
def home():
    ocr_ready = is_ocr_available()
    return render_template("index.html", ocr_ready=ocr_ready)


# -----------------------------
# Prediction Route
# -----------------------------
@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({
            "prediction": "Error",
            "message": "Machine learning model is not currently loaded on the server."
        }), 503

    # Support form-data and JSON requests
    if request.is_json:
        data = request.get_json() or {}
        news = data.get("news", "")
        lang_pref = data.get("language", "auto")
        simple_mode = bool(data.get("simple_mode", False))
        source_url = data.get("source_url", "")
        source_domain = data.get("source_domain", "")
        input_type = data.get("input_type", "Text")
    else:
        news = request.form.get("news", "")
        lang_pref = request.form.get("language", "auto")
        simple_mode = request.form.get("simple_mode", "false").lower() in ("true", "1")
        source_url = request.form.get("source_url", "")
        source_domain = request.form.get("source_domain", "")
        input_type = request.form.get("input_type", "Text")

    news = (news or "").strip()
    if not news:
        return jsonify({
            "prediction": "Error",
            "message": "Please enter news article text before analyzing."
        }), 400

    if len(news) > MAX_ARTICLE_CHARS:
        news = news[:MAX_ARTICLE_CHARS]

    try:
        # Determine language
        detected_lang = detect_language(news)
        user_lang = detected_lang if lang_pref == "auto" else lang_pref

        was_translated = False
        original_hindi = None
        analysis_text = news

        # Feature 1: Regional Language Translation Pipeline
        if user_lang == "hi" or contains_hindi(news):
            trans_result = translate_to_english(news, source_lang="hi")
            if not trans_result["success"]:
                return jsonify({
                    "prediction": "Error",
                    "message": trans_result["error"],
                    "language": "hi",
                    "translation_failed": True
                }), 422

            analysis_text = trans_result["translated_text"]
            was_translated = trans_result["was_translated"]
            original_hindi = news

        # Feature 2 & Pipeline: Preprocess and predict
        cleaned = clean_text(analysis_text)

        # Handle edge-case: completely empty after cleaning
        if not cleaned:
            return jsonify({
                "prediction": "Error",
                "message": (
                    "Text contained only stopwords, numbers, or unsupported symbols. "
                    "Please provide substantive news article sentences."
                )
            }), 400

        # Model inference
        prediction_raw = model.predict([cleaned])[0]
        probabilities = model.predict_proba([cleaned])[0]

        # In this dataset: Class 0 = Fake, Class 1 = Real
        prob_fake = float(probabilities[0])
        prob_real = float(probabilities[1])
        confidence = float(max(probabilities))

        if str(prediction_raw) in ["1", "Real", "real"]:
            result = "Real"
        else:
            result = "Fake"

        # Feature 7: Uncertain Result Warning
        is_uncertain = confidence < UNCERTAINTY_THRESHOLD
        uncertainty_warning = None
        if is_uncertain:
            uncertainty_warning = {
                "flagged": True,
                "threshold": UNCERTAINTY_THRESHOLD,
                "confidence": confidence,
                "message_en": (
                    f"Low confidence ({round(confidence*100)}%). The statistical score is close to the 50/50 decision boundary. "
                    "Linguistic signals are mixed or subtle. Do not rely on this prediction without independent verification."
                ),
                "message_hi": (
                    f"कम विश्वास स्कोर ({round(confidence*100)}%)। यह स्कोर निर्णय सीमा के बेहद करीब है। "
                    "कृपया बिना स्वतंत्र जांच के केवल इस निष्कर्ष पर भरोसा न करें।"
                ),
                "disclaimer": "Model confidence is an uncalibrated statistical estimate, not real-world certainty."
            }

        # Feature 4 & 8: Explainable Results (Simple and Detailed Modes)
        explanation = explain_prediction(
            model=model,
            cleaned_text=cleaned,
            raw_text=analysis_text,
            simple_mode=simple_mode,
            language=user_lang
        )

        # Feature 9: Related Fact-Check Search
        fact_check = search_fact_checks(analysis_text, language_code="en" if user_lang != "hi" else "hi")

        timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        response_data = {
            "prediction": result,
            "confidence": confidence,
            "prob_real": prob_real,
            "prob_fake": prob_fake,
            "is_uncertain": is_uncertain,
            "uncertainty_warning": uncertainty_warning,
            "explanation": explanation,
            "fact_check": fact_check,
            "language": user_lang,
            "was_translated": was_translated,
            "original_hindi": original_hindi,
            "source_url": source_url,
            "source_domain": source_domain,
            "input_type": input_type,
            "timestamp": timestamp_str
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({
            "prediction": "Error",
            "message": f"Analysis encountered an internal error: {str(e)}"
        }), 500


# -----------------------------
# Feature 2: URL Fetch Route
# -----------------------------
@app.route("/fetch-url", methods=["POST"])
def fetch_url():
    data = request.get_json() if request.is_json else request.form
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({
            "success": False,
            "error": "Please provide an article URL."
        }), 400

    result = fetch_article_from_url(url)
    status_code = 200 if result["success"] else 400
    return jsonify(result), status_code


# -----------------------------
# Feature 3: Screenshot OCR Route
# -----------------------------
@app.route("/ocr-upload", methods=["POST"])
def ocr_upload():
    if "image" not in request.files:
        return jsonify({
            "success": False,
            "error": "No image file was uploaded."
        }), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({
            "success": False,
            "error": "Empty filename received."
        }), 400

    preferred_lang = request.form.get("language", "eng")

    # Save to a temporary file safely and guarantee cleanup
    suffix = os.path.splitext(secure_filename(file.filename))[1].lower()
    if suffix not in (".png", ".jpg", ".jpeg"):
        return jsonify({
            "success": False,
            "error": "Unsupported file format. Please upload a PNG or JPG/JPEG screenshot."
        }), 400

    temp_fd, temp_path = tempfile.mkstemp(suffix=suffix)
    os.close(temp_fd)

    try:
        file.save(temp_path)
        ocr_result = extract_text_from_image(temp_path, preferred_lang=preferred_lang)
        status_code = 200 if ocr_result["success"] else 400
        return jsonify(ocr_result), status_code
    finally:
        # Guarantee immediate deletion of uploaded screenshot
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


# -----------------------------
# Feature 6: User Feedback Route
# -----------------------------
@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json() if request.is_json else request.form
    sentiment = data.get("sentiment", "")
    comment = data.get("comment", "")
    prediction = data.get("prediction", "")
    confidence = data.get("confidence", 0.0)
    news_excerpt = data.get("news_excerpt", "")

    client_id = request.remote_addr or "anonymous"

    result = save_feedback(
        sentiment=sentiment,
        comment=comment,
        prediction=prediction,
        confidence=confidence,
        news_excerpt=news_excerpt,
        client_id=client_id
    )

    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


# -----------------------------
# Feature 9: Fact-Check Route
# -----------------------------
@app.route("/fact-check", methods=["POST"])
def fact_check_route():
    data = request.get_json() if request.is_json else request.form
    query = data.get("query") or data.get("text") or ""
    language = data.get("language", "en")

    result = search_fact_checks(query, language_code=language)
    return jsonify(result)


# -----------------------------
# Feature 10: Download Report Route
# -----------------------------
@app.route("/download-report", methods=["POST"])
def download_report():
    data = request.get_json() or {}
    report_format = (data.get("format") or "html").lower()

    if report_format == "txt":
        content = generate_text_report(data)
        return Response(
            content,
            mimetype="text/plain; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=FakeNews_Analysis_Report.txt"}
        )
    else:
        content = generate_html_report(data)
        return Response(
            content,
            mimetype="text/html; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=FakeNews_Analysis_Report.html"}
        )


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
