import streamlit as st
import openai
from typing import List
from tinytroupe.persona import Persona
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("🧠 TinyTroupe Persona Simulator")

name = st.text_input("Name", "Aisha")
role = st.selectbox("Archetype / Role", ["Budget-conscious professional", "Trend-seeking teen", "Tech-savvy shopper"])
budget_sensitive = st.checkbox("Budget sensitive", value=True)
design_attentive = st.checkbox("Design attentive", value=True)
risk_aversion = st.selectbox("Risk aversion", ["low", "medium", "high"], index=1)
feature = st.text_area("Feature / Variant Under Test", "16-month 0% APR; anti-reflection coating")

if st.button("🧪 Run Simulation"):
    persona = Persona(
        name=name,
        role=role,
        budget_sensitive=budget_sensitive,
        design_attentive=design_attentive,
        risk_aversion=risk_aversion,
    )
    internal_thoughts = persona.think(feature)
    recommendation = persona.talk(feature)

    st.subheader("🧩 THINK (Internal Reasoning)")
    st.write(internal_thoughts)

    st.subheader("💬 TALK (Final Recommendation)")
    st.write(recommendation)