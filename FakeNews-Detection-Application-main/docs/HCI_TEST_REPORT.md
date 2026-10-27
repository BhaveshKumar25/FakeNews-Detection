# HCI Test & Verification Report: Shneiderman's 8 Golden Rules & Fitts' Law

**Project:** FakeNews AI - Explainable Fake News Detection & Fact-Checking System  
**Audit Scope:** Ben Shneiderman's Eight Golden Rules of Interface Design & Fitts' Law  
**Test Suite:** Pytest + Manual Browser Workflow Audit  
**Date:** October 2026  
**Status:** All 41 Automated Tests Passed (100% Pass Rate). All 9 HCI Principles Verified.

---

## 1. Executive Summary

This report documents the rigorous verification of Human–Computer Interaction (HCI) principles implemented in the FakeNews AI web application. The audit evaluated consistency, keyboard shortcut accessibility, informative feedback, task completion and closure, error prevention and simple recovery, reversible actions (including the newly added Undo clear mechanism), user locus of control, short-term memory reduction, and Fitts' Law touch target sizing on desktop and mobile viewports.

---

## 2. Automated Test Suite Execution

### Test Execution Command
```powershell
pytest
```

### Overall Metrics
- **Total Tests Collected:** 41
- **Passed:** 41
- **Failed:** 0
- **Execution Time:** ~2.00 seconds
- **Pass Rate:** 100%

