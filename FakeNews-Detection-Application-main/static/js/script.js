// =========================================================
// FakeNews AI - Client Application Script
// =========================================================

// State Management
let currentLang = localStorage.getItem("fakenews_lang") || "en";
let simpleMode = localStorage.getItem("fakenews_simple_mode") !== "false"; // Default true
let lastPredictionData = null;
let selectedFeedbackSentiment = null;
let currentSourceUrl = "";
let currentSourceDomain = "";
let currentInputType = "Text";
let selectedOcrFile = null;

// =========================================================
// Internationalization (i18n) Dictionary: English & Hindi
// =========================================================
const translations = {
    en: {
        nav_home: "Home",
        nav_features: "Features",
        nav_stats: "Statistics",
        nav_history: "History",
        nav_about: "About",
        lang_btn: "हिन्दी",
        mode_btn_simple: "Simple Mode: ON",
        mode_btn_detailed: "Detailed Mode",
        hero_title: 'Detect Fake News <span>Using Machine Learning</span>',
        hero_subtitle: "Transparent, explainable fake news analysis powered by TF-IDF, Logistic Regression, multi-language support, and verified fact-checking sources.",
        badge_ai: "AI Powered",
        badge_pipeline: "TF-IDF + Logistic Regression",
        badge_multilingual: "English + Hindi Support",
        badge_accuracy: "97.3% Model Accuracy",
        analyzer_heading: '<i class="fa-solid fa-newspaper"></i> Analyze News Content',
        tab_text: "Direct Text",
        tab_url: "News URL",
        tab_ocr: "Screenshot OCR",
        btn_fetch_url: "Fetch Article",
        url_https_note: "Note: HTTPS secures the connection, but does not guarantee the truthfulness of the article.",
        ocr_drop_text: "Click or Drag & Drop a news screenshot (PNG, JPG, JPEG up to 5MB)",
        ocr_lang_label: "OCR Language:",
        btn_ocr_extract: "Extract Text",
        btn_example: "Use Example",
        btn_analyze: "Analyze News",
        btn_clear: "Clear",
        loader_analyzing: "Analyzing using AI...",
        uncertainty_heading: "⚠️ Low Confidence / Uncertain Result:",
        translation_heading: "Hindi to English Translation Applied:",
        prob_disclaimer: "Statistical probability based on training vocabulary patterns, not guaranteed factual truth.",
        explanation_heading: "Model Explanation",
        words_favoring_real: "Words Favoring Real News:",
        words_favoring_fake: "Words Favoring Fake News:",
        source_heading: "Source Investigation",
        factcheck_heading: "Related Fact-Check Investigation",
        manual_factcheck_title: "Check Verified Independent Fact-Check Portals:",
        feedback_heading: "Was this analysis accurate or helpful?",
        fb_helpful: "Helpful",
        fb_incorrect: "Seems Incorrect",
        fb_unsure: "Unsure",
        btn_submit_feedback: "Submit Feedback",
        btn_dl_html: "Download HTML Report",
        btn_dl_txt: "Download TXT Report",
        btn_share: "Share / Copy Summary",
        section_features_title: "Key Capabilities & Features",
        feature_1_title: "TF-IDF & Logistic Regression",
        feature_1_desc: "Trained on thousands of real-world articles for high-speed, lightweight classification with mathematical interpretability.",
        feature_2_title: "Regional Language Pipeline",
        feature_2_desc: "Native Hindi support with automatic language detection, translation safeguards, and transparent processing notification.",
        feature_3_title: "Safe URL Article Extraction",
        feature_3_desc: "Safely extracts text, domain, and publication metadata from news links with SSRF protection and user editing.",
        feature_4_title: "Screenshot OCR Analysis",
        feature_4_desc: "Extracts text from screenshots with privacy safeguards, immediate temp cleanup, and multilingual OCR capabilities.",
        feature_5_title: "Explainable AI (XAI)",
        feature_5_desc: "Visualizes influential words favoring real or fake classifications with Simple Language and Detailed statistical modes.",
        feature_6_title: "Fact-Check Integration",
        feature_6_desc: "Connects to Google Fact Check Tools API and certified fact-checking portals for real-world claim verification.",
        section_stats_title: "Model Performance & Architecture",
        stat_acc: "Model Accuracy",
        stat_speed: "Average Inference Time",
        stat_articles: "Balanced Training Articles",
        history_heading: "Recent Predictions",
        btn_clear_history: "Clear History",
        history_empty: "No predictions yet.",
        footer_desc: "An academic Human–Computer Interaction (HCI) project combining machine learning, natural language processing, explainable AI, and fact-checking interfaces to empower informed digital reading.",
        placeholder_text: "Paste complete news article or headline here (English or हिन्दी)..."
    },
    hi: {
        nav_home: "होम",
        nav_features: "सुविधाएं",
        nav_stats: "आंकड़े",
        nav_history: "इतिहास",
        nav_about: "बारे में",
        lang_btn: "English",
        mode_btn_simple: "सरल मोड: चालू",
        mode_btn_detailed: "विस्तृत मोड",
        hero_title: 'फर्जी खबरों की पहचान <span>मशीन लर्निंग द्वारा</span>',
        hero_subtitle: "TF-IDF, लॉजिस्टिक रिग्रेशन, बहुभाषी समर्थन और सत्यापित फैक्ट-चेक स्रोतों द्वारा संचालित पारदर्शी और व्याख्यात्मक समाचार विश्लेषण।",
        badge_ai: "एआई संचालित",
        badge_pipeline: "TF-IDF + लॉजिस्टिक रिग्रेशन",
        badge_multilingual: "हिंदी + अंग्रेजी समर्थन",
        badge_accuracy: "97.3% मॉडल सटीकता",
        analyzer_heading: '<i class="fa-solid fa-newspaper"></i> समाचार सामग्री का विश्लेषण करें',
        tab_text: "सीधा पाठ (Text)",
        tab_url: "वेबसाइट लिंक (URL)",
        tab_ocr: "स्क्रीनशॉट (OCR)",
        btn_fetch_url: "लेख लोड करें",
        url_https_note: "नोट: HTTPS केवल सुरक्षित कनेक्शन की पुष्टि करता है, लेख की सच्चाई की नहीं।",
        ocr_drop_text: "समाचार स्क्रीनशॉट यहां क्लिक या ड्रैग करें (PNG, JPG, 5MB तक)",
        ocr_lang_label: "ओसीआर भाषा:",
        btn_ocr_extract: "टेक्स्ट निकालें",
        btn_example: "उदाहरण का उपयोग करें",
        btn_analyze: "विश्लेषण करें",
        btn_clear: "हटाएं (Clear)",
        loader_analyzing: "एआई द्वारा विश्लेषण जारी है...",
        uncertainty_heading: "⚠️ कम विश्वास स्कोर / अनिश्चित परिणाम:",
        translation_heading: "हिंदी से अंग्रेजी अनुवाद लागू किया गया:",
        prob_disclaimer: "प्रशिक्षण शब्दावली पैटर्न पर आधारित सांख्यिकीय संभावना, न कि पूर्ण तथ्यात्मक प्रमाण।",
        explanation_heading: "मॉडल व्याख्या (Explainability)",
        words_favoring_real: "सच्ची खबर की ओर संकेत करने वाले शब्द:",
        words_favoring_fake: "फर्जी खबर की ओर संकेत करने वाले शब्द:",
        source_heading: "स्रोत जांच (Source Investigation)",
        factcheck_heading: "संबंधित फैक्ट-चेक जांच",
        manual_factcheck_title: "सत्यापित स्वतंत्र फैक्ट-चेक पोर्टलों पर खोजें:",
        feedback_heading: "क्या यह विश्लेषण उपयोगी या सही लगा?",
        fb_helpful: "उपयोगी",
        fb_incorrect: "गलत लगा",
        fb_unsure: "अनिश्चित",
        btn_submit_feedback: "प्रतिक्रिया भेजें",
        btn_dl_html: "HTML रिपोर्ट डाउनलोड करें",
        btn_dl_txt: "TXT रिपोर्ट डाउनलोड करें",
        btn_share: "सारांश शेयर / कॉपी करें",
        section_features_title: "प्रमुख विशेषताएं एवं क्षमताएं",
        feature_1_title: "TF-IDF एवं लॉजिस्टिक रिग्रेशन",
        feature_1_desc: "हजारों वास्तविक लेखों पर प्रशिक्षित, उच्च गति और पारदर्शी व्याख्यात्मक वर्गीकरण।",
        feature_2_title: "क्षेत्रीय भाषा पाइपलाइन",
        feature_2_desc: "स्वचालित भाषा पहचान, अनुवाद सुरक्षा और पारदर्शी सूचना के साथ सहज हिंदी समर्थन।",
        feature_3_title: "सुरक्षित URL से लेख निष्कर्षण",
        feature_3_desc: "SSRF सुरक्षा और उपयोगकर्ता संपादन के साथ समाचार लिंक से पाठ और मेटाडेटा निष्कर्षण।",
        feature_4_title: "स्क्रीनशॉट ओसीआर विश्लेषण",
        feature_4_desc: "गोपनीयता सुरक्षा और बहुभाषी ओसीआर के साथ स्क्रीनशॉट से तुरंत टेक्स्ट निष्कर्षण।",
        feature_5_title: "व्याख्यात्मक एआई (XAI)",
        feature_5_desc: "सरल और विस्तृत सांख्यिकीय मोड में सच्ची या भ्रामक श्रेणी की ओर झुकाव वाले शब्दों का प्रदर्शन।",
        feature_6_title: "फैक्ट-चेक एकीकरण",
        feature_6_desc: "वास्तविक दावों की पुष्टि के लिए Google Fact Check Tools API और मान्यता प्राप्त फैक्ट-चेक पोर्टल।",
        section_stats_title: "मॉडल प्रदर्शन एवं वास्तुकला",
        stat_acc: "मॉडल सटीकता",
        stat_speed: "औसत विश्लेषण समय",
        stat_articles: "संतुलित प्रशिक्षण लेख",
        history_heading: "हाल के विश्लेषण",
        btn_clear_history: "इतिहास हटाएं",
        history_empty: "अभी कोई विश्लेषण नहीं हुआ है।",
        footer_desc: "जागरूक डिजिटल पठन के लिए मशीन लर्निंग, एनएलपी, एक्सएआई और फैक्ट-चेक इंटरफेस का एक अकादमिक एचसीआई प्रोजेक्ट।",
        placeholder_text: "पूरा समाचार लेख या शीर्षक यहाँ पेस्ट करें (अंग्रेजी या हिन्दी में)..."
    }
};

