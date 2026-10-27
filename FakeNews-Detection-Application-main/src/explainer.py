"""Explainable AI (XAI) module for TF-IDF + Logistic Regression."""
import numpy as np


def explain_prediction(model, cleaned_text, raw_text="", simple_mode=False, language="en"):
    """
    Computes feature contributions for the TF-IDF + Logistic Regression pipeline.
    
    In this model:
      - Class 0 = Fake
      - Class 1 = Real
      - Logit z = sum(tfidf_i * coef_i) + intercept
      - A positive impact (tfidf_i * coef_i > 0) pushes the prediction toward REAL (Class 1).
      - A negative impact (tfidf_i * coef_i < 0) pushes the prediction toward FAKE (Class 0).
      
    Returns a dictionary containing top influential words for both classes,
    plain-language explanation, and honest disclaimers.
    """
    result = {
        "supported": False,
        "simple_mode": simple_mode,
        "language": language,
        "real_words": [],
        "fake_words": [],
        "summary": "",
        "disclaimer": (
            "Model feature attribution reflects statistical word associations learned from training data. "
            "Influential words indicate stylistic and lexical tendencies, NOT verified factual truth or falsehood."
        )
    }

    if not cleaned_text or not cleaned_text.strip():
        result["summary"] = (
            "No extractable English vocabulary words were found after cleaning. "
            "A reliable word-by-word feature explanation cannot be generated for this input."
            if language == "en" else
            "सफाई के बाद कोई निकालने योग्य शब्द नहीं मिले। इस इनपुट के लिए शब्द-दर-शब्द व्याख्या उत्पन्न नहीं की जा सकती।"
        )
        return result

    try:
        tfidf = model.named_steps.get("tfidf")
        classifier = model.named_steps.get("classifier")

        if tfidf is None or classifier is None:
            result["summary"] = "The pipeline steps do not support feature weight extraction."
            return result

        feature_names = np.array(tfidf.get_feature_names_out())
        coefs = classifier.coef_[0]

        # Vectorize cleaned text
        x_vec = tfidf.transform([cleaned_text])
        nonzero_indices = x_vec.nonzero()[1]

        if len(nonzero_indices) == 0:
            result["summary"] = (
                "The words in this text were not present in the model's learned 20,000-word vocabulary. "
                "The prediction relied on baseline prior probabilities rather than specific vocabulary cues."
            )
            return result

        contributions = []
        for idx in nonzero_indices:
            word = str(feature_names[idx])
            weight = float(x_vec[0, idx])
            coef = float(coefs[idx])
            impact = weight * coef
            contributions.append({
                "word": word,
                "weight": round(weight, 4),
                "coef": round(coef, 4),
                "impact": round(impact, 4),
                # If impact > 0 pushes toward Real (Class 1); if impact < 0 pushes toward Fake (Class 0)
                "favors": "Real" if impact > 0 else "Fake",
                "abs_impact": abs(impact)
            })

        # Separate words favoring Real vs Fake, sorted by absolute impact
        real_words = [c for c in contributions if c["favors"] == "Real"]
        fake_words = [c for c in contributions if c["favors"] == "Fake"]

        real_words.sort(key=lambda x: x["abs_impact"], reverse=True)
        fake_words.sort(key=lambda x: x["abs_impact"], reverse=True)

        result["supported"] = True
        result["real_words"] = real_words[:8]
        result["fake_words"] = fake_words[:8]

        # Generate readable explanation based on mode and language
        top_real_names = [w["word"] for w in real_words[:3]]
        top_fake_names = [w["word"] for w in fake_words[:3]]

        if simple_mode:
            if language == "hi":
                if len(fake_words) > len(real_words):
                    result["summary"] = (
                        f"इस लेख में प्रयुक्त कुछ शब्द ({', '.join(top_fake_names) if top_fake_names else 'संकेत'}) "
                        "आमतौर पर गैर-सत्यापित या भ्रामक खबरों में देखे जाने वाले पैटर्न से मेल खाते हैं।"
                    )
                else:
                    result["summary"] = (
                        f"इस लेख की शब्दावली ({', '.join(top_real_names) if top_real_names else 'संकेत'}) "
                        "पारंपरिक समाचार रिपोर्टिंग की शैली से काफी मिलती-जुलती है।"
                    )
            else:
                if len(fake_words) > len(real_words):
                    result["summary"] = (
                        f"Words such as {', '.join([repr(w) for w in top_fake_names]) if top_fake_names else 'certain phrasing'} "
                        "align with lexical patterns frequently observed in sensational or unverified claims."
                    )
                else:
                    result["summary"] = (
                        f"Words such as {', '.join([repr(w) for w in top_real_names]) if top_real_names else 'standard journalistic wording'} "
                        "align with vocabulary typical of verified reporting in the training dataset."
                    )
        else:
            # Detailed mode
            if language == "hi":
                result["summary"] = (
                    f"TF-IDF और लॉजिस्टिक रिग्रेशन विश्लेषण: "
                    f"सत्य (Real) की ओर झुकाव वाले मुख्य शब्द: {', '.join(top_real_names) if top_real_names else 'कोई नहीं'}; "
                    f"भ्रामक (Fake) की ओर झुकाव वाले मुख्य शब्द: {', '.join(top_fake_names) if top_fake_names else 'कोई नहीं'}।"
                )
            else:
                result["summary"] = (
                    f"Linear model log-odds decomposition: "
                    f"Top tokens increasing probability of REAL: {', '.join(top_real_names) if top_real_names else 'None'}; "
                    f"Top tokens increasing probability of FAKE: {', '.join(top_fake_names) if top_fake_names else 'None'}."
                )

    except Exception as e:
        result["supported"] = False
        result["summary"] = f"Feature contribution analysis encountered an unexpected error: {str(e)}"

    return result
