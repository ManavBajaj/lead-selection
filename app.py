import html
import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account


def esc(value):
    """HTML-escape a sheet value so stray <, >, ", or ` characters can't
    break the surrounding markdown/HTML structure."""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def initials(name):
    parts = [p for p in str(name or "").strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def get_review_queue(df):
    reviewed_rows = st.session_state.setdefault("reviewed_rows", set())
    pending_mask = df[APPROVAL_COL].astype(str).str.strip().isin(["", "pending_review"])
    return df[pending_mask & ~df.index.isin(reviewed_rows)]

# ─── CONFIG ───────────────────────────────────────────────────────────────────
SHEET_ID = "1SAVhTWod1nQynvmkgLiM_a6yfC0PVSTtwpXPqhK9cEA"
SHEET_NAME = "Leads"
APPROVAL_COL = "approval_status"

# NOTE: move this to st.secrets / environment variables — a hardcoded
# service-account key in source is a real credential leak risk.
SERVICE_ACCOUNT_INFO = {
    "type": "service_account",
    "project_id": "aaw-automation",
    "private_key_id": "6c32ee12d6ed9ef512e744a5ab498d7902574313",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC1n9JaXIQz8E4x\n+Lk7tV8n67KzbVA+BJn5jSywpT7nSNAc+UQqjyxXYMlbigd9aTfLRhZLD53Bm7e3\nZhoeyp5hhFqta2Qq9qOFSHI7TbDr178CIFxFpeibWs4lYgFdEMWr/BYiKHsG7Ug/\nDgVNgl3fYY1kQKBpZAXUNGoHsXNHYW0+Fht8s/b+MV9q2opb3657pigbC+FN+uxz\nyAtzRhrBcqn1/HetJEy8epLvTHTDvcCBxerAe86IBoXDAoeu71/QmVyXNUg2snfm\np+z/zSI7oi+fpLVJgg9reAxyx1szYAcVZNEWYGOo/DDkywriOxE1xrt/GHAwRPvs\n0OVbwN8JAgMBAAECggEAIyBk64sHGpB4XxvOn2ilna/tINycb1IugWA3a3aaItsn\nPONMtrp4BfI3H1gjuLKX0t2cRCoiBabbMkIx/RCM7ylM7Etf1RtcZtOrHCMbe5F/\nZKbjkajTwvAd/Ibm4pvyzx9zHGod2SodFezdQ69Z/nD8io4hOCDbK75zX0eHlx9C\nINgEEKcGY4SJxP0fw24QsnnxzkgTgQB1PpMcjbkrkZB5LtWI6CO2/Mb8dtUVbTOt\n7i5Hm8dJKGoq2CjY7paIHBOKIACniXyJaWRmFg4NKS2vEDyCwVdfvbojIBHfKQSc\neM7G+y/+kHprCQYzZTevcCx/VxvujWipCjY3w45YvQKBgQDi04egFe4k0+Zw9oW/\nTPuyUuGd+vL0R4ebUcbDAR8TEwm1HH+7jjqvZau6aBI4qSKngYnsAiA2/UKNJyck\n0fT0A/Mb7V8w/lT8MCzT+hLTy7Xw5UE78GFFvPh/j3nA23UMR4O6puSLiQ/TNVOj\n83kyLwmQLT55+w8EJsAoOLN35wKBgQDM+/lJcLARVMoG4edEwWrcDg3UYtTYZvlM\n6TQED7d5idolmXe7LZVZYrmSwByuVXAyMI/mD7bigAOWUowXCLIkKu/tlMuTxhFH\n+At/kyVjRq7msJ8oMtoJBKRVHoBVbsP9OCwavPsnBpiogds1Vwi1uc8YDzxEv388\nAKcBuzdTjwKBgDC18HhGfV/XSbOUnWBZreu7tMvyal5fRhXq195kzUGRYxJLznp+\nrsef8+MSGmekmtaSEQZn5ncoqDQb5mIX3JzShFDJBxpEZAfMaLQVDhoBs07KTNoM\nYzdQv6TVMPZjqp06dmWNFaOJiaZ320BoNuy6ATm/HZ2gdrcTg0yf8JqdAoGBAJty\nXepehXavKQGtIHeYgdPc6InuZOCyvk2f761Aye9mJcMrrYuJlt+RKY9rFpTx/8Jf\n51AdDKCZWZ8OfGQfWRBqa0Zs9zDaHFLKfNXDHbA6cvpIaHnQjl4WYhSWq9WdyQzn\nIzMnqwI+U1g+GaFKnjVJcg4Zx6eO3QsAp6V9dwhrAoGARjbYx8Gb/k+tgOuaDDvI\nNDyr4JIZw3FX7s95KCc44+3Tr4ws4VE5OSIeNZ5HKpCCXfJQjW9vIedY5qXWQTIY\n8jqZwbt+P7sdEZxowh4qa6v+UNeTJKsRzoy+1P/l6GSkTL4lUkltDhDY/aXJL4NL\nIHF6Jfumin/fyOPWlYGi5ZY=\n-----END PRIVATE KEY-----\n",
    "client_email": "aaw-automation@aaw-automation.iam.gserviceaccount.com",
    "client_id": "101341220386034274407",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/aaw-automation%40aaw-automation.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Lead Review", page_icon="✉️", layout="centered")

# ─── STYLES ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  :root {
    --accent: #7c9e87;
    --accent-soft: rgba(124, 158, 135, 0.12);
    --bg-card: #121212;
    --bg-inset: #0a0a0a;
    --border: #232323;
    --text-primary: #f2f2f2;
    --text-secondary: #8a8a8a;
    --text-muted: #4a4a4a;
  }

  .block-container { padding-top: 4.5rem; max-width: 640px; }

  /* ── Header ── */
  .app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 4px;
  }
  .app-title {
    font-size: 22px;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    margin: 0;
  }
  .app-subtitle {
    font-size: 13px;
    color: var(--text-muted);
    margin-top: 2px;
  }
  hr { border-color: var(--border) !important; margin: 18px 0 22px 0 !important; }

  /* ── Progress ── */
  .progress-wrap { margin-bottom: 22px; }
  .progress-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 8px;
  }
  .progress-text { font-size: 12.5px; color: var(--text-secondary); font-weight: 500; }
  .progress-count { font-size: 12.5px; color: var(--text-muted); }
  div[data-testid="stProgress"] > div > div {
    background-color: #1c1c1c !important;
    border-radius: 20px !important;
    height: 6px !important;
  }
  div[data-testid="stProgress"] > div > div > div {
    background-image: linear-gradient(90deg, #5c7a66, var(--accent)) !important;
    border-radius: 20px !important;
  }

  /* ── Card ── */
  .card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 30px 32px;
    margin-bottom: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.28);
  }
  .card-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
  .card-top-left { display: flex; align-items: center; gap: 16px; }
  .linkedin-btn {
    flex-shrink: 0;
    display: flex; align-items: center; gap: 6px;
    background: #161b18;
    border: 1px solid #263029;
    color: var(--accent);
    font-size: 11.5px;
    font-weight: 600;
    text-decoration: none;
    padding: 7px 12px 7px 10px;
    border-radius: 20px;
    transition: all 0.15s ease;
  }
  .linkedin-btn:hover {
    background: var(--accent-soft);
    border-color: rgba(124, 158, 135, 0.4);
    transform: translateY(-1px);
  }
  .linkedin-btn svg { width: 13px; height: 13px; flex-shrink: 0; }
  .avatar {
    flex-shrink: 0;
    width: 52px; height: 52px;
    border-radius: 50%;
    background: linear-gradient(135deg, #2a3a2f, #1a241d);
    border: 1px solid #2f3f34;
    color: var(--accent);
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; font-weight: 700; letter-spacing: 0.02em;
  }
  .tag {
    display: inline-block;
    background: var(--accent-soft);
    border: 1px solid rgba(124, 158, 135, 0.28);
    color: var(--accent);
    font-size: 10.5px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 8px;
  }
  .contact-name { font-size: 21px; font-weight: 700; color: var(--text-primary); line-height: 1.25; }
  .contact-title { font-size: 13px; color: var(--text-secondary); margin-top: 2px; }
  .contact-email { color: var(--text-muted); text-decoration: none; }
  .contact-email:hover { color: var(--accent); }

  .divider-soft { height: 1px; background: var(--border); margin: 22px 0; }

  .section-label {
    font-size: 10px; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px;
  }
  .section-text { font-size: 14px; color: #b8b8b8; line-height: 1.7; }
  .section-block + .section-block { margin-top: 20px; }

  .company-row { display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: 6px; }
  .company-name { color: #e2e2e2; font-weight: 600; font-size: 14.5px; }
  .company-link { color: var(--text-muted); font-size: 12px; text-decoration: none; }
  .company-link:hover { color: var(--accent); }

  .insight-box {
    background: var(--accent-soft);
    border: 1px solid rgba(124, 158, 135, 0.22);
    border-radius: 10px;
    padding: 12px 14px;
    font-size: 13.5px;
    color: #a9c4b1;
    font-style: italic;
    line-height: 1.6;
  }

  /* ── Email preview ── */
  .email-label-row {
    display: flex; align-items: center; gap: 6px;
    margin: 22px 2px 8px 2px;
  }
  .email-preview {
    background: var(--bg-inset);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 22px;
  }
  .email-subject {
    font-size: 14.5px; font-weight: 600; color: #d8d8d8;
    padding-bottom: 12px; margin-bottom: 12px;
    border-bottom: 1px dashed #1f1f1f;
  }
  .email-body { font-size: 13px; color: #888; line-height: 1.85; white-space: pre-wrap; }

  /* ── Buttons ── */
  div[data-testid="stHorizontalBlock"] button {
    border-radius: 12px !important;
    height: 46px !important;
    font-weight: 600 !important;
    font-size: 14.5px !important;
    transition: all 0.15s ease !important;
    border: 1px solid var(--border) !important;
  }
  div[data-testid="stHorizontalBlock"] button:hover { transform: translateY(-1px); }
  button[kind="primary"] {
    background: linear-gradient(135deg, #5c7a66, #46614f) !important;
    border: none !important;
  }
  button[kind="primary"]:hover { box-shadow: 0 6px 16px rgba(92, 122, 102, 0.35) !important; }
  button[kind="secondary"] {
    background: #161616 !important;
    color: #d0817e !important;
  }
  button[kind="secondary"]:hover { border-color: #3a2323 !important; background: #1a1414 !important; }

  /* ── Done state ── */
  .done-state { text-align: center; padding: 70px 20px 30px 20px; }
  .done-emoji { font-size: 46px; }
  .done-title {
    font-size: 21px; font-weight: 700; color: var(--text-primary);
    margin-top: 14px; letter-spacing: -0.01em;
  }
  .done-sub { font-size: 13.5px; color: var(--text-muted); margin-top: 6px; }

  div[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 14px 10px;
  }
  div[data-testid="stMetricValue"] { font-size: 26px !important; }
</style>
""", unsafe_allow_html=True)


# ─── GOOGLE SHEETS ────────────────────────────────────────────────────────────
@st.cache_resource
def get_worksheet():
    creds = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(creds)
    sh = client.open_by_key(SHEET_ID)
    return sh.worksheet(SHEET_NAME)


@st.cache_data(ttl=10)
def load_data():
    ws = get_worksheet()
    records = ws.get_all_records()
    return pd.DataFrame(records), ws.row_values(1)


def write_decision(row_index, decision, headers):
    ws = get_worksheet()
    if APPROVAL_COL not in headers:
        col_idx = len(headers) + 1
        ws.update_cell(1, col_idx, APPROVAL_COL)
    else:
        col_idx = headers.index(APPROVAL_COL) + 1
    ws.update_cell(row_index + 2, col_idx, decision)
    load_data.clear()


def mark_reviewed(row_index):
    st.session_state.setdefault("reviewed_rows", set()).add(row_index)


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    header_html = "".join([
        '<div class="app-header">',
        '<div><p class="app-title">✉️ Lead Review</p>',
        '<p class="app-subtitle">Approve or reject leads before outreach</p></div>',
        '</div>',
    ])
    st.markdown(header_html, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    try:
        df, headers = load_data()
    except Exception as e:
        st.error(f"Could not connect to Google Sheet: {e}")
        return

    if APPROVAL_COL not in df.columns:
        df[APPROVAL_COL] = ""

    pending = get_review_queue(df)
    total = len(df)
    reviewed = total - len(pending)

    # ── ALL DONE ──
    if len(pending) == 0:
        done_html = "".join([
            '<div class="done-state">',
            '<div class="done-emoji">🎉</div>',
            '<div class="done-title">All done!</div>',
            '<div class="done-sub">You\'ve reviewed all leads.</div>',
            '</div>',
        ])
        st.markdown(done_html, unsafe_allow_html=True)
        approved = len(df[df[APPROVAL_COL] == "approved"])
        rejected = len(df[df[APPROVAL_COL] == "rejected"])
        c1, c2 = st.columns(2)
        c1.metric("✅ Approved", approved)
        c2.metric("❌ Rejected", rejected)
        return

    # ── PROGRESS ──
    progress_html = "".join([
        '<div class="progress-wrap"><div class="progress-row">',
        f'<span class="progress-text">{reviewed} of {total} reviewed</span>',
        f'<span class="progress-count">{len(pending)} left</span>',
        '</div></div>',
    ])
    st.markdown(progress_html, unsafe_allow_html=True)
    st.progress(reviewed / total if total > 0 else 0)
    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

    # ── CURRENT LEAD ──
    row = pending.iloc[0]
    row_index = pending.index[0]

    desc = str(row.get("business_description", ""))
    desc_short = desc[:400] + "..." if len(desc) > 400 else desc

    contact_name = row.get("contact_name", "")
    category = row.get("industry") or row.get("business_category", "")
    linkedin = row.get("contact_linkedin", "")

    linkedin_svg = (
        '<svg viewBox="0 0 24 24" fill="currentColor">'
        '<path d="M20.45 20.45h-3.55v-5.57c0-1.33-.02-3.03-1.85-3.03-1.85 0-2.14 '
        '1.45-2.14 2.94v5.66H9.36V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 '
        '3.6 0 4.27 2.37 4.27 5.45v6.29zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 '
        '2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45z"/></svg>'
    )
    linkedin_btn = (
        f'<a class="linkedin-btn" href="{esc(linkedin)}" target="_blank">{linkedin_svg}<span>LinkedIn</span></a>'
        if linkedin else ""
    )

    card_parts = [
        '<div class="card">',
        '<div class="card-top">',
        '<div class="card-top-left">',
        f'<div class="avatar">{esc(initials(contact_name))}</div>',
        '<div>',
        f'<span class="tag">{esc(category)}</span>' if category else "",
        f'<div class="contact-name">{esc(contact_name)}</div>',
        f'<div class="contact-title">{esc(row.get("contact_title", ""))} &nbsp;·&nbsp; ',
        f'<a class="contact-email" href="mailto:{esc(row.get("contact_email",""))}">',
        f'{esc(row.get("contact_email",""))}</a></div>',
        '</div></div>',
        linkedin_btn,
        '</div>',

        '<div class="divider-soft"></div>',

        '<div class="section-block">',
        '<div class="section-label">Company</div>',
        '<div class="company-row">',
        f'<span class="company-name">{esc(row.get("business_name",""))}</span>',
        f'<a class="company-link" href="{esc(row.get("business_website",""))}" target="_blank">',
        f'{esc(row.get("business_domain",""))} ↗</a>',
        '</div></div>',

        '<div class="section-block">',
        '<div class="section-label">About</div>',
        f'<div class="section-text">{esc(desc_short)}</div>',
        '</div>',

        '<div class="section-block">',
        '<div class="section-label">AI Insight</div>',
        f'<div class="insight-box">💡 {esc(row.get("ai_insight",""))}</div>',
        '</div>',

        '</div>',
    ]
    st.markdown("".join(card_parts), unsafe_allow_html=True)

    # ── EMAIL PREVIEW ──
    st.markdown('<div class="email-label-row"><span class="section-label" style="margin:0">Email Preview</span></div>',
                unsafe_allow_html=True)
    email_html = "".join([
        '<div class="email-preview">',
        f'<div class="email-subject">📧 {esc(row.get("email_subject",""))}</div>',
        f'<div class="email-body">{esc(row.get("email_body",""))}</div>',
        '</div>',
    ])
    st.markdown(email_html, unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── BUTTONS ──
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✕  Reject", key="reject", use_container_width=True):
            mark_reviewed(row_index)
            write_decision(row_index, "rejected", headers)
            st.rerun()
    with col2:
        if st.button("✓  Approve", key="approve", type="primary", use_container_width=True):
            mark_reviewed(row_index)
            write_decision(row_index, "approved", headers)
            st.rerun()
    with col3:
        if st.button("↷  Later", key="later", use_container_width=True):
            mark_reviewed(row_index)
            st.rerun()


if __name__ == "__main__":
    main()