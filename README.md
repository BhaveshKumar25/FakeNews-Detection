# FakeNews AI - Explainable Fake News Detection & Fact-Checking System

An academic **Human–Computer Interaction (HCI)** and **Machine Learning** application designed to classify news articles as **Real** or **Fake**, provide **transparent, feature-level explanations**, support **English and Hindi** inputs, extract news directly from **URLs** and **Screenshots (OCR)**, and connect users with **certified fact-checking sources**.

---

## 🌟 Key Features

### 1. Machine Learning Classification & Uncertainty Detection
- **TF-IDF + Logistic Regression**: High-speed, interpretable inference trained on balanced datasets.
- **Uncertain Result Warning**: Automatically flags predictions with confidence near the decision boundary (e.g., $< 65\%$), cautioning users against over-relying on statistical scores.
- **Responsible AI Principles**: Explicitly distinguishes between linguistic vocabulary patterns and real-world verified truth.

### 2. Regional Language Support (English & Hindi)
- **Automatic Language Detection**: Detects Devanagari script for Hindi inputs.
- **Translation Pipeline**: Translates Hindi news to English before passing to the model, ensuring reliable inference without feeding untranslated text into an English-only model.
- **Transparent Notice**: Informs the user when translation was performed, showing original and translated snippets.
- **Full UI Localization**: Seamless toggle between English and Hindi interface labels, hints, and error alerts.

### 3. News URL Detection
- **Safe Extraction**: Accepts valid HTTP/HTTPS news links.
- **SSRF & Security Safeguards**: Rejects private IP ranges (`10.x`, `192.168.x`, `172.16-31.x`), loopback (`127.0.0.1`, `localhost`), link-local, and non-HTTP protocols.
- **Metadata Extraction**: Parses article headline, publisher domain, publication date, and body paragraphs.
- **Interactive Review**: Displays extracted content in an editable textarea so users can verify or adjust text before classification.

### 4. News Screenshot OCR Analysis
- **Image Support**: Accepts valid PNG, JPG, and JPEG screenshots up to 5 MB.
- **Multilingual OCR Engine**: Integrated with Tesseract OCR supporting English (`eng`) and Hindi (`hin`) traineddata.
- **Privacy & Safety**: Temporary image uploads are processed in memory / temporary directories and deleted immediately after text extraction.

### 5. Explainable AI (XAI)
- **Feature Contribution**: Computes exact linear model log-odds impacts ($x_i \cdot w_i$).
- **Visual Vocabulary Chips**: Real-favoring tokens highlighted in green; Fake-favoring tokens highlighted in red/coral.
- **Honest Limitations**: Displays explicit notices when text contains out-of-vocabulary or uninformative tokens rather than hallucinating explanations.

### 6. Simple Language vs Detailed Technical Mode
- **Dual Audience Design**: One-click switch between accessible plain-language explanations (for non-technical readers) and granular statistical metrics (TF-IDF weights, log-odds coefficients).
- **HCI Alignment**: Adheres to Nielsen's heuristics: visibility of system status, match between system and the real world, and error prevention.

### 7. Source & Publisher Investigation
- **Publisher Domain Identification**: Shows source domain extracted from URLs or metadata.
- **Transit Encryption Warning**: Explains that an HTTPS connection only secures data in transit and does not verify publisher credibility.
- **One-Click External Lookup**: Direct link to investigate publisher reputability on Google Search.

### 8. Related Fact-Check Integration
- **Google Fact Check Tools API**: Connects to the official Google Fact Check Tools API when configured.
- **Verified Fact-Checking Portals**: Provides direct, query-prefilled links to independent fact-check organizations (Google Fact Check Explorer, Snopes, PolitiFact, Alt News, BOOM Live) if API key is not configured or no exact matches are found.

### 9. User Feedback System
- **Rating & Sentiment**: Options for "Helpful 👍", "Seems Incorrect ⚠️", and "Unsure ❓".
- **Comment Field**: Optional user feedback without requiring account registration or collecting personal data (PII).
- **SQLite Persistence**: Stored safely in `data/feedback.db` with rate-limiting and validation.

### 10. Shareable Analysis Reports
- **Multi-Format Export**: Generates styled, printable standalone HTML reports and plain-text (.txt) reports.
- **Web Share API**: One-click sharing on supported browsers, with automatic clipboard copy fallback.
- **XSS Protection**: Complete HTML escaping of user inputs and excerpts.

---

## 💻 System Requirements

- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: Version 3.10 to 3.13 (tested and verified on Python 3.13 64-bit)
- **OCR Engine (Screenshot OCR)**:
  - **Option 1 (Recommended on Windows 10/11)**: Built-in Windows OCR via `winocr` (`pip install winocr` — already included in `requirements.txt`). Works out-of-the-box without installing external software.
  - **Option 2 (Fallback / Cross-Platform)**: [UB-Mannheim Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) with optional Hindi (`hin.traineddata`) language pack.

