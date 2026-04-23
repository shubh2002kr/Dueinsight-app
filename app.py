import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="DueInsight — DD Workstation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# UI STYLE
# ---------------------------------------------------
def apply_custom_style(dark_mode):
    bg_color      = "#0e1117" if dark_mode else "#f8f9fa"
    card_bg       = "rgba(255,255,255,0.05)" if dark_mode else "rgba(255,255,255,0.8)"
    text_color    = "#30b2c9"
    # All body / content text inside cards: near-white in dark, near-black in light
    content_text  = "#f0f0f0" if dark_mode else "#111111"
    border_color  = "rgba(255,255,255,0.1)" if dark_mode else "rgba(0,0,0,0.1)"
    divider_color = "rgba(255,255,255,0.1)" if dark_mode else "rgba(0,0,0,0.1)"
    accent        = "#00dfd8"

    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg_color}; }}
        /* Make all component iframes transparent */
        iframe {{ background: transparent !important; }}
        .stIFrame {{ background: transparent !important; }}
        /* Shrink logo iframe to content width */
        div[data-testid="column"]:first-child iframe {{
            width: fit-content !important;
            max-width: 200px !important;
        }}
        .card {{
            background: {card_bg};
            padding: 30px;
            border-radius: 20px;
            border: 1px solid {border_color};
            margin-bottom: 25px;
            color: {content_text};
        }}
        /* All plain text inside a card inherits content_text */
        .card p, .card span, .card div, .card li {{
            color: {content_text};
        }}
        .main-title {{
            text-align: center;
            font-size: 54px;
            font-weight: 800;
            color: #30b2c9;
            margin-bottom: 5px;
        }}
        .section-title {{
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 20px;
            color: {text_color};
        }}
        .universal-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px,1fr));
            gap: 15px;
        }}
        .btn-ui {{
            text-align: center;
            padding: 12px;
            border-radius: 10px;
            font-weight: 600;
            color: white !important;
            text-decoration: none !important;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }}
        .list-item-btn {{
            display: block;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 12px;
            background: rgba(128,128,128,0.08);
            text-decoration: none !important;
            color: {content_text} !important;
            border-left: 5px solid {accent};
            font-size: 14px;
            line-height: 1.5;
        }}
        .list-item-btn:hover {{
            background: rgba(128,128,128,0.16);
            color: {content_text} !important;
        }}
        /* "No results" / empty-state paragraphs */
        .empty-state {{
            font-size: 14px;
            color: {content_text};
            opacity: 0.55;
        }}
        /* Divider inside litigation card */
        .lit-divider {{
            border-top: 1px solid {divider_color};
            padding-top: 15px;
        }}
        </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------
# HEADER & THEME
# ---------------------------------------------------
# Logo embedded as base64 — no external file dependency
_logo_b64 = "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"

top_col1, top_col2 = st.columns([10, 1])
dark_mode = True

with top_col1:
    import streamlit.components.v1 as _ch
    _ch.html(f"""
    <style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      html, body {{
        background: transparent !important;
        overflow: hidden;
        width: fit-content;
        height: fit-content;
      }}

      .logo-outer {{
        position: relative;
        display: inline-flex;
        width: fit-content;
        animation: logoPop 0.7s cubic-bezier(.34,1.4,.64,1) both;
      }}

      /* Animated gradient border using pseudo-element */
      .logo-outer::before {{
        content: '';
        position: absolute;
        inset: -2px;
        border-radius: 14px;
        background: linear-gradient(90deg,
          rgba(0,223,216,0) 0%,
          rgba(0,223,216,0.8) 25%,
          rgba(48,178,201,0.9) 50%,
          rgba(0,223,216,0.8) 75%,
          rgba(0,223,216,0) 100%
        );
        background-size: 300% 100%;
        animation: borderSweep 3s linear infinite;
        z-index: 0;
        opacity: 0.6;
      }}

      /* Outer glow pulse */
      .logo-outer::after {{
        content: '';
        position: absolute;
        inset: -4px;
        border-radius: 16px;
        background: transparent;
        box-shadow: 0 0 0 1px rgba(0,223,216,0.15);
        animation: outerPulse 2.5s ease-in-out infinite;
        z-index: 0;
      }}

      @keyframes borderSweep {{
        0%   {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
      }}

      @keyframes outerPulse {{
        0%,100% {{ box-shadow: 0 0 0 1px rgba(0,223,216,0.10), 0 0 10px rgba(0,223,216,0.05); }}
        50%      {{ box-shadow: 0 0 0 2px rgba(0,223,216,0.35), 0 0 22px rgba(0,223,216,0.18); }}
      }}

      .logo-wrap {{
        position: relative;
        z-index: 1;
        display: inline-flex;
        align-items: center;
        padding: 7px 16px;
        border-radius: 12px;
        width: fit-content;
        background: {"rgba(18,22,32,0.92)" if dark_mode else "rgba(255,255,255,0.95)"};
        border: 1px solid {"rgba(255,255,255,0.08)" if dark_mode else "rgba(0,0,0,0.08)"};
        transition: box-shadow 0.3s, transform 0.3s;
        cursor: pointer;
      }}

      .logo-wrap:hover {{
        transform: scale(1.05) translateY(-1px);
        box-shadow: 0 6px 28px rgba(0,223,216,0.25);
      }}
      .logo-wrap:hover ~ * {{ }}

      .logo-wrap img {{
        height: 30px;
        width: auto;
        display: block;
        {"mix-blend-mode: lighten;" if dark_mode else ""}
        animation: logoFloat 4s ease-in-out infinite;
      }}

      @keyframes logoFloat {{
        0%,100% {{ transform: translateY(0px);   filter: drop-shadow(0 0 2px rgba(0,223,216,0.0)); }}
        50%      {{ transform: translateY(-2px);  filter: drop-shadow(0 0 8px rgba(0,223,216,0.4)); }}
      }}

      @keyframes logoPop {{
        from {{ opacity:0; transform:translateX(-20px) scale(0.85); }}
        to   {{ opacity:1; transform:translateX(0) scale(1); }}
      }}
    </style>

    <div class="logo-outer">
      <div class="logo-wrap">
        <img src="data:image/png;base64,{_logo_b64}" alt="Acquisory" />
      </div>
    </div>
    """, height=56, scrolling=False)

apply_custom_style(dark_mode)

# ── Animated Hero Header ─────────────────────────────────────────────────────
import streamlit.components.v1 as components_hero

hero_bg        = "#0e1117"                    if dark_mode else "#f0f4f8"
subtitle_color = "rgba(255,255,255,0.55)"     if dark_mode else "rgba(0,0,0,0.50)"
orb1_c         = "rgba(0,223,216,0.13)"       if dark_mode else "rgba(0,223,216,0.08)"
orb2_c         = "rgba(48,178,201,0.10)"      if dark_mode else "rgba(48,178,201,0.06)"
grid_col       = "rgba(255,255,255,0.03)"     if dark_mode else "rgba(0,0,0,0.03)"
stat_sep_c     = "rgba(255,255,255,0.08)"     if dark_mode else "rgba(0,0,0,0.08)"
input_bg       = "rgba(255,255,255,0.06)"     if dark_mode else "rgba(255,255,255,0.9)"
input_bdr      = "rgba(0,223,216,0.20)"       if dark_mode else "rgba(0,180,180,0.25)"
input_col      = "#f0f0f0"                    if dark_mode else "#111111"
input_ph       = "rgba(255,255,255,0.30)"     if dark_mode else "rgba(0,0,0,0.35)"

