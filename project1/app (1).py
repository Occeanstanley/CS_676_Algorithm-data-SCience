# app.py — Final Edition (Feedback Viewer + DownloadButton Fix + Clickable Footer)
import gradio as gr
import pandas as pd
import datetime
import os
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from inference_service import score_url, _plain_summary

APP_TITLE = "🧠 Credibility Insight System"
APP_SUBTITLE = "Assess and improve the credibility of online sources using AI + Human Feedback."
FEEDBACK_FILE = "feedback_logs.csv"

# ───────────────────────────────────────────────────────────
def adaptive_alpha(base_alpha=0.5):
    if not os.path.exists(FEEDBACK_FILE):
        return base_alpha
    df = pd.read_csv(FEEDBACK_FILE)
    if len(df) < 5:
        return base_alpha
    agree_rate = df["feedback"].mean()
    adjusted = min(0.9, max(0.1, base_alpha + (agree_rate - 0.5) * 0.2))
    return round(adjusted, 2)

# ───────────────────────────────────────────────────────────
def ui_score(url: str, alpha: float, fetch_html: bool):
    if not isinstance(url, str) or not url.strip():
        return (
            gr.update(value=0.0, visible=False),
            gr.update(value="☆☆☆☆☆", visible=False),
            _colored_bar(0.0),
            _plain_summary(0.0),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
        )
    try:
        dynamic_alpha = adaptive_alpha(alpha)
        res = score_url(url.strip(), alpha=dynamic_alpha, fetch_html=bool(fetch_html))
        s = float(res.get("score", 0.0))
        k = int(res.get("stars", 0))
        stars = "⭐" * k + "☆" * (5 - k)
        summary_html = _plain_summary(
            s,
            domain=res.get("domain", ""),
            category=res.get("category", ""),
            confidence=res.get("confidence", ""),
        )
        return (
            gr.update(value=s, visible=True),
            gr.update(value=stars, visible=True),
            _colored_bar(s),
            summary_html,
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=True),
        )
    except Exception as e:
        return (
            gr.update(value=0.0, visible=False),
            gr.update(value="☆☆☆☆☆", visible=False),
            _colored_bar(0.0),
            f"<div><b>Runtime error:</b> {e}</div>",
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
        )