### Detailed Test Log
| Test Name | Module | Description | Result |
|---|---|---|---|
| `test_home_page_loads` | `tests/test_app.py` | Confirms HTTP 200, logo, text area, and analyzer card | **PASSED** |
| `test_empty_prediction_input` | `tests/test_app.py` | Confirms empty text returns HTTP 400 with helpful guidance | **PASSED** |
| `test_stopwords_only_input` | `tests/test_app.py` | Confirms stopwords-only input is rejected non-destructively | **PASSED** |
| `test_normal_english_prediction` | `tests/test_app.py` | Verifies end-to-end prediction, confidence, XAI chips, fact-check | **PASSED** |
| `test_real_fake_class_mapping` | `tests/test_app.py` | Verifies Class 1 maps to Real and Class 0 maps to Fake | **PASSED** |
| `test_uncertainty_warning_triggered` | `tests/test_app.py` | Verifies low confidence scores trigger uncertainty warning banner | **PASSED** |
| `test_json_payload_support` | `tests/test_app.py` | Validates REST API JSON payload interoperability | **PASSED** |
| `test_hindi_prediction_endpoint_success` | `tests/test_app.py` | Confirms Hindi news triggers translation and completes inference | **PASSED** |
| `test_hindi_translation_failure_endpoint` | `tests/test_app.py` | Confirms translation network errors return HTTP 422 cleanly | **PASSED** |
| `test_model_unloaded_error` | `tests/test_app.py` | Confirms unloaded model returns HTTP 503 service unavailable | **PASSED** |
| `test_keyboard_shortcuts_and_fitts_elements_in_html` | `tests/test_app.py` | Confirms `aria-keyshortcuts`, modal `#shortcutsModal`, and `#analyzeBtn`/`#clearBtn` | **PASSED** |
| `test_explainer_with_real_model` | `tests/test_explainer.py` | Validates mathematical feature attribution ($x_i \cdot w_i$) | **PASSED** |
| `test_explainer_empty_input_honesty` | `tests/test_explainer.py` | Confirms honesty when no vocabulary matches exist | **PASSED** |
| `test_simple_vs_detailed_mode` | `tests/test_explainer.py` | Confirms plain-language vs mathematical decomposition output | **PASSED** |
| `test_hindi_explanation_summary` | `tests/test_explainer.py` | Confirms Hindi explanation summaries in both modes | **PASSED** |
| `test_extract_search_query` | `tests/test_fact_check.py` | Verifies clean headline query extraction for fact checks | **PASSED** |
| `test_manual_links_generation` | `tests/test_fact_check.py` | Validates generation of verified portal query links | **PASSED** |
| `test_search_fact_checks_without_api_key` | `tests/test_fact_check.py` | Confirms graceful fallback to manual links without API key | **PASSED** |
| `test_search_fact_checks_with_mock_api` | `tests/test_fact_check.py` | Confirms parsing of Google Fact Check Tools API response | **PASSED** |
| `test_save_valid_feedback` | `tests/test_feedback.py` | Verifies SQLite feedback recording and schema validation | **PASSED** |
| `test_reject_invalid_sentiment` | `tests/test_feedback.py` | Validates rejection of malformed sentiment strings | **PASSED** |
| `test_feedback_endpoint_post` | `tests/test_feedback.py` | Verifies HTTP POST `/feedback` returns HTTP 200 with row ID | **PASSED** |
| `test_feedback_rate_limiting` | `tests/test_feedback.py` | Validates sliding-window IP rate limiter (max 8 per min) | **PASSED** |
| `test_language_detection` | `tests/test_multilingual.py` | Confirms Devanagari detection for Hindi text | **PASSED** |
| `test_english_translation_bypass` | `tests/test_multilingual.py` | Confirms English bypasses translation pipeline without overhead | **PASSED** |
| `test_hindi_translation_pipeline_success` | `tests/test_multilingual.py` | Confirms multi-provider translation pipeline execution | **PASSED** |
| `test_hindi_translation_failure_handling` | `tests/test_multilingual.py` | Confirms graceful handling when translation is offline | **PASSED** |
| `test_ocr_invalid_file_extension` | `tests/test_ocr.py` | Confirms non-image uploads are rejected immediately | **PASSED** |
| `test_ocr_small_dimensions` | `tests/test_ocr.py` | Confirms images smaller than 50×50 are rejected | **PASSED** |
| `test_ocr_oversized_file` | `tests/test_ocr.py` | Confirms images larger than 5MB are rejected | **PASSED** |
| `test_ocr_mock_success` | `tests/test_ocr.py` | Confirms Tesseract OCR fallback text extraction | **PASSED** |
| `test_ocr_winocr_mock_success` | `tests/test_ocr.py` | Confirms Windows OCR (`winocr`) text extraction | **PASSED** |
| `test_ocr_upload_endpoint_cleanup` | `tests/test_ocr.py` | Verifies temporary uploaded screenshots are deleted immediately | **PASSED** |
| `test_generate_text_report` | `tests/test_reports.py` | Validates formatting of plain-text analysis report | **PASSED** |
| `test_generate_html_report_escaping` | `tests/test_reports.py` | Verifies HTML report escaping against XSS vulnerabilities | **PASSED** |
| `test_download_report_endpoint` | `tests/test_reports.py` | Confirms `/download-report` sets attachment headers | **PASSED** |
| `test_url_ssrf_filtering` | `tests/test_url_fetcher.py` | Validates blocking of private, loopback, and local IPs | **PASSED** |
| `test_valid_public_url` | `tests/test_url_fetcher.py` | Confirms public HTTP/HTTPS URLs pass safety check | **PASSED** |
| `test_fetch_url_success` | `tests/test_url_fetcher.py` | Verifies extraction of headline, domain, date, and text | **PASSED** |
| `test_fetch_url_timeout_handling` | `tests/test_url_fetcher.py` | Confirms 10-second timeout returns helpful error | **PASSED** |
| `test_fetch_url_forbidden_handling` | `tests/test_url_fetcher.py` | Confirms paywall and 403 responses are handled gracefully | **PASSED** |

---

## 3. Manual Browser & HCI Usability Audit

A comprehensive manual inspection and browser verification was conducted across the live application at `http://127.0.0.1:5000/`.

### Verified Principles & Observations:

1. **Rule 1 — Strive for Consistency:**
   - Visual: Cards, buttons, and badges share identical border-radii (`14px` on buttons, `20px` on cards), shadows, and unified `Poppins` typography across both Dark and Light themes.
   - Functional: All three input tabs (Direct Text, News URL, Screenshot OCR) stage text into the identical `#news` textarea before submitting to the unified ML pipeline.
   - Linguistic: Switching language to Hindi (`हिन्दी`) consistently translates all navigation links, buttons, headers, and placeholders.