hero_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'Inter', -apple-system, sans-serif;
    background: {hero_bg};
    padding: 0;
    overflow: hidden;
  }}

  /* ── Hero wrapper ── */
  .hero-wrap {{
    position: relative;
    text-align: center;
    padding: 44px 20px 32px;
    overflow: hidden;
    border-radius: 20px;
    background: {hero_bg};
  }}

  /* Animated grid */
  .hero-wrap::before {{
    content: '';
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient({grid_col} 1px, transparent 1px),
      linear-gradient(90deg, {grid_col} 1px, transparent 1px);
    background-size: 40px 40px;
    animation: gridDrift 18s linear infinite;
    pointer-events: none;
  }}
  @keyframes gridDrift {{
    from {{ background-position: 0 0; }}
    to   {{ background-position: 40px 40px; }}
  }}

  /* Floating orbs */
  .orb {{
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    pointer-events: none;
    animation: orbFloat 8s ease-in-out infinite alternate;
  }}
  .orb1 {{ width:320px; height:320px; background:{orb1_c}; top:-90px; left:-50px; animation-delay:0s; }}
  .orb2 {{ width:260px; height:260px; background:{orb2_c}; bottom:-70px; right:-30px; animation-delay:-3s; }}
  .orb3 {{ width:160px; height:160px; background:rgba(0,223,216,0.06); top:20px; right:18%; animation-delay:-5s; }}
  @keyframes orbFloat {{
    from {{ transform: translate(0,0) scale(1); }}
    to   {{ transform: translate(18px,14px) scale(1.08); }}
  }}

  /* Badge */
  .hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(0,223,216,0.10);
    border: 1px solid rgba(0,223,216,0.28);
    border-radius: 30px;
    padding: 5px 14px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: #00dfd8;
    margin-bottom: 18px;
    position: relative; z-index: 1;
    animation: fadeDown 0.55s ease both;
  }}
  .badge-dot {{
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #00dfd8;
    animation: blink 1.5s ease-in-out infinite;
  }}
  @keyframes blink {{ 0%,100%{{opacity:1;}} 50%{{opacity:0.2;}} }}

  /* Title */
  .hero-title {{
    font-size: 58px;
    font-weight: 900;
    letter-spacing: -2px;
    line-height: 1;
    margin-bottom: 12px;
    background: linear-gradient(135deg, #ffffff 0%, #30b2c9 40%, #00dfd8 70%, #ffffff 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradShift 5s ease infinite, fadeUp 0.65s ease 0.1s both;
    position: relative; z-index: 1;
  }}
  @keyframes gradShift {{
    0%,100% {{ background-position: 0% 50%; }}
    50%      {{ background-position: 100% 50%; }}
  }}

  /* Subtitle */
  .hero-sub {{
    font-size: 14px;
    font-weight: 500;
    color: {subtitle_color};
    letter-spacing: 0.3px;
    margin-bottom: 28px;
    position: relative; z-index: 1;
    animation: fadeUp 0.65s ease 0.22s both;
  }}

  /* Stats */
  .hero-stats {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 28px;
    margin-top: 22px;
    position: relative; z-index: 1;
    animation: fadeUp 0.65s ease 0.38s both;
  }}
  .stat-item {{ text-align: center; }}
  .stat-num {{
    font-size: 17px; font-weight: 800;
    color: #00dfd8; line-height: 1;
  }}
  .stat-lbl {{
    font-size: 9.5px; font-weight: 600;
    letter-spacing: 0.06em; text-transform: uppercase;
    color: {subtitle_color}; margin-top: 3px;
  }}
  .stat-sep {{
    width: 1px; height: 28px;
    background: {stat_sep_c};
  }}

  @keyframes fadeUp {{
    from {{ opacity:0; transform:translateY(14px); }}
    to   {{ opacity:1; transform:translateY(0); }}
  }}
  @keyframes fadeDown {{
    from {{ opacity:0; transform:translateY(-8px); }}
    to   {{ opacity:1; transform:translateY(0); }}
  }}
</style>
</head>
<body>
<div class="hero-wrap">
  <div class="orb orb1"></div>
  <div class="orb orb2"></div>
  <div class="orb orb3"></div>

  <div class="hero-badge">
    <span class="badge-dot"></span>
    Advanced Due Diligence Platform
  </div>

  <div class="hero-title">DueInsight</div>
  <div class="hero-sub">Advanced Due Diligence &amp; Litigation Workstation</div>

</div>
</body>
</html>"""

components_hero.html(hero_html, height=200, scrolling=False)

# Also style Streamlit inputs globally
st.markdown(f"""
<style>
div[data-testid="stTextInput"] > div > div > input {{
    background: {input_bg} !important;
    border: 1px solid {input_bdr} !important;
    border-radius: 14px !important;
    color: {input_col} !important;
    font-size: 15px !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}}