// Apply UI Language
function applyLanguage(lang) {
    currentLang = lang;
    localStorage.setItem("fakenews_lang", lang);
    const dict = translations[lang] || translations.en;

    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (dict[key]) {
            el.innerHTML = dict[key];
        }
    });

    const langBtnText = document.getElementById("langBtnText");
    if (langBtnText) langBtnText.innerText = dict.lang_btn;

    const newsArea = document.getElementById("news");
    if (newsArea && dict.placeholder_text) {
        newsArea.setAttribute("placeholder", dict.placeholder_text);
    }

    updateModeButtonText();
}

function toggleLanguage() {
    const nextLang = currentLang === "en" ? "hi" : "en";
    applyLanguage(nextLang);
    showToast(nextLang === "hi" ? "भाषा बदलकर हिन्दी कर दी गई है" : "Language switched to English");
}

// Simple vs Detailed Language Mode (Feature 8)
function toggleSimpleMode() {
    simpleMode = !simpleMode;
    localStorage.setItem("fakenews_simple_mode", simpleMode);
    updateModeButtonText();

    if (lastPredictionData) {
        renderExplanation(lastPredictionData.explanation);
    }

    const modeMsg = simpleMode 
        ? (currentLang === "hi" ? "सरल व्याख्या मोड सक्रिय" : "Simple Language Mode enabled") 
        : (currentLang === "hi" ? "विस्तृत सांख्यिकीय मोड सक्रिय" : "Detailed Statistical Mode enabled");
    showToast(modeMsg);
}

