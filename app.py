import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="IT Asset Dashboard",
    page_icon="💻",
    layout="wide"
)

# =========================
# CSS
# =========================
st.markdown("""
<style>

.stApp {
    background: linear-gradient(180deg,#0f172a,#111827);
    color:white;
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

h1 {
    color:white !important;
    text-align:center;
}

[data-testid="metric-container"]{
    background:rgba(255,255,255,0.05);
    border-radius:15px;
    padding:15px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# GOOGLE SHEET CSV
# =========================
sheet_url = "https://docs.google.com/spreadsheets/d/1JbU_0hNzrYNAGvoEnN0etL9DkJ0vnhbtM6KNHBYtUgY/export?format=csv"

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():

    df = pd.read_csv(sheet_url)

    return df

df = load_data()

# =========================
# CLEAN COLUMN
# =========================
df.columns = (
    df.columns.astype(str)
    .str.strip()
)

# =========================
# TITLE
# =========================
st.title("💻 IT Asset Dashboard")

# =========================
# KPI
# =========================
total_asset = len(df)

notebook_count = (
    df['Device']
    .astype(str)
    .str.contains("Notebook", case=False)
    .sum()
)

computer_count = (
    df['Device']
    .astype(str)
    .str.contains("Computer", case=False)
    .sum()
)

repair_count = (
    df['Status']
    .astype(str)
    .str.contains("Repair", case=False)
    .sum()
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("สินทรัพย์ทั้งหมด", total_asset)
c2.metric("Notebook", notebook_count)
c3.metric("Computer", computer_count)
c4.metric("Repair", repair_count)

# =========================
# SEARCH
# =========================
search = st.text_input(
    "🔍 ค้นหา Asset / User / Device"
)

# =========================
# FILTER
# =========================
df_show = df.copy()

if search:

    df_show = df_show[
        df_show.astype(str)
        .apply(
            lambda row:
            row.str.contains(
                search,
                case=False,
                na=False
            ).any(),
            axis=1
        )
    ]

# =========================
# CHART
# =========================
col1, col2 = st.columns(2)

with col1:

    fig = px.pie(
        df,
        names='Status',
        title='สถานะอุปกรณ์',
        hole=0.5
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig2 = px.bar(
        df,
        x='Department',
        color='Status',
        title='Asset ตามแผนก'
    )

    fig2.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# =========================
# TABLE
# =========================
st.subheader("📋 รายการทรัพย์สิน IT")

st.dataframe(
    df_show,
    use_container_width=True,
    height=500
)

# =========================
# DOWNLOAD CSV
# =========================
csv = df_show.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    "📥 ดาวน์โหลด CSV",
    csv,
    "it_asset.csv",
    "text/csv",
    use_container_width=True
)