div[data-testid="stTextInput"] > div > div > input:focus {{
    border-color: rgba(0,223,216,0.60) !important;
    box-shadow: 0 0 0 3px rgba(0,223,216,0.12) !important;
    outline: none !important;
}}
div[data-testid="stTextInput"] > div > div > input::placeholder {{
    color: {input_ph} !important;
}}
/* Remove white background from all input wrappers */
div[data-testid="stTextInput"] {{
    background: transparent !important;
}}
div[data-testid="stTextInput"] > div {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}
div[data-testid="stTextInput"] > div > div {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# SEARCH SECTION
# ---------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    person_input  = st.text_input("Person",  placeholder="👤 Person Name",  key="p_input", label_visibility="collapsed")
    company_input = st.text_input("Company", placeholder="🏢 Company Name", key="c_input", label_visibility="collapsed")

p_name = person_input.strip()
c_name = company_input.strip()

# ---------------------------------------------------
# LOGIC & RESULTS BLOCK
# ---------------------------------------------------
if p_name or c_name:
    search_term = p_name if p_name else c_name
    st.divider()

    # ── URL-safe versions ────────────────────────────────────────────────────
    # q_encoded  : quoted version for embedding inside Google search query strings
    # q_raw      : the plain search term (used in paths like dilisense)
    q_encoded  = urllib.parse.quote(f'"{search_term}"')   # → %22search+term%22
    q_raw      = urllib.parse.quote(search_term)           # → search+term (no quotes)

    # ── LinkedIn search query ────────────────────────────────────────────────
    if p_name and c_name:
        ln_query = f'site:linkedin.com/ intitle:"{p_name}" "{c_name}"'
    elif p_name:
        ln_query = f'site:linkedin.com/ intitle:"{p_name}"'
    else:
        ln_query = f'site:linkedin.com/company "{c_name}"'

    ln_search_url = f"https://www.google.com/search?q={urllib.parse.quote(ln_query)}"

    # ── Data Fetching ────────────────────────────────────────────────────────
    news               = []
    litigation_results = []

    with st.spinner(f"Analysing {search_term}…"):

        # Google News RSS
        try:
            news_url  = f"https://news.google.com/rss/search?q={q_encoded}"
            news_resp = requests.get(news_url, timeout=5)
            news_resp.raise_for_status()
            # Use "lxml-xml" if available, fall back to "xml"
            try:
                soup_news = BeautifulSoup(news_resp.content, "lxml-xml")
            except Exception:
                soup_news = BeautifulSoup(news_resp.content, "xml")
            news = soup_news.find_all("item")[:15]
        except Exception:
            pass

        # Indian Kanoon scrape
        try:
            ik_url  = f"https://indiankanoon.org/search/?formInput=%22{q_raw}%22"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            ik_resp = requests.get(ik_url, headers=headers, timeout=5)
            ik_resp.raise_for_status()
            soup_ik = BeautifulSoup(ik_resp.text, "html.parser")
            for item in soup_ik.select(".result")[:6]:
                a = item.find("a")
                if a and a.get("href"):
                    litigation_results.append({
                        "title": a.get_text(strip=True),
                        "link" : "https://indiankanoon.org" + a["href"]
                    })
        except Exception:
            pass

    # ── Layout ───────────────────────────────────────────────────────────────
    l_col, r_col = st.columns(2)

    with l_col:
        # ── Profile Research — Premium Animated iframe ────────────────────────
        import streamlit.components.v1 as components_profile

        pr_bg_card  = "rgba(255,255,255,0.05)" if dark_mode else "rgba(255,255,255,0.88)"
        pr_card_bdr = "rgba(255,255,255,0.10)" if dark_mode else "rgba(0,0,0,0.10)"

        profile_tabs = [
            ("🔍", "About Profile",    "#34495e", "rgba(52,73,94,0.35)",
             f"https://www.google.com/search?q=allintitle:{q_encoded}+biography"),
            ("📇", "Contacts",         "#3498db", "rgba(52,152,219,0.35)",
             f"https://www.google.com/search?q=site:rocketreach.co+{q_encoded}"),
            ("🪟", "Glassdoor",        "#2ecc71", "rgba(46,204,113,0.35)",
             f"https://www.google.com/search?q=site:glassdoor.co.in+{q_encoded}"),
            ("💻", "Naukri",           "#0057FF", "rgba(0,87,255,0.35)",
             f"https://www.google.com/search?q=site:naukri.com+{q_encoded}"),
            ("📦", "AmbitionBox",      "#FF7A00", "rgba(255,122,0,0.35)",
             f"https://www.google.com/search?q=site:ambitionbox.com+{q_encoded}"),
            ("📞", "Justdial",         "#003A9B", "rgba(0,58,155,0.35)",
             f"https://www.google.com/search?q=site:justdial.com+{q_encoded}"),
            ("📍", "Magicpin",         "#FF4A00", "rgba(255,74,0,0.35)",
             f"https://www.google.com/search?q=site:magicpin.in+{q_encoded}"),
            ("🍽️", "EazyDiner",        "#D32F2F", "rgba(211,47,47,0.35)",
             f"https://www.google.com/search?q=site:eazydiner.com+{q_encoded}"),
            ("🏢", "Zauba",            "#6f42c1", "rgba(111,66,193,0.35)",
             f"https://www.google.com/search?q=site:zaubacorp.com+{q_encoded}"),
            ("🤖", "ChatGPT",          "#10a37f", "rgba(16,163,127,0.35)",
             f"https://chatgpt.com/?q={q_raw}"),
        ]

        profile_cards_html = ""
        for i, (icon, name, color, glow, url) in enumerate(profile_tabs):
            delay = i * 0.06
            profile_cards_html += f"""
            <a href="{url}" target="_blank" class="pr-card" style="--c:{color};--g:{glow};animation-delay:{delay}s">
              
              <div class="pr-glow"></div>
              <div class="pr-inner">
                <div class="pr-icon-wrap">
                  <span class="pr-icon">{icon}</span>
                </div>
                <span class="pr-name">{name}</span>
                <span class="pr-arr">↗</span>
              </div>
            </a>"""

        profile_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'Inter', -apple-system, sans-serif;
    background: {pr_bg_card};
    border: 1px solid {pr_card_bdr};
    border-radius: 20px;
    padding: 22px;
    overflow: visible;
  }}

  .sec-title {{
    font-size: 18px;
    font-weight: 800;
    color: #30b2c9;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 10px;
    letter-spacing: -0.3px;
  }}
  .sec-title::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, rgba(0,223,216,0.35), transparent);
  }}

  /* ── Grid ── */
  .pr-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
  }}

  /* ── Card ── */
  .pr-card {{
    position: relative;
    border-radius: 13px;
    border: 1px solid rgba(255,255,255,0.07);
    background: linear-gradient(135deg, color-mix(in srgb, var(--c) 22%, #0e1117), color-mix(in srgb, var(--c) 10%, #0e1117));
    text-decoration: none;
    overflow: hidden;
    cursor: pointer;
    opacity: 0;
    transform: scale(0.88) translateY(12px);
    animation: popIn 0.45s cubic-bezier(.34,1.4,.64,1) forwards;
    transition: transform 0.22s cubic-bezier(.34,1.5,.64,1),
                box-shadow 0.22s ease,
                border-color 0.22s ease;
  }}
  @keyframes popIn {{
    to {{ opacity: 1; transform: scale(1) translateY(0); }}
  }}

  .pr-card:hover {{
    transform: translateY(-5px) scale(1.04);
    box-shadow: 0 12px 32px rgba(0,0,0,0.35), 0 0 0 1px var(--c);
    border-color: var(--c);
  }}

  /* Radial glow that appears on hover */
  .pr-glow {{
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 50% 110%, var(--g), transparent 65%);
    opacity: 0;
    transition: opacity 0.28s ease;
    pointer-events: none;
  }}
  .pr-card:hover .pr-glow {{ opacity: 1; }}

  .pr-inner {{
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 7px;
    padding: 16px 10px 12px;
  }}

  /* Icon circle */
  .pr-icon-wrap {{
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(255,255,255,0.10);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.22s cubic-bezier(.34,1.5,.64,1), background 0.2s;
    position: relative;
  }}
  .pr-icon-wrap::after {{
    content: '';
    position: absolute;
    inset: -3px;
    border-radius: 50%;
    border: 1.5px solid var(--c);
    opacity: 0;
    transform: scale(0.8);
    transition: opacity 0.22s, transform 0.22s;
  }}
  .pr-card:hover .pr-icon-wrap {{
    transform: scale(1.18) rotate(-6deg);
    background: rgba(255,255,255,0.16);
  }}
  .pr-card:hover .pr-icon-wrap::after {{
    opacity: 0.7;
    transform: scale(1);
    animation: ring 1.3s ease-in-out infinite;
  }}
  @keyframes ring {{
    0%,100% {{ opacity:0.7; transform:scale(1); }}
    50%      {{ opacity:0.2; transform:scale(1.18); }}
  }}

  .pr-icon {{ font-size: 18px; line-height: 1; }}

  .pr-name {{
    font-size: 11px;
    font-weight: 700;
    color: rgba(255,255,255,0.88);
    text-align: center;
    letter-spacing: 0.1px;
    line-height: 1.2;
    transition: color 0.18s;
  }}
  .pr-card:hover .pr-name {{ color: #fff; }}

  /* Arrow indicator top-right */
  .pr-arr {{
    position: absolute;
    top: 8px;
    right: 9px;
    font-size: 9px;
    color: rgba(255,255,255,0.25);
    transition: color 0.18s, transform 0.18s;
  }}
  .pr-card:hover .pr-arr {{
    color: rgba(255,255,255,0.85);
    transform: translate(2px,-2px);
  }}
</style>
</head>
<body>
  <div class="sec-title">🧑‍💼 Profile Research</div>
  <div class="pr-grid">
    {profile_cards_html}
  </div>
</body>
</html>"""

        components_profile.html(profile_html, height=520, scrolling=False)

        # ── Litigation Records — Premium Animated iframe ─────────────────────
        # ── Litigation Records — Premium Animated iframe ─────────────────────
        import streamlit.components.v1 as components_lit

        lt_bg_card  = "rgba(255,255,255,0.05)" if dark_mode else "rgba(255,255,255,0.88)"
        lt_card_bdr = "rgba(255,255,255,0.10)" if dark_mode else "rgba(0,0,0,0.10)"
        lt_entry_bg = "rgba(255,255,255,0.04)" if dark_mode else "#ffffff"
        lt_entry_bdr = "rgba(255,255,255,0.08)" if dark_mode else "rgba(0,0,0,0.08)"
        lt_title_c = "#f0f0f0" if dark_mode else "#111111"
        lt_meta_c = "#6b7a8d" if dark_mode else "#888888"
        lt_hover_bg = "rgba(255,255,255,0.07)" if dark_mode else "rgba(0,0,0,0.03)"

        # Quick-access button cards
        target_company = c_name.strip() if c_name.strip() else p_name.strip()
        search_term = p_name if p_name else c_name
        q_encoded = urllib.parse.quote(f'"{search_term}"')
        q_raw = urllib.parse.quote(search_term)

        litigation_ai_prompt = f"""
Conduct a comprehensive legal due diligence and litigation search for the company {target_company}, including all its subsidiaries, group entities, affiliates, past entities, and associated businesses, along with its promoters, directors, key managerial personnel (KMPs), and beneficial owners.

The objective is to identify any legal risks, disputes, or red flags across District Courts, High Courts, and the Supreme Court of India.

Please cover pending, disposed, and stayed cases across jurisdictions, including civil disputes, criminal cases, corporate and commercial litigation, insolvency and bankruptcy proceedings, cheque bounce cases under NI Act Section 138, employment or labour disputes, and regulatory or compliance-related cases.

Also check FIRs, charge sheets, police complaints, ED, CBI, Income Tax Department, and SFIO actions.

Analyse litigation frequency and patterns, jurisdiction-wise distribution, nature and severity of disputes, repeat allegations, systemic issues, adverse judicial observations, penalties, NCLT, NCLAT, insolvency, liquidation, restructuring, recovery actions by banks or financial institutions, blacklisting, corruption, bribery, kickback allegations, cross-border litigation, and international arbitration.

Use sources including eCourts India, High Court records, Supreme Court records, SCC Online, Manupatra, public court orders, and public filings.

Output a structured summary of findings, case-wise details with party name, case number, court, status, brief facts, key legal risks and red flags, and an overall litigation risk rating as Low, Medium, or High.
"""

        ai_prompt_encoded = urllib.parse.quote(litigation_ai_prompt)

        quick_btns_html = f"""
        <a href="https://ecourts.gov.in/ecourts_home/" target="_blank" class="quick-btn" style="--qc:#e67e22;">
        <span class="qb-icon">🏛️</span><span class="qb-name">eCourts India</span><span class="qb-arr">↗</span>
        </a>

        <a href="https://www.sci.gov.in/case-status-case-no/" target="_blank" class="quick-btn" style="--qc:#c0392b;">
        <span class="qb-icon">🔱</span><span class="qb-name">Supreme Court</span><span class="qb-arr">↗</span>
        </a>

        <a href="https://services.ecourts.gov.in/ecourtindia_v6/?p=high_court/index&app_token=" target="_blank" class="quick-btn" style="--qc:#8e44ad;">
        <span class="qb-icon">⚖️</span><span class="qb-name">High Court</span><span class="qb-arr">↗</span>
        </a>

        <a href="https://ecourts.gov.in/ecourts2.0//?p=dist_court&app_token=" target="_blank" class="quick-btn" style="--qc:#27ae60;">
        <span class="qb-icon">🏢</span><span class="qb-name">District Court</span><span class="qb-arr">↗</span>
        </a>

        <a href="https://indiankanoon.org/search/?formInput=%22{q_raw}%22" target="_blank" class="quick-btn" style="--qc:#30b2c9;">
        <span class="qb-icon">📚</span><span class="qb-name">Indian Kanoon</span><span class="qb-arr">↗</span>
        </a>

        
        <a href="https://chatgpt.com/?q={ai_prompt_encoded}" target="_blank" class="quick-btn" style="--qc:#10a37f;">
        <span class="qb-icon">🤖</span><span class="qb-name">ChatGPT</span><span class="qb-arr">↗</span>
        </a>

        """

        # Litigation result cards
        if "litigation_results" not in locals():
            litigation_results = []

        lit_cards_html = ""
        for i, res in enumerate(litigation_results):
            delay = i * 0.07
            lit_cards_html += f"""
            <a href="{res['link']}" target="_blank" class="news-card" style="animation-delay:{delay}s">
              <div class="news-card-inner">
                <div class="news-bar"></div>
                <div class="news-body">
                  <div class="news-meta">
                    <span class="news-source">Indian Kanoon</span>
                    <span class="news-dot">·</span>
                    <span class="news-date">Court Record</span>
                  </div>
                  <div class="news-title">{res['title']}</div>
                  <div class="news-cta">View judgment <span class="news-arrow">→</span></div>
                </div>
                <div class="news-badge">⚖️</div>
              </div>
            </a>
            """

        lt_empty = "<div class='no-news'>No instant records found. Use the databases above.</div>" if not lit_cards_html else ""
        lt_num = max(len(litigation_results), 1)
        lt_h = min(180 + lt_num * 100, 680)

        if not litigation_results:
            lt_h = 220

        import streamlit.components.v1 as components_lit

        lt_bg_card = "rgba(255,255,255,0.05)" if dark_mode else "rgba(255,255,255,0.88)"
        lt_card_bdr = "rgba(255,255,255,0.10)" if dark_mode else "rgba(0,0,0,0.10)"
        lt_entry_bg = "rgba(255,255,255,0.04)" if dark_mode else "#ffffff"
        lt_entry_bdr = "rgba(255,255,255,0.08)" if dark_mode else "rgba(0,0,0,0.08)"
        lt_title_c = "#f0f0f0" if dark_mode else "#111111"
        lt_meta_c = "#6b7a8d" if dark_mode else "#888888"
        lt_hover_bg = "rgba(255,255,255,0.07)" if dark_mode else "rgba(0,0,0,0.03)"

        lt_empty = "<div class='no-news'>No instant records found. Use the databases above.</div>" if not lit_cards_html else ""
        lt_num = max(len(litigation_results), 1)
        lt_h = 220 if not litigation_results else min(180 + lt_num * 100, 680)

        lit_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: Inter, sans-serif;
    background: {lt_bg_card};
    border: 1px solid {lt_card_bdr};
    border-radius: 20px;
    padding: 22px;
    overflow: visible;
}}
.sec-title {{
    font-size: 18px;
    font-weight: 800;
    color: #30b2c9;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.sec-title::after {{
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, rgba(0,223,216,0.35), transparent);
}}
.quick-row {{
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
    flex-wrap: wrap;
}}
.quick-btn {{
    flex: 1;
    min-width: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 9px 12px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.08);
    background: color-mix(in srgb, var(--qc) 18%, transparent);
    text-decoration: none;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}}
.quick-btn:hover {{
    transform: translateY(-3px) scale(1.03);
    box-shadow: 0 8px 22px rgba(0,0,0,0.28), 0 0 0 1px var(--qc);
}}
.qb-icon {{ font-size: 15px; }}
.qb-name {{
    font-size: 12px;
    font-weight: 700;
    color: rgba(255,255,255,0.9);
    white-space: nowrap;
}}
.qb-arr {{
    font-size: 10px;
    color: rgba(255,255,255,0.4);
    margin-left: auto;
}}
.divider {{
    height: 1px;
    background: linear-gradient(to right, rgba(0,223,216,0.2), transparent);
    margin-bottom: 14px;
}}
.news-feed {{
    display: flex;
    flex-direction: column;
    gap: 9px;
}}
.news-card {{
    border-radius: 12px;
    background: {lt_entry_bg};
    border: 1px solid {lt_entry_bdr};
    text-decoration: none;
    overflow: hidden;
    display: block;
    opacity: 0;
    transform: translateX(-16px);
    animation: slideIn 0.45s ease forwards;
    transition: background 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}}
.news-card:hover {{
    background: {lt_hover_bg};
    transform: translateX(4px);
    box-shadow: 0 6px 24px rgba(0,0,0,0.22), -3px 0 0 #e74c1e;
}}
@keyframes slideIn {{
    to {{ opacity: 1; transform: translateX(0); }}
}}
.news-card-inner {{
    display: flex;
    align-items: stretch;
}}
.news-bar {{
    width: 3px;
    background: linear-gradient(180deg, #e74c1e, #d35400);
}}
.news-body {{
    flex: 1;
    padding: 11px 10px 11px 13px;
}}
.news-meta {{
    display: flex;
    gap: 5px;
    margin-bottom: 5px;
}}
.news-source {{
    font-size: 10px;
    font-weight: 700;
    color: #e67e22;
    text-transform: uppercase;
}}
.news-dot,
.news-date {{
    font-size: 10px;
    color: {lt_meta_c};
}}
.news-title {{
    font-size: 12.5px;
    font-weight: 600;
    color: {lt_title_c};
    line-height: 1.45;
}}
.news-cta {{
    font-size: 10.5px;
    font-weight: 600;
    color: rgba(230,126,34,0.7);
    margin-top: 5px;
}}
.news-badge {{
    font-size: 18px;
    padding: 10px 12px 10px 0;
    display: flex;
    align-items: center;
    opacity: 0.45;
}}
.no-news {{
    text-align: center;
    padding: 20px;
    font-size: 12.5px;
    color: {lt_meta_c};
}}
</style>
</head>
<body>
    <div class="sec-title">⚖️ Litigation &amp; Court Records</div>
    <div class="quick-row">{quick_btns_html}</div>
    <div class="divider"></div>
    <div class="news-feed">{lit_cards_html if lit_cards_html else lt_empty}</div>
</body>
</html>"""

        components_lit.html(lit_html, height=lt_h, scrolling=True)

    with r_col:
        import streamlit.components.v1 as components_news

        news_items = []
        for n in news:
            link_tag = n.find("link")
            title_tag = n.find("title")
            source_tag = n.find("source")
            pub_tag = n.find("pubDate")

            if link_tag and title_tag:
                news_items.append({
                    "href": link_tag.get_text(strip=True),
                    "title": title_tag.get_text(strip=True).replace('"', "&quot;"),
                    "source": source_tag.get_text(strip=True) if source_tag else "News",
                    "date": pub_tag.get_text(strip=True)[:16] if pub_tag else ""
                })

        news_cards_html = ""
        for i, item in enumerate(news_items):
            news_cards_html += f"""
            <a href="{item['href']}" target="_blank" class="news-card" style="animation-delay:{i * 0.07}s">
                <div class="news-card-inner">
                    <div class="news-bar"></div>
                    <div class="news-body">
                        <div class="news-meta">
                            <span class="news-source">{item['source']}</span>
                            <span class="news-dot">·</span>
                            <span class="news-date">{item['date']}</span>
                        </div>
                        <div class="news-title">{item['title']}</div>
                        <div class="news-cta">Read article →</div>
                    </div>
                    <div class="news-badge">📰</div>
                </div>
            </a>"""

        empty_html = "<div class='no-news'>No recent news found for this search.</div>" if not news_cards_html else ""

        nw_bg_card = "rgba(255,255,255,0.05)" if dark_mode else "rgba(255,255,255,0.88)"
        nw_card_bdr = "rgba(255,255,255,0.10)" if dark_mode else "rgba(0,0,0,0.10)"
        nw_entry_bg = "rgba(255,255,255,0.04)" if dark_mode else "#ffffff"
        nw_entry_bdr = "rgba(255,255,255,0.08)" if dark_mode else "rgba(0,0,0,0.08)"
        nw_title_c = "#f0f0f0" if dark_mode else "#111111"
        nw_meta_c = "#6b7a8d" if dark_mode else "#888888"
        iframe_h = min(80 + max(len(news_items), 1) * 105, 700)

        news_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: Inter, sans-serif;
    background: {nw_bg_card};
    border: 1px solid {nw_card_bdr};
    border-radius: 20px;
    padding: 22px;
}}
.sec-title {{
    font-size: 18px;
    font-weight: 800;
    color: #30b2c9;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.live-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #00dfd8;
    animation: blink 1.4s ease-in-out infinite;
}}
@keyframes blink {{
    50% {{ opacity: 0.3; transform: scale(0.7); }}
}}
.news-feed {{
    display: flex;
    flex-direction: column;
    gap: 9px;
}}
.news-card {{
    border-radius: 12px;
    background: {nw_entry_bg};
    border: 1px solid {nw_entry_bdr};
    text-decoration: none;
    overflow: hidden;
    display: block;
    opacity: 0;
    transform: translateX(-16px);
    animation: slideIn 0.45s ease forwards;
}}
@keyframes slideIn {{
    to {{ opacity: 1; transform: translateX(0); }}
}}
.news-card-inner {{
    display: flex;
    align-items: stretch;
}}
.news-bar {{
    width: 3px;
    background: linear-gradient(180deg, #00dfd8, #30b2c9);
}}
.news-body {{
    flex: 1;
    padding: 11px 10px 11px 13px;
}}
.news-meta {{
    display: flex;
    gap: 5px;
    margin-bottom: 5px;
}}
.news-source {{
    font-size: 10px;
    font-weight: 700;
    color: #00dfd8;
    text-transform: uppercase;
}}
.news-dot,
.news-date {{
    font-size: 10px;
    color: {nw_meta_c};
}}
.news-title {{
    font-size: 12.5px;
    font-weight: 600;
    color: {nw_title_c};
    line-height: 1.45;
}}
.news-cta {{
    font-size: 10.5px;
    font-weight: 600;
    color: rgba(0,223,216,0.7);
    margin-top: 5px;
}}
.news-badge {{
    font-size: 18px;
    padding: 10px 12px 10px 0;
    display: flex;
    align-items: center;
    opacity: 0.45;
}}
.no-news {{
    text-align: center;
    padding: 30px;
    font-size: 13px;
    color: {nw_meta_c};
}}
</style>
</head>
<body>
    <div class="sec-title"><span class="live-dot"></span>Media Coverage</div>
    <div class="news-feed">{news_cards_html if news_cards_html else empty_html}</div>
</body>
</html>"""

        components_news.html(news_html, height=iframe_h, scrolling=True)

        # ── Digital Footprint — Premium Animated iframe ───────────────────────
        import streamlit.components.v1 as components

        df_bg_card = "rgba(255,255,255,0.05)" if dark_mode else "rgba(255,255,255,0.88)"
        df_card_bdr = "rgba(255,255,255,0.10)" if dark_mode else "rgba(0,0,0,0.10)"
        df_title = "#30b2c9"

        footprint_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'Inter', -apple-system, sans-serif;
    background: {df_bg_card};
    border: 1px solid {df_card_bdr};
    border-radius: 20px;
    padding: 20px;
    overflow: visible;
  }}

  .sec-title {{
    font-size: 20px;
    font-weight: 800;
    color: {df_title};
    margin-bottom: 20px;
    letter-spacing: -0.3px;
    display: flex;
    align-items: center;
    gap: 10px;
  }}

  .sec-title::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, rgba(0,223,216,0.3), transparent);
  }}

  .fp-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
  }}

  .fp-card {{
    position: relative;
    border-radius: 14px;
    padding: 12px 10px 10px;
    text-decoration: none;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    overflow: hidden;
    cursor: pointer;
    border: 1px solid transparent;
    transition: transform 0.22s cubic-bezier(.34,1.56,.64,1),
                box-shadow 0.22s ease,
                border-color 0.22s ease;
    animation: cardIn 0.5s cubic-bezier(.34,1.2,.64,1) both;
  }}

  .fp-card:nth-child(1) {{ animation-delay: 0.05s; }}
  .fp-card:nth-child(2) {{ animation-delay: 0.10s; }}
  .fp-card:nth-child(3) {{ animation-delay: 0.15s; }}
  .fp-card:nth-child(4) {{ animation-delay: 0.20s; }}
  .fp-card:nth-child(5) {{ animation-delay: 0.25s; }}
  .fp-card:nth-child(6) {{ animation-delay: 0.30s; }}

  @keyframes cardIn {{
    from {{ opacity: 0; transform: translateY(18px) scale(0.93); }}
    to   {{ opacity: 1; transform: translateY(0) scale(1); }}
  }}

  .fp-card::after {{
    content: '';
    position: absolute;
    inset: -1px;
    border-radius: 15px;
    opacity: 0;
    background: radial-gradient(ellipse at 50% 0%, var(--accent), transparent 65%);
    transition: opacity 0.3s ease;
    pointer-events: none;
  }}

  .fp-card:hover::after {{ opacity: 0.45; }}

  .fp-card:hover {{
    transform: translateY(-5px) scale(1.03);
    box-shadow: 0 14px 36px rgba(0,0,0,0.35), 0 0 0 1px var(--accent);
    border-color: var(--accent) !important;
  }}

  .fp-icon-wrap {{
    width: 38px;
    height: 38px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    z-index: 1;
    transition: transform 0.22s cubic-bezier(.34,1.56,.64,1);
  }}

  .fp-card:hover .fp-icon-wrap {{
    transform: scale(1.15) rotate(-4deg);
  }}

  .fp-icon-wrap::after {{
    content: '';
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    border: 1.5px solid var(--accent);
    opacity: 0;
    transform: scale(0.85);
    transition: opacity 0.25s, transform 0.25s;
  }}

  .fp-card:hover .fp-icon-wrap::after {{
    opacity: 0.6;
    transform: scale(1);
    animation: ring-pulse 1.2s ease-in-out infinite;
  }}

  @keyframes ring-pulse {{
    0%, 100% {{ opacity: 0.6; transform: scale(1); }}
    50% {{ opacity: 0.2; transform: scale(1.15); }}
  }}

  .fp-icon {{
    font-size: 17px;
    line-height: 1;
  }}

  .fp-name {{
    font-size: 11px;
    font-weight: 700;
    color: rgba(255,255,255,0.92);
    text-align: center;
    letter-spacing: 0.2px;
    position: relative;
    z-index: 1;
  }}

  .fp-label {{
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.45);
    position: relative;
    z-index: 1;
  }}

  .fp-arrow {{
    position: absolute;
    top: 10px;
    right: 10px;
    font-size: 10px;
    color: rgba(255,255,255,0.3);
    transition: color 0.2s, transform 0.2s;
  }}

  .fp-card:hover .fp-arrow {{
    color: rgba(255,255,255,0.85);
    transform: translate(2px, -2px);
  }}

  .fp-linkedin {{ background: linear-gradient(135deg,#003f6b,#0a66c2); --accent:#0a66c2; }}
  .fp-twitter {{ background: linear-gradient(135deg,#111,#1c1c1c); --accent:#e7e7e7; }}
  .fp-instagram {{ background: linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045); --accent:#fd1d1d; }}
  .fp-facebook {{ background: linear-gradient(135deg,#0a3e8f,#1877f2); --accent:#1877f2; }}
  .fp-reddit {{ background: linear-gradient(135deg,#a33200,#ff4500); --accent:#ff4500; }}
  .fp-youtube {{ background: linear-gradient(135deg,#8b0000,#ff0000); --accent:#ff0000; }}
</style>
</head>
<body>
  <div class="sec-title">🌐 Digital Footprint</div>

  <div class="fp-grid">
    <a href="{ln_search_url}" target="_blank" class="fp-card fp-linkedin">
      <span class="fp-arrow">↗</span>
      <div class="fp-icon-wrap" style="background:rgba(255,255,255,0.12);">
        <span class="fp-icon">💼</span>
      </div>
      <span class="fp-name">LinkedIn</span>
      <span class="fp-label">Professional</span>
    </a>

    <a href="https://www.google.com/search?q=site:x.com+{q_encoded}" target="_blank" class="fp-card fp-twitter">
      <span class="fp-arrow">↗</span>
      <div class="fp-icon-wrap" style="background:rgba(255,255,255,0.10);">
        <span class="fp-icon">𝕏</span>
      </div>
      <span class="fp-name">Twitter / X</span>
      <span class="fp-label">Microblog</span>
    </a>

    <a href="https://www.google.com/search?q=site:instagram.com+{q_encoded}" target="_blank" class="fp-card fp-instagram">
      <span class="fp-arrow">↗</span>
      <div class="fp-icon-wrap" style="background:rgba(255,255,255,0.12);">
        <span class="fp-icon">📸</span>
      </div>
      <span class="fp-name">Instagram</span>
      <span class="fp-label">Visual Media</span>
    </a>

    <a href="https://www.google.com/search?q=site:facebook.com+{q_encoded}" target="_blank" class="fp-card fp-facebook">
      <span class="fp-arrow">↗</span>
      <div class="fp-icon-wrap" style="background:rgba(255,255,255,0.12);">
        <span class="fp-icon">👥</span>
      </div>
      <span class="fp-name">Facebook</span>
      <span class="fp-label">Social Network</span>
    </a>

    <a href="https://www.google.com/search?q=site:reddit.com+{q_encoded}" target="_blank" class="fp-card fp-reddit">
      <span class="fp-arrow">↗</span>
      <div class="fp-icon-wrap" style="background:rgba(255,255,255,0.12);">
        <span class="fp-icon">🤖</span>
      </div>
      <span class="fp-name">Reddit</span>
      <span class="fp-label">Community</span>
    </a>

    <a href="https://www.google.com/search?q=site:youtube.com+{q_encoded}" target="_blank" class="fp-card fp-youtube">
      <span class="fp-arrow">↗</span>
      <div class="fp-icon-wrap" style="background:rgba(255,255,255,0.12);">
        <span class="fp-icon">▶️</span>
      </div>
      <span class="fp-name">YouTube</span>
      <span class="fp-label">Video</span>
    </a>
  </div>
</body>
</html>"""

        components.html(footprint_html, height=290, scrolling=False)

    # ── Compliance Section — rendered via st.components.v1.html() ─────────────
    import streamlit.components.v1 as components

    bg_card = "rgba(255,255,255,0.05)" if dark_mode else "rgba(255,255,255,0.85)"
    db_entry_bg = "rgba(255,255,255,0.06)" if dark_mode else "#ffffff"
    db_entry_bdr = "rgba(255,255,255,0.09)" if dark_mode else "rgba(0,0,0,0.09)"
    db_name_col = "#f0f0f0" if dark_mode else "#111111"
    db_desc_col = "#8a97a6" if dark_mode else "#666666"
    tab_idle_bg = "rgba(255,255,255,0.05)" if dark_mode else "rgba(0,0,0,0.05)"
    tab_idle_col = "#7a8a99" if dark_mode else "#666666"
    tab_bdr = "rgba(255,255,255,0.09)" if dark_mode else "rgba(0,0,0,0.09)"
    bar_bdr = "rgba(255,255,255,0.13)" if dark_mode else "rgba(0,0,0,0.13)"
    title_col = "#30b2c9"
    card_bdr = "rgba(255,255,255,0.10)" if dark_mode else "rgba(0,0,0,0.10)"

    def db_card(icon, icon_bg, name, desc, badge, badge_color, url):
        return f"""
        <a href="{url}" target="_blank" class="db-entry">
          <div class="db-hdr">
            <div class="db-icon" style="background:{icon_bg}">{icon}</div>
            <span class="db-name">{name}</span>
          </div>
          <p class="db-desc">{desc}</p>
          <div class="db-foot">
            <span class="db-badge" style="background:{badge_color}">{badge}</span>
            <span class="db-cta">Search →</span>
          </div>
        </a>"""

    t1 = (
        db_card("🇺🇸", "rgba(13,71,161,0.3)", "OFAC SDN List",
                "U.S. Treasury sanctions — Specially Designated Nationals & blocked persons.",
                "USA · Treasury", "#0d47a1", "https://sanctionssearch.ofac.treas.gov/") +
        db_card("🌐", "rgba(243,156,18,0.3)", "OpenSanctions",
                "Aggregated global sanctions, PEPs and watchlists from 200+ sources worldwide.",
                "Global · Open Data", "#c87f0a", f"https://www.opensanctions.org/search/?q={q_encoded}") +
        db_card("🔍", "rgba(22,160,133,0.3)", "Dilisense",
                "Real-time AML/KYC screening across sanctions, PEPs and adverse-media databases.",
                "Global · AML/KYC", "#16a085", f"https://dilisense.com/en/search/{q_raw}") +
        db_card("⚖️", "rgba(127,140,141,0.3)", "FCPA Enforcement",
                "SEC Foreign Corrupt Practices Act enforcement actions and case database.",
                "USA · SEC", "#5d6d7e", "https://www.sec.gov/enforce/sec-enforcement-actions-fcpa-cases") +
        db_card("🇪🇺", "rgba(41,128,185,0.3)", "EU Sanctions Map",
                "Official European Union consolidated list of persons & entities under sanctions.",
                "EU · EEAS", "#1a6fa0", "https://www.sanctionsmap.eu/") +
        db_card("🌏", "rgba(192,57,43,0.3)", "UN Sanctions",
                "United Nations Security Council consolidated sanctions list.",
                "Global · UN", "#c0392b", "https://www.un.org/securitycouncil/content/un-sc-consolidated-list")
    )

    t2 = (
        db_card("📈", "rgba(41,128,185,0.3)", "SEBI Orders",
                "Securities & Exchange Board of India enforcement orders, adjudication & appeal rulings.",
                "India · SEBI", "#2471a3",
                "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=2&ssid=9&smid=77") +
        db_card("🏚️", "rgba(142,68,173,0.3)", "IBBI Insolvency",
                "Insolvency & Bankruptcy Board of India — orders on corporate insolvency proceedings.",
                "India · IBBI", "#7d3c98", "https://ibbi.gov.in/orders/ibbi") +
        db_card("🕵️", "rgba(192,57,43,0.3)", "SFIO Prosecution",
                "Serious Fraud Investigation Office — prosecution complaints & fraud case records.",
                "India · MCA", "#a93226", "https://sfio.gov.in/en/document-category/prosecution/") +
        db_card("⚠️", "rgba(211,84,0,0.3)", "Watchout Investors",
                "Alerts on defaulting promoters, fraudulent companies & investor complaints in India.",
                "India · Investors", "#ba4a00", "https://www.watchoutinvestors.com/") +
        db_card("🏦", "rgba(39,174,96,0.3)", "RBI Defaulters",
                "Reserve Bank of India — wilful defaulters list and credit information disclosures.",
                "India · RBI", "#1e8449", "https://www.rbi.org.in/Scripts/bs_viewcontent.aspx?Id=2009") +
        db_card("📋", "rgba(20,143,119,0.3)", "NCLT Orders",
                "National Company Law Tribunal orders on corporate disputes, mergers & winding up.",
                "India · NCLT", "#148f77", "https://nclt.gov.in/en/content/orders")
    )

    t3 = (
        db_card("💳", "rgba(44,62,80,0.3)", "CIBIL Defaulters",
                "Credit bureau suit-filed accounts and wilful defaulter records in India.",
                "India · Credit", "#2c3e50", "https://suit.cibil.com/") +
        db_card("📄", "rgba(44,62,80,0.3)", "SEC EDGAR",
                "Full-text search of SEC filings — 10-K, 8-K, proxy statements and enforcement disclosures.",
                "USA · SEC", "#1a252f",
                f"https://efts.sec.gov/LATEST/search-index?q={q_encoded}&dateRange=custom&startdt=2000-01-01") +
        db_card("🏛️", "rgba(52,73,94,0.3)", "FINRA BrokerCheck",
                "FINRA broker and firm registration, licensing history and disciplinary records.",
                "USA · FINRA", "#34495e", f"https://www.finra.org/search?search={q_raw}") +
        db_card("🏢", "rgba(0,58,155,0.3)", "MCA 21 Portal",
                "Ministry of Corporate Affairs — company master data, charges, directors & filings.",
                "India · MCA", "#003a9b", "https://www.mca.gov.in/") +
        db_card("📊", "rgba(0,119,181,0.3)", "Bloomberg FIGI",
                "Open global financial instrument identifier and entity lookup database.",
                "Global · Finance", "#0077b5", f"https://www.openfigi.com/search#!?query={q_raw}") +
        db_card("🔎", "rgba(39,174,96,0.3)", "OpenCorporates",
                "World's largest open database of companies — 200M+ entities across jurisdictions.",
                "Global · Corporate", "#1d8348", f"https://opencorporates.com/companies?q={q_raw}")
    )

    t4 = (
        db_card("🧾", "rgba(39,174,96,0.3)", "GST Portal",
                "Goods & Services Tax Network — GSTIN verification and taxpayer search.",
                "India · GST", "#1e8449", "https://services.gst.gov.in/services/searchtp") +
        db_card("👷", "rgba(26,188,156,0.3)", "EPFO Establishment",
                "Employees' Provident Fund Organisation — employer establishment search & compliance.",
                "India · EPFO", "#148f77",
                "https://unifiedportal-emp.epfindia.gov.in/publicPortal/no-auth/misReport/home/loadEstSearchHome") +
        db_card("🏭", "rgba(41,128,185,0.3)", "ESIC Portal",
                "Employees' State Insurance Corporation — employer registration and compliance search.",
                "India · ESIC", "#1a5276", "https://www.esic.in/EmployerPortal/ESICEmployerSearch.aspx") +
        db_card("📑", "rgba(142,68,173,0.3)", "Income Tax PAN",
                "Income Tax Department — PAN verification and TAN/TDS compliance check.",
                "India · IT Dept", "#6c3483",
                "https://www.incometax.gov.in/iec/foportal/help/know-your-pan") +
        db_card("🏗️", "rgba(211,84,0,0.3)", "Labour Compliance",
                "Shram Suvidha portal — factory & contractor registration, labour law compliance.",
                "India · Labour", "#a04000", "https://shramsuvidha.gov.in/") +
        db_card("📦", "rgba(52,73,94,0.3)", "IEC / DGFT",
                "Directorate General of Foreign Trade — Importer Exporter Code lookup.",
                "India · DGFT", "#2e4057", "https://www.dgft.gov.in/CP/?opt=iecieTrck")
    )

    compliance_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: {bg_card};
    border: 1px solid {card_bdr};
    border-radius: 20px;
    padding: 28px;
    color: {db_name_col};
  }}

  .sec-title {{
    font-size: 22px;
    font-weight: 700;
    color: {title_col};
    margin-bottom: 20px;
  }}

  .tab-bar {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    border-bottom: 2px solid {bar_bdr};
    margin-bottom: 24px;
  }}

  .tab-btn {{
    padding: 10px 16px;
    border-radius: 10px 10px 0 0;
    border: 1px solid {tab_bdr};
    border-bottom: none;
    background: {tab_idle_bg};
    color: {tab_idle_col};
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    position: relative;
    bottom: -2px;
    transition: background .18s, color .18s, border-color .18s;
    outline: none;
  }}

  .tab-btn:hover {{ background: rgba(0,223,216,0.09); color: #00dfd8; }}

  .tab-btn.active {{
    background: rgba(0,223,216,0.14);
    color: #00dfd8;
    border-color: rgba(0,223,216,0.38);
  }}

  .panel {{ display: none; }}
  .panel.active {{ display: block; }}

  .db-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
  }}

  .db-entry {{
    background: {db_entry_bg};
    border: 1px solid {db_entry_bdr};
    border-radius: 14px;
    padding: 18px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    text-decoration: none;
    transition: transform .18s, box-shadow .18s, border-color .18s;
  }}

  .db-entry:hover {{
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(0,0,0,0.28);
    border-color: rgba(0,223,216,0.45);
  }}

  .db-hdr {{ display: flex; align-items: center; gap: 12px; }}

  .db-icon {{
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 19px;
    flex-shrink: 0;
  }}

  .db-name {{
    font-size: 14px;
    font-weight: 700;
    color: {db_name_col};
    line-height: 1.25;
  }}

  .db-desc {{
    font-size: 11.5px;
    color: {db_desc_col};
    line-height: 1.55;
    flex: 1;
  }}

  .db-foot {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 2px;
  }}

  .db-badge {{
    font-size: 9.5px;
    font-weight: 700;
    letter-spacing: .06em;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 20px;
    color: #fff;
  }}

  .db-cta {{
    font-size: 12px;
    font-weight: 700;
    color: #00dfd8;
    opacity: .85;
  }}

  .db-entry:hover .db-cta {{ opacity: 1; }}
