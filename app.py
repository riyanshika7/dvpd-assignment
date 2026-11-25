from pathlib import Path
import re
import random
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="PlayPulse | App Store Analytics",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
APPS_FILE = BASE_DIR / "googleplaystore.csv"
REVIEWS_FILE = BASE_DIR / "googleplaystore_user_reviews.csv"

PALETTE = {
    "cyan": "#55E6D2",
    "blue": "#7AA7FF",
    "purple": "#B69CFF",
    "pink": "#FF8DB7",
    "yellow": "#FFD477",
    "green": "#80E0A7",
    "red": "#FF8C8C",
    "muted": "#9AAAC0",
    "ink": "#EAF1FF",
    "panel": "#151F32",
    "bg": "#0B1220",
}

CHART_TEMPLATE = "plotly_dark"

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
      :root { --pp-bg:#0B1220; --pp-panel:#151F32; --pp-text:#EAF1FF; --pp-muted:#9AAAC0; --pp-cyan:#55E6D2; }
      html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
      .stApp { background: radial-gradient(circle at 12% 0%, rgba(85,230,210,.10), transparent 27%), radial-gradient(circle at 92% 4%, rgba(182,156,255,.12), transparent 26%), #0B1220; color:var(--pp-text); }
      [data-testid="stHeader"] { background: rgba(11,18,32,.72); }
      [data-testid="stSidebar"] { background: linear-gradient(180deg,#111B2D 0%,#0D1728 100%); border-right:1px solid rgba(154,170,192,.13); }
      [data-testid="stSidebar"] > div { padding-top: 1.2rem; }
      .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1500px; }
      h1,h2,h3 { font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.035em; }
      h1 { color:#F4F7FF; }
      h2,h3 { color:#EAF1FF; }
      p, label, .stCaption { color:#B7C4D8; }
      [data-testid="stMetric"] { background:transparent; }
      [data-testid="stMetricValue"] { color:#F4F7FF; }
      [data-testid="stMetricLabel"] { color:#9AAAC0; }
      div[data-testid="stVerticalBlockBorderWrapper"] { border-color:rgba(154,170,192,.16) !important; }
      .pp-hero { position:relative; overflow:hidden; padding:27px 30px; border-radius:22px; border:1px solid rgba(155,180,220,.20); background:linear-gradient(112deg,rgba(23,43,65,.96),rgba(28,31,65,.92) 58%,rgba(49,34,76,.86)); box-shadow:0 18px 55px rgba(0,0,0,.22); margin-bottom:20px; }
      .pp-hero:after { content:''; }
      .pp-eyebrow { display:inline-block; padding:5px 10px; border-radius:999px; background:rgba(85,230,210,.12); color:#82F3E4; font-size:11px; font-weight:800; letter-spacing:.13em; text-transform:uppercase; }
      .pp-title { font-family:'Space Grotesk',sans-serif; font-size:clamp(30px,4vw,43px); line-height:1.08; font-weight:700; color:#F4F7FF; margin:12px 0 8px; letter-spacing:-.055em; }
      .pp-subtitle { max-width:700px; color:#B7C7DC; font-size:14px; line-height:1.65; margin:0; }
      .pp-hero-side { position:absolute; right:30px; bottom:23px; z-index:1; color:rgba(234,241,255,.78); font-size:12px; text-align:right; }
      .pp-card { border:1px solid rgba(154,170,192,.16); background:linear-gradient(145deg,rgba(24,36,56,.96),rgba(17,27,44,.92)); border-radius:17px; padding:17px 18px; min-height:116px; box-shadow:0 10px 30px rgba(0,0,0,.13); }
      .pp-card-label { font-size:11px; color:#9AAAC0; text-transform:uppercase; letter-spacing:.10em; font-weight:800; }
      .pp-card-value { font-family:'Space Grotesk',sans-serif; font-size:28px; font-weight:700; color:#F4F7FF; margin-top:9px; line-height:1.1; }
      .pp-card-note { font-size:11px; color:#8FA2BC; margin-top:7px; }
      .pp-section-kicker { color:#55E6D2; text-transform:uppercase; letter-spacing:.13em; font-size:10px; font-weight:800; margin-bottom:5px; }
      .pp-section-title { font-family:'Space Grotesk',sans-serif; font-size:21px; color:#F1F5FF; font-weight:700; letter-spacing:-.03em; margin:0 0 5px; }
      .pp-section-note { color:#91A2BA; font-size:12px; margin-bottom:12px; }
      .pp-tag { display:inline-block; padding:4px 9px; border-radius:8px; background:rgba(182,156,255,.13); color:#D3C5FF; font-size:11px; font-weight:700; margin-right:5px; }
      .pp-insight { padding:13px 15px; border-radius:13px; border-left:3px solid #55E6D2; background:rgba(85,230,210,.075); color:#C6D8E8; font-size:13px; line-height:1.55; }
      .pp-mini { color:#8FA2BC; font-size:11px; }
      .stButton > button { border-radius:11px; border:1px solid rgba(85,230,210,.42); background:linear-gradient(100deg,rgba(85,230,210,.16),rgba(182,156,255,.16)); color:#EAF1FF; font-weight:700; transition:all .2s ease; }
      .stButton > button:hover { border-color:#55E6D2; color:#FFFFFF; box-shadow:0 0 0 3px rgba(85,230,210,.08); transform:translateY(-1px); }
      .stTextInput input, .stNumberInput input { border-radius:10px !important; }
      [data-baseweb="select"] > div { border-radius:10px !important; }
      .stTabs [data-baseweb="tab-list"] { gap:7px; border-bottom:1px solid rgba(154,170,192,.15); }
      .stTabs [data-baseweb="tab"] { border-radius:10px 10px 0 0; padding:10px 15px; color:#AAB9CE; }
      .stTabs [aria-selected="true"] { color:#73F0DF !important; background:rgba(85,230,210,.08); }
      [data-testid="stDataFrame"] { border:1px solid rgba(154,170,192,.14); border-radius:12px; overflow:hidden; }
      hr { border-color:rgba(154,170,192,.14); }
      footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Preparing app data...")
def load_apps(path_string: str) -> tuple[pd.DataFrame, dict]:
    path = Path(path_string)
    raw = pd.read_csv(path, low_memory=False, on_bad_lines="skip")
    raw.columns = [str(c).strip() for c in raw.columns]
    original_rows = len(raw)

    required = {"App", "Category"}
    missing = required - set(raw.columns)
    if missing:
        raise ValueError(f"The apps CSV is missing required columns: {', '.join(sorted(missing))}")

    df = raw.copy()
    df["App"] = df["App"].astype("string").str.strip()
    df["Category"] = df["Category"].astype("string").str.strip().str.upper()
    # The source file contains one malformed row whose category is often '1.9'.
    df = df[df["Category"].str.match(r"^[A-Z][A-Z_]+$", na=False)]
    df = df[df["App"].notna() & (df["App"].str.len() > 0)]

    if "Rating" in df:
        df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
        df.loc[~df["Rating"].between(0, 5), "Rating"] = np.nan
    else:
        df["Rating"] = np.nan

    if "Reviews" in df:
        df["Reviews"] = pd.to_numeric(df["Reviews"].astype(str).str.replace(",", "", regex=False), errors="coerce").fillna(0)
    else:
        df["Reviews"] = 0

    if "Installs" in df:
        installs = df["Installs"].astype(str).str.replace(r"[+,]", "", regex=True).str.strip()
        df["Installs"] = pd.to_numeric(installs, errors="coerce").fillna(0)
    else:
        df["Installs"] = 0

    if "Price" in df:
        df["Price"] = pd.to_numeric(df["Price"].astype(str).str.replace(r"[$,]", "", regex=True), errors="coerce").fillna(0)
    else:
        df["Price"] = 0.0

    if "Type" in df:
        df["Type"] = df["Type"].astype("string").str.strip().str.title()
        df.loc[~df["Type"].isin(["Free", "Paid"]), "Type"] = "Unknown"
    else:
        df["Type"] = np.where(df["Price"] > 0, "Paid", "Free")

    if "Content Rating" not in df:
        df["Content Rating"] = "Not specified"
    df["Content Rating"] = df["Content Rating"].fillna("Not specified").astype(str).str.strip()

    if "Genres" not in df:
        df["Genres"] = "Not specified"
    df["Genres"] = df["Genres"].fillna("Not specified").astype(str).str.strip()

    if "Last Updated" in df:
        df["Last Updated"] = pd.to_datetime(df["Last Updated"], errors="coerce")
    else:
        df["Last Updated"] = pd.NaT

    df["Installs (M)"] = df["Installs"] / 1_000_000
    df["Reviews (K)"] = df["Reviews"] / 1_000
    df["Price Label"] = np.where(df["Price"] > 0, "Paid", "Free")
    df = df.drop_duplicates(subset=["App"], keep="first").reset_index(drop=True)

    audit = {
        "source_rows": original_rows,
        "clean_rows": len(df),
        "removed_rows": max(original_rows - len(df), 0),
        "missing_ratings": int(df["Rating"].isna().sum()),
        "categories": int(df["Category"].nunique()),
    }
    return df, audit


@st.cache_data(show_spinner="Reading review sentiment...")
def load_reviews(path_string: str) -> pd.DataFrame:
    reviews = pd.read_csv(path_string, low_memory=False, on_bad_lines="skip")
    reviews.columns = [str(c).strip() for c in reviews.columns]
    if "App" not in reviews.columns or "Sentiment" not in reviews.columns:
        return pd.DataFrame()
    reviews["App"] = reviews["App"].astype("string").str.strip()
    reviews["Sentiment"] = reviews["Sentiment"].astype("string").str.strip().str.title()
    reviews = reviews[reviews["Sentiment"].isin(["Positive", "Neutral", "Negative"])]
    summary = reviews.groupby(["App", "Sentiment"]).size().unstack(fill_value=0)
    summary.columns = [f"{c} Reviews" for c in summary.columns]
    summary = summary.reset_index()
    for col in ["Positive Reviews", "Neutral Reviews", "Negative Reviews"]:
        if col not in summary:
            summary[col] = 0
    if "Sentiment_Polarity" in reviews.columns:
        polarity = pd.to_numeric(reviews["Sentiment_Polarity"], errors="coerce").groupby(reviews["App"]).mean()
        summary = summary.merge(polarity.rename("Avg Sentiment Polarity"), on="App", how="left")
    return summary


def pretty_number(value) -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "—"
    if not np.isfinite(value):
        return "—"
    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"


def chart_layout(fig, height=340):
    fig.update_layout(
        template=CHART_TEMPLATE,
        height=height,
        margin=dict(l=12, r=12, t=45, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#C5D2E5", size=11),
        title_font=dict(family="Space Grotesk, sans-serif", size=15, color="#EEF3FF"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="#18263A", bordercolor="#55E6D2", font_color="#F4F7FF"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="rgba(154,170,192,.18)")
    fig.update_yaxes(gridcolor="rgba(154,170,192,.10)", zeroline=False, linecolor="rgba(154,170,192,.18)")
    return fig


def section_heading(kicker: str, title: str, note: str = ""):
    st.markdown(
        f'<div class="pp-section-kicker">{kicker}</div><div class="pp-section-title">{title}</div><div class="pp-section-note">{note}</div>',
        unsafe_allow_html=True,
    )


def kpi_card(col, label: str, value: str, note: str, icon: str):
    with col:
        st.markdown(
            f'<div class="pp-card"><div style="display:flex;justify-content:space-between;align-items:center"><div class="pp-card-label">{label}</div><div style="font-size:19px">{icon}</div></div><div class="pp-card-value">{value}</div><div class="pp-card-note">{note}</div></div>',
            unsafe_allow_html=True,
        )


def apply_plotly_style(fig, height=340):
    return chart_layout(fig, height)


# Load source data.
if not APPS_FILE.exists():
    st.error("I couldn't find `googleplaystore.csv` next to `app.py`.")
    st.info("Place `googleplaystore.csv` in the same folder as this file, then refresh the page.")
    st.stop()

try:
    apps, audit = load_apps(str(APPS_FILE))
except Exception as exc:
    st.error(f"Couldn't read the apps dataset: {exc}")
    st.stop()

reviews_summary = pd.DataFrame()
if REVIEWS_FILE.exists():
    try:
        reviews_summary = load_reviews(str(REVIEWS_FILE))
        if not reviews_summary.empty:
            apps = apps.merge(reviews_summary, on="App", how="left")
            for col in ["Positive Reviews", "Neutral Reviews", "Negative Reviews"]:
                apps[col] = apps[col].fillna(0).astype(int)
    except Exception as exc:
        st.sidebar.warning(f"Review sentiment file couldn't be loaded: {exc}")

# -----------------------------------------------------------------------------
# Sidebar: filters
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 📱 PlayPulse")
st.sidebar.caption("Your app-store analytics studio")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Explore the data")
search_text = st.sidebar.text_input("Find an app", placeholder="Try Spotify, Canva, WhatsApp…")

all_categories = sorted(apps["Category"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Categories",
    options=all_categories,
    default=[],
    placeholder="All categories",
    help="Leave empty to include every category.",
)

type_options = [x for x in ["Free", "Paid", "Unknown"] if x in apps["Type"].unique()]
selected_types = st.sidebar.multiselect("App type", options=type_options, default=[x for x in type_options if x != "Unknown"])

rating_range = st.sidebar.slider("Minimum app rating", 0.0, 5.0, (0.0, 5.0), 0.1)
install_labels = {
    "Any number": 0,
    "1K+ installs": 1_000,
    "10K+ installs": 10_000,
    "100K+ installs": 100_000,
    "1M+ installs": 1_000_000,
    "10M+ installs": 10_000_000,
    "100M+ installs": 100_000_000,
}
min_install_label = st.sidebar.selectbox("Install threshold", list(install_labels.keys()), index=0)
content_options = sorted(apps["Content Rating"].dropna().unique().tolist())
selected_content = st.sidebar.multiselect("Audience rating", options=content_options, default=[])

with st.sidebar.expander("⚙️ Display options", expanded=False):
    sort_choice = st.selectbox("Sort app list by", ["Most installs", "Highest rating", "Most reviews", "Lowest price", "Most expensive"])
    top_n = st.slider("Number of apps in rankings", 5, 25, 10)
    show_unknown_ratings = st.checkbox("Include apps without a rating", value=False)

filtered = apps.copy()
if selected_categories:
    filtered = filtered[filtered["Category"].isin(selected_categories)]
if selected_types:
    filtered = filtered[filtered["Type"].isin(selected_types)]
if selected_content:
    filtered = filtered[filtered["Content Rating"].isin(selected_content)]
if search_text.strip():
    filtered = filtered[filtered["App"].str.contains(re.escape(search_text.strip()), case=False, na=False)]
filtered = filtered[filtered["Installs"] >= install_labels[min_install_label]]
if show_unknown_ratings:
    filtered = filtered[filtered["Rating"].isna() | filtered["Rating"].between(*rating_range)]
else:
    filtered = filtered[filtered["Rating"].between(*rating_range)]

if sort_choice == "Most installs":
    filtered = filtered.sort_values("Installs", ascending=False)
elif sort_choice == "Highest rating":
    filtered = filtered.sort_values(["Rating", "Reviews"], ascending=[False, False])
elif sort_choice == "Most reviews":
    filtered = filtered.sort_values("Reviews", ascending=False)
elif sort_choice == "Lowest price":
    filtered = filtered.sort_values("Price", ascending=True)
else:
    filtered = filtered.sort_values("Price", ascending=False)

# Hero / brand area.
st.markdown(
    f"""
    <div class="pp-hero">
      <div class="pp-eyebrow">Data stories, made interactive</div>
      <div class="pp-title">PlayPulse<span style="color:#55E6D2">.</span></div>
      <p class="pp-subtitle">Explore the Google Play Store through ratings, installs, categories and user sentiment. Filter the catalogue, compare app patterns and uncover what makes an app stand out.</p>
      <div class="pp-hero-side">APP INTELLIGENCE<br><span style="color:#55E6D2;font-weight:800">DISCOVER · COMPARE · LEARN</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Friendly status line and quick surprise interaction.
status_left, status_right = st.columns([3, 1])
with status_left:
    st.markdown(
        f'<span class="pp-tag">{len(filtered):,} apps in view</span><span class="pp-tag">{filtered["Category"].nunique()} categories</span><span class="pp-tag">Historical dataset snapshot</span>',
        unsafe_allow_html=True,
    )
with status_right:
    if st.button("🎲 Surprise me with an app", width="stretch", disabled=filtered.empty):
        st.session_state["surprise_app"] = filtered.sample(1).iloc[0]["App"]

if st.session_state.get("surprise_app"):
    surprise = apps[apps["App"] == st.session_state["surprise_app"]]
    if not surprise.empty:
        item = surprise.iloc[0]
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            c1.markdown(f"**Your random discovery: {item['App']}**  \n{item['Category'].replace('_', ' ').title()} · {item['Type']} app")
            c2.metric("Rating", f"{item['Rating']:.1f} ⭐" if pd.notna(item["Rating"]) else "Not rated")
            c3.metric("Installs", pretty_number(item["Installs"]))
            c4.metric("Price", f"${item['Price']:.2f}" if item["Price"] > 0 else "Free")

if filtered.empty:
    st.warning("No apps match these filters. Try widening the rating range or clearing one of the filters.")
    st.stop()

# Summary metrics.
valid_ratings = filtered["Rating"].dropna()
avg_rating = valid_ratings.mean() if not valid_ratings.empty else np.nan
free_share = (filtered["Type"] == "Free").mean() * 100
avg_reviews = filtered["Reviews"].mean()
median_installs = filtered["Installs"].median()

k1, k2, k3, k4 = st.columns(4, gap="medium")
kpi_card(k1, "Apps matching filters", f"{len(filtered):,}", "Live count based on your filters", "🧩")
kpi_card(k2, "Average rating", f"{avg_rating:.2f} ⭐" if pd.notna(avg_rating) else "—", f"Across {len(valid_ratings):,} rated apps", "⭐")
kpi_card(k3, "Free apps", f"{free_share:.1f}%", "Share of apps in the current view", "🎁")
kpi_card(k4, "Median installs", pretty_number(median_installs), "Typical install count in this view", "📈")

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

# Main app sections.
tab_overview, tab_explorer, tab_category, tab_reviews, tab_quality = st.tabs(
    ["Overview", "🔎 App Explorer", "🗂️ Category Lab", "💬 Review Signals", "🧪 Data Quality"]
)

with tab_overview:
    section_heading("THE BIG PICTURE", "What's happening in the app universe?", "A quick visual scan of the apps that match your current filters.")
    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        cat_counts = filtered["Category"].value_counts().head(top_n).sort_values()
        fig = px.bar(
            x=cat_counts.values,
            y=[x.replace("_", " ").title() for x in cat_counts.index],
            orientation="h",
            text=cat_counts.values,
            title=f"Top {min(top_n, len(cat_counts))} categories by app count",
            color=cat_counts.values,
            color_continuous_scale=[[0, "#536A9F"], [0.55, "#7AA7FF"], [1, "#55E6D2"]],
        )
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(coloraxis_showscale=False, xaxis_title="Number of apps", yaxis_title="")
        st.plotly_chart(apply_plotly_style(fig, 390), width="stretch", config={"displayModeBar": False})
    with right:
        rated = filtered.dropna(subset=["Rating"])
        fig = px.histogram(
            rated,
            x="Rating",
            nbins=20,
            title="How are apps rated?",
            color_discrete_sequence=[PALETTE["purple"]],
            opacity=0.9,
        )
        fig.update_layout(xaxis_title="App rating (out of 5)", yaxis_title="Number of apps", bargap=0.08)
        st.plotly_chart(apply_plotly_style(fig, 390), width="stretch", config={"displayModeBar": False})

    left, right = st.columns(2, gap="large")
    with left:
        type_counts = filtered["Type"].value_counts().rename_axis("App type").reset_index(name="Apps")
        fig = px.pie(type_counts, names="App type", values="Apps", hole=0.68, title="Free vs paid mix", color="App type", color_discrete_map={"Free": PALETTE["cyan"], "Paid": PALETTE["purple"], "Unknown": PALETTE["yellow"]})
        fig.update_traces(textposition="outside", textinfo="percent+label", marker=dict(line=dict(color="#0B1220", width=3)))
        st.plotly_chart(apply_plotly_style(fig, 330), width="stretch", config={"displayModeBar": False})
    with right:
        scatter = filtered.dropna(subset=["Rating"]).copy()
        scatter = scatter[scatter["Installs"] > 0]
        if len(scatter) > 2500:
            scatter = scatter.sample(2500, random_state=42)
        fig = px.scatter(
            scatter,
            x="Installs",
            y="Rating",
            color="Type",
            size="Reviews",
            size_max=17,
            hover_name="App",
            hover_data={"Category": True, "Price": ":.2f", "Installs": ":,", "Reviews": ":,"},
            log_x=True,
            title="Popularity vs rating",
            color_discrete_map={"Free": PALETTE["cyan"], "Paid": PALETTE["purple"], "Unknown": PALETTE["yellow"]},
        )
        fig.update_layout(xaxis_title="Installs (log scale)", yaxis_title="Rating / 5")
        st.plotly_chart(apply_plotly_style(fig, 330), width="stretch", config={"displayModeBar": False})

    top_apps = filtered.sort_values(["Installs", "Rating"], ascending=[False, False]).head(6)
    if not top_apps.empty:
        leader = top_apps.iloc[0]
        st.markdown(
            f'<div class="pp-insight">💡 <b>Quick insight:</b> <b>{leader["App"]}</b> leads this filtered view by installs, with about <b>{pretty_number(leader["Installs"])}</b> installs. Use the App Explorer tab to compare it with similar apps.</div>',
            unsafe_allow_html=True,
        )

with tab_explorer:
    section_heading("THE CATALOGUE", "Find your next data point", "Search, compare and sort individual apps. The filters in the sidebar apply here too.")
    sort_col = {"Most installs": "Installs", "Highest rating": "Rating", "Most reviews": "Reviews", "Lowest price": "Price", "Most expensive": "Price"}[sort_choice]
    ascending = sort_choice in ["Lowest price"]
    table_df = filtered.sort_values(sort_col, ascending=ascending).head(500).copy()
    display_cols = [c for c in ["App", "Category", "Rating", "Installs", "Reviews", "Type", "Price", "Content Rating"] if c in table_df.columns]
    display_df = table_df[display_cols].copy()
    if "Category" in display_df:
        display_df["Category"] = display_df["Category"].str.replace("_", " ").str.title()
    st.caption(f"Showing up to 500 apps · Sorted by {sort_choice.lower()}")
    st.dataframe(
        display_df,
        width="stretch",
        height=440,
        hide_index=True,
        column_config={
            "Rating": st.column_config.NumberColumn("Rating ⭐", format="%.2f"),
            "Installs": st.column_config.NumberColumn("Installs", format="%d"),
            "Reviews": st.column_config.NumberColumn("Reviews", format="%d"),
            "Price": st.column_config.NumberColumn("Price ($)", format="$%.2f"),
        },
    )
    st.markdown("#### Compare a specific app")
    app_names = sorted(filtered["App"].dropna().unique().tolist())
    chosen_app = st.selectbox("Choose an app to inspect", app_names, index=0)
    selected = filtered[filtered["App"] == chosen_app].iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Category", str(selected["Category"]).replace("_", " ").title())
    c2.metric("Rating", f"{selected['Rating']:.2f} ⭐" if pd.notna(selected["Rating"]) else "Not rated")
    c3.metric("Installs", pretty_number(selected["Installs"]))
    c4.metric("Reviews", pretty_number(selected["Reviews"]))
    st.caption(f"Audience: {selected['Content Rating']} · Type: {selected['Type']} · Price: {'$' + format(selected['Price'], '.2f') if selected['Price'] > 0 else 'Free'}")

with tab_category:
    section_heading("ZOOM IN", "Category Lab", "Pick one category and explore its pricing, ratings and most-installed apps.")
    category_choices = sorted(filtered["Category"].dropna().unique().tolist())
    chosen_category = st.selectbox("Select a category", category_choices, key="category_lab_select")
    cat_df = filtered[filtered["Category"] == chosen_category].copy()
    c1, c2, c3 = st.columns(3)
    c1.metric("Apps in category", f"{len(cat_df):,}")
    c2.metric("Average rating", f"{cat_df['Rating'].mean():.2f} ⭐" if cat_df["Rating"].notna().any() else "—")
    c3.metric("Median installs", pretty_number(cat_df["Installs"].median()))
    left, right = st.columns(2, gap="large")
    with left:
        cat_top = cat_df.nlargest(top_n, "Installs").sort_values("Installs")
        fig = px.bar(cat_top, x="Installs", y="App", orientation="h", title=f"Most installed apps · {chosen_category.replace('_', ' ').title()}", color="Rating", color_continuous_scale=[[0, "#FF8DB7"], [1, "#55E6D2"]], hover_data=["Reviews", "Price", "Type"])
        fig.update_layout(xaxis_title="Installs", yaxis_title="", coloraxis_colorbar_title="Rating")
        st.plotly_chart(apply_plotly_style(fig, 390), width="stretch", config={"displayModeBar": False})
    with right:
        price_df = cat_df.copy()
        price_df["Price group"] = np.where(price_df["Price"] > 0, "Paid", "Free")
        fig = px.box(price_df, x="Price group", y="Rating", color="Price group", title="Rating spread: free vs paid", color_discrete_map={"Free": PALETTE["cyan"], "Paid": PALETTE["purple"]}, points="outliers")
        fig.update_layout(xaxis_title="", yaxis_title="Rating / 5", showlegend=False)
        st.plotly_chart(apply_plotly_style(fig, 390), width="stretch", config={"displayModeBar": False})
    st.markdown("#### Category standouts")
    standouts = cat_df.sort_values(["Rating", "Reviews"], ascending=[False, False]).dropna(subset=["Rating"]).head(5)
    if standouts.empty:
        st.info("There are no rated apps in this category after applying your current filters.")
    else:
        st.dataframe(standouts[["App", "Rating", "Installs", "Reviews", "Type", "Price"]], width="stretch", hide_index=True)

with tab_reviews:
    section_heading("WHAT USERS ARE SAYING", "Review Signals", "A sentiment snapshot from the optional user-review dataset.")
    if reviews_summary.empty or not {"Positive Reviews", "Neutral Reviews", "Negative Reviews"}.issubset(apps.columns):
        st.info("Review sentiment data wasn't found. Keep `googleplaystore_user_reviews.csv` beside `app.py` to unlock this section.")
    else:
        review_view = filtered.copy()
        sentiment_totals = {
            "Positive": int(review_view["Positive Reviews"].sum()),
            "Neutral": int(review_view["Neutral Reviews"].sum()),
            "Negative": int(review_view["Negative Reviews"].sum()),
        }
        total_sentiment = sum(sentiment_totals.values())
        a, b, c = st.columns(3)
        a.metric("Positive reviews", pretty_number(sentiment_totals["Positive"]))
        b.metric("Neutral reviews", pretty_number(sentiment_totals["Neutral"]))
        c.metric("Negative reviews", pretty_number(sentiment_totals["Negative"]))
        left, right = st.columns(2, gap="large")
        with left:
            sent_df = pd.DataFrame({"Sentiment": list(sentiment_totals.keys()), "Reviews": list(sentiment_totals.values())})
            fig = px.pie(sent_df, names="Sentiment", values="Reviews", hole=0.66, title="Overall review sentiment", color="Sentiment", color_discrete_map={"Positive": PALETTE["green"], "Neutral": PALETTE["yellow"], "Negative": PALETTE["pink"]})
            fig.update_traces(textposition="outside", textinfo="percent+label", marker=dict(line=dict(color="#0B1220", width=3)))
            st.plotly_chart(apply_plotly_style(fig, 350), width="stretch", config={"displayModeBar": False})
        with right:
            top_sentiment = review_view.nlargest(top_n, "Positive Reviews").sort_values("Positive Reviews")
            fig = go.Figure()
            for label, color in [("Positive Reviews", PALETTE["green"]), ("Neutral Reviews", PALETTE["yellow"]), ("Negative Reviews", PALETTE["pink"])]:
                fig.add_trace(go.Bar(name=label.replace(" Reviews", ""), x=top_sentiment[label], y=top_sentiment["App"], orientation="h", marker_color=color))
            fig.update_layout(barmode="stack", title="Review mix for apps with most positive reviews", xaxis_title="Number of reviews", yaxis_title="")
            st.plotly_chart(apply_plotly_style(fig, 350), width="stretch", config={"displayModeBar": False})
        if total_sentiment:
            positive_pct = sentiment_totals["Positive"] / total_sentiment * 100
            st.markdown(f'<div class="pp-insight">💬 <b>Sentiment pulse:</b> <b>{positive_pct:.1f}%</b> of labelled reviews in this filtered view are positive. Sentiment is calculated from the supplied review sample, not from every Play Store review.</div>', unsafe_allow_html=True)

with tab_quality:
    section_heading("BEHIND THE NUMBERS", "Data Quality & Method", "A transparent view of what was cleaned before the analysis.")
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Rows in source", f"{audit['source_rows']:,}")
    q2.metric("Rows after cleaning", f"{audit['clean_rows']:,}")
    q3.metric("Rows removed", f"{audit['removed_rows']:,}")
    q4.metric("Categories", f"{audit['categories']}")
    st.markdown("#### Cleaning steps applied")
    st.markdown(
        """
        - Removed rows with missing app names or malformed category labels.
        - Converted ratings, reviews, installs and prices into numeric columns.
        - Treated invalid ratings outside the 0–5 range as missing values.
        - Standardized app type and audience-rating labels.
        - Removed duplicate app names, keeping the first available record.
        - Parsed the last-updated field where available.
        """
    )
    st.markdown("#### Missing ratings")
    rating_missing = int(apps["Rating"].isna().sum())
    rating_present = len(apps) - rating_missing
    missing_df = pd.DataFrame({"Rating status": ["Available", "Missing"], "Apps": [rating_present, rating_missing]})
    fig = px.pie(missing_df, names="Rating status", values="Apps", hole=0.68, title="Rating completeness", color="Rating status", color_discrete_map={"Available": PALETTE["cyan"], "Missing": PALETTE["pink"]})
    fig.update_traces(textposition="outside", textinfo="percent+label")
    st.plotly_chart(apply_plotly_style(fig, 320), width="stretch", config={"displayModeBar": False})
    st.caption("Dataset note: the commonly distributed Google Play Store CSV is a historical snapshot, not a live feed of current Play Store listings. Interpret the results as patterns in this dataset only.")

st.markdown("---")
foot1, foot2 = st.columns([3, 1])
with foot1:
    st.markdown("<span class='pp-mini'>BUILT WITH STREAMLIT + PLOTLY · DATA STORYTELLING MINI PROJECT</span>", unsafe_allow_html=True)
with foot2:
    st.markdown("<div style='text-align:right' class='pp-mini'>PLAYPULSE v2.0</div>", unsafe_allow_html=True)