# ───────────────────────────────────────────────────────────
def log_feedback(feedback_choice, url, score, stars):
    if not feedback_choice:
        return "⚠️ Please select 'Credible' or 'Not Credible'."

    feedback_value = 1 if str(feedback_choice).strip() == "👍 Credible" else 0

    record = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": url,
        "score": score,
        "stars": stars,
        "feedback": feedback_value,
    }
    df = pd.DataFrame([record])
    if os.path.exists(FEEDBACK_FILE):
        df.to_csv(FEEDBACK_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(FEEDBACK_FILE, index=False)
    return "✅ Thank you! Your feedback helps refine our model."

# ───────────────────────────────────────────────────────────
def show_dashboard():
    if not os.path.exists(FEEDBACK_FILE):
        return "📊 No feedback data yet.", None

    df = pd.read_csv(FEEDBACK_FILE)
    df["feedback"] = pd.to_numeric(df["feedback"], errors="coerce").fillna(0).astype(int)

    total = len(df)
    credible = df["feedback"].sum()
    not_credible = total - credible
    avg_score = round(df["score"].mean(), 2)
    credible_pct = round((credible / total) * 100, 1)
    not_credible_pct = 100.0 - credible_pct

    # Improved pie chart
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    wedges, texts, autotexts = ax.pie(
        [credible, not_credible],
        labels=["👍 Credible", "👎 Not Credible"],
        autopct="%1.1f%%",
        startangle=90,
        colors=["#33cc85", "#ff6666"],
        pctdistance=0.72,
        labeldistance=1.1,
        textprops={"color": "#111", "fontsize": 12, "weight": "bold"},
    )
    for t in autotexts:
        t.set_color("#111")
    ax.axis("equal")
    ax.set_title("User Feedback Distribution", fontsize=14, weight="bold")

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    img_html = f"<img src='data:image/png;base64,{img_base64}' width='350'/>"

    stats_html = f"""
    <div style='background:#1e1f24;color:#e8e8e8;padding:12px;border-radius:10px;margin-top:12px;'>
        <h4>📈 Feedback Analytics</h4>
        <p><b>Total Feedback:</b> {total}</p>
        <p><b>Credible Votes:</b> {credible} ({credible_pct}%)</p>
        <p><b>Not Credible Votes:</b> {not_credible} ({not_credible_pct}%)</p>
        <p><b>Average Score:</b> {avg_score}</p>
        <p><b>Adaptive α:</b> {adaptive_alpha()}</p>
    </div>
    """
    return stats_html, img_html

# ───────────────────────────────────────────────────────────
def view_feedback_table():
    if not os.path.exists(FEEDBACK_FILE):
        return "<p>No feedback yet.</p>"
    df = pd.read_csv(FEEDBACK_FILE)
    return df.to_html(index=False, classes="feedback-table")

# ───────────────────────────────────────────────────────────
def _colored_bar(score: float) -> str:
    pct = round(score * 100)
    bar_color = "#33cc85" if pct > 70 else "#ffcc66" if pct > 40 else "#ff6666"
    return f"""
    <div style="width:100%;background:#2b2b2b;border-radius:10px;height:18px;margin-top:6px;">
      <div style="width:{pct}%;height:100%;background:{bar_color};
                  border-radius:10px;transition:width 0.6s;"></div>
    </div>
    <p style="font-weight:600;margin-top:4px;">{pct}% Credibility</p>
    """

# ───────────────────────────────────────────────────────────
with gr.Blocks(
    theme=gr.themes.Soft(primary_hue="emerald", secondary_hue="teal"),
    title=APP_TITLE,
    css="""
      #root {max-width: 900px; margin: auto;}
      .gradio-container {background:linear-gradient(145deg,#1a1b1f,#24262b);}
      .feedback-table {border-collapse: collapse; width: 100%; color: #e8e8e8;}
      .feedback-table th, .feedback-table td {border: 1px solid #444; padding: 6px; text-align: left;}
      .feedback-table th {background-color: #2b2b2b;}
    """
) as demo:

    # HEADER
    gr.Markdown(f"""
    <div style='text-align:center;padding:20px 0;background:linear-gradient(90deg,#1e3c72,#2a5298);
                border-radius:12px;margin-bottom:20px;color:white;'>
        <h2>{APP_TITLE}</h2>
        <p style='font-size:16px;'>{APP_SUBTITLE}</p>
    </div>
    """)

    # HELP
    with gr.Accordion("❓ Help & Instructions", open=False):
        gr.Markdown("""
        **How to Use**
        1. Paste a website or article URL.  
        2. Click **Evaluate** to analyze credibility.  
        3. Review score + summary, then submit feedback.  
        4. Use the dashboard to monitor performance.

        **Model Overview**
        - Combines rule-based metrics + ML signals.
        - Adjusts with user feedback over time (adaptive α).
        """)

    # URL Input
    url = gr.Textbox(label="🔗 Enter Article or Website URL", placeholder="https://example.com/article...")
    evaluate_btn = gr.Button("🔎 Evaluate", variant="primary")

    with gr.Accordion("⚙️ Advanced settings", open=False):
        alpha = gr.Slider(0, 1, 0.5, step=0.05, label="Alpha (ML Weight)")
        fetch = gr.Checkbox(label="Fetch HTML (optional)")

    # RESULTS
    results_group = gr.Group(visible=False)
    with results_group:
        gr.Markdown("### 🧩 Evaluation Results")
        with gr.Row():
            score_out = gr.Number(label="Credibility Score (0–1)", visible=False)
            stars_out = gr.Textbox(label="⭐ Star Rating", visible=False)
        bar_out = gr.HTML(label="Credibility Level")
        summary_out = gr.HTML(label="Credibility Summary")

    # FEEDBACK
    feedback_section = gr.Group(visible=False)
    with feedback_section:
        gr.Markdown("---")
        gr.Markdown("### 🗳️ User Feedback")
        with gr.Row():
            feedback_choice = gr.Radio(["👍 Credible", "👎 Not Credible"], label="Was this result accurate?")
            submit_btn = gr.Button("Submit Feedback", variant="primary")
        feedback_status = gr.Textbox(label="Feedback Status", interactive=False)

    # DASHBOARD
    dashboard_section = gr.Group(visible=False)
    with dashboard_section:
        gr.Markdown("### 📈 Feedback Analytics Dashboard")
        with gr.Row():
            refresh_btn = gr.Button("🔄 Refresh")
            # ✅ Fixed: Gradio 4.x+ supports `value` instead of `file_name`
            download_btn = gr.DownloadButton("⬇️ Download Feedback CSV", value=FEEDBACK_FILE)
            view_btn = gr.Button("👁️ View Feedback Table")
        dashboard_html = gr.HTML()
        chart_html = gr.HTML()
        table_html = gr.HTML()

    # FOOTER
    gr.Markdown("""
    <hr style='margin-top:30px;opacity:0.3;'>
    <div style='text-align:center;color:#aaa;font-size:13px;'>
        © 2025 <a href='https://www.linkedin.com/in/stanleyoccean' target='_blank' style='color:#58a6ff;text-decoration:none;'>Stanley Occean</a> —
        <a href='https://occeanstanley9.github.io' target='_blank' style='color:#58a6ff;text-decoration:none;'>Portfolio</a><br>
        Built with ❤️ using Gradio + Python
    </div>
    """)

    # INTERACTIONS
    evaluate_btn.click(
        fn=ui_score,
        inputs=[url, alpha, fetch],
        outputs=[
            score_out, stars_out, bar_out, summary_out,
            results_group, feedback_section, dashboard_section,
        ],
        show_progress=True,
    )
    submit_btn.click(fn=log_feedback, inputs=[feedback_choice, url, score_out, stars_out], outputs=[feedback_status])
    refresh_btn.click(fn=show_dashboard, outputs=[dashboard_html, chart_html])
    view_btn.click(fn=view_feedback_table, outputs=table_html)

demo.launch()
