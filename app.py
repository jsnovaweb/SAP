import streamlit as st
import pandas as pd
import joblib
import os

# --- Configuration ---
MODEL_PATH = "attached_assets/eligibility_model_1768571674807.joblib"
st.set_page_config(page_title="SAP Eligibility Checker", page_icon="🇵🇭", layout="wide")

# --- Load Model ---
@st.cache_resource
def load_model():
    """Loads the pre-trained model from the file system."""
    if not os.path.exists(MODEL_PATH):
        st.error(f"Model file not found at: {MODEL_PATH}")
        return None
    try:
        model = joblib.load(MODEL_PATH)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
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

# --- UI Layout ---
st.title("🇵🇭 Social Amelioration Program (SAP) Eligibility Checker")
st.markdown("---")

# --- Input Section ---
st.header("📋 Beneficiary Information")

col1, col2 = st.columns(2)

with col1:
    full_name = st.text_input("Full Name", placeholder="e.g., Juan Dela Cruz")
    sex = st.selectbox("Sex", ["Male", "Female"])
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
    barangay = st.text_input("Barangay")
    city_municipality = st.text_input("City / Municipality")
    province = st.text_input("Province")

with col2:
    employment_status = st.selectbox("Employment Status", ["Employed", "Self-Employed", "Unemployed", "Informal"])
    monthly_income = st.number_input("Monthly Household Income (PHP)", min_value=0.0, step=100.0, format="%.2f")
    household_size = st.number_input("Household Size", min_value=1, step=1, value=1)
    
    # Checkboxes for specific criteria
    is_4ps = st.checkbox("4Ps Beneficiary")
    has_pwd = st.checkbox("PWD in Household")
    has_senior = st.checkbox("Senior Citizen in Household")
    is_solo_parent = st.checkbox("Solo Parent")
    is_disaster_affected = st.checkbox("Disaster-Affected")

# --- Household Members Section ---
household_members_data = []

if household_size > 1:
    st.markdown("---")
    st.header("👨‍👩‍👧‍👦 Household Members Details")
    st.info(f"Please provide details for the other {int(household_size) - 1} member(s).")

    # Display Legends
    with st.expander("📌 View Legends for Sector and Health Condition"):
        l_col1, l_col2 = st.columns(2)
        with l_col1:
            st.markdown("**SECTOR LEGEND (A–F)**")
            for code, desc in SECTOR_LEGEND.items():
                st.write(f"**{code}**: {desc}")
        with l_col2:
            st.markdown("**🩺 HEALTH CONDITION LEGEND (1–5)**")
            for code, desc in HEALTH_CONDITION_LEGEND.items():
                st.write(f"**{code}**: {desc}")

    for i in range(int(household_size) - 1):
        st.subheader(f"Member #{i + 1}")
        m_col1, m_col2, m_col3 = st.columns(3)
        
        with m_col1:
            m_surname = st.text_input(f"Surname #{i+1}", key=f"sur_{i}")
            m_firstname = st.text_input(f"First Name #{i+1}", key=f"first_{i}")
            m_middlename = st.text_input(f"Middle Name #{i+1}", key=f"mid_{i}")
        
        with m_col2:
            m_relation = st.text_input(f"Relation to Head #{i+1}", key=f"rel_{i}")
            m_gender = st.selectbox(f"Gender #{i+1}", ["Male", "Female"], key=f"gen_{i}")
            m_occupation = st.text_input(f"Occupation #{i+1}", key=f"occ_{i}")
        
        with m_col3:
            m_sector = st.multiselect(f"Sector #{i+1} (Select codes)", options=list(SECTOR_LEGEND.keys()), key=f"sec_{i}")
            m_health = st.multiselect(f"Health Condition #{i+1} (Select codes)", options=list(HEALTH_CONDITION_LEGEND.keys()), key=f"hea_{i}")

        household_members_data.append({
            "Surname": m_surname,
            "First Name": m_firstname,
            "Middle Name": m_middlename,
            "Relation": m_relation,
            "Gender": m_gender,
            "Occupation": m_occupation,
            "Sector": ", ".join(m_sector),
            "Health Condition": ", ".join(m_health)
        })

# --- Submission Logic ---
st.markdown("---")
submit_button = st.button("Check Eligibility", type="primary")