function updateModeButtonText() {
    const modeBtnText = document.getElementById("modeBtnText");
    const modeBadge = document.getElementById("modeBadge");
    const dict = translations[currentLang] || translations.en;

    if (modeBtnText) {
        modeBtnText.innerText = simpleMode ? dict.mode_btn_simple : dict.mode_btn_detailed;
    }
    if (modeBadge) {
        modeBadge.innerText = simpleMode ? "(Simple Mode)" : "(Detailed Technical Mode)";
    }
}

// =========================================================
// Input Tabs (Feature 2 & 3 HCI Workflow)
// =========================================================
function switchInputTab(tab) {
    document.querySelectorAll(".tabBtn").forEach(btn => btn.classList.remove("active"));
    document.querySelectorAll(".tabPane").forEach(pane => pane.classList.remove("active"));

    if (tab === "text") {
        document.getElementById("tabBtnText").classList.add("active");
        document.getElementById("tabText").classList.add("active");
        currentInputType = "Text";
    } else if (tab === "url") {
        document.getElementById("tabBtnUrl").classList.add("active");
        document.getElementById("tabUrl").classList.add("active");
        currentInputType = "URL";
    } else if (tab === "ocr") {
        document.getElementById("tabBtnOcr").classList.add("active");
        document.getElementById("tabOcr").classList.add("active");
        currentInputType = "Screenshot";
    }
}

// =========================================================
// Feature 2: Fetch Article URL
// =========================================================
async function fetchArticleUrl() {
    const urlInput = document.getElementById("urlInput");
    const url = (urlInput.value || "").trim();

    if (!url) {
        showToast("Please enter an article URL first.");
        urlInput.focus();
        return;
    }

    if (!url.startsWith("http://") && !url.startsWith("https://")) {
        showToast("URL must start with http:// or https://");
        urlInput.focus();
        return;
    }

    setLoader(true, "Validating & fetching article from URL...");

    try {
        const response = await fetch("/fetch-url", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: url })
        });

        const data = await response.json();
        setLoader(false);

        if (!data.success) {
            showToast(data.error || "Could not fetch article.");
            return;
        }

        currentSourceUrl = url;
        currentSourceDomain = data.domain || "";

        // Display preview info
        const previewCard = document.getElementById("urlPreviewCard");
        document.getElementById("urlPreviewTitle").innerText = data.title || "No Title";
        document.getElementById("urlPreviewDomain").innerText = data.domain || "Unknown Domain";
        document.getElementById("urlPreviewDate").innerText = data.publish_date || "Not Specified";
        previewCard.style.display = "block";

        // Insert extracted article text into news area for user review & editing
        const newsArea = document.getElementById("news");
        newsArea.value = (data.title ? data.title + "\n\n" : "") + data.text;
        updateCharCount();

        // Switch user to text tab to review and edit
        switchInputTab("text");
        showToast("Article extracted! Review or edit text, then click Analyze.");

    } catch (err) {
        setLoader(false);
        console.error(err);
        showToast("Failed to fetch article from URL.");
    }
}

// =========================================================
// Feature 3: Screenshot OCR
// =========================================================
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (!["image/png", "image/jpeg", "image/jpg"].includes(file.type)) {
        showToast("Please select a valid PNG or JPG/JPEG image.");
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        showToast("Image size exceeds 5MB limit.");
        return;
    }

    selectedOcrFile = file;
    document.getElementById("ocrDropText").innerHTML = `
        <strong>Selected file:</strong> ${file.name} (${(file.size / 1024).toFixed(1)} KB)<br>
        <small>Click "Extract Text" below to run OCR</small>
    `;
}

