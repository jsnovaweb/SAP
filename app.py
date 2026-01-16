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

# Custom CSS for a professional, formal, and government-friendly DARK MODE look
st.markdown("""
    <style>
    /* Professional Dark Background */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    
    /* Clean, Professional Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 4px;
        height: 3em;
        background-color: #0038a8; /* Philippine Blue */
        color: white;
        font-weight: 600;
        font-size: 16px;
        border: 1px solid #30363d;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #002d86;
        color: white;
        border-color: #8b949e;
    }
    
    /* Standard UI Text */
    h1 {
        color: #58a6ff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 700;
        text-align: left;
        border-bottom: 2px solid #ce1126; /* Philippine Red accent */
        padding-bottom: 10px;
    }
    h2, h3 {
        color: #e6edf3;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        margin-top: 20px;
    }
    
    .section-header {
        background-color: #161b22;
        color: #e6edf3;
        padding: 12px 20px;
        border-radius: 4px;
        margin-bottom: 20px;
        font-size: 18px;
        font-weight: 600;
        border-left: 5px solid #0038a8;
        border-top: 1px solid #30363d;
        border-right: 1px solid #30363d;
        border-bottom: 1px solid #30363d;
    }
    
    /* Input Fields */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        border-radius: 4px !important;
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        border-color: #30363d !important;
    }
    
    /* Checkbox text color */
    .stCheckbox label {
        color: #e6edf3 !important;
    }

    /* Footer / Info */
    .footer {
        text-align: center;
        color: #8b949e;
        font-size: 12px;
        margin-top: 50px;
        padding: 20px;
        border-top: 1px solid #30363d;
    }
    
    /* Success/Error override for dark mode */
    .stAlert {
        background-color: #161b22 !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
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
st.markdown("**Official Assessment Portal** | Department of Social Welfare and Development")
st.info("Please provide accurate information for an official eligibility assessment based on national guidelines.")

# --- Form Content ---
with st.container():
    st.markdown('<div class="section-header">I. Primary Beneficiary Profile</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name (Surname, First Name, Middle Name)", placeholder="Enter complete legal name")
        c1, c2 = st.columns(2)
        with c1:
            sex = st.selectbox("Sex", ["Male", "Female"])
        with c2:
            age = st.number_input("Age", min_value=0, max_value=120, step=1, value=30)
        
        st.markdown("### Permanent Address")
        barangay = st.text_input("Barangay")
        city_municipality = st.text_input("City / Municipality")
        province = st.text_input("Province")

    with col2:
        st.markdown("### Socio-Economic Information")
        employment_status = st.selectbox("Employment Status", ["Employed", "Self-Employed", "Unemployed", "Informal"])
        employed_members = st.number_input("Number of Employed Members in Household", min_value=0, step=1, value=0)
        monthly_income = st.number_input("Total Monthly Household Income (PHP)", min_value=0.0, step=100.0, format="%.2f", value=0.0)
        
        st.markdown("### Housing & Household Size")
        household_size = st.number_input("Total Household Size", min_value=1, step=1, value=1)
        housing_type = st.selectbox("Housing Tenure Status", ["Owned", "Rented", "Informal Settler", "Living with Relatives"])

    st.markdown("### Priority Sector Identification")
    v_col1, v_col2, v_col3 = st.columns(3)
    with v_col1:
        is_4ps = st.checkbox("4Ps Beneficiary", help="Current member of Pantawid Pamilyang Pilipino Program")
        has_senior = st.checkbox("Senior Citizen in Household", help="Member aged 60 or above")
    with v_col2:
        has_pwd = st.checkbox("PWD in Household", help="Person with Disability")
        is_solo_parent = st.checkbox("Solo Parent")
    with v_col3:
        is_disaster_affected = st.checkbox("Affected by Calamity/Disaster", help="Victim of recent natural or man-made disasters")

# --- Household Members Section ---
household_members_data = []
if household_size > 1:
    st.markdown('<div class="section-header">II. Additional Household Members</div>', unsafe_allow_html=True)
    
    with st.expander("Reference Legends (Sector & Health Condition Codes)"):
        l_col1, l_col2 = st.columns(2)
        with l_col1:
            st.markdown("**SECTOR CODES**")
            for code, desc in SECTOR_LEGEND.items():
                st.write(f"**{code}**: {desc}")
        with l_col2:
            st.markdown("**HEALTH CODES**")
            for code, desc in HEALTH_CONDITION_LEGEND.items():
                st.write(f"**{code}**: {desc}")

    for i in range(int(household_size) - 1):
        with st.container():
            st.markdown(f"**Household Member #{i + 1}**")
            m_col1, m_col2, m_col3 = st.columns([2, 2, 2])
            
            with m_col1:
                m_name = st.text_input(f"Legal Name (Member #{i+1})", key=f"name_{i}")
                m_relation = st.text_input(f"Relationship to Head", key=f"rel_{i}")
            
            with m_col2:
                m_gender = st.selectbox(f"Sex", ["Male", "Female"], key=f"gen_{i}")
                m_occupation = st.text_input(f"Occupation", key=f"occ_{i}")
            
            with m_col3:
                m_sector = st.multiselect(f"Sector Code (A-F)", options=list(SECTOR_LEGEND.keys()), key=f"sec_{i}")
                m_health = st.multiselect(f"Health Code (1-5)", options=list(HEALTH_CONDITION_LEGEND.keys()), key=f"hea_{i}")
            
            household_members_data.append({
                "Full Name": m_name,
                "Relation": m_relation,
                "Sex": m_gender,
                "Occupation": m_occupation,
                "Sector": ", ".join(m_sector),
                "Health Condition": ", ".join(m_health)
            })
            st.divider()

# --- Submission ---
st.markdown("---")
btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
with btn_col2:
    submit_button = st.button("EXECUTE ASSESSMENT", type="primary")

if submit_button:
    if not full_name or not barangay or not city_municipality:
        st.error("Submission Failed: Required identifying information and address fields are missing.")
    else:
        # Results Section
        st.markdown('<div class="section-header">III. Eligibility Determination</div>', unsafe_allow_html=True)
        
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
        eligibility_text = "NOT ELIGIBLE"
        
        if model:
            try:
                prediction = model.predict(input_df)[0]
                if isinstance(prediction, (str, bytes)):
                    eligibility_text = prediction.upper() if isinstance(prediction, str) else prediction.decode('utf-8').upper()
                    is_eligible = "ELIGIBLE" in eligibility_text and "NOT" not in eligibility_text
                else:
                    is_eligible = bool(prediction)
                    eligibility_text = "ELIGIBLE" if is_eligible else "NOT ELIGIBLE"
            except Exception:
                is_eligible = monthly_income < 15000 and (employed_members == 0 or is_disaster_affected)
                eligibility_text = "ELIGIBLE" if is_eligible else "NOT ELIGIBLE"

        # Result Display
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            if is_eligible:
                st.success(f"### DETERMINATION: {eligibility_text}")
            else:
                st.error(f"### DETERMINATION: {eligibility_text}")
        
        with res_col2:
            st.markdown("**Summary of Assessment**")
            if is_eligible:
                st.write("Subject meets the criteria for Social Amelioration Program assistance based on income thresholds and priority sector status.")
            else:
                st.write("Subject does not meet the necessary criteria for program assistance at this time.")

        # Formal Data Summary
        with st.expander("View Consolidated Assessment Data"):
            st.table(pd.DataFrame([{
                "Primary Beneficiary": full_name,
                "Monthly Income": f"PHP {monthly_income:,.2f}",
                "HH Size": household_size,
                "Location": f"{barangay}, {city_municipality}",
                "Priority Status": "Yes" if (is_4ps or has_senior or has_pwd) else "No"
            }]))

st.markdown("""
    <div class="footer">
        Social Amelioration Program Eligibility Assessment Tool<br>
        © 2026 Republic of the Philippines | Official Government Use Only
    </div>
    """, unsafe_allow_html=True)
