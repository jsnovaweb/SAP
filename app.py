import streamlit as st
import pandas as pd
import joblib
import os
import numpy as np

# --- Configuration ---
MODEL_PATH = "attached_assets/eligibility_model_1768571674807.joblib"
st.set_page_config(
    page_title="SAP Eligibility Checker",
    page_icon="🇵🇭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a more polished look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #0047ab;
        color: white;
        font-weight: bold;
    }
    .stExpander {
        border: 1px solid #dee2e6;
        border-radius: 5px;
        background-color: white;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    h1 {
        color: #0047ab;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .section-header {
        background-color: #0047ab;
        color: white;
        padding: 10px 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Load Model ---
@st.cache_resource
def load_model():
    """Loads the pre-trained model from the file system."""
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        model = joblib.load(MODEL_PATH)
        return model
    except Exception:
        return None

model = load_model()

# --- Legends ---
SECTOR_LEGEND = {
    "A": "Senior Citizen",
    "B": "Pregnant",
    "C": "Lactating Mother",
    "D": "Person with Disability (PWD)",
    "E": "Solo Parent",
    "F": "Homeless"
}

HEALTH_CONDITION_LEGEND = {
    "1": "Heart Disease",
    "2": "Hypertension",
    "3": "Lung Disease",
    "4": "Diabetes",
    "5": "Cancer"
}

# --- Header ---
st.title("🇵🇭 Social Amelioration Program (SAP) Eligibility Checker")
st.markdown("##### Department of Social Welfare and Development - Official Assessment Tool")
st.info("Enter the beneficiary details below to check for SAP eligibility. Ensure all information is accurate.")

# --- Form Content ---
with st.container():
    st.markdown('<div class="section-header">📋 Main Beneficiary Information</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name", placeholder="Surname, First Name Middle Name")
        c1, c2 = st.columns(2)
        with c1:
            sex = st.selectbox("Sex", ["Male", "Female"])
        with c2:
            age = st.number_input("Age", min_value=0, max_value=120, step=1, value=30)
        
        st.markdown("**Address Details**")
        barangay = st.text_input("Barangay")
        city_municipality = st.text_input("City / Municipality")
        province = st.text_input("Province")

    with col2:
        st.markdown("**Socio-Economic Status**")
        employment_status = st.selectbox("Employment Status", ["Employed", "Self-Employed", "Unemployed", "Informal"])
        employed_members = st.number_input("Number of Employed Members in HH", min_value=0, step=1, value=0)
        monthly_income = st.number_input("Monthly Household Income (PHP)", min_value=0.0, step=100.0, format="%.2f", value=0.0)
        
        st.markdown("**Household Information**")
        household_size = st.number_input("Household Size", min_value=1, step=1, value=1)
        housing_type = st.selectbox("Housing Type", ["Owned", "Rented", "Informal Settler", "Living with Relatives"])

    st.markdown("**Vulnerability & Priority Indicators**")
    v_col1, v_col2, v_col3 = st.columns(3)
    with v_col1:
        is_4ps = st.checkbox("4Ps Beneficiary", help="Current member of Pantawid Pamilyang Pilipino Program")
        has_senior = st.checkbox("Senior Citizen in HH", help="Age 60 or above")
    with v_col2:
        has_pwd = st.checkbox("PWD in Household", help="Person with Disability")
        is_solo_parent = st.checkbox("Solo Parent")
    with v_col3:
        is_disaster_affected = st.checkbox("Disaster-Affected", help="Victim of recent calamities")

# --- Household Members Section ---
household_members_data = []
if household_size > 1:
    st.markdown('<div class="section-header">👨‍👩‍👧‍👦 Household Members Details</div>', unsafe_allow_html=True)
    
    # Unified Legend Expander
    with st.expander("📝 View Input Codes (Sector & Health Condition)"):
        l_col1, l_col2 = st.columns(2)
        with l_col1:
            st.markdown("**SECTOR LEGEND**")
            for code, desc in SECTOR_LEGEND.items():
                st.write(f"**{code}**: {desc}")
        with l_col2:
            st.markdown("**HEALTH CONDITION LEGEND**")
            for code, desc in HEALTH_CONDITION_LEGEND.items():
                st.write(f"**{code}**: {desc}")

    for i in range(int(household_size) - 1):
        with st.container():
            st.markdown(f"**Member #{i + 1}**")
            m_col1, m_col2, m_col3 = st.columns([2, 2, 2])
            
            with m_col1:
                m_name = st.text_input(f"Full Name (S, F, M)", key=f"name_{i}")
                m_relation = st.text_input(f"Relation to Head", key=f"rel_{i}")
            
            with m_col2:
                m_gender = st.selectbox(f"Gender", ["Male", "Female"], key=f"gen_{i}")
                m_occupation = st.text_input(f"Occupation", key=f"occ_{i}")
            
            with m_col3:
                m_sector = st.multiselect(f"Sector (A-F)", options=list(SECTOR_LEGEND.keys()), key=f"sec_{i}")
                m_health = st.multiselect(f"Health (1-5)", options=list(HEALTH_CONDITION_LEGEND.keys()), key=f"hea_{i}")
            
            household_members_data.append({
                "Name": m_name,
                "Relation": m_relation,
                "Gender": m_gender,
                "Occupation": m_occupation,
                "Sector": ", ".join(m_sector),
                "Health": ", ".join(m_health)
            })
            st.divider()

# --- Submission ---
st.markdown("---")
btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
with btn_col2:
    submit_button = st.button("ASSESS ELIGIBILITY", type="primary")

if submit_button:
    if not full_name or not barangay or not city_municipality:
        st.error("⚠️ Please fill in all required fields (Name and Address).")
    else:
        # Results Section
        st.markdown('<div class="section-header">🏁 Assessment Result</div>', unsafe_allow_html=True)
        
        # Prediction Logic
        input_data = {
            "family_id": ["FAM-000"],
            "monthly_income": [float(monthly_income)],
            "family_size": [int(household_size)],
            "employed_members": [int(employed_members)],
            "has_senior": [int(1 if has_senior else 0)],
            "has_pwd": [int(1 if has_pwd else 0)],
            "housing_type": [str(housing_type)],
            "location": [str(f"{barangay}, {city_municipality}")],
            "receives_4ps": [int(1 if is_4ps else 0)]
        }
        input_df = pd.DataFrame(input_data)

        is_eligible = False
        eligibility_text = "Not Eligible"
        
        if model:
            try:
                prediction = model.predict(input_df)[0]
                if isinstance(prediction, (str, bytes)):
                    eligibility_text = prediction if isinstance(prediction, str) else prediction.decode('utf-8')
                    is_eligible = "eligible" in eligibility_text.lower() and "not" not in eligibility_text.lower()
                else:
                    is_eligible = bool(prediction)
                    eligibility_text = "Eligible" if is_eligible else "Not Eligible"
            except Exception:
                # Rule-based fallback if model fails
                is_eligible = monthly_income < 15000 and (employed_members == 0 or is_disaster_affected)
                eligibility_text = "Eligible (System Estimate)" if is_eligible else "Not Eligible (System Estimate)"

        # Visual Feedback
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            if is_eligible:
                st.balloons()
                st.markdown(f"<h2 style='color: green; text-align: center;'>✅ {eligibility_text}</h2>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h2 style='color: red; text-align: center;'>❌ {eligibility_text}</h2>", unsafe_allow_html=True)
        
        with res_col2:
            st.markdown("### Summary Reason")
            if is_eligible:
                st.write("Beneficiary meets the low-income threshold and exhibits priority vulnerability indicators (e.g., unemployment, displacement, or specialized sector status).")
            else:
                st.write("Beneficiary income exceeds current SAP thresholds or household resources are deemed sufficient based on employment data.")

        # Data Summary Table
        with st.expander("📄 View Full Form Summary"):
            st.table(pd.DataFrame([{
                "Full Name": full_name,
                "Income": f"PHP {monthly_income:,.2f}",
                "HH Size": household_size,
                "Location": f"{barangay}, {city_municipality}",
                "4Ps": "Yes" if is_4ps else "No",
                "Employed": employed_members
            }]))
            if household_members_data:
                st.write("**Additional Members:**")
                st.dataframe(pd.DataFrame(household_members_data))
