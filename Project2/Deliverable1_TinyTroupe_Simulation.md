# Project 2 – TinyTroupe for Simulation (Deliverable 1)
**Author:** Stanley Occean  
**Date:** 2025-10-16  
**Course:** Project 2 – Algorithm Data Science

---

## 🎯 Purpose
Demonstrate agent‑based **persona simulation** using the **TinyTroupe** Python package for rapid, low‑cost feedback generation in feature testing.  
This deliverable shows setup, installation, and initial run results using the persona *Aisha*.

---

## ⚙️ Setup Instructions
### Environment
- Python 3.10+
- Packages: `tinytroupe`, `streamlit`, `gradio`, `pydantic`, `python-dotenv`

### Installation
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install tinytroupe streamlit gradio pydantic==2.* python-dotenv
```

### Minimal Example
```python
from tinytroupe import TinyPerson, TinyGroup, TinyTask

aisha = TinyPerson(
    name="Aisha",
    bio="Budget‑conscious professional, values aesthetics and financing options.",
    goals=["Pick the best TV ad for her needs"],
    traits={"budget_sensitive": True, "design_attentive": True, "risk_aversion": "medium"}
)

ads = [
    "Ad 1 (LG): a9 Processor, Dolby Vision IQ.",
    "Ad 2 (Samsung): 4K & 8K range, Real Depth Enhancer, Anti‑Reflection, 48‑month 0% APR financing.",
    "Ad 3 (Wayfair): 55‑inch budget TV, free shipping over $35."
]

prompt = f"Evaluate these ads and pick one. Explain your reasoning. Ads: {ads}"
task = TinyTask(instructions=prompt)
group = TinyGroup([aisha])
result = group.run(task)
print(result.summary)
```

---

## 🧠 Persona Run Evidence
**Scenario:** Evaluate 3 TV ads (LG, Samsung, Wayfair).  
**Persona:** Aisha – budget‑conscious, aesthetics‑driven, values affordability.

### Key Observations
- **THINK:** Evaluated features, financing, and design.  
- **TALK:** Preferred **Samsung Ad 2** for 4K/8K variety, anti‑reflection display, and 0% APR financing.  
- Persona shows reasoning consistency and balanced feedback.

---

## 💬 Quality Analysis
| Aspect | Observation |
|--------|--------------|
| Consistency | Maintains focus on affordability and design |
| Realism | Produces human-like reasoning |
| Limitation | May overemphasize available features |
| Mitigation | Add persona diversity and evidence-seeking prompts |

---

## 🧩 Future Personas
- **Eddie:** Accessibility-first senior user  
- **Ravi:** Gamer and performance tester  
- **Maya:** Parent, values durability and safety

---

## 🧾 Summary
TinyTroupe enables AI‑based user simulation, saving cost and time in product feedback collection. This deliverable confirms the tool’s viability for realistic, persona‑based evaluation.