2. **Rule 2 — Enable Frequent Users to Use Shortcuts:**
   - Pressing `Ctrl + Enter` instantly triggers analysis from inside the textarea.
   - Pressing `Esc` clears inputs or closes the shortcuts cheatsheet modal.
   - Pressing `Ctrl + Z` undoes an accidental clear action and restores the article.
   - Pressing `Alt + 1`, `Alt + 2`, `Alt + 3` switches input tabs instantly.
   - Pressing `Alt + L` switches language; `Alt + M` toggles explanation mode; `Alt + T` toggles theme.
   - Pressing `?` or `Alt + K` displays the Keyboard Shortcuts reference modal.
   - Normal text typing inside the textarea is completely uninhibited.

3. **Rule 3 — Offer Informative Feedback:**
   - Input: Live character counter updates in real time (`X / 15000 Characters`).
   - Processing: Progressive loader cycles through explicit milestones every 1100ms.
   - Output: Result card presents multi-dimensional feedback: numerical confidence (e.g., `85%`), circular SVG progress ring, linear bar, colored classification badges, and floating toasts.

4. **Rule 4 — Design Dialogs to Yield Closure:**
   - A distinct 3-phase journey (Input -> Processing -> Resolution) ensures the user understands when work is complete.
   - Feedback submission clearly closes with `"✓ Feedback saved. Thank you!"`.
   - Report download triggers an immediate browser download with confirmation toast.

5. **Rule 5 — Offer Error Prevention and Simple Error Handling:**
   - Empty input is prevented with non-blocking toast guidance.
   - `maxlength="15000"` and file constraints prevent buffer overflows or invalid file formats.
   - SSRF protection blocks attempts to access private or loopback networks.
   - If an error occurs, user text is preserved inside the textarea for immediate editing.

6. **Rule 6 — Permit Easy Reversal of Actions:**
   - Clicking "Clear" or pressing `Esc` caches previous text in `lastClearedState` and presents an interactive toast with an `"Undo (Ctrl+Z)"` button.
   - Extracted text from URLs and Screenshot OCR is staged into the editable textarea *prior* to analysis, allowing users to modify or remove noise before running inference.
   - Users can toggle between "Helpful", "Seems Incorrect", and "Unsure" before submitting.
   - "Clear History" resets the local prediction log with one click.

7. **Rule 7 — Support an Internal Locus of Control:**
   - The user initiates all actions. No automated unprompted submissions occur.
   - Users configure their preferred modality (Text/URL/OCR), explanation depth (Simple/Detailed), language (EN/HI), and theme (Dark/Light).
   - High-contrast `:focus-visible` styling (`outline: 2px solid #00D9FF !important`) provides complete keyboard navigation.

8. **Rule 8 — Reduce Short-Term Memory Load:**
   - Prediction Result Card displays the article excerpt, domain, positive/negative word chips, and fact-check references simultaneously.
   - History section remembers the last 8 analyzed news items with timestamps and confidence scores.
   - User settings (language, mode, theme) persist automatically in `localStorage`.
   - "Use Example" button allows instant trial without searching for sample news.

9. **Fitts' Law (Target Size & Distance):**
   - Movement Time $MT = a + b \log_2(1 + D/W)$.
   - Target Size ($W$): `#analyzeBtn` is prominently sized with `min-height: 54px`, `flex: 2`, `padding: 16px 36px`, meeting WCAG 2.5.5 Level AAA ($> 44\times 44\text{px}$). `#clearBtn` is sized at `min-height: 54px`, `flex: 1`, separated by a $16\text{px}$ gap to prevent misclicks.
   - Target Distance ($D$): Positioned directly adjacent underneath the text input area, minimizing cursor/thumb travel distance.
   - Mobile Viewport: On screen widths $\le 640\text{px}$, buttons stack vertically to 100% width, placing large touch targets right in the natural thumb zone.

---

## 4. Remaining Issues & External Software Requirements

- **Remaining Software Bugs:** 0 reproducible bugs found. All 41 tests pass.
- **External Configuration:**
  - **Windows OCR (`winocr`)**: Functions natively on Windows 10/11 with zero external installation.
  - **Tesseract OCR**: Optional fallback if running on Linux or legacy OS.
  - **Google Fact Check Tools API**: Connects automatically if `FACT_CHECK_API_KEY` is set in `.env`; otherwise cleanly falls back to pre-filled manual fact-checking portals without fabricating ratings.