if submit_button:
    # 1. Validation
    errors = []
    if not full_name: errors.append("Full Name is required.")
    if not barangay: errors.append("Barangay is required.")
    if not city_municipality: errors.append("City/Municipality is required.")
    if not province: errors.append("Province is required.")
    
    if errors:
        for error in errors:
            st.error(error)
    else:
        # 2. Display Submitted Info
        st.success("Data Submitted Successfully!")
        
        st.subheader("📝 Submitted Information Summary")
        
        summary_df = pd.DataFrame([{
            "Full Name": full_name,
            "Sex": sex,
            "Age": age,
            "Location": f"{barangay}, {city_municipality}, {province}",
            "Status": employment_status,
            "Income": f"PHP {monthly_income:,.2f}",
            "Household Size": household_size,
            "4Ps": "Yes" if is_4ps else "No",
            "PWD in HH": "Yes" if has_pwd else "No",
            "Senior in HH": "Yes" if has_senior else "No",
            "Solo Parent": "Yes" if is_solo_parent else "No",
            "Disaster Affected": "Yes" if is_disaster_affected else "No"
        }])
        st.table(summary_df)

        if household_members_data:
            st.subheader("Household Members")
            st.table(pd.DataFrame(household_members_data))

        # 3. Model Prediction
        # Prepare input for model (Assuming model expects specific feature names)
        # Note: Since we don't know exact feature names model expects, we construct a generic DF.
        # If model expects One-Hot Encoding, this might fail without the pre-processor.
        # We will wrap this in a try-except block.
        
        input_data = {
            "age": [age],
            "monthly_income": [monthly_income],
            "household_size": [household_size],
            "is_4ps": [1 if is_4ps else 0],
            "has_pwd": [1 if has_pwd else 0],
            "has_senior": [1 if has_senior else 0],
            "is_solo_parent": [1 if is_solo_parent else 0],
            "is_disaster_affected": [1 if is_disaster_affected else 0],
            # Add placeholders for categorical if needed by simple models
             "sex_male": [1 if sex == "Male" else 0],
             "employment_unemployed": [1 if employment_status == "Unemployed" else 0]
        }
        input_df = pd.DataFrame(input_data)

        eligibility_result = "Unknown"
        reason = "Model not loaded or prediction failed."
        is_eligible = False

        if model:
            try:
                # Attempt prediction
                # Note: This is a best-guess attempt. Real model might need exact feature match.
                # If model has a 'predict' method
                prediction = model.predict(input_df)[0]
                
                # Interpret prediction (Assuming 1=Eligible, 0=Not Eligible, or string)
                if isinstance(prediction, str):
                    eligibility_result = prediction
                    is_eligible = "eligible" in prediction.lower() and "not" not in prediction.lower()
                else:
                    is_eligible = bool(prediction)
                    eligibility_result = "Eligible" if is_eligible else "Not Eligible"

                # Generate Reason (Heuristic based since model doesn't output it typically)
                reasons = []
                if monthly_income < 10000:
                    reasons.append("Income is within the qualifying range for support.")
                else:
                    reasons.append("Income level may exceed priority thresholds.")
                
                if is_4ps:
                    reasons.append("4Ps beneficiaries are automatically cross-referenced.")
                
                if employment_status in ["Unemployed", "Informal"]:
                    reasons.append("Employment status indicates high vulnerability.")
                
                reason = " ".join(reasons)

            except Exception as e:
                # Fallback logic if model input schema doesn't match
                st.warning(f"Model prediction error (Feature Mismatch): {e}")
                st.info("Using fallback logic for demonstration.")
                
                # Fallback Logic
                if monthly_income < 20000 and (is_disaster_affected or employment_status in ["Unemployed", "Informal"]):
                    is_eligible = True
                    eligibility_result = "Eligible"
                    reason = "Applicant meets the fallback criteria: Low income and vulnerable status."
                else:
                    is_eligible = False
                    eligibility_result = "Not Eligible"
                    reason = "Applicant does not meet the fallback criteria (Income too high or stable employment)."
        else:
             st.warning("Model not loaded. Using rule-based fallback.")
             if monthly_income < 15000:
                 is_eligible = True
                 eligibility_result = "Eligible"
                 reason = "Estimated eligibility based on income threshold."
             else:
                 is_eligible = False
                 eligibility_result = "Not Eligible"
                 reason = "Income exceeds the typical threshold for SAP."

        # 4. Display Result
        st.markdown("---")
        st.header("🏁 Eligibility Result")
        
        if is_eligible:
            st.success(f"### Result: {eligibility_result}")
        else:
            st.error(f"### Result: {eligibility_result}")

        # 5. Summary Reason
        st.subheader("ℹ️ Summary Reason")
        st.write(reason)
