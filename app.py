import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="IT Asset Dashboard",
    page_icon="💻",
    layout="wide"
)

# =========================================
# CUSTOM CSS
# =========================================
st.markdown("""
<style>

.main {
    background-color: #0f172a;
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

.stMetric {
    background-color: #1e293b;
    padding: 15px;
    border-radius: 15px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.3);
}

div[data-testid="stExpander"] {
    border-radius: 10px;
    overflow: hidden;
}

h1, h2, h3 {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# GOOGLE SHEETS CONNECT
# =========================================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json",
    scope
)

client = gspread.authorize(creds)

sheet = client.open("IT_ASSET").sheet1

# =========================================
# LOAD DATA
# =========================================
data = sheet.get_all_records()

df = pd.DataFrame(data)

df.columns = df.columns.str.strip()

# =========================================
# SIDEBAR
# =========================================
st.sidebar.title("💻 IT Asset System")

menu = st.sidebar.radio(
    "เมนู",
    [
        "Dashboard",
        "Add Asset"
    ]
)

# =========================================
# DASHBOARD
# =========================================
if menu == "Dashboard":

    st.title("💻 IT Asset Dashboard")

    st.markdown("ระบบจัดการทรัพย์สินไอที")

    st.divider()

    # =====================================
    # KPI
    # =====================================
    total_assets = len(df)

    active_assets = len(
        df[df["Status"] == "Active"]
    ) if not df.empty else 0

    repair_assets = len(
        df[df["Status"] == "Repair"]
    ) if not df.empty else 0

    dept_count = df["Department"].nunique() \
        if not df.empty else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "💻 จำนวนทั้งหมด",
        total_assets
    )

    col2.metric(
        "✅ Active",
        active_assets
    )

    col3.metric(
        "🔧 Repair",
        repair_assets
    )

    col4.metric(
        "🏢 Departments",
        dept_count
    )

    st.divider()

    # =====================================
    # SEARCH
    # =====================================
    search = st.text_input(
        "🔍 ค้นหา Asset / User / Device"
    )

    if search:

        filtered_df = df[
            df.astype(str)
            .apply(
                lambda x: x.str.contains(
                    search,
                    case=False
                )
            )
            .any(axis=1)
        ]

    else:
        filtered_df = df

    # =====================================
    # CHARTS
    # =====================================
    col_chart1, col_chart2 = st.columns(2)

    # =====================================
    # PIE CHART
    # =====================================
    with col_chart1:

        st.subheader("📊 ประเภทอุปกรณ์")

        device_count = (
            filtered_df["Device"]
            .value_counts()
            .reset_index()
        )

        device_count.columns = [
            "Device",
            "Count"
        ]

        fig_pie = px.pie(
            device_count,
            names="Device",
            values="Count",
            hole=0.45
        )

        fig_pie.update_traces(
            texttemplate="%{label}<br>%{value} เครื่อง",
            textposition="inside"
        )

        fig_pie.update_layout(
            paper_bgcolor="#0f172a",
            font_color="white"
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

    # =====================================
    # BAR CHART
    # =====================================
    with col_chart2:

        st.subheader("🏢 อุปกรณ์แต่ละแผนก")

        dept_data = (
            filtered_df["Department"]
            .value_counts()
            .reset_index()
        )

        dept_data.columns = [
            "Department",
            "Count"
        ]

        fig_bar = px.bar(
            dept_data,
            x="Department",
            y="Count",
            text="Count"
        )

        fig_bar.update_traces(
            texttemplate='%{y} เครื่อง',
            textposition='outside'
        )

        fig_bar.update_layout(
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            font_color="white"
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )

    st.divider()

    # =====================================
    # TABLE
    # =====================================
    st.subheader("📋 รายการทรัพย์สิน")

    for index, row in filtered_df.iterrows():

        with st.expander(
            f"💻 {row['Asset ID']} | {row['Device']} | {row['User']}"
        ):

            colA, colB = st.columns(2)

            with colA:

                new_device = st.text_input(
                    "Device",
                    value=row["Device"],
                    key=f"device_{index}"
                )

                new_brand = st.text_input(
                    "Brand",
                    value=row["Brand"],
                    key=f"brand_{index}"
                )

                new_user = st.text_input(
                    "User",
                    value=row["User"],
                    key=f"user_{index}"
                )

            with colB:

                new_department = st.text_input(
                    "Department",
                    value=row["Department"],
                    key=f"dept_{index}"
                )

                new_serial = st.text_input(
                    "SerialNumber",
                    value=row["SerialNumber"],
                    key=f"serial_{index}"
                )

                new_status = st.selectbox(
                    "Status",
                    [
                        "Active",
                        "Repair",
                        "Spare",
                        "Dispose"
                    ],
                    index=[
                        "Active",
                        "Repair",
                        "Spare",
                        "Dispose"
                    ].index(row["Status"]),
                    key=f"status_{index}"
                )

            btn1, btn2 = st.columns(2)

            # =================================
            # SAVE EDIT
            # =================================
            with btn1:

                if st.button(
                    f"💾 บันทึก {row['Asset ID']}",
                    key=f"save_{index}"
                ):

                    sheet.update(
                        f"B{index+2}",
                        [[new_device]]
                    )

                    sheet.update(
                        f"C{index+2}",
                        [[new_brand]]
                    )

                    sheet.update(
                        f"D{index+2}",
                        [[new_user]]
                    )

                    sheet.update(
                        f"E{index+2}",
                        [[new_department]]
                    )

                    sheet.update(
                        f"F{index+2}",
                        [[new_serial]]
                    )

                    sheet.update(
                        f"G{index+2}",
                        [[new_status]]
                    )

                    st.toast(
                        "✅ บันทึกข้อมูลสำเร็จ",
                        icon="🎉"
                    )

                    st.rerun()

            # =================================
            # DELETE
            # =================================
            with btn2:

                confirm = st.checkbox(
                    f"ยืนยันการลบ {row['Asset ID']}",
                    key=f"confirm_{index}"
                )

                if confirm:

                    if st.button(
                        f"🗑 ลบ {row['Asset ID']}",
                        key=f"delete_{index}"
                    ):

                        sheet.delete_rows(index + 2)

                        st.toast(
                            "🗑 ลบข้อมูลสำเร็จ",
                            icon="⚠️"
                        )

                        st.rerun()

# =========================================
# ADD ASSET
# =========================================
if menu == "Add Asset":

    st.title("➕ เพิ่มทรัพย์สิน")

    with st.form("asset_form"):

        asset_id = st.text_input("Asset ID")
        device = st.text_input("Device")
        brand = st.text_input("Brand")
        user = st.text_input("User")
        department = st.text_input("Department")
        serial = st.text_input("SerialNumber")

        status = st.selectbox(
            "Status",
            [
                "Active",
                "Repair",
                "Spare",
                "Dispose"
            ]
        )

        submit = st.form_submit_button(
            "เพิ่มข้อมูล"
        )

        if submit:

            new_data = [
                asset_id,
                device,
                brand,
                user,
                department,
                serial,
                status
            ]

            sheet.append_row(new_data)

            st.toast(
                "✅ เพิ่มข้อมูลสำเร็จ",
                icon="🎉"
            )

            st.balloons()

            st.rerun()