---

## 🚀 Windows PowerShell Setup Instructions

### 1. Open Windows PowerShell in Project Directory
```powershell
cd <path_to_project>
```

### 2. Create and Activate Virtual Environment
```powershell
# Create virtual environment if not already present
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```
*(If PowerShell displays an Execution Policy restriction, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Optional Environment Configuration
Copy `.env.example` to `.env` if you wish to customize configuration:
```powershell
Copy-Item .env.example .env
```
Available environment variables:
- `FACT_CHECK_API_KEY`: Google Fact Check Tools API key (optional).
- `UNCERTAINTY_THRESHOLD`: Decimal between 0.50 and 0.90 (default `0.65`).
- `TESSERACT_CMD`: Explicit path to `tesseract.exe` (optional fallback, e.g., `C:\Program Files\Tesseract-OCR\tesseract.exe`).
- `REQUEST_TIMEOUT_SECONDS`: Request timeout for external fetches (default `6`).

### 5. Run Automated Tests
```powershell
# Execute complete pytest suite
pytest
```
*Expected result: 40 passed tests covering all features with zero failures.*

### 6. Start the Flask Application
```powershell
python app.py
```

### 7. Access the Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📷 OCR Setup: Windows Built-in OCR & Tesseract (Windows)

The application provides a two-tiered OCR engine:
1. **Windows OCR (`winocr`)**: Built directly into Windows 10/11 WinRT media APIs. No external installers or path configuration required! Installed via `pip install winocr`.
2. **Tesseract OCR (Fallback)**:
   - Download the Windows installer from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
   - During installation, check the box for **Additional script data** -> **Devanagari script** and **Additional language data** -> **Hindi**.
   - Default installation path is `C:\Program Files\Tesseract-OCR\tesseract.exe`. The application automatically searches this location and system `PATH`.
   - If installed elsewhere, specify the path in `.env`:
     ```env
     TESSERACT_CMD=C:\Your\Path\To\tesseract.exe
     ```

---

## 🔍 Google Fact Check Tools API Configuration

1. Visit [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project and enable the **Fact Check Tools API**.
3. Generate an API Key under **APIs & Services > Credentials**.
4. Add the key to your `.env` file:
   ```env
   FACT_CHECK_API_KEY=AIzaSy...YourKeyHere
   ```
5. If no API key is provided, the application automatically displays verified, prefilled manual search buttons to Google Fact Check Explorer, Snopes, PolitiFact, and Alt News.

---

## 🧪 Automated Testing Details

The automated test suite uses `pytest` with extensive mocking for external network dependencies, ensuring test execution is 100% reliable even offline.

Test coverage summary:
- **`tests/test_app.py`**: Home page rendering, valid predictions, empty input handling, stopwords-only rejection, real/fake class-label mapping, uncertainty warning thresholding, JSON payload support.
- **`tests/test_multilingual.py`**: Devanagari detection, English bypass, translation pipeline, translation failure graceful error handling.
- **`tests/test_url_fetcher.py`**: SSRF prevention (blocking loopback, private IPv4, local hostnames), safe HTTPS extraction, timeout handling, HTTP 403 / paywall handling.
- **`tests/test_ocr.py`**: Image file type validation, dimension checks, text extraction, temp file guaranteed cleanup.
- **`tests/test_explainer.py`**: Feature attribution math ($x_i \cdot w_i$), direction mapping (positive favors Real, negative favors Fake), vocabulary absence honesty, simple vs detailed modes, Hindi explanation output.
- **`tests/test_fact_check.py`**: Headline query extraction, manual portal links, mock API success parsing, missing key graceful fallback.
- **`tests/test_feedback.py`**: SQLite feedback persistence, sentiment validation, comment truncation, client rate-limiting.
- **`tests/test_reports.py`**: Text report formatting, HTML report XSS safety, attachment download headers.

---

## 🛡️ Responsible AI & Ethical HCI Notice

1. **Statistical Inference**: This system utilizes TF-IDF and Logistic Regression trained on historical news articles. Predictions reflect stylistic and lexical patterns, **not infallible factual truth**.
2. **Uncertainty Communication**: When a confidence score falls below the configurable threshold, a prominent warning advises the user to perform independent verification.
3. **Transport Security ≠ Reliability**: An HTTPS padlock icon only proves encrypted transit, not journalistic authenticity.
4. **Human in the Loop**: AI tools are assistive. High-stakes claims must always be verified through certified fact-checkers subscribing to the International Fact-Checking Network (IFCN) code of principles.
