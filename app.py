import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import matplotlib
matplotlib.use('Agg')
from recommendations import get_recommendations
from report_generator import generate_pdf_report

# ── Load models ───────────────────────────────────────────────────────────────
model         = joblib.load('heart_model_framingham.pkl')
scaler        = joblib.load('scaler_framingham.pkl')
feature_names = joblib.load('feature_names_framingham.pkl')
explainer     = joblib.load('shap_explainer_framingham.pkl')

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Heart Disease Risk Predictor",
    page_icon="🫀",
    layout="wide"
)

# ── CSS styling ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .section-header {
        background: linear-gradient(90deg, #1a6fa8 0%, #2196c4 100%);
        color: white;
        padding: 10px 18px;
        border-radius: 8px;
        margin-bottom: 16px;
        font-size: 18px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🫀 Heart Disease Risk Predictor")
st.markdown("Based on the **Framingham Heart Study** — predicts your **10-year risk** of developing heart disease.")
st.markdown("---")

# ── About section ─────────────────────────────────────────────────────────────
with st.expander("ℹ️  About This App — Click to expand", expanded=False):
    st.markdown("**What is this app?**")
    st.markdown("This is an AI-powered Heart Disease Risk Predictor built using the **Framingham Heart Study** dataset — one of the most respected cardiovascular research studies in history, tracking over 4,000 patients across decades.")

    st.markdown("**What does it predict?**")
    st.markdown("It estimates your **10-year risk** of developing coronary heart disease (CHD) based on 14 health and lifestyle factors you provide.")

    st.markdown("**How does the AI work?**")
    st.markdown("A **Logistic Regression** model was trained on the Framingham dataset. It was selected after comparing three models (also tested: Random Forest, XGBoost). The model achieved an **AUC of 0.70**, which is within the published range for Framingham-based ML research.")

    st.markdown("**What is SHAP?**")
    st.markdown("SHAP (SHapley Additive exPlanations) is a technique that breaks down the AI's prediction and tells you *which* factors drove your risk up or down — and by how much. This makes the AI **explainable**, not just a black box.")

    st.markdown("**Who built this?**")
    st.markdown("This app was built as a complete end-to-end clinical decision support system, combining machine learning, explainable AI, personalised recommendations, and a downloadable PDF report.")

    st.info("⚠️ **Important:** This tool is for **educational purposes only**. It is not a medical diagnosis. Always consult a licensed physician.")

st.markdown("---")

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🧾 Patient Summary")
st.sidebar.markdown("Your entered details will appear here after you click Predict.")

# ── Input form ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Enter Your Health Details</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    male = st.selectbox(
        "Gender",
        options=[1, 0],
        format_func=lambda x: "Male" if x == 1 else "Female"
    )
    age             = st.slider("Age (years)",          min_value=20,   max_value=90,  value=45)
    currentSmoker   = st.selectbox(
        "Currently Smoking?",
        options=[1, 0],
        format_func=lambda x: "Yes" if x == 1 else "No"
    )
    cigsPerDay      = st.slider("Cigarettes Per Day",   min_value=0,    max_value=60,  value=0)
    BPMeds          = st.selectbox(
        "On Blood Pressure Medication?",
        options=[0, 1],
        format_func=lambda x: "Yes" if x == 1 else "No"
    )
    prevalentStroke = st.selectbox(
        "History of Stroke?",
        options=[0, 1],
        format_func=lambda x: "Yes" if x == 1 else "No"
    )
    prevalentHyp    = st.selectbox(
        "History of Hypertension?",
        options=[0, 1],
        format_func=lambda x: "Yes" if x == 1 else "No"
    )

with col2:
    diabetes  = st.selectbox(
        "Has Diabetes?",
        options=[0, 1],
        format_func=lambda x: "Yes" if x == 1 else "No"
    )
    totChol   = st.slider("Total Cholesterol (mg/dL)", min_value=100,  max_value=600, value=200)
    sysBP     = st.slider("Systolic Blood Pressure",   min_value=80,   max_value=300, value=120)
    diaBP     = st.slider("Diastolic Blood Pressure",  min_value=40,   max_value=200, value=80)
    BMI       = st.slider("BMI",                       min_value=10.0, max_value=60.0, value=25.0, step=0.1)
    heartRate = st.slider("Heart Rate (bpm)",          min_value=40,   max_value=200, value=75)
    glucose   = st.slider("Glucose Level (mg/dL)",     min_value=40,   max_value=400, value=85)

st.markdown("---")


