import streamlit as st
import pandas as pd
import joblib

# --- Page Configuration ---
st.set_page_config(
    page_title="SAP Eligibility Checker",
    page_icon="🇵🇭",
    layout="wide"
)

# --- Load Model ---
@st.cache_resource
def load_model():
    try:
        model = joblib.load("model/eligibility_model.joblib")
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

# --- UI Header ---
st.title("🇵🇭 Social Amelioration Program (SAP) Eligibility Checker")
st.markdown("---")

# --- Beneficiary Inputs ---
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
    employment_status = st.selectbox(
        "Employment Status",
        ["Employed", "Self-Employed", "Unemployed", "Informal"]
    )
    employed_members = st.number_input(
        "Number of Employed Members", min_value=0, step=1, value=0
    )
    monthly_income = st.number_input(
        "Monthly Household Income (PHP)", min_value=0.0, step=100.0, format="%.2f"
    )
    household_size = st.number_input("Household Size", min_value=1, step=1, value=1)
    housing_type = st.selectbox(
        "Housing Type",
        ["Owned", "Rented", "Informal Settler", "Living with Relatives"]
    )

# --- Vulnerable / Priority Checkboxes ---
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
    st.info(f"Please provide details for the other {household_size - 1} member(s).")

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

    for i in range(household_size - 1):
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
            m_sector = st.multiselect(
                f"Sector #{i+1} (Select codes)", options=list(SECTOR_LEGEND.keys()), key=f"sec_{i}"
            )
            m_health = st.multiselect(
                f"Health Condition #{i+1} (Select codes)", options=list(HEALTH_CONDITION_LEGEND.keys()), key=f"hea_{i}"
            )
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

# --- Submission & Prediction ---
st.markdown("---")
if st.button("Check Eligibility", type="primary"):
    # Validate
    errors = []
    if not full_name: errors.append("Full Name is required.")
    if not barangay: errors.append("Barangay is required.")
    if not city_municipality: errors.append("City/Municipality is required.")
    if not province: errors.append("Province is required.")
    if errors:
        for error in errors:
            st.error(error)
        st.stop()

    # Show Submitted Info
    st.subheader("📝 Submitted Information Summary")
    summary_df = pd.DataFrame([{
        "Full Name": full_name,
        "Sex": sex,
        "Age": age,
        "Location": f"{barangay}, {city_municipality}, {province}",
        "Status": employment_status,
        "Employed Members": employed_members,
        "Income": f"PHP {monthly_income:,.2f}",
        "Household Size": household_size,
        "Housing Type": housing_type,
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

    # Prepare input for model
    input_data = pd.DataFrame([{
        "family_id": "FAM-000",
        "monthly_income": monthly_income,
        "family_size": household_size,
        "employed_members": employed_members,
        "has_senior": int(has_senior),
        "has_pwd": int(has_pwd),
        "is_solo_parent": int(is_solo_parent),
        "is_disaster_affected": int(is_disaster_affected),
        "receives_4ps": int(is_4ps),
        "housing_type": housing_type,
        "location": f"{barangay}, {city_municipality}",
        "employment_status": employment_status
    }])

    # --- Prediction & Reasoning ---
    if model:
        try:
            pred = model.predict(input_data)[0]
            is_eligible = bool(pred)
            eligibility_result = "Eligible" if is_eligible else "Not Eligible"
        except Exception as e:
            st.warning(f"Model prediction error: {e}")
            st.info("Using fallback rule-based logic.")
            if monthly_income < 20000 and not is_4ps:
                is_eligible = True
                eligibility_result = "Eligible"
            else:
                is_eligible = False
                eligibility_result = "Not Eligible"
    else:
        st.warning("Model not loaded. Using fallback logic.")
        if monthly_income < 20000 and not is_4ps:
            is_eligible = True
            eligibility_result = "Eligible"
        else:
            is_eligible = False
            eligibility_result = "Not Eligible"

    # --- Display Result ---
    st.markdown("---")
    st.header("🏁 Eligibility Result")
    if is_eligible:
        st.success(f"### Result: {eligibility_result}")
    else:
        st.error(f"### Result: {eligibility_result}")

    # --- Detailed Summary ---
    st.subheader("ℹ️ Detailed Summary")
    detailed_reasons = []
    if monthly_income < 10000:
        detailed_reasons.append(f"- Monthly income PHP {monthly_income:,.2f} is below the SAP threshold, increasing eligibility.")
    elif monthly_income < 20000:
        detailed_reasons.append(f"- Monthly income PHP {monthly_income:,.2f} is near the threshold; eligibility depends on vulnerability factors.")
    else:
        detailed_reasons.append(f"- Monthly income PHP {monthly_income:,.2f} exceeds the typical SAP threshold; only strong vulnerability factors may qualify.")

    if has_senior: detailed_reasons.append("- Household has a Senior Citizen without pension, increasing eligibility.")
    if is_solo_parent: detailed_reasons.append("- Applicant is a Solo Parent, increasing eligibility.")
    if has_pwd: detailed_reasons.append("- Household has a Person with Disability (PWD), increasing eligibility.")
    if is_disaster_affected: detailed_reasons.append("- Household is disaster-affected, increasing eligibility.")
    if is_4ps: detailed_reasons.append("- Applicant is already a 4Ps beneficiary, priority rules apply.")
    if household_size > 5: detailed_reasons.append(f"- Household size is {household_size}, higher dependency increases eligibility.")
    if employment_status in ["Unemployed", "Informal"]:
        detailed_reasons.append(f"- Employment status ({employment_status}) indicates informal sector vulnerability.")

    if is_eligible:
        detailed_reasons.append("- Overall assessment: Household meets SAP eligibility criteria.")
    else:
        detailed_reasons.append("- Overall assessment: Household does not meet sufficient SAP criteria.")

    st.write("\n".join(detailed_reasons))
