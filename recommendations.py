# recommendations.py
# Personalized health recommendations based on patient inputs

def get_recommendations(male, age, currentSmoker, cigsPerDay, BPMeds,
                         prevalentStroke, prevalentHyp, diabetes,
                         totChol, sysBP, diaBP, BMI, heartRate, glucose, risk_pct):
    """
    Takes all 14 patient inputs + the predicted risk percentage.
    Returns a dictionary with three lists:
      - urgent      : 🚨 needs immediate medical attention
      - important   : ⚠️  should actively work on improving
      - maintain    : ✅  things that are good — keep it up
    """

    urgent    = []
    important = []
    maintain  = []

    # ── SMOKING ──────────────────────────────────────────────────────────────
    if currentSmoker == 1 and cigsPerDay > 20:
        urgent.append(
            "🚨 **Heavy Smoker Alert:** You smoke more than 20 cigarettes a day. "
            "This is one of the single biggest modifiable risk factors for heart disease. "
            "Speak to your doctor about a structured quit plan — medications and nicotine "
            "replacement therapy significantly improve success rates."
        )
    elif currentSmoker == 1 and cigsPerDay > 0:
        important.append(
            "⚠️ **Smoking:** You are a current smoker. Even a small number of cigarettes "
            "per day substantially raises your heart disease risk. Consider a quit plan — "
            "apps like Smoke Free or speaking to your GP are great starting points."
        )
    else:
        maintain.append(
            "✅ **Non-Smoker:** You do not smoke. This is excellent for your heart health. "
            "Avoid exposure to secondhand smoke where possible."
        )

    # ── BLOOD PRESSURE ───────────────────────────────────────────────────────
    if sysBP >= 140 or diaBP >= 90:
        urgent.append(
            f"🚨 **High Blood Pressure (Stage 2):** Your reading is {sysBP}/{diaBP} mmHg, "
            "which is in the Stage 2 hypertension range. This directly strains the heart. "
            "Please consult your doctor promptly. Reduce salt intake, limit alcohol, "
            "exercise regularly, and take any prescribed medication consistently."
        )
    elif sysBP >= 130 or diaBP >= 80:
        important.append(
            f"⚠️ **Elevated Blood Pressure:** Your reading is {sysBP}/{diaBP} mmHg. "
            "This is above the healthy range. Steps to lower it: reduce processed/salty foods, "
            "aim for 30 minutes of brisk walking daily, manage stress, and limit alcohol."
        )
    elif sysBP >= 120:
        important.append(
            f"⚠️ **Slightly Elevated Systolic BP:** Your systolic pressure is {sysBP} mmHg. "
            "This is in the 'elevated' category. Monitor it regularly and maintain an "
            "active lifestyle to prevent it from rising further."
        )
    else:
        maintain.append(
            f"✅ **Blood Pressure is Normal:** Your reading of {sysBP}/{diaBP} mmHg is healthy. "
            "Keep maintaining a low-sodium diet and regular physical activity."
        )

    # ── CHOLESTEROL ──────────────────────────────────────────────────────────
    if totChol >= 240:
        urgent.append(
            f"🚨 **High Cholesterol:** Your total cholesterol is {totChol} mg/dL, "
            "which is in the 'High' range (≥240). High cholesterol silently builds up "
            "plaque in arteries. Reduce saturated fats (red meat, full-fat dairy), "
            "increase fibre (oats, beans, vegetables), and ask your doctor about statins."
        )
    elif totChol >= 200:
        important.append(
            f"⚠️ **Borderline Cholesterol:** Your total cholesterol is {totChol} mg/dL. "
            "This is in the borderline range (200–239). Switch to healthy fats "
            "(olive oil, nuts, avocado), increase physical activity, and get "
            "a full lipid panel (LDL/HDL breakdown) from your doctor."
        )
    else:
        maintain.append(
            f"✅ **Cholesterol is Normal:** Your total cholesterol of {totChol} mg/dL "
            "is in the healthy range. Continue with a balanced, low-saturated-fat diet."
        )

    # ── BMI ──────────────────────────────────────────────────────────────────
    if BMI >= 30:
        urgent.append(
            f"🚨 **Obese BMI ({BMI:.1f}):** A BMI of 30 or above significantly increases "
            "strain on the heart. Even a 5–10% reduction in body weight can meaningfully "
            "reduce your heart disease risk. Focus on caloric deficit through diet changes "
            "and aim for 150 minutes of moderate exercise per week."
        )
    elif BMI >= 25:
        important.append(
            f"⚠️ **Overweight BMI ({BMI:.1f}):** Your BMI is in the overweight range (25–29.9). "
            "Aim for gradual weight loss through portion control and regular exercise. "
            "Even losing 5 kg can improve blood pressure and cholesterol."
        )
    elif BMI < 18.5:
        important.append(
            f"⚠️ **Underweight BMI ({BMI:.1f}):** A BMI below 18.5 can indicate nutritional "
            "deficiency, which also affects heart health. Consult a doctor or dietitian "
            "to ensure you're getting adequate nutrients."
        )
    else:
        maintain.append(
            f"✅ **Healthy BMI ({BMI:.1f}):** Your BMI is in the healthy range (18.5–24.9). "
            "Maintain your current weight through balanced eating and regular movement."
        )

    # ── GLUCOSE ──────────────────────────────────────────────────────────────
    if glucose >= 126:
        urgent.append(
            f"🚨 **Diabetic Glucose Level ({glucose} mg/dL):** A fasting glucose of 126+ "
            "is in the diabetic range. Uncontrolled blood sugar damages blood vessels and "
            "nerves around the heart. Consult your doctor immediately for an HbA1c test. "
            "Reduce sugary foods, refined carbohydrates, and increase physical activity."
        )
    elif glucose >= 100:
        important.append(
            f"⚠️ **Pre-Diabetic Glucose Level ({glucose} mg/dL):** Your glucose is in the "
            "pre-diabetic range (100–125). This is reversible. Cut out sugary drinks, "
            "reduce white rice/bread/pasta, walk after meals, and get tested annually."
        )
    else:
        maintain.append(
            f"✅ **Glucose is Normal ({glucose} mg/dL):** Your blood sugar is in the healthy "
            "range. Maintain a low-sugar, high-fibre diet to keep it there."
        )

    # ── HEART RATE ───────────────────────────────────────────────────────────
    if heartRate > 100:
        important.append(
            f"⚠️ **Elevated Heart Rate ({heartRate} bpm):** A resting heart rate above 100 "
            "(tachycardia) can indicate stress, dehydration, thyroid issues, or poor "
            "cardiovascular fitness. Stay hydrated, practice deep breathing, reduce "
            "caffeine, and consult a doctor if it persists."
        )
    elif heartRate < 60:
        maintain.append(
            f"✅ **Low-Normal Heart Rate ({heartRate} bpm):** A resting heart rate below 60 "
            "often indicates good cardiovascular fitness (common in athletes). "
            "If you feel dizzy or fatigued, mention it to your doctor."
        )
    else:
        maintain.append(
            f"✅ **Heart Rate is Normal ({heartRate} bpm):** Your resting heart rate is "
            "in the healthy range (60–100 bpm). Regular aerobic exercise helps keep it low."
        )

    # ── DIABETES ─────────────────────────────────────────────────────────────
    if diabetes == 1:
        urgent.append(
            "🚨 **Diagnosed Diabetes:** People with diabetes are 2–4× more likely to develop "
            "heart disease. Strict blood sugar control is essential. Take all prescribed "
            "medications, monitor glucose regularly, follow a diabetic-friendly diet, "
            "and have a cardiac check-up at least once a year."
        )

    # ── HYPERTENSION (pre-existing) ──────────────────────────────────────────
    if prevalentHyp == 1:
        important.append(
            "⚠️ **Pre-existing Hypertension:** You have a history of hypertension. "
            "Even if your current BP reading looks okay, consistent management is vital. "
            "Take medications as prescribed, track your BP at home weekly, "
            "and attend all follow-up appointments."
        )

    # ── STROKE HISTORY ───────────────────────────────────────────────────────
    if prevalentStroke == 1:
        urgent.append(
            "🚨 **History of Stroke:** A previous stroke substantially raises your risk "
            "of a future cardiac event. You should be under regular specialist care. "
            "Antiplatelet or anticoagulant therapy, blood pressure control, and lifestyle "
            "changes are critical. Do not skip any medical appointments."
        )

    # ── BP MEDICATION ────────────────────────────────────────────────────────
    if BPMeds == 1:
        important.append(
            "⚠️ **On Blood Pressure Medication:** Ensure you are taking your medication "
            "consistently — missing doses can cause dangerous spikes. Do not stop "
            "medication without consulting your doctor, even if your BP reads normal. "
            "Report any side effects promptly."
        )

    # ── AGE ──────────────────────────────────────────────────────────────────
    if age >= 65:
        important.append(
            f"⚠️ **Age ({age} years):** Age is a non-modifiable risk factor, but risk can "
            "be managed. At 65+, annual cardiac screenings are recommended. "
            "Stay physically active, maintain social connections (good for heart health), "
            "and review all medications with your doctor regularly."
        )
    elif age >= 50:
        important.append(
            f"⚠️ **Age ({age} years):** From age 50 onward, heart disease risk increases. "
            "Schedule a preventive cardiac health check-up if you haven't recently. "
            "Regular exercise and diet become even more important now."
        )

    # ── GENDER-SPECIFIC ──────────────────────────────────────────────────────
    if male == 0 and age >= 50:
        important.append(
            "⚠️ **Post-Menopausal Risk:** Women's heart disease risk rises significantly "
            "after menopause. Estrogen previously offered some protection. Now is the time "
            "to be more vigilant about blood pressure, cholesterol, and weight management."
        )

    # ── HIGH OVERALL RISK MESSAGE ─────────────────────────────────────────────
    if risk_pct >= 20:
        urgent.append(
            f"🚨 **Overall Risk is High ({risk_pct}%):** Your predicted 10-year risk of "
            "heart disease is in the high range. Please schedule a full cardiovascular "
            "assessment with your doctor as soon as possible. Bring this report with you."
        )
    elif risk_pct >= 10:
        important.append(
            f"⚠️ **Moderate Overall Risk ({risk_pct}%):** Your risk is moderate. "
            "Addressing the factors flagged above can meaningfully reduce this. "
            "A preventive cardiology consultation is strongly recommended."
        )

    return {
        "urgent"   : urgent,
        "important": important,
        "maintain" : maintain
    }