# ── Helper: health benchmarks ─────────────────────────────────────────────────
def get_benchmarks(totChol, sysBP, diaBP, BMI, heartRate, glucose, currentSmoker, cigsPerDay):
    rows = []

    if totChol < 200:
        status, score = "Normal ✅", min(totChol / 200 * 50, 50)
    elif totChol < 240:
        status, score = "Borderline ⚠️", 65
    else:
        status, score = "High 🔴", min(90, 70 + (totChol - 240) / 10)
    rows.append({"Metric": "Total Cholesterol", "Your Value": f"{totChol} mg/dL",
                 "Normal Range": "< 200 mg/dL", "Status": status, "score": score})

    if sysBP < 120:
        status, score = "Normal ✅", 30
    elif sysBP < 130:
        status, score = "Elevated ⚠️", 55
    elif sysBP < 140:
        status, score = "High Stage 1 ⚠️", 70
    else:
        status, score = "High Stage 2 🔴", min(95, 80 + (sysBP - 140) / 10)
    rows.append({"Metric": "Systolic BP", "Your Value": f"{sysBP} mmHg",
                 "Normal Range": "< 120 mmHg", "Status": status, "score": score})

    if diaBP < 80:
        status, score = "Normal ✅", 30
    elif diaBP < 90:
        status, score = "High Stage 1 ⚠️", 65
    else:
        status, score = "High Stage 2 🔴", min(95, 75 + (diaBP - 90) / 5)
    rows.append({"Metric": "Diastolic BP", "Your Value": f"{diaBP} mmHg",
                 "Normal Range": "< 80 mmHg", "Status": status, "score": score})

    if BMI < 18.5:
        status, score = "Underweight ⚠️", 55
    elif BMI < 25:
        status, score = "Normal ✅", 25
    elif BMI < 30:
        status, score = "Overweight ⚠️", 60
    else:
        status, score = "Obese 🔴", min(95, 70 + (BMI - 30) * 1.5)
    rows.append({"Metric": "BMI", "Your Value": f"{BMI:.1f}",
                 "Normal Range": "18.5 – 24.9", "Status": status, "score": score})

    if 60 <= heartRate <= 100:
        status, score = "Normal ✅", 25
    elif heartRate < 60:
        status, score = "Low ⚠️", 50
    else:
        status, score = "High ⚠️", 60
    rows.append({"Metric": "Heart Rate", "Your Value": f"{heartRate} bpm",
                 "Normal Range": "60 – 100 bpm", "Status": status, "score": score})

    if glucose < 100:
        status, score = "Normal ✅", 25
    elif glucose < 126:
        status, score = "Pre-diabetic ⚠️", 60
    else:
        status, score = "Diabetic Range 🔴", min(95, 75 + (glucose - 126) / 10)
    rows.append({"Metric": "Fasting Glucose", "Your Value": f"{glucose} mg/dL",
                 "Normal Range": "< 100 mg/dL", "Status": status, "score": score})

    if currentSmoker == 0:
        status, score = "Normal ✅", 10
    elif cigsPerDay <= 10:
        status, score = "Borderline ⚠️", 55
    else:
        status, score = "High Risk 🔴", min(95, 65 + cigsPerDay)
    rows.append({"Metric": "Smoking", "Your Value": f"{'Yes' if currentSmoker else 'No'} ({cigsPerDay}/day)",
                 "Normal Range": "Non-smoker", "Status": status, "score": score})

    return rows


# ── Helper: health bar chart ──────────────────────────────────────────────────
def make_health_bar_chart(bench_rows):
    metrics = [r["Metric"] for r in bench_rows]
    scores  = [r["score"]  for r in bench_rows]
    labels  = [f"{r['Your Value']}  —  {r['Status']}" for r in bench_rows]

    colors_list = []
    for r in bench_rows:
        if "✅" in r["Status"]:
            colors_list.append("#1a9850")
        elif "⚠️" in r["Status"]:
            colors_list.append("#f77f00")
        else:
            colors_list.append("#d73027")

    fig = go.Figure(go.Bar(
        x            = scores,
        y            = metrics,
        orientation  = 'h',
        marker_color = colors_list,
        text         = labels,
        textposition = 'outside',
        cliponaxis   = False,
    ))
    fig.update_layout(
        title        = "Health Status — How Each Value Compares to Normal",
        xaxis        = dict(range=[0, 130], showticklabels=False, showgrid=False, zeroline=False),
        yaxis        = dict(autorange="reversed"),
        height       = 380,
        margin       = dict(t=50, b=20, l=130, r=250),
        paper_bgcolor= "rgba(0,0,0,0)",
        plot_bgcolor = "rgba(0,0,0,0)",
    )
    fig.add_vline(x=50, line_dash="dash", line_color="gray", line_width=1,
                  annotation_text="Caution line", annotation_position="top")
    return fig