// Drag & Drop Setup
const dropZone = document.getElementById("dropZone");
if (dropZone) {
    ["dragenter", "dragover"].forEach(name => {
        dropZone.addEventListener(name, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add("dragover");
        });
    });
    ["dragleave", "drop"].forEach(name => {
        dropZone.addEventListener(name, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove("dragover");
        });
    });
    dropZone.addEventListener("drop", (e) => {
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileSelect({ target: { files: e.dataTransfer.files } });
        }
    });
}

async function runOcrUpload() {
    if (!selectedOcrFile) {
        showToast("Please choose or drop an image file first.");
        return;
    }

    const ocrLang = document.getElementById("ocrLangSelect").value || "eng";
    const formData = new FormData();
    formData.append("image", selectedOcrFile);
    formData.append("language", ocrLang);

    setLoader(true, "Extracting text using Optical Character Recognition (OCR)...");

    try {
        const response = await fetch("/ocr-upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        setLoader(false);

        if (!data.success) {
            showToast(data.error || "OCR extraction failed.");
            return;
        }

        const newsArea = document.getElementById("news");
        newsArea.value = data.text;
        updateCharCount();

        switchInputTab("text");
        showToast("Text extracted from screenshot! Review or edit before analyzing.");

    } catch (err) {
        setLoader(false);
        console.error(err);
        showToast("OCR processing error.");
    }
}

// =========================================================
// Prediction Workflow
// =========================================================
const loaderMessages = [
    "Validating news content...",
    "Checking language & translation pipeline...",
    "Extracting TF-IDF feature weights...",
    "Running Logistic Regression classifier...",
    "Evaluating prediction confidence & uncertainty...",
    "Querying fact-check databases..."
];
let loaderInterval = null;
let loaderIdx = 0;

function setLoader(show, initialText) {
    const loader = document.getElementById("loader");
    const text = document.getElementById("loaderText");
    const resultCard = document.getElementById("resultCard");

    if (show) {
        loader.style.display = "flex";
        if (resultCard) resultCard.style.display = "none";
        text.innerText = initialText || loaderMessages[0];
        loaderIdx = 0;
        clearInterval(loaderInterval);
        loaderInterval = setInterval(() => {
            loaderIdx = (loaderIdx + 1) % loaderMessages.length;
            text.innerText = loaderMessages[loaderIdx];
        }, 1100);
    } else {
        clearInterval(loaderInterval);
        loader.style.display = "none";
    }
}

async function predictNews() {
    const textarea = document.getElementById("news");
    const news = (textarea.value || "").trim();

    if (!news) {
        showToast("Please enter or fetch news text first.");
        textarea.focus();
        return;
    }

    setLoader(true);

    try {
        const payload = {
            news: news,
            language: currentLang,
            simple_mode: simpleMode,
            source_url: currentSourceUrl,
            source_domain: currentSourceDomain,
            input_type: currentInputType
        };

        const response = await fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        setLoader(false);

        if (data.prediction === "Error") {
            showToast(data.message || "Prediction error occurred.");
            return;
        }

        lastPredictionData = data;
        showPrediction(data, news);

    } catch (error) {
        setLoader(false);
        console.error(error);
        showToast("Prediction failed. Please check server connection.");
    }
}

// =========================================================
// Show Prediction Results (HCI & Feature Integration)
// =========================================================
function showPrediction(data, rawNews) {
    const resultCard = document.getElementById("resultCard");
    const predictionLabel = document.getElementById("predictionLabel");
    const predictionIcon = document.getElementById("predictionIcon");
    const confidenceText = document.getElementById("confidenceText");
    const confidencePercent = document.getElementById("confidencePercent");
    const progressBar = document.getElementById("progressBar");
    const circle = document.getElementById("circleProgress");

    resultCard.style.display = "block";
    resultCard.style.opacity = "1";
    resultCard.className = "resultCard"; // reset classes

    const confidence = Math.round(data.confidence * 100);
    confidenceText.innerText = "Confidence : " + confidence + "%";
    confidencePercent.innerText = confidence + "%";
    progressBar.style.width = confidence + "%";

    const circumference = 314;
    circle.style.strokeDashoffset = circumference - (confidence / 100) * circumference;

    // Feature 7: Uncertainty Warning
    const uncertaintyBanner = document.getElementById("uncertaintyBanner");
    const uncertaintyMsg = document.getElementById("uncertaintyMessage");
    if (data.is_uncertain && data.uncertainty_warning) {
        resultCard.classList.add("uncertain");
        predictionLabel.innerText = "UNCERTAIN / " + data.prediction.toUpperCase();
        predictionIcon.className = "fa-solid fa-triangle-exclamation uncertainIcon";
        circle.style.stroke = "#ffb300";

        const msgText = currentLang === "hi" 
            ? data.uncertainty_warning.message_hi 
            : data.uncertainty_warning.message_en;
        uncertaintyMsg.innerText = msgText;
        uncertaintyBanner.style.display = "flex";
    } else if (data.prediction === "Real") {
        resultCard.classList.add("real");
        predictionLabel.innerText = "REAL NEWS";
        predictionIcon.className = "fa-solid fa-circle-check realIcon";
        circle.style.stroke = "#00ff88";
        uncertaintyBanner.style.display = "none";
    } else {
        resultCard.classList.add("fake");
        predictionLabel.innerText = "FAKE NEWS";
        predictionIcon.className = "fa-solid fa-circle-xmark fakeIcon";
        circle.style.stroke = "#ff4b4b";
        uncertaintyBanner.style.display = "none";
    }

    // Feature 1: Translation Banner
    const transBanner = document.getElementById("translationBanner");
    const transDetails = document.getElementById("translationDetails");
    if (data.was_translated) {
        transBanner.style.display = "flex";
        transDetails.innerHTML = `
            Original Hindi input was automatically translated to English for model analysis.<br>
            <small style="opacity:0.85;">Original: "${(data.original_hindi || "").substring(0, 120)}..."</small>
        `;
    } else {
        transBanner.style.display = "none";
    }

    // Feature 4 & 8: Explainable Results
    renderExplanation(data.explanation);

    // Feature 5: Source Verification
    renderSourceVerification(data);

    // Feature 9: Fact-Check Results
    renderFactChecks(data.fact_check);

    // Feature 6: Reset Feedback State
    resetFeedbackUi();

    // Preserve History
    addHistory(rawNews, data.prediction, confidence, data.is_uncertain);

    // Scroll to result smoothly
    resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// Render Explainable AI Section
function renderExplanation(expl) {
    if (!expl) return;
    const summaryEl = document.getElementById("explanationSummary");
    const realChips = document.getElementById("realChips");
    const fakeChips = document.getElementById("fakeChips");
    const detailedTable = document.getElementById("detailedStatsTable");

    summaryEl.innerText = expl.summary || "No specific feature explanation available.";
    realChips.innerHTML = "";
    fakeChips.innerHTML = "";

    if (expl.real_words && expl.real_words.length > 0) {
        expl.real_words.forEach(w => {
            const chip = document.createElement("span");
            chip.className = "wordChip real";
            chip.innerHTML = `<i class="fa-solid fa-plus"></i> ${w.word} ${simpleMode ? "" : `(${w.impact})`}`;
            realChips.appendChild(chip);
        });
    } else {
        realChips.innerHTML = '<span style="font-size:12px; opacity:0.6;">None observed</span>';
    }

    if (expl.fake_words && expl.fake_words.length > 0) {
        expl.fake_words.forEach(w => {
            const chip = document.createElement("span");
            chip.className = "wordChip fake";
            chip.innerHTML = `<i class="fa-solid fa-minus"></i> ${w.word} ${simpleMode ? "" : `(${w.impact})`}`;
            fakeChips.appendChild(chip);
        });
    } else {
        fakeChips.innerHTML = '<span style="font-size:12px; opacity:0.6;">None observed</span>';
    }

    if (!simpleMode && expl.supported) {
        detailedTable.style.display = "block";
        detailedTable.innerHTML = `
            <div style="font-size:11px; opacity:0.8; margin-top:10px; border-top:1px dashed rgba(255,255,255,0.15); padding-top:8px;">
                <strong>Technical Weights:</strong> Impact = TF-IDF Weight × Logistic Regression Coef.
                Positive impacts push toward Real; negative impacts push toward Fake.
            </div>
        `;
    } else {
        detailedTable.style.display = "none";
    }
}

// Render Source Verification
function renderSourceVerification(data) {
    const sourceCard = document.getElementById("sourceCard");
    const metaDetails = document.getElementById("sourceMetaDetails");
    const searchBtn = document.getElementById("sourceSearchBtn");

    if (data.source_domain || currentSourceDomain) {
        const domain = data.source_domain || currentSourceDomain;
        sourceCard.style.display = "block";
        metaDetails.innerHTML = `
            <div><strong>Publisher Domain:</strong> ${domain}</div>
            <div style="font-size:12px; color:#ffb300; margin-top:4px;">
                <i class="fa-solid fa-shield-halved"></i>
                HTTPS encryption protects transit security, but does NOT establish journalistic credibility or factual accuracy.
            </div>
        `;
        searchBtn.href = `https://www.google.com/search?q=${encodeURIComponent(domain + " news credibility fact check")}`;
    } else {
        sourceCard.style.display = "none";
    }
}

// Render Fact Checks
function renderFactChecks(fc) {
    const msgEl = document.getElementById("factCheckMessage");
    const claimsList = document.getElementById("factCheckClaimsList");
    const manualGrid = document.getElementById("manualLinksGrid");

    claimsList.innerHTML = "";
    manualGrid.innerHTML = "";

    if (!fc) return;

    msgEl.innerText = fc.message || "";

    if (fc.claims && fc.claims.length > 0) {
        fc.claims.forEach(c => {
            const card = document.createElement("div");
            card.className = "factClaimCard";
            card.innerHTML = `
                <div><strong>Claim:</strong> "${c.claim}"</div>
                <div style="font-size:12px; margin-top:4px;">
                    <strong>Rating:</strong> <span style="color:#ffb300; font-weight:600;">${c.rating}</span> |
                    <strong>Fact-Checker:</strong> ${c.publisher}
                    ${c.url ? ` | <a href="${c.url}" target="_blank" rel="noopener noreferrer" style="color:var(--secondary);">Read Review <i class="fa-solid fa-arrow-up-right-from-square" style="font-size:10px;"></i></a>` : ""}
                </div>
            `;
            claimsList.appendChild(card);
        });
    }

    if (fc.manual_links && fc.manual_links.length > 0) {
        fc.manual_links.forEach(link => {
            const a = document.createElement("a");
            a.className = "manualCard";
            a.href = link.url;
            a.target = "_blank";
            a.rel = "noopener noreferrer";
            a.innerHTML = `
                <span>${link.name}</span>
                <i class="fa-solid fa-arrow-up-right-from-square"></i>
            `;
            manualGrid.appendChild(a);
        });
    }
}

// =========================================================
// Feature 6: User Feedback
// =========================================================
function selectFeedbackSentiment(sentiment, btn) {
    selectedFeedbackSentiment = sentiment;
    document.querySelectorAll(".fbBtn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
}

function resetFeedbackUi() {
    selectedFeedbackSentiment = null;
    document.querySelectorAll(".fbBtn").forEach(b => b.classList.remove("active"));
    const commentEl = document.getElementById("feedbackComment");
    if (commentEl) commentEl.value = "";
    const statusEl = document.getElementById("feedbackStatus");
    if (statusEl) statusEl.innerText = "";
}

async function submitFeedback() {
    if (!selectedFeedbackSentiment) {
        showToast("Please select a feedback option (Helpful, Incorrect, or Unsure).");
        return;
    }

    const comment = (document.getElementById("feedbackComment").value || "").trim();
    const statusEl = document.getElementById("feedbackStatus");

    const payload = {
        sentiment: selectedFeedbackSentiment,
        comment: comment,
        prediction: lastPredictionData ? lastPredictionData.prediction : "",
        confidence: lastPredictionData ? lastPredictionData.confidence : 0.0,
        news_excerpt: lastPredictionData ? (document.getElementById("news").value || "").substring(0, 150) : ""
    };

    try {
        const response = await fetch("/feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const res = await response.json();
        if (res.success) {
            statusEl.innerText = "✓ Feedback saved. Thank you!";
            showToast("Thank you for your feedback!");
            setTimeout(() => { resetFeedbackUi(); }, 3500);
        } else {
            showToast(res.error || "Could not save feedback.");
        }
    } catch (e) {
        console.error(e);
        showToast("Failed to submit feedback.");
    }
}

// =========================================================
// Feature 10: Shareable Analysis Report
// =========================================================
async function downloadReport(format) {
    if (!lastPredictionData) {
        showToast("Please analyze an article first before downloading a report.");
        return;
    }

    const reportPayload = {
        format: format,
        timestamp: lastPredictionData.timestamp,
        prediction: lastPredictionData.prediction,
        confidence: lastPredictionData.confidence,
        is_uncertain: lastPredictionData.is_uncertain,
        input_type: lastPredictionData.input_type || currentInputType,
        source_url: lastPredictionData.source_url || currentSourceUrl || "N/A",
        source_domain: lastPredictionData.source_domain || currentSourceDomain || "N/A",
        was_translated: lastPredictionData.was_translated,
        explanation_summary: lastPredictionData.explanation ? lastPredictionData.explanation.summary : "",
        influential_real: lastPredictionData.explanation ? lastPredictionData.explanation.real_words : [],
        influential_fake: lastPredictionData.explanation ? lastPredictionData.explanation.fake_words : [],
        article_excerpt: (document.getElementById("news").value || "").substring(0, 300),
        fact_check_message: lastPredictionData.fact_check ? lastPredictionData.fact_check.message : "",
        fact_check_links: lastPredictionData.fact_check ? lastPredictionData.fact_check.manual_links : []
    };

    try {
        const response = await fetch("/download-report", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(reportPayload)
        });

        if (!response.ok) throw new Error("Report generation failed");

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `FakeNews_Report_${format.toUpperCase()}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showToast(`Downloaded ${format.toUpperCase()} report successfully!`);
    } catch (err) {
        console.error(err);
        showToast("Failed to generate downloadable report.");
    }
}

async function shareSummary() {
    if (!lastPredictionData) {
        showToast("Please analyze an article first.");
        return;
    }

    const pred = lastPredictionData.prediction.toUpperCase();
    const conf = Math.round(lastPredictionData.confidence * 100);
    const uncertainNote = lastPredictionData.is_uncertain ? " (⚠️ Low Confidence Warning)" : "";
    const summary = `FakeNews AI Verification Report:\n• Classification: ${pred} NEWS${uncertainNote}\n• Model Confidence: ${conf}%\n• Source Domain: ${currentSourceDomain || "Direct Input"}\n• Analysis Disclaimer: Statistical NLP model; verify with certified fact-checkers.\nVerified via FakeNews AI`;

    if (navigator.share) {
        try {
            await navigator.share({
                title: "FakeNews AI Analysis Result",
                text: summary
            });
            showToast("Summary shared successfully!");
            return;
        } catch (e) {
            // User cancelled or share failed, fallback to clipboard
        }
    }

    // Fallback: Copy to clipboard
    try {
        await navigator.clipboard.writeText(summary);
        showToast("✓ Summary copied to clipboard!");
    } catch (err) {
        showToast("Could not access clipboard.");
    }
}

// =========================================================
// History Management (Preserved & Enhanced)
// =========================================================
function addHistory(news, prediction, confidence, isUncertain) {
    let history = JSON.parse(localStorage.getItem("predictionHistory")) || [];
    history.unshift({
        news: (news || "").substring(0, 100),
        prediction: prediction,
        confidence: confidence,
        isUncertain: Boolean(isUncertain),
        time: new Date().toLocaleTimeString()
    });
    history = history.slice(0, 8);
    localStorage.setItem("predictionHistory", JSON.stringify(history));
    renderHistory();
}

function renderHistory() {
    const container = document.getElementById("historyList");
    if (!container) return;

    const history = JSON.parse(localStorage.getItem("predictionHistory")) || [];
    if (history.length === 0) {
        container.innerHTML = `
            <div class="historyEmpty" data-i18n="history_empty">
                ${translations[currentLang]?.history_empty || "No predictions yet."}
            </div>
        `;
        return;
    }

    container.innerHTML = "";
    history.forEach(item => {
        let badgeText = item.prediction === "Real" ? "🟢 REAL NEWS" : "🔴 FAKE NEWS";
        if (item.isUncertain) badgeText = "🟡 UNCERTAIN (" + item.prediction + ")";

        container.innerHTML += `
            <div class="historyItem">
                <div class="historyTitle">${badgeText}</div>
                <div class="historyNews">${escapeHtml(item.news)}</div>
                <div class="historyFooter">
                    Confidence: <strong>${item.confidence}%</strong><br>
                    <small>${item.time}</small>
                </div>
            </div>
        `;
    });
}

function clearHistory() {
    localStorage.removeItem("predictionHistory");
    renderHistory();
    showToast("Prediction history cleared.");
}

function escapeHtml(text) {
    if (!text) return "";
    return text.replace(/[&<>"']/g, function(m) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
}

// =========================================================
// Utility Actions (Clear, Undo Reversal, Example, Counter, Toast)
// =========================================================
let lastClearedState = null;

function clearText() {
    const textarea = document.getElementById("news");
    const previousText = (textarea.value || "").trim();
    if (previousText) {
        lastClearedState = {
            text: textarea.value,
            sourceUrl: currentSourceUrl,
            sourceDomain: currentSourceDomain,
            inputType: currentInputType
        };
    }
    textarea.value = "";
    updateCharCount();
    currentSourceUrl = "";
    currentSourceDomain = "";
    selectedOcrFile = null;
    const urlInput = document.getElementById("urlInput");
    if (urlInput) urlInput.value = "";
    const previewCard = document.getElementById("urlPreviewCard");
    if (previewCard) previewCard.style.display = "none";
    const resultCard = document.getElementById("resultCard");
    if (resultCard) resultCard.style.display = "none";
    textarea.focus();

    if (lastClearedState) {
        showToast("Inputs cleared.", "Undo (Ctrl+Z)", undoClear);
    } else {
        showToast("Cleared inputs.");
    }
}

function undoClear() {
    if (!lastClearedState) return;
    const textarea = document.getElementById("news");
    textarea.value = lastClearedState.text;
    currentSourceUrl = lastClearedState.sourceUrl || "";
    currentSourceDomain = lastClearedState.sourceDomain || "";
    if (lastClearedState.inputType) {
        switchInputTab(lastClearedState.inputType.toLowerCase());
    }
    updateCharCount();
    lastClearedState = null;
    showToast("Inputs restored!");
    textarea.focus();
}

function pasteExample() {
    const sampleEn = `Breaking News: Scientists at an international summit confirmed today that a new clean energy solar cell has reached record efficiency in verified laboratory tests.`;
    const sampleHi = `ताज़ा ख़बर: भारतीय वैज्ञानिकों ने सौर ऊर्जा सेल में एक महत्वपूर्ण तकनीकी सफलता हासिल की है जिसकी स्वतंत्र प्रयोगशालाओं द्वारा पुष्टि की गई है।`;
    
    const textarea = document.getElementById("news");
    textarea.value = currentLang === "hi" ? sampleHi : sampleEn;
    updateCharCount();
    showToast("Example news pasted!");
}

function updateCharCount() {
    const textarea = document.getElementById("news");
    const counter = document.getElementById("charCount");
    if (textarea && counter) {
        counter.innerText = textarea.value.length + " / 15000 Characters";
    }
}

const textareaEl = document.getElementById("news");
if (textareaEl) {
    textareaEl.addEventListener("input", updateCharCount);
}

let toastTimer = null;
function showToast(message, actionText, actionCallback) {
    const toast = document.getElementById("toast");
    if (!toast) return;
    clearTimeout(toastTimer);
    toast.innerHTML = "";

    const span = document.createElement("span");
    span.innerText = message;
    toast.appendChild(span);

    if (actionText && typeof actionCallback === "function") {
        const actionBtn = document.createElement("button");
        actionBtn.className = "toastActionBtn";
        actionBtn.innerText = actionText;
        actionBtn.onclick = (e) => {
            e.stopPropagation();
            actionCallback();
            toast.className = "toast";
        };
        toast.appendChild(actionBtn);
    }

    toast.className = "toast show";
    toastTimer = setTimeout(() => {
        toast.className = "toast";
    }, actionText ? 5000 : 3200);
}

// Keyboard Shortcuts Modal Toggle (Shneiderman Rule 2, 7 & 8)
function toggleShortcutsModal() {
    const modal = document.getElementById("shortcutsModal");
    if (!modal) return;
    const isVisible = modal.style.display === "flex";
    modal.style.display = isVisible ? "none" : "flex";
}

// Theme Toggle (Shneiderman Rule 7: Internal Locus of Control)
function toggleTheme() {
    document.body.classList.toggle("light");
    const isLight = document.body.classList.contains("light");
    localStorage.setItem("fakenews_theme", isLight ? "light" : "dark");
    const themeBtn = document.querySelector(".themeBtn");
    if (themeBtn) {
        themeBtn.querySelector("i").className = isLight ? "fa-solid fa-sun" : "fa-solid fa-moon";
    }
    showToast(isLight ? "Light theme enabled" : "Dark theme enabled");
}

const themeBtn = document.querySelector(".themeBtn");
if (themeBtn) {
    // Load saved theme
    if (localStorage.getItem("fakenews_theme") === "light") {
        document.body.classList.add("light");
        themeBtn.querySelector("i").className = "fa-solid fa-sun";
    }
    themeBtn.onclick = toggleTheme;
}

// =========================================================
// Shneiderman Rule 2: Keyboard Shortcuts (Accessible & Non-conflicting)
// =========================================================
document.addEventListener("keydown", function(e) {
    const activeEl = document.activeElement;
    const isEditing = activeEl && (activeEl.tagName === "INPUT" || activeEl.tagName === "TEXTAREA");

    // 1. Ctrl + Enter or Cmd + Enter: Trigger Analysis
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        predictNews();
        return;
    }

    // 2. Ctrl + Z (when not editing text in textarea): Undo accidental clear
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z" && !isEditing) {
        if (lastClearedState) {
            e.preventDefault();
            undoClear();
            return;
        }
    }

    // 3. Escape: Close modal if open, otherwise clear inputs
    if (e.key === "Escape") {
        const modal = document.getElementById("shortcutsModal");
        if (modal && modal.style.display === "flex") {
            modal.style.display = "none";
            return;
        }
        clearText();
        return;
    }

    // 4. Alt + 1, Alt + 2, Alt + 3: Switch Input Tabs
    if (e.altKey && (e.key === "1" || e.code === "Digit1")) {
        e.preventDefault();
        switchInputTab("text");
        return;
    }
    if (e.altKey && (e.key === "2" || e.code === "Digit2")) {
        e.preventDefault();
        switchInputTab("url");
        return;
    }
    if (e.altKey && (e.key === "3" || e.code === "Digit3")) {
        e.preventDefault();
        switchInputTab("ocr");
        return;
    }

    // 5. Alt + L: Toggle Language (English / Hindi)
    if (e.altKey && (e.key.toLowerCase() === "l" || e.code === "KeyL")) {
        e.preventDefault();
        toggleLanguage();
        return;
    }

    // 6. Alt + M: Toggle Simple / Detailed Mode
    if (e.altKey && (e.key.toLowerCase() === "m" || e.code === "KeyM")) {
        e.preventDefault();
        toggleSimpleMode();
        return;
    }

    // 7. Alt + T: Toggle Theme (Dark / Light)
    if (e.altKey && (e.key.toLowerCase() === "t" || e.code === "KeyT")) {
        e.preventDefault();
        toggleTheme();
        return;
    }

    // 8. Alt + K: Toggle Keyboard Shortcuts Modal
    if (e.altKey && (e.key.toLowerCase() === "k" || e.code === "KeyK")) {
        e.preventDefault();
        toggleShortcutsModal();
        return;
    }

    // 9. '?' pressed outside text inputs: Toggle Keyboard Shortcuts Modal
    if (e.key === "?" && !isEditing) {
        e.preventDefault();
        toggleShortcutsModal();
        return;
    }
});

// Cursor Glow Effect
const glow = document.getElementById("cursorGlow");
if (glow) {
    document.addEventListener("mousemove", e => {
        glow.style.left = (e.clientX - 120) + "px";
        glow.style.top = (e.clientY - 120) + "px";
    });
}

// Statistics Animation (Preserved)
function animateCounters() {
    const counters = document.querySelectorAll(".counter");
    counters.forEach(counter => {
        const target = parseFloat(counter.dataset.target);
        const suffix = counter.dataset.suffix || "";
        let current = 0;
        const increment = target / 80;

        function updateCounter() {
            current += increment;
            if (current >= target) {
                counter.innerHTML = target + suffix;
            } else {
                counter.innerHTML = (target < 10 ? current.toFixed(1) : Math.floor(current)) + suffix;
                requestAnimationFrame(updateCounter);
            }
        }
        updateCounter();
    });
}

const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateCounters();
            statsObserver.disconnect();
        }
    });
}, { threshold: 0.3 });

const statsSection = document.querySelector(".stats");
if (statsSection) {
    statsObserver.observe(statsSection);
}

// Window Onload Initialization
window.addEventListener("DOMContentLoaded", () => {
    applyLanguage(currentLang);
    renderHistory();
    updateCharCount();
});
