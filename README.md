# 🌐 Credibility Insight System — AI-Powered Source Evaluation

### 📊 Project 1 – Deliverables 1 to 3  
**Author:** Stanley Occean  
**Course:** CS661 – Python Programming (Fall 2025)  
**Institution:** Pace University – Seidenberg School of CSIS  

---

## 🚀 Overview
The **Credibility Insight System** is an AI-driven web application that analyzes the **credibility of online articles or websites**.  
It combines **rule-based heuristics**, **machine-learning simulation**, and **user feedback loops** to refine trust scores dynamically.

This project was completed as **Deliverables 1–3**, covering:
1. **System Design + Prototype Setup**  
2. **Functional App Implementation + Interactive Feedback Dashboard**  
3. **Retraining Pipeline for Adaptive Learning**

---

## 🧩 Core Features
- **Hybrid Scoring Algorithm** – blends rule-based and ML logic via adjustable α-weight.  
- **Live Feedback Loop** – users mark predictions as “👍 Credible” or “👎 Not Credible.”  
- **Adaptive Alpha Mechanism** – model self-adjusts based on aggregated feedback.  
- **Analytics Dashboard** – real-time pie charts, credibility distribution, and download option.  
- **Retraining Script** – lightweight logistic regression retrains using stored feedback logs.  
- **Clean Dark-Themed UI** – responsive Gradio 4.x interface with Markdown help, footer, and color-coded credibility bars.

---

## 🧱 Project Structure

---

## 🧠 Architecture Summary

### 1️⃣ Inference Engine (`inference_service.py`)
- Parses the domain and assigns reputation tiers (e.g., `.gov`, `.edu`, or verified outlets).
- Computes rule-based trust score + simulated ML component.
- Produces **hybrid credibility score**, **star rating**, and **HTML summary box**.

### 2️⃣ User Interface (`app.py`)
- Built with **Gradio 4.x** (soft emerald/teal theme).  
- Supports URL evaluation, adjustable α, and optional HTML fetching.  
- Displays:
  - Numeric score  
  - Star rating  
  - Color-coded credibility bar  
  - Explanation summary  
  - User feedback section  
  - Analytics dashboard  

### 3️⃣ Retraining Script (`train_nn.py`)
- Loads CSV/JSON feedback logs.  
- Cleans & labels data (“Credible” → 1 / “Not Credible” → 0).  
- Trains a **Logistic Regression** model to learn user consensus trends.  
- Saves the updated model to `/artifacts/model.joblib`.

---

## 📷 Screenshots (Deliverables 1 – 3)
| Deliverable | Preview |
|--------------|----------|
| **1 – UI Prototype** | ![Deliverable 1](2025-11-09%20(18).png) |
| **2 – Feedback Loop Added** | ![Deliverable 2](2025-11-09%20(19).png) |
| **3 – Dashboard + Retraining Integration** | ![Deliverable 3](2025-11-09%20(20).png) |
| **Final Live App** | ![Final App](2025-11-09%20(21).png) |
| **Feedback Analytics** | ![Analytics](2025-11-09%20(22).png) |
| **Retraining Logs** | ![Retraining](2025-11-09%20(23).png) |

---

## 🧩 Technical Stack
| Category | Technologies |
|-----------|---------------|
| **Frontend / UI** | Gradio 4.x |
| **Backend Logic** | Python 3.10+, Requests, Random |
| **Machine Learning** | Scikit-Learn (Logistic Regression), Joblib |
| **Data Handling** | Pandas, NumPy |
| **Visualization** | Matplotlib |
| **Version Control** | GitHub |
| **Deployment** | Gradio App / Hugging Face Spaces (live demo) |

---

## ⚙️ Installation & Run

```bash
# 1️⃣ Clone repository
git clone https://github.com/<your-username>/credibility-insight-system.git
cd credibility-insight-system

# 2️⃣ Create environment & install dependencies
pip install -r requirements.txt

# 3️⃣ Launch the Gradio app
python app.py