# ── Predict button ────────────────────────────────────────────────────────────
if st.button("🔍 Predict My Heart Disease Risk", use_container_width=True):

    input_data = pd.DataFrame([[
        male, age, currentSmoker, cigsPerDay, BPMeds,
        prevalentStroke, prevalentHyp, diabetes,
        totChol, sysBP, diaBP, BMI, heartRate, glucose
    ]], columns=feature_names)

    input_scaled    = scaler.transform(input_data)
    input_scaled_df = pd.DataFrame(input_scaled, columns=feature_names)

    risk_prob = model.predict_proba(input_scaled_df)[0][1]
    risk_pct  = round(risk_prob * 100, 1)

    if risk_pct >= 20:
        risk_label = "High Risk"
        risk_color = "#d73027"
    elif risk_pct >= 10:
        risk_label = "Moderate Risk"
        risk_color = "#fc8d59"
    else:
        risk_label = "Low Risk"
        risk_color = "#1a9850"

    # ── Sidebar summary ───────────────────────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Gender:** {'Male' if male == 1 else 'Female'}")
    st.sidebar.markdown(f"**Age:** {age} years")
    st.sidebar.markdown(f"**Smoker:** {'Yes' if currentSmoker == 1 else 'No'}")
    st.sidebar.markdown(f"**Cigarettes/Day:** {cigsPerDay}")
    st.sidebar.markdown(f"**BP Medication:** {'Yes' if BPMeds == 1 else 'No'}")
    st.sidebar.markdown(f"**Stroke History:** {'Yes' if prevalentStroke == 1 else 'No'}")
    st.sidebar.markdown(f"**Hypertension:** {'Yes' if prevalentHyp == 1 else 'No'}")
    st.sidebar.markdown(f"**Diabetes:** {'Yes' if diabetes == 1 else 'No'}")
    st.sidebar.markdown(f"**Total Cholesterol:** {totChol} mg/dL")
    st.sidebar.markdown(f"**Systolic BP:** {sysBP}")
    st.sidebar.markdown(f"**Diastolic BP:** {diaBP}")
    st.sidebar.markdown(f"**BMI:** {BMI}")
    st.sidebar.markdown(f"**Heart Rate:** {heartRate} bpm")
    st.sidebar.markdown(f"**Glucose:** {glucose} mg/dL")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Risk Result")
    st.sidebar.markdown(
        f"<span style='color:{risk_color}; font-size:20px; font-weight:bold'>"
        f"{risk_pct}% — {risk_label}</span>",
        unsafe_allow_html=True
    )

    # ── Risk gauge ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Your Predicted Risk Score</div>', unsafe_allow_html=True)

    gauge_fig = go.Figure(go.Indicator(
        mode   = "gauge+number+delta",
        value  = risk_pct,
        number = {'suffix': "%", 'font': {'size': 48}},
        delta  = {'reference': 10, 'increasing': {'color': "#d73027"}, 'decreasing': {'color': "#1a9850"}},
        gauge  = {
            'axis'   : {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar'    : {'color': risk_color},
            'bgcolor': "white",
            'steps'  : [
                {'range': [0,  10], 'color': '#d4edda'},
                {'range': [10, 20], 'color': '#fff3cd'},
                {'range': [20, 100],'color': '#f8d7da'},
            ],
            'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': risk_pct}
        },
        title  = {'text': f"10-Year Heart Disease Risk — {risk_label}", 'font': {'size': 20}}
    ))
    gauge_fig.update_layout(
        height=350,
        margin=dict(t=60, b=20, l=40, r=40),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(gauge_fig, use_container_width=True)

    if risk_pct >= 20:
        st.error(f"⚠️ **{risk_pct}% — High Risk** of developing heart disease in the next 10 years.")
    elif risk_pct >= 10:
        st.warning(f"🟡 **{risk_pct}% — Moderate Risk** of developing heart disease in the next 10 years.")
    else:
        st.success(f"✅ **{risk_pct}% — Low Risk** of developing heart disease in the next 10 years.")

    st.markdown("---")

    # ── Health benchmarks ─────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🏥 How Your Values Compare to Healthy Ranges</div>', unsafe_allow_html=True)
    st.markdown("The table and chart below compare each of your values against clinically accepted normal ranges.")

    bench_rows = get_benchmarks(totChol, sysBP, diaBP, BMI, heartRate, glucose, currentSmoker, cigsPerDay)

    n_normal = sum("✅" in r["Status"] for r in bench_rows)
    n_border = sum("⚠️" in r["Status"] for r in bench_rows)
    n_high   = sum("🔴" in r["Status"] for r in bench_rows)

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("✅ Normal",     n_normal)
    mc2.metric("⚠️ Borderline", n_border)
    mc3.metric("🔴 High Risk",  n_high)

    st.markdown("####")
    bench_df = pd.DataFrame([{k: v for k, v in r.items() if k != "score"} for r in bench_rows])
    st.dataframe(
        bench_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Metric"      : st.column_config.TextColumn("Health Metric", width="medium"),
            "Your Value"  : st.column_config.TextColumn("Your Value",    width="small"),
            "Normal Range": st.column_config.TextColumn("Normal Range",  width="small"),
            "Status"      : st.column_config.TextColumn("Status",        width="medium"),
        }
    )

    st.markdown("####")
    health_bar_fig = make_health_bar_chart(bench_rows)
    st.plotly_chart(health_bar_fig, use_container_width=True)

    st.markdown("---")

    # ── SHAP breakdown ────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🔍 Why Is Your Risk This Level?</div>', unsafe_allow_html=True)
    st.markdown("Each bar shows how much that factor **increased** 🔴 or **decreased** 🔵 your risk score.")

    shap_values = explainer.shap_values(input_scaled_df)

    if isinstance(shap_values, list):
        shap_vals_patient = shap_values[1][0]
    elif shap_values.ndim == 3:
        shap_vals_patient = shap_values[0, :, 1]
    else:
        shap_vals_patient = shap_values[0]

    shap_series = pd.Series(shap_vals_patient, index=feature_names).sort_values()
    bar_colors  = ['#d73027' if v > 0 else '#4575b4' for v in shap_series.values]

    shap_fig = go.Figure(go.Bar(
        x            = shap_series.values,
        y            = shap_series.index,
        orientation  = 'h',
        marker_color = bar_colors,
        text         = [f"{v:+.4f}" for v in shap_series.values],
        textposition = 'outside'
    ))
    shap_fig.update_layout(
        title        = "Risk Factor Breakdown — What Is Driving Your Risk?",
        xaxis_title  = "SHAP Value (Impact on Risk Score)",
        yaxis_title  = "",
        height       = 500,
        margin       = dict(t=50, b=40, l=160, r=80),
        paper_bgcolor= "rgba(0,0,0,0)",
        plot_bgcolor = "rgba(0,0,0,0)",
        xaxis        = dict(zeroline=True, zerolinewidth=2, zerolinecolor='black'),
    )
    st.plotly_chart(shap_fig, use_container_width=True)

    st.markdown("---")

    # ── Recommendations ───────────────────────────────────────────────────────
    st.markdown('<div class="section-header">💊 Personalised Health Recommendations</div>', unsafe_allow_html=True)
    st.markdown("Based on your inputs, here are specific, actionable steps tailored to your health profile.")

    recs = get_recommendations(
        male, age, currentSmoker, cigsPerDay, BPMeds,
        prevalentStroke, prevalentHyp, diabetes,
        totChol, sysBP, diaBP, BMI, heartRate, glucose, risk_pct
    )

    if recs["urgent"]:
        st.markdown("### 🚨 Urgent — Please Discuss With Your Doctor")
        for item in recs["urgent"]:
            st.error(item)

    if recs["important"]:
        st.markdown("### ⚠️ Important — Work on Improving These")
        for item in recs["important"]:
            st.warning(item)

    if recs["maintain"]:
        st.markdown("### ✅ Keep It Up — These Look Good")
        for item in recs["maintain"]:
            st.success(item)

    st.markdown("---")

    # ── PDF download ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📄 Download Your Report</div>', unsafe_allow_html=True)
    st.markdown("Click the button below to download a full PDF report — suitable to share with your doctor.")

    shap_tuples = sorted(
        zip(feature_names, shap_vals_patient),
        key=lambda x: abs(x[1]),
        reverse=True
    )

    pdf_bytes = generate_pdf_report(
        male=male, age=age, currentSmoker=currentSmoker,
        cigsPerDay=cigsPerDay, BPMeds=BPMeds,
        prevalentStroke=prevalentStroke, prevalentHyp=prevalentHyp,
        diabetes=diabetes, totChol=totChol, sysBP=sysBP,
        diaBP=diaBP, BMI=BMI, heartRate=heartRate, glucose=glucose,
        risk_pct=risk_pct, risk_label=risk_label, risk_color_hex=risk_color,
        bench_rows=bench_rows,
        shap_data=shap_tuples,
        recs=recs,
    )

    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_bytes,
        file_name=f"heart_risk_report_{age}yrs_{risk_label.replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )


# ── Footer disclaimer ─────────────────────────────────────────────────────────
st.markdown("---")
st.warning(
    "⚠️ **Medical Disclaimer** — This application is built for **educational and research "
    "purposes only**. It is not a substitute for professional medical advice, diagnosis, or "
    "treatment. The predictions are based on a statistical model trained on the Framingham "
    "Heart Study dataset and carry inherent uncertainty (model AUC ≈ 0.70). **Always consult "
    "a qualified physician or cardiologist** before making any health decisions. Do not use "
    "this app in a clinical or emergency setting."
)
st.caption("Heart Disease Risk Predictor — Built using the Framingham Heart Study | Powered by Python, Streamlit, scikit-learn & SHAP")