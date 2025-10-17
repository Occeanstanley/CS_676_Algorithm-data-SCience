import streamlit as st
import openai
from tinytroupe.persona import Persona

# Load OpenAI key from secrets or env
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else None

# Sidebar: Persona Info
st.sidebar.title("👤 Persona Setup")
name = st.sidebar.text_input("Name", "Aisha")
role = st.sidebar.selectbox("Archetype / Role", [
    "Budget-conscious professional",
    "Tech-savvy teenager",
    "Cautious parent"
])
budget_sensitive = st.sidebar.checkbox("💰 Budget sensitive", value=True)
design_attentive = st.sidebar.checkbox("🎨 Design attentive", value=True)
risk_aversion = st.sidebar.select_slider("⚠️ Risk Aversion", ["low", "medium", "high"], value="medium")

# Main input for feature/variant
st.title("🧠 TinyTroupe Persona Simulator")
feature_text = st.text_area("✏️ Describe the feature or product to test:", 
    "A new anti-reflective glasses option for $79.99, includes 15-month breakage warranty.")

if st.button("🧪 Run Simulation"):
    with st.spinner("Thinking..."):

        persona = Persona(
            name=name,
            archetype=role,
            features={
                "budget_sensitive": budget_sensitive,
                "design_attentive": design_attentive,
                "risk_aversion": risk_aversion
            }
        )

        result = persona.evaluate(feature_text)

        # Output Reasoning
        st.subheader("🧩 THINK (Internal Reasoning)")
        st.write(result["think"])

        st.subheader("💬 TALK (Final Recommendation)")
        st.write(result["talk"])
