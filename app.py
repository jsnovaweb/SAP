import streamlit as st
import pandas as pd
import joblib
import os
import numpy as np

# --- Configuration ---
MODEL_PATH = "attached_assets/eligibility_model_1768571674807.joblib"
st.set_page_config(
    page_title="SAP Eligibility Checker",
    page_icon="🌈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a "Kids/Friendly" look with a light background
st.markdown("""
    <style>
    /* Light Background */
    .stApp {
        background-color: #FFF9E6; /* Soft light yellow */
    }
    
    /* Rounded, Friendly Containers */
    .main {
        background-color: #FFF9E6;
    }
    
    /* Big, Happy Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        height: 4em;
        background-color: #FF6B6B; /* Soft Red/Pink */
        color: white;
        font-weight: bold;
        font-size: 24px !important;
        border: 4px solid #FFD93D;
        box-shadow: 0 4px 0px #EE5253;
        transition: transform 0.1s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        color: white;
    }
    
    /* Card Styling */
    .stExpander, div[data-testid="stVerticalBlock"] > div {
        border-radius: 20px;
    }

    /* Titles and Text */
    h1 {
        color: #4D96FF; /* Friendly Blue */
        font-family: 'Comic Sans MS', cursive, sans-serif;
        text-align: center;
        font-size: 50px !important;
    }
    h2, h3, .stMarkdown {
        color: #6BCB77; /* Soft Green */
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    
    .section-header {
        background-color: #4D96FF;
        color: white;
        padding: 20px;
        border-radius: 25px;
        margin-bottom: 25px;
        text-align: center;
        font-size: 30px;
        font-weight: bold;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        border: 5px solid #6BCB77;
    }
    
    /* Input Styling */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 15px !important;
        border: 3px solid #4D96FF !important;
        background-color: white !important;
        font-size: 18px !important;
    }

    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 40px;
        color: #FF6B6B;
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
    "A": "Grandparents (Senior)",
    "B": "Moms with Babies inside (Pregnant)",
    "C": "Moms feeding Babies (Lactating)",
    "D": "Special Friends (PWD)",
    "E": "Super Parents (Solo Parent)",
    "F": "Friends with no house (Homeless)"
}

HEALTH_CONDITION_LEGEND = {
    "1": "Heart (Heart Disease)",
    "2": "Strong Blood (Hypertension)",
    "3": "Breathing (Lung Disease)",
    "4": "Sugar (Diabetes)",
    "5": "Big Sickness (Cancer)"
}

# --- Header ---
st.markdown("<h1>🌟 Helper Bot 🌟</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #FF9F45;'>Let's see if we can help your family today!</h3>", unsafe_allow_html=True)

# --- Form Content ---
with st.container():
    st.markdown('<div class="section-header">🏠 Tell us about you!</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("What is your name? 😊", placeholder="Write your name here!")
        c1, c2 = st.columns(2)
        with c1:
            sex = st.selectbox("Are you a Boy or Girl?", ["Male", "Female"])
        with c2:
            age = st.number_input("How old are you? 🎂", min_value=0, max_value=120, step=1, value=30)
        
        st.markdown("### 📍 Where do you live?")
        barangay = st.text_input("Village Name (Barangay)")
        city_municipality = st.text_input("Town Name (City)")
        province = st.text_input("Big Place Name (Province)")

    with col2:
        st.markdown("### 💰 Money & Work")
        employment_status = st.selectbox("Do you have a job?", ["Employed", "Self-Employed", "Unemployed", "Informal"])
        employed_members = st.number_input("How many people in your house have jobs?", min_value=0, step=1, value=0)
        monthly_income = st.number_input("How much money does your house get? (PHP)", min_value=0.0, step=100.0, format="%.2f", value=0.0)
        
        st.markdown("### 🏘️ Your House")
        household_size = st.number_input("How many people live in your house? 👨‍👩‍👧‍👦", min_value=1, step=1, value=1)
        housing_type = st.selectbox("What kind of house is it?", ["Owned", "Rented", "Informal Settler", "Living with Relatives"])

    st.markdown("### 📝 Special Things")
    v_col1, v_col2, v_col3 = st.columns(3)
    with v_col1:
        is_4ps = st.checkbox("Are you in 4Ps? 🎒", help="Special help from the government")
        has_senior = st.checkbox("Is there a Grandparent in the house? 👵", help="Someone 60 years old or older")
    with v_col2:
        has_pwd = st.checkbox("Is there a Special Friend? ♿", help="Person with Disability")
        is_solo_parent = st.checkbox("Are you a Super Parent? 🦸", help="Solo Parent")
    with v_col3:
        is_disaster_affected = st.checkbox("Did a storm hurt your house? ⛈️", help="Victim of a disaster")

# --- Household Members Section ---
household_members_data = []
if household_size > 1:
    st.markdown('<div class="section-header">👨‍👩‍👧‍👦 Who else lives with you?</div>', unsafe_allow_html=True)
    
    # Unified Legend Expander
    with st.expander("📖 Click here to learn about the special codes!"):
        l_col1, l_col2 = st.columns(2)
        with l_col1:
            st.markdown("**Groups**")
            for code, desc in SECTOR_LEGEND.items():
                st.write(f"**{code}**: {desc}")
        with l_col2:
            st.markdown("**Health**")
            for code, desc in HEALTH_CONDITION_LEGEND.items():
                st.write(f"**{code}**: {desc}")

    for i in range(int(household_size) - 1):
        with st.container():
            st.markdown(f"### Family Member #{i + 1}")
            m_col1, m_col2, m_col3 = st.columns([2, 2, 2])
            
            with m_col1:
                m_name = st.text_input(f"What is their name? (Member #{i+1})", key=f"name_{i}")
                m_relation = st.text_input(f"How are they related to you?", key=f"rel_{i}")
            
            with m_col2:
                m_gender = st.selectbox(f"Boy or Girl?", ["Male", "Female"], key=f"gen_{i}")
                m_occupation = st.text_input(f"What do they do for work?", key=f"occ_{i}")
            
            with m_col3:
                m_sector = st.multiselect(f"Pick a Group (A-F)", options=list(SECTOR_LEGEND.keys()), key=f"sec_{i}")
                m_health = st.multiselect(f"Pick a Health code (1-5)", options=list(HEALTH_CONDITION_LEGEND.keys()), key=f"hea_{i}")
            
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
    submit_button = st.button("🚀 CLICK TO CHECK! 🚀", type="primary")

if submit_button:
    if not full_name or not barangay or not city_municipality:
        st.error("Oops! Please tell us your name and where you live first! 🙊")
    else:
        # Results Section
        st.markdown('<div class="section-header">🌈 We have the answer!</div>', unsafe_allow_html=True)
        
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
                is_eligible = monthly_income < 15000 and (employed_members == 0 or is_disaster_affected)
                eligibility_text = "Eligible" if is_eligible else "Not Eligible"

        # Visual Feedback
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            if is_eligible:
                st.balloons()
                st.markdown(f"<h1 style='color: #6BCB77; text-shadow: 2px 2px #fff;'>🎉 YES! 🎉</h1>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align: center;'>You can get help!</h3>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h1 style='color: #FF6B6B; text-shadow: 2px 2px #fff;'>Sorry...</h1>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align: center;'>Not this time.</h3>", unsafe_allow_html=True)
        
        with res_col2:
            st.markdown("### 🎈 Why?")
            if is_eligible:
                st.write("Yay! Your family meets the rules for help because your house needs a little extra support right now! 🏠✨")
            else:
                st.write("It looks like your family has enough for now. But don't worry, keep being awesome! 🌟")

        # Data Summary Table
        with st.expander("📝 See everything you told us"):
            st.table(pd.DataFrame([{
                "Name": full_name,
                "Money": f"PHP {monthly_income:,.2f}",
                "Family Size": household_size,
                "Place": f"{barangay}, {city_municipality}",
                "4Ps": "Yes" if is_4ps else "No",
            }]))