</style>
</head>
<body>
  <div class="sec-title">Compliance &amp; Database</div>

  <div class="tab-bar">
    <button class="tab-btn active" data-panel="p1">🌍 Global Sanctions</button>
    <button class="tab-btn" data-panel="p2">⚖️ Indian Regulatory</button>
    <button class="tab-btn" data-panel="p3">🏢 Corporate &amp; Financial</button>
    <button class="tab-btn" data-panel="p4">🛠️ Statutory &amp; Tax</button>
  </div>

  <div id="p1" class="panel active"><div class="db-grid">{t1}</div></div>
  <div id="p2" class="panel"><div class="db-grid">{t2}</div></div>
  <div id="p3" class="panel"><div class="db-grid">{t3}</div></div>
  <div id="p4" class="panel"><div class="db-grid">{t4}</div></div>

  <script>
    document.querySelectorAll('.tab-btn').forEach(function(btn) {{
      btn.addEventListener('click', function() {{
        document.querySelectorAll('.tab-btn').forEach(function(b) {{ b.classList.remove('active'); }});
        document.querySelectorAll('.panel').forEach(function(p) {{ p.classList.remove('active'); }});
        btn.classList.add('active');
        document.getElementById(btn.dataset.panel).classList.add('active');
        window.parent.postMessage({{ type: 'streamlit:setFrameHeight', height: document.body.scrollHeight + 20 }}, '*');
      }});
    }});

    window.addEventListener('load', function() {{
      window.parent.postMessage({{ type: 'streamlit:setFrameHeight', height: document.body.scrollHeight + 20 }}, '*');
    }});
  </script>
