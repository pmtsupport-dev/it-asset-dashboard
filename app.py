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
# CUSTOM CSS
# =========================
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(180deg, #020617 0%, #0f172a 100%);
    color: white;
}

/* Hide Menu */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main */
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Title */
h1 {
    color: white !important;
    font-size: 42px !important;
    font-weight: bold !important;
}

/* Metric */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 20px;
    backdrop-filter: blur(10px);
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
}

/* Buttons */
.stButton > button {
    width: 100%;
    border-radius: 12px;
    height: 50px;
    border: none;
    background: linear-gradient(90deg,#06b6d4,#3b82f6);
    color: white;
    font-weight: bold;
    font-size: 16px;
}

/* Text Input */
.stTextInput input {
    border-radius: 12px;
}

/* Mobile */
@media (max-width: 768px) {

    h1 {
        font-size: 30px !important;
    }

}

</style>
""", unsafe_allow_html=True)

# =========================
# GOOGLE SHEET CSV
# =========================
sheet_url = "https://docs.google.com/spreadsheets/d/19t2bqMYMBi_nmHJlZbSCHILG8-mDqssb-v3rTpUI2gY/export?format=csv"

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():

    df = pd.read_csv(sheet_url)

    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\n", "")
    )

    return df

# =========================
# SESSION STATE
# =========================
if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# =========================
# SEARCH
# =========================
search = st.text_input(
    "🔍 ค้นหา Asset / User / Device"
)

# =========================
# FILTER SEARCH
# =========================
if search:

    df_show = df[
        df.astype(str)
        .apply(
            lambda row:
            row.str.contains(search, case=False).any(),
            axis=1
        )
    ]

else:

    df_show = df

# =========================
# KPI
# =========================
total_asset = len(df)

notebook_count = (
    df["Device"]
    .astype(str)
    .str.contains("Notebook", case=False)
    .sum()
)

computer_count = (
    df["Device"]
    .astype(str)
    .str.contains("Computer", case=False)
    .sum()
)

repair_count = (
    df["Status"]
    .astype(str)
    .str.contains("Repair", case=False)
    .sum()
)

# =========================
# TITLE
# =========================
st.title("💻 IT Asset Dashboard")

# =========================
# KPI CARDS
# =========================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("สินทรัพย์ทั้งหมด", total_asset)

with c2:
    st.metric("Notebook", notebook_count)

with c3:
    st.metric("Computer", computer_count)

with c4:
    st.metric("Repair", repair_count)

# =========================
# CHARTS
# =========================
col1, col2 = st.columns(2)

with col1:

    fig = px.pie(
        df,
        names="Status",
        hole=0.55,
        title="สถานะอุปกรณ์"
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        height=420
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

    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        height=420
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# =========================
# TABLE EDITOR
# =========================
st.subheader("📋 รายการทรัพย์สิน")

edited_df = st.data_editor(
    df_show,
    num_rows="dynamic",
    use_container_width=True,
    height=500,
    key="asset_editor"
)

# =========================
# UPDATE BUTTON
# =========================
if st.button("✅ อัปเดตข้อมูล", use_container_width=True):

    st.session_state.df = edited_df.copy()

    st.success("✅ แก้ไขข้อมูลเรียบร้อย")

    st.toast(
        "อัปเดตข้อมูลสำเร็จ",
        icon="✅"
    )

# =========================
# ADD ASSET
# =========================
st.subheader("➕ เพิ่มทรัพย์สินใหม่")

with st.form("add_asset"):

    c1, c2, c3 = st.columns(3)

    with c1:
        asset_id = st.text_input("Asset ID")

    with c2:
        device = st.selectbox(
            "Device",
            ["Notebook", "Computer", "Printer", "Monitor"]
        )

    with c3:
        brand = st.text_input("Brand")

    c4, c5, c6 = st.columns(3)

    with c4:
        user = st.text_input("User")

    with c5:
        department = st.text_input("Department")

    with c6:
        serial = st.text_input("Serial Number")

    status = st.selectbox(
        "Status",
        ["Active", "Repair", "Spare"]
    )

    submit = st.form_submit_button("💾 เพิ่มข้อมูล")

    if submit:

        new_row = {
            "Asset ID": asset_id,
            "Device": device,
            "Brand": brand,
            "User": user,
            "Department": department,
            "SerialNumber": serial,
            "Status": status
        }

        new_df = pd.concat(
            [st.session_state.df, pd.DataFrame([new_row])],
            ignore_index=True
        )

        st.session_state.df = new_df

        st.success("✅ เพิ่มข้อมูลเรียบร้อย")

        st.toast(
            "เพิ่ม Asset สำเร็จ",
            icon="✅"
        )

# =========================
# DELETE
# =========================
st.subheader("🗑 ลบข้อมูล")

delete_index = st.number_input(
    "กรอกเลข Index ที่ต้องการลบ",
    min_value=0,
    step=1
)

if st.button("❌ ลบข้อมูล"):

    try:

        new_df = st.session_state.df.drop(delete_index)

        new_df = new_df.reset_index(drop=True)

        st.session_state.df = new_df

        st.success("✅ ลบข้อมูลเรียบร้อย")

    except:

        st.error("❌ ลบไม่สำเร็จ")

# =========================
# SAVE CSV
# =========================
st.subheader("💾 บันทึกข้อมูล")

csv = st.session_state.df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="📥 ดาวน์โหลด CSV",
    data=csv,
    file_name="it_asset_dashboard.csv",
    mime="text/csv",
    use_container_width=True
)

# =========================
# REFRESH
# =========================
if st.button("🔄 Refresh"):

    st.cache_data.clear()

    st.session_state.df = load_data()

    st.rerun()

# =========================
# SUMMARY
# =========================
st.markdown(f"""
<div style="
background: rgba(255,255,255,0.05);
padding:15px;
border-radius:15px;
margin-top:10px;
border:1px solid rgba(255,255,255,0.1);
">

📊 จำนวนทรัพย์สินทั้งหมด:
<b>{len(st.session_state.df)}</b> รายการ

</div>
""", unsafe_allow_html=True)
