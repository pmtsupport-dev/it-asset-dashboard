import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials

=========================
PAGE CONFIG
=========================

st.set_page_config(
page_title="IT Asset Dashboard",
page_icon="💻",
layout="wide"
)

=========================
STYLE
=========================

st.markdown("""

""", unsafe_allow_html=True)

=========================
GOOGLE SHEET CONNECT
=========================

scope = [
"https://www.googleapis.com/auth/spreadsheets",
"https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
"service_account.json",
scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open("IT_ASSET").sheet1

=========================
LOAD DATA
=========================

@st.cache_data(ttl=5)
def load_data():

data = sheet.get_all_records()

df = pd.DataFrame(data)

if len(df) == 0:

    df = pd.DataFrame(columns=[
        "Asset ID",
        "Device",
        "Brand",
        "User",
        "Department",
        "SerialNumber",
        "Status"
    ])

df = df.astype(str)

return df
=========================
SESSION
=========================

if "df" not in st.session_state:
st.session_state.df = load_data()

df = st.session_state.df

=========================
TITLE
=========================

st.title("💻 IT Asset Dashboard")

=========================
SEARCH
=========================

search = st.text_input("🔍 ค้นหา")

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
=========================
KPI
=========================

total_asset = len(df)

notebook_count = (
df["Device"]
.str.contains("Notebook", case=False, na=False)
.sum()
)

computer_count = (
df["Device"]
.str.contains("Computer", case=False, na=False)
.sum()
)

repair_count = (
df["Status"]
.str.contains("Repair", case=False, na=False)
.sum()
)

=========================
KPI DISPLAY
=========================

c1, c2, c3, c4 = st.columns(4)

c1.metric("สินทรัพย์ทั้งหมด", total_asset)
c2.metric("Notebook", notebook_count)
c3.metric("Computer", computer_count)
c4.metric("Repair", repair_count)

=========================
CHART
=========================

st.subheader("📊 สรุปข้อมูลอุปกรณ์")

col1, col2 = st.columns(2)

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
    hole=0.5
)

fig.update_traces(
    textinfo="label+value"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

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
    color="Department",
    text="Count",
    barmode="group"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)
=========================
TABLE
=========================

st.subheader("📋 รายการทรัพย์สิน")

edited_df = st.data_editor(
df_show,
use_container_width=True,
num_rows="dynamic",
hide_index=True
)

=========================
SAVE TABLE
=========================

if st.button("💾 บันทึกตาราง"):

edited_df = edited_df.astype(str)

sheet.clear()

sheet.update(
    [edited_df.columns.values.tolist()] +
    edited_df.values.tolist()
)

st.session_state.df = edited_df

st.success("✅ บันทึกข้อมูลเรียบร้อย")

st.cache_data.clear()

st.rerun()
=========================
ADD DATA
=========================

st.subheader("➕ เพิ่มทรัพย์สินใหม่")

with st.form("add_form"):

asset_id = st.text_input("Asset ID")
device = st.text_input("Device")
brand = st.text_input("Brand")
user = st.text_input("User")
department = st.text_input("Department")
serial = st.text_input("SerialNumber")

status = st.selectbox(
    "Status",
    ["Active", "Spare", "Repair"]
)

submit = st.form_submit_button("➕ เพิ่มข้อมูล")

if submit:

    new_row = pd.DataFrame([{
        "Asset ID": asset_id,
        "Device": device,
        "Brand": brand,
        "User": user,
        "Department": department,
        "SerialNumber": serial,
        "Status": status
    }])

    new_df = pd.concat(
        [df, new_row],
        ignore_index=True
    )

    new_df = new_df.astype(str)

    sheet.clear()

    sheet.update(
        [new_df.columns.values.tolist()] +
        new_df.values.tolist()
    )

    st.session_state.df = new_df

    st.success("✅ เพิ่มข้อมูลเรียบร้อย")

    st.cache_data.clear()

    st.rerun()
=========================
DELETE
=========================

st.subheader("🗑️ ลบข้อมูล")

delete_asset = st.selectbox(
"เลือก Asset ID ที่ต้องการลบ",
df["Asset ID"].astype(str).unique()
)

if st.button("❌ ลบข้อมูล"):

new_df = df[
    df["Asset ID"].astype(str)
    != str(delete_asset)
]

new_df = new_df.reset_index(drop=True)

sheet.clear()

sheet.update(
    [new_df.columns.values.tolist()] +
    new_df.values.tolist()
)

st.session_state.df = new_df

st.success("✅ ลบข้อมูลเรียบร้อย")

st.cache_data.clear()

st.rerun()
=========================
DOWNLOAD CSV
=========================

csv = df.to_csv(
index=False
).encode("utf-8-sig")

st.download_button(
"📥 ดาวน์โหลด CSV",
csv,
"it_asset.csv",
"text/csv"
)

=========================
REFRESH
=========================

if st.button("🔄 Refresh"):

st.cache_data.clear()

st.session_state.df = load_data()

st.rerun()
