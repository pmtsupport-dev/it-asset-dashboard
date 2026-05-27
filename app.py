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
# STYLE
# =========================
st.markdown("""
<style>

.stApp{
    background: linear-gradient(180deg,#020617,#0f172a);
    color:white;
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

h1,h2,h3,h4,label,p,div{
    color:white;
}

[data-testid="metric-container"]{
    background: rgba(255,255,255,0.05);
    border-radius:16px;
    padding:15px;
    border:1px solid rgba(255,255,255,0.08);
}

.stButton > button{
    border-radius:12px;
    border:none;
    background:#2563eb;
    color:white;
    font-weight:bold;
    height:45px;
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

    if "SerialNumber" in df.columns:
        df["SerialNumber"] = (
            df["SerialNumber"]
            .astype(str)
        )

    return df

# =========================
# SESSION STATE
# =========================
if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# =========================
# TITLE
# =========================
st.title("💻 IT Asset Dashboard")

# =========================
# SEARCH
# =========================
search = st.text_input(
    "🔍 ค้นหา Asset / User / Device"
)

# =========================
# FILTER
# =========================
if search:

    df_show = df[
        df.astype(str)
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

else:

    df_show = df.copy()

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
# CHART
# =========================
st.subheader("📊 สรุปข้อมูลอุปกรณ์")

col1, col2 = st.columns(2)

# =========================
# PIE CHART
# =========================
with col1:

    status_count = (
        df["Status"]
        .value_counts()
        .reset_index()
    )

    status_count.columns = [
        "Status",
        "Count"
    ]

    fig = px.pie(
        status_count,
        names="Status",
        values="Count",
        title="จำนวนอุปกรณ์ตามสถานะ",
        hole=0.5
    )

    fig.update_traces(
        textinfo="label+value"
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        height=450
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================
# BAR CHART
# =========================
with col2:

    device_department = (
        df.groupby(
            ["Department", "Device"]
        )
        .size()
        .reset_index(name="Count")
    )

    fig2 = px.bar(
        device_department,
        x="Department",
        y="Count",
        color="Device",
        barmode="group",
        text="Count",
        title="จำนวนอุปกรณ์แยกตามแผนก"
    )

    fig2.update_traces(
        textposition="outside"
    )

    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        height=450,
        xaxis_title="แผนก",
        yaxis_title="จำนวนอุปกรณ์"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# =========================
# TABLE
# =========================
st.subheader("📋 รายการทรัพย์สิน")

edited_df = st.data_editor(
    df_show,
    use_container_width=True,
    num_rows="dynamic",
    hide_index=True,
    key="editor"
)

# =========================
# EDIT DATA
# =========================
st.subheader("✏️ แก้ไขข้อมูลย้อนหลัง")

asset_list = (
    edited_df["Asset ID"]
    .astype(str)
    .tolist()
)

selected_asset = st.selectbox(
    "เลือก Asset ID",
    asset_list
)

selected_index = edited_df[
    edited_df["Asset ID"]
    .astype(str)
    == str(selected_asset)
].index[0]

with st.form("edit_form"):

    asset_id = st.text_input(
        "Asset ID",
        value=str(
            edited_df.loc[selected_index, "Asset ID"]
        )
    )

    device = st.text_input(
        "Device",
        value=str(
            edited_df.loc[selected_index, "Device"]
        )
    )

    brand = st.text_input(
        "Brand",
        value=str(
            edited_df.loc[selected_index, "Brand"]
        )
    )

    user = st.text_input(
        "User",
        value=str(
            edited_df.loc[selected_index, "User"]
        )
    )

    department = st.text_input(
        "Department",
        value=str(
            edited_df.loc[selected_index, "Department"]
        )
    )

    serial = st.text_input(
        "SerialNumber",
        value=str(
            edited_df.loc[selected_index, "SerialNumber"]
        )
    )

    status = st.selectbox(
        "Status",
        ["Active", "Spare", "Repair"],
        index=0
    )

    submit_edit = st.form_submit_button(
        "💾 บันทึกการแก้ไข"
    )

    if submit_edit:

        edited_df["SerialNumber"] = (
            edited_df["SerialNumber"]
            .astype(str)
        )

        edited_df.loc[selected_index, "Asset ID"] = str(asset_id)
        edited_df.loc[selected_index, "Device"] = str(device)
        edited_df.loc[selected_index, "Brand"] = str(brand)
        edited_df.loc[selected_index, "User"] = str(user)
        edited_df.loc[selected_index, "Department"] = str(department)
        edited_df.loc[selected_index, "SerialNumber"] = str(serial)
        edited_df.loc[selected_index, "Status"] = str(status)

        st.session_state.df = edited_df.copy()

        st.success("✅ แก้ไขข้อมูลเรียบร้อย")

# =========================
# ADD DATA
# =========================
st.subheader("➕ เพิ่มทรัพย์สินใหม่")

with st.form("add_form"):

    new_asset = st.text_input("Asset ID")
    new_device = st.text_input("Device")
    new_brand = st.text_input("Brand")
    new_user = st.text_input("User")
    new_department = st.text_input("Department")
    new_serial = st.text_input("SerialNumber")

    new_status = st.selectbox(
        "Status",
        ["Active", "Spare", "Repair"]
    )

    submit = st.form_submit_button(
        "➕ เพิ่มข้อมูล"
    )

    if submit:

        new_row = {
            "Asset ID": str(new_asset),
            "Device": str(new_device),
            "Brand": str(new_brand),
            "User": str(new_user),
            "Department": str(new_department),
            "SerialNumber": str(new_serial),
            "Status": str(new_status)
        }

        new_df = pd.concat(
            [st.session_state.df,
            pd.DataFrame([new_row])],
            ignore_index=True
        )

        st.session_state.df = new_df

        st.success("✅ เพิ่มข้อมูลเรียบร้อย")

# =========================
# DELETE
# =========================
st.subheader("🗑️ ลบข้อมูล")

delete_asset = st.selectbox(
    "เลือก Asset ID ที่ต้องการลบ",
    edited_df["Asset ID"]
    .astype(str)
)

if st.button("❌ ลบข้อมูล"):

    new_df = edited_df[
        edited_df["Asset ID"]
        .astype(str)
        != str(delete_asset)
    ]

    st.session_state.df = new_df

    st.success("✅ ลบข้อมูลเรียบร้อย")

# =========================
# DOWNLOAD CSV
# =========================
csv = st.session_state.df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    "📥 ดาวน์โหลด CSV",
    csv,
    "it_asset.csv",
    "text/csv",
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

📊 จำนวนทรัพย์สินทั้งหมด :
<b>{len(st.session_state.df)}</b> รายการ

</div>
""", unsafe_allow_html=True)
