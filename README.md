---
title: "Credibility Insight System — AI-Powered Source Evaluation"
subtitle: "Project 1 Deliverables 1–3"
author: "Stanley Occean"
course: "CS676 – Algorithm Data Science (Fall 2025)"
institution: "Pace University – Seidenberg School of CSIS"
date: "November 2025"
---

# 🌐 Credibility Insight System — AI-Powered Source Evaluation

### 📊 Project 1 – Deliverables 1 to 3  
**Author:** Stanley Occean  
**Course:** Algorithm Data Science (Fall 2025)  
**Institution:** Pace University – Seidenberg School of CSIS  

🔗 **Live Demo:** [Launch the App on Hugging Face Spaces 🚀](https://occeanstanley9-credibility-scoring-space.hf.space/)

---

## 🚀 Overview
The **Credibility Insight System** is an AI-driven web application that evaluates the **credibility of online sources** using a hybrid model that merges **rule-based heuristics**, **machine-learning simulation**, and **human feedback refinement**.

This project fulfills **Deliverables 1–3** of the semester capstone:

1. **System Design + Prototype Setup**  
2. **Functional App Implementation + Interactive Feedback Dashboard**  
3. **Retraining Pipeline for Adaptive Learning**

---

## 🧠 Core Features
- **Hybrid Scoring Algorithm** – Combines rule-based domain reputation and simulated ML scoring.  
- **Live Feedback Loop** – Users can label results as “👍 Credible” or “👎 Not Credible.”  
- **Adaptive Alpha Mechanism** – Adjusts credibility weighting automatically based on user consensus.  
- **Analytics Dashboard** – Displays real-time feedback distribution, average scores, and download option.  
- **Retraining Script** – Uses collected feedback data to retrain a lightweight logistic regression model.  
- **Dark-Themed UI** – Built with Gradio 4.x using modern gradients and clear data visualization.

---

## 🧱 Project Structure

---

## 🧩 Architecture Summary

### 1️⃣ Inference Engine (`inference_service.py`)
- Parses the domain and assigns trust levels (e.g., `.gov`, `.edu`, or verified publishers).  
- Calculates rule-based credibility, simulated ML score, and final blended output.  
- Produces hybrid score, star rating, and dynamic explanation box.

### 2️⃣ User Interface (`app.py`)
- Built with **Gradio 4.x** (emerald/teal theme).  
- Supports URL input, alpha adjustment, and optional HTML analysis.  
- Includes:
  - Numeric score  
  - Star rating  
  - Color-coded credibility bar  
  - Credibility summary card  
  - Feedback input and dashboard

### 3️⃣ Retraining Script (`train_nn.py`)
- Loads and cleans feedback logs (`CSV` or `JSON`).  
- Maps textual feedback into binary labels (`Credible` → 1, `Not Credible` → 0).  
- Trains a **Logistic Regression** model for adaptive refinement.  
- Exports model artifact to `/artifacts/model.joblib`.

---

## 🧰 Technical Stack

| Category | Technologies |
|-----------|--------------|
| **Frontend / UI** | Gradio 4.x |
| **Backend Logic** | Python 3.10+, Requests, Random |
| **Machine Learning** | Scikit-Learn (Logistic Regression), Joblib |
| **Data Handling** | Pandas, NumPy |
| **Visualization** | Matplotlib |
| **Version Control** | GitHub |
| **Deployment** | Hugging Face Spaces |

---

## ⚙️ Installation & Run

```bash
# 1️⃣ Clone repository
git clone https://github.com/Occeanstanley/CS_676_Algorithm-data-Science.git
cd CS_676_Algorithm-data-Science/project1

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Launch the Gradio app
python app.py