</body>
</html>"""

    components.html(compliance_html, height=620, scrolling=False)


# ── Footer ────────────────────────────────────────────────────────────────────
footer_text = "#555" if not dark_mode else "rgba(255,255,255,0.25)"
footer_hover = "#00dfd8"

st.markdown(f"""
<style>
.footer {{
    text-align: center;
    padding: 28px 0 18px;
    animation: footerFade 1s ease 0.5s both;
}}

.footer-text {{
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.08em;
    color: {footer_text};
    display: inline-flex;
    align-items: center;
    gap: 7px;
    transition: color 0.3s;
}}

.footer-text:hover {{ color: {footer_hover}; }}

.footer-dot {{
    display: inline-block;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #00dfd8;
    animation: dotPulse 2s ease-in-out infinite;
    flex-shrink: 0;
}}

.footer-name {{
    font-weight: 700;
    background: linear-gradient(90deg, #30b2c9, #00dfd8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.05em;
}}

@keyframes dotPulse {{
    0%,100% {{ opacity: 0.3; transform: scale(0.8); }}
    50% {{ opacity: 1; transform: scale(1.3); }}
}}

@keyframes footerFade {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
</style>

<div class="footer">
    <span class="footer-text">
        <span class="footer-dot"></span>
        Built by &nbsp;<span class="footer-name">Shubh Kumar</span>
    </span>
</div>
""", unsafe_allow_html=True)


