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
# GOOGLE SHEET CSV
# =========================
sheet_url = "https://docs.google.com/spreadsheets/d/1JbU_0hNzrYNAGvoEnN0etL9DkJ0vnhbtM6KNHBYtUgY/export?format=csv"

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():

    # อ่านแบบไม่มี header
    df = pd.read_csv(sheet_url, header=None)

    return df

df = load_data()

# =========================
# FIX HEADER
# =========================
df.columns = [
    "Asset ID",
    "Device",
    "Brand",
    "User",
    "Department",
    "SerialNumber",
    "Status"
]

# ลบแถวหัวตารางเดิม
df = df.iloc[1:].reset_index(drop=True)

# =========================
# TITLE
# =========================
st.title("💻 IT Asset Dashboard")

# =========================
# KPI
# =========================
total_asset = len(df)

notebook_count = (
    df["Device"]
    .astype(str)
    .str.contains("Notebook", case=False, na=False)
    .sum()
)

computer_count = (
    df["Device"]
    .astype(str)
    .str.contains("Computer", case=False, na=False)
    .sum()
)

repair_count = (
    df["Status"]
    .astype(str)
    .str.contains("Repair", case=False, na=False)
    .sum()
)

# =========================
# KPI DISPLAY
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("สินทรัพย์ทั้งหมด", total_asset)
c2.metric("Notebook", notebook_count)
c3.metric("Computer", computer_count)
c4.metric("Repair", repair_count)

# =========================
# SEARCH
# =========================
search = st.text_input(
    "🔍 ค้นหา"
)

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
        names="Status",
        hole=0.5,
        title="สถานะอุปกรณ์"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig2 = px.bar(
        df,
        x="Department",
        color="Status",
        title="Asset ตามแผนก"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# =========================
# TABLE
# =========================
st.subheader("📋 รายการทรัพย์สิน")

st.dataframe(
    df_show,
    use_container_width=True,
    height=500
)
