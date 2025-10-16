# Project 2 – TinyTroupe for Simulation (Deliverable 2)
**Author:** Stanley Occean  
**Date:** 2025-10-16  
**Objective:** Develop an interactive beta app for persona-based simulation using **Streamlit** and **TinyTroupe**.

---

## 🧱 Overview
The beta version demonstrates a **Streamlit app** that allows users to:
- Choose personas (Aisha, Ravi, Maya, Eddie)
- Input product features
- View AI-simulated THINK → TALK responses
- Compare feedback across personas

---

## 💻 App Structure
```
tinytroupe-simulator/
├─ app.py
├─ requirements.txt
├─ README.md
├─ assets/
│   └─ tinytroupe_aisha_tv_ads.png
```

### Key Components
- **simulate_response()** – placeholder function for persona simulation
- **Persona sidebar** – select or define persona traits
- **Feature input** – text area for ads/features
- **Output display** – THINK (reasoning) and TALK (response)

---

## 🚀 How to Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

**Example Persona:**
```
Name: Aisha
Archetype: Budget-conscious professional
Feature: "Ad 2 (Samsung): 4K/8K, Real Depth Enhancer, Anti-Reflection, 0% APR financing"
```

**Output:**  
- THINK: Notes pros, affordability, design.  
- TALK: Prefers Samsung due to balance and affordability.

---

## 📈 Next Steps
- Integrate TinyTroupe live via `TinyPerson` and `TinyTask`
- Add persona database (JSON or SQLite)
- Implement exportable feedback reports (CSV/JSONL)
- Prepare deployment for Hugging Face Spaces

---

## ✅ Deliverable Summary
| Component | Status |
|------------|---------|
| App UI | ✅ Completed |
| Persona Simulation | ✅ Working Stub |
| Documentation | ✅ Done |
| Multi-persona Comparison | 🟡 Next |
| Deployment Setup | 🟡 Next (Deliverable 3) |
