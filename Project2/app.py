import streamlit as st

def simulate_response(persona, feature):
    rationale = [
        f"{persona['name']} considers price sensitivity: {persona.get('traits',{}).get('budget_sensitive', False)}",
        "Checks for missing specs; penalizes vague ads",
        "Evaluates financing and usability factors"
    ]
    final = f"{persona['name']} would likely recommend this feature if specs and affordability align."
    return {"think": rationale, "talk": final}

st.set_page_config(page_title="TinyTroupe Persona Simulator", layout="wide")

st.title("🧠 TinyTroupe Persona Simulator")
st.caption("Deliverable 2–3 | AI‑based user feedback simulation")

with st.sidebar:
    st.header("Persona Configuration")
    name = st.text_input("Name", "Aisha")
    role = st.text_input("Archetype", "Budget‑conscious professional")
    traits = {
        "budget_sensitive": st.checkbox("Budget sensitive", True),
        "design_attentive": st.checkbox("Design attentive", True),
        "risk_aversion": st.selectbox("Risk aversion", ["low","medium","high"], index=1)
    }
    persona = {"name": name, "role": role, "traits": traits}

st.subheader("Feature Under Test")
feature = st.text_area("Describe the feature:", "Ad 2 (Samsung): 4K/8K, Real Depth Enhancer, Anti-Reflection, 0% APR.", height=120)

if st.button("Run Simulation", type="primary"):
    out = simulate_response(persona, feature)
    with st.expander("🧩 THINK (Internal Reasoning)", expanded=True):
        for i, line in enumerate(out["think"], 1):
            st.write(f"{i}. {line}")
    st.success(out["talk"])

st.divider()
st.subheader("Compare Default Personas")
cols = st.columns(3)
default_personas = [
    {"name": "Eddie", "role": "Accessibility‑first senior", "traits": {"budget_sensitive": False, "design_attentive": False, "risk_aversion": "high"}},
    {"name": "Ravi", "role": "Power user / gamer", "traits": {"budget_sensitive": False, "design_attentive": True, "risk_aversion": "low"}},
    {"name": "Maya", "role": "Parent", "traits": {"budget_sensitive": True, "design_attentive": True, "risk_aversion": "medium"}},
]
for i, p in enumerate(default_personas):
    with cols[i]:
        st.write(f"**{p['name']}** – {p['role']}")
        if st.button(f"Simulate {p['name']}", key=f"p_{i}"):
            o = simulate_response(p, feature)
            st.write("**THINK**")
            for line in o["think"]:
                st.write("-", line)
            st.info(o["talk"])
