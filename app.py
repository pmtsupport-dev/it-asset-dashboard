import streamlit as st
import pandas as pd
import plotly.express as px
import sheets_helper as sh

# =========================
# PAGE CONFIG
# อ่าน query param ก่อน เพื่อเลือก layout ให้เหมาะกับหน้าจอ
# หน้าแจ้งซ่อม/ประวัติ (เปิดจากมือถือผ่าน QR) ใช้ layout แคบแบบแอปมือถือ
# หน้า dashboard (เปิดจากคอม) ใช้ layout กว้าง
# =========================
_view = st.query_params.get("view", "dashboard")
_page_layout = "centered" if _view in ("repair", "history") else "wide"

st.set_page_config(
    page_title="IT Asset & Repair System",
    page_icon="💻",
    layout=_page_layout
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
    height:48px;
    font-size:16px;
}

/* ทำให้ตัวหนังสือในช่องกรอกข้อมูลอ่านง่าย ชัดเจน ตัดกับพื้นหลัง */
.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div{
    background-color:#ffffff !important;
    color:#0f172a !important;
    font-size:16px !important;
    border-radius:12px !important;
    border:1px solid #cbd5e1 !important;
    caret-color:#0f172a !important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder{
    color:#64748b !important;
    opacity:1 !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label{
    font-weight:600 !important;
    font-size:15px !important;
    color:#e2e8f0 !important;
}

/* ==================================================
   MOBILE APP STYLE — ใช้เฉพาะหน้าแจ้งซ่อม/ประวัติซ่อม
   ================================================== */
.mobile-header{
    display:flex;
    align-items:center;
    gap:14px;
    background:linear-gradient(135deg,#2563eb,#1d4ed8);
    padding:22px 20px;
    border-radius:0 0 24px 24px;
    margin:-4rem -1rem 24px -1rem;
    box-shadow:0 8px 24px rgba(37,99,235,0.35);
}
.mobile-header .icon{
    font-size:34px;
    line-height:1;
}
.mobile-header .title{
    font-size:20px;
    font-weight:800;
    color:white;
    margin:0;
}
.mobile-header .subtitle{
    font-size:13px;
    color:rgba(255,255,255,0.85);
    margin:2px 0 0 0;
}

.info-card{
    background:rgba(255,255,255,0.06);
    border:1px solid rgba(255,255,255,0.14);
    border-radius:18px;
    padding:18px 20px;
    margin-bottom:18px;
}
.info-card .row{
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:6px 0;
    font-size:14px;
    border-bottom:1px solid rgba(255,255,255,0.06);
}
.info-card .row:last-child{ border-bottom:none; }
.info-card .label{ color:#94a3b8; }
.info-card .value{ color:#ffffff; font-weight:700; text-align:right; }
.info-card .note{ margin-top:10px; color:#e2e8f0; font-size:14px; line-height:1.5; }
.info-card .subnote{ color:#94a3b8; font-size:12.5px; margin-top:6px; }

.status-badge{
    display:inline-block;
    padding:4px 14px;
    border-radius:999px;
    font-size:12px;
    font-weight:800;
}
.status-pending{ background:#fef3c7; color:#92400e; }
.status-progress{ background:#dbeafe; color:#1e40af; }
.status-done{ background:#dcfce7; color:#166534; }
</style>
""", unsafe_allow_html=True)


def mobile_header(icon, title, subtitle):
    """แสดงหัวข้อสไตล์แอปมือถือ (การ์ดสีน้ำเงินโค้งมน ด้านบนสุดของหน้า)"""
    st.markdown(f"""
    <div class="mobile-header">
        <div class="icon">{icon}</div>
        <div>
            <p class="title">{title}</p>
            <p class="subtitle">{subtitle}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def status_badge(status):
    """คืนค่า HTML ของป้ายสถานะสี ตามสถานะของตั๋ว"""
    cls = {
        "รอดำเนินการ": "status-pending",
        "กำลังซ่อม": "status-progress",
        "เสร็จแล้ว": "status-done",
    }.get(status, "status-pending")
    return f'<span class="status-badge {cls}">{status}</span>'

# =========================
# รายการอุปกรณ์ — อ่านสดจาก Google Sheet ผ่าน Service Account เดียวกับตั๋วซ่อม
# (แคชไว้ 30 วินาที ลด quota การเรียก Google Sheets API, ล้างแคชทันทีหลังแก้ไข/เพิ่ม/ลบ)
# =========================
@st.cache_data(ttl=30)
def load_data():
    records = sh.get_all_assets()
    df = pd.DataFrame(records)
    if df.empty:
        return df
    df.columns = df.columns.str.strip().str.replace("\n", "")
    if "SerialNumber" in df.columns:
        df["SerialNumber"] = df["SerialNumber"].astype(str)
    if "Asset ID" in df.columns:
        df["Asset ID"] = df["Asset ID"].astype(str).str.strip()
    return df


def get_asset(asset_id, df):
    match = df[df["Asset ID"].astype(str) == str(asset_id)]
    if len(match) == 0:
        return None
    return match.iloc[0]


# =========================================================
# VIEW 1: ฟอร์มแจ้งซ่อม (เปิดจากการสแกน QR ที่ตัวอุปกรณ์)
# URL: ?view=repair&asset_id=XXXX
# =========================================================
def show_repair_form(asset_id, df):
    mobile_header("🔧", "แจ้งซ่อมอุปกรณ์ไอที", "กรอกรายละเอียดด้านล่างเพื่อแจ้งซ่อม")

    if not asset_id:
        st.warning("ไม่พบรหัสอุปกรณ์ (asset_id) กรุณาสแกน QR code ที่ติดอยู่บนอุปกรณ์อีกครั้ง")
        return

    asset = get_asset(asset_id, df)
    if asset is None:
        st.error(f"ไม่พบอุปกรณ์รหัส **{asset_id}** ในระบบ กรุณาติดต่อฝ่ายไอที")
        return

    st.markdown(f"""
    <div class="info-card">
        <div class="row"><span class="label">Asset ID</span><span class="value">{asset['Asset ID']}</span></div>
        <div class="row"><span class="label">อุปกรณ์</span><span class="value">{asset.get('Device', '-')} {asset.get('Brand', '')}</span></div>
        <div class="row"><span class="label">แผนก</span><span class="value">{asset.get('Department', '-')}</span></div>
        <div class="row"><span class="label">ผู้ใช้ปัจจุบัน</span><span class="value">{asset.get('User', '-')}</span></div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("repair_form"):
        problem = st.text_area(
            "📝 ปัญหาที่พบ *",
            placeholder="อธิบายอาการ/ปัญหาที่พบโดยละเอียด เช่น เปิดไม่ติด, จอฟ้า, พิมพ์งานไม่ออก",
            height=130
        )
        reported_by = st.text_input("👤 ชื่อผู้แจ้ง *", placeholder="ชื่อ-นามสกุล")
        submitted = st.form_submit_button("📨 ส่งแจ้งซ่อม", use_container_width=True)

        if submitted:
            if not problem.strip() or not reported_by.strip():
                st.error("กรุณากรอกปัญหาที่พบและชื่อผู้แจ้งให้ครบถ้วน")
            else:
                with st.spinner("กำลังบันทึกข้อมูล..."):
                    ticket_id = sh.add_repair_ticket(
                        asset_id=asset["Asset ID"],
                        device=asset.get("Device", ""),
                        brand=asset.get("Brand", ""),
                        user=asset.get("User", ""),
                        department=asset.get("Department", ""),
                        problem=problem.strip(),
                        reported_by=reported_by.strip(),
                    )
                st.success(f"✅ แจ้งซ่อมสำเร็จ! หมายเลขตั๋ว: **{ticket_id}**")
                st.balloons()


# =========================================================
# VIEW 2: ประวัติ/สถานะการซ่อมของอุปกรณ์
# URL: ?view=history&asset_id=XXXX
# =========================================================
def show_repair_history(asset_id, df):
    mobile_header("📋", "ประวัติการซ่อม", "สถานะล่าสุดของการแจ้งซ่อมเครื่องนี้")

    if not asset_id:
        st.warning("ไม่พบรหัสอุปกรณ์ (asset_id) กรุณาสแกน QR code อีกครั้ง")
        return

    asset = get_asset(asset_id, df)
    if asset is None:
        st.error(f"ไม่พบอุปกรณ์รหัส **{asset_id}** ในระบบ")
        return

    st.markdown(f"""
    <div class="info-card">
        <div class="row"><span class="label">Asset ID</span><span class="value">{asset['Asset ID']}</span></div>
        <div class="row"><span class="label">อุปกรณ์</span><span class="value">{asset.get('Device', '-')} {asset.get('Brand', '')}</span></div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("กำลังโหลดประวัติ..."):
        tickets = sh.get_tickets_by_asset(asset_id)

    if not tickets:
        st.info("ยังไม่มีประวัติการแจ้งซ่อมสำหรับอุปกรณ์นี้")
        return

    for t in sorted(tickets, key=lambda x: x.get("ReportedAt", ""), reverse=True):
        status = t.get("Status", "รอดำเนินการ")
        st.markdown(f"""
        <div class="info-card">
            <div class="row"><span class="label">เลขตั๋ว</span><span class="value">{t.get('Ticket ID')}</span></div>
            <div class="row"><span class="label">วันที่แจ้ง</span><span class="value">{t.get('ReportedAt')}</span></div>
            <div class="row"><span class="label">สถานะ</span><span class="value">{status_badge(status)}</span></div>
            <div class="note"><b>ปัญหา:</b> {t.get('Problem')}</div>
            <div class="subnote">แจ้งโดย {t.get('ReportedBy')}</div>
        </div>
        """, unsafe_allow_html=True)


# =========================================================
# VIEW 3: DASHBOARD หลัก (โค้ดเดิมของคุณ + แท็บตั๋วซ่อมสำหรับ admin)
# =========================================================
def show_dashboard():
    st.title("💻 IT Asset & Repair Dashboard")

    tab_asset, tab_repair = st.tabs(["📦 สินทรัพย์", "🔧 ตั๋วซ่อม (Admin)"])

    # ---------------- TAB 1: สินทรัพย์ (อ่าน/เขียนตรงเข้า Google Sheet) ----------------
    with tab_asset:
        df = load_data()

        search = st.text_input("🔍 ค้นหา Asset / User / Device")

        if df.empty:
            st.warning("ยังไม่มีข้อมูลอุปกรณ์ในชีต หรือเชื่อมต่อ Google Sheets ไม่สำเร็จ")
            df_show = df
        elif search:
            df_show = df[
                df.astype(str)
                .apply(lambda row: row.str.contains(search, case=False, na=False).any(), axis=1)
            ]
        else:
            df_show = df.copy()

        total_asset = len(df)
        notebook_count = df["Device"].astype(str).str.contains("Notebook|Laptop", case=False, na=False).sum() if not df.empty else 0
        computer_count = df["Device"].astype(str).str.contains("Computer|Desktop|PC", case=False, na=False).sum() if not df.empty else 0
        printer_count = df["Device"].astype(str).str.contains("Printer|Brother|Canon|HP|Epson", case=False, na=False).sum() if not df.empty else 0
        repair_count = df["Status"].astype(str).str.contains("Repair", case=False, na=False).sum() if not df.empty else 0

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("📦 สินทรัพย์ทั้งหมด", total_asset)
        with c2:
            st.metric("💻 Notebook", notebook_count)
        with c3:
            st.metric("🖥️ Computer", computer_count)
        with c4:
            st.metric("🖨️ Printer", printer_count)
        with c5:
            st.metric("🔧 Repair", repair_count)

        if not df.empty:
            st.subheader("📊 สรุปข้อมูลอุปกรณ์")
            col1, col2 = st.columns(2)

            with col1:
                status_count = df["Status"].value_counts().reset_index()
                status_count.columns = ["Status", "Count"]
                fig = px.pie(
                    status_count, names="Status", values="Count",
                    title="จำนวนอุปกรณ์ตามสถานะ", hole=0.5, color="Status",
                    color_discrete_map={"Active": "#22c55e", "Repair": "#ef4444", "Spare": "#f59e0b"}
                )
                fig.update_traces(textinfo="label+value")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=450)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                device_department = df.groupby(["Department", "Device"]).size().reset_index(name="Count")
                fig2 = px.bar(
                    device_department, x="Department", y="Count", color="Department",
                    text="Count", barmode="group", title="จำนวนอุปกรณ์แยกตามแผนก",
                    color_discrete_map={
                        "IT": "#3b82f6", "HR": "#ec4899", "Finance": "#f59e0b",
                        "Sales": "#22c55e", "Marketing": "#8b5cf6", "Admin": "#ef4444"
                    }
                )
                fig2.update_traces(textposition="outside")
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white",
                    height=450, xaxis_title="แผนก", yaxis_title="จำนวนอุปกรณ์", legend_title="Department"
                )
                st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📋 รายการทรัพย์สิน")
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        st.caption("ตารางนี้แสดงผลอย่างเดียว การแก้ไข/เพิ่ม/ลบ ให้ใช้ฟอร์มด้านล่าง (บันทึกลง Google Sheet ทันที)")

        # ---------- แก้ไขข้อมูล ----------
        st.subheader("✏️ แก้ไขข้อมูลอุปกรณ์")
        if df.empty:
            st.info("ยังไม่มีอุปกรณ์ให้แก้ไข")
        else:
            asset_list = df["Asset ID"].astype(str).tolist()
            selected_asset = st.selectbox("เลือก Asset ID ที่ต้องการแก้ไข", asset_list, key="edit_select")
            row = df[df["Asset ID"].astype(str) == str(selected_asset)].iloc[0]

            with st.form("edit_form"):
                device_f = st.text_input("Device", value=str(row.get("Device", "")))
                brand_f = st.text_input("Brand", value=str(row.get("Brand", "")))
                user_f = st.text_input("User", value=str(row.get("User", "")))
                department_f = st.text_input("Department", value=str(row.get("Department", "")))
                serial_f = st.text_input("SerialNumber", value=str(row.get("SerialNumber", "")))
                status_options = ["Active", "Spare", "Repair"]
                current_status = str(row.get("Status", "Active"))
                status_index = status_options.index(current_status) if current_status in status_options else 0
                status_f = st.selectbox("Status", status_options, index=status_index)
                submit_edit = st.form_submit_button("💾 บันทึกการแก้ไข", use_container_width=True)

                if submit_edit:
                    with st.spinner("กำลังบันทึกลง Google Sheet..."):
                        sh.update_asset(selected_asset, {
                            "Device": device_f,
                            "Brand": brand_f,
                            "User": user_f,
                            "Department": department_f,
                            "SerialNumber": serial_f,
                            "Status": status_f,
                        })
                    st.cache_data.clear()
                    st.success("✅ แก้ไขข้อมูลเรียบร้อย บันทึกลง Google Sheet แล้ว")
                    st.rerun()

        # ---------- เพิ่มทรัพย์สินใหม่ ----------
        st.subheader("➕ เพิ่มทรัพย์สินใหม่")
        with st.form("add_form"):
            new_asset = st.text_input("Asset ID")
            new_device = st.text_input("Device")
            new_brand = st.text_input("Brand")
            new_user = st.text_input("User")
            new_department = st.text_input("Department")
            new_serial = st.text_input("SerialNumber")
            new_status = st.selectbox("Status", ["Active", "Spare", "Repair"], key="add_status")
            submit = st.form_submit_button("➕ เพิ่มข้อมูล", use_container_width=True)

            if submit:
                existing_ids = df["Asset ID"].astype(str).tolist() if not df.empty else []
                if not new_asset.strip():
                    st.error("กรุณากรอก Asset ID")
                elif new_asset.strip() in existing_ids:
                    st.error(f"Asset ID '{new_asset}' มีอยู่แล้วในระบบ กรุณาใช้รหัสอื่น")
                else:
                    with st.spinner("กำลังบันทึกลง Google Sheet..."):
                        sh.add_asset({
                            "Asset ID": new_asset.strip(),
                            "Device": new_device,
                            "Brand": new_brand,
                            "User": new_user,
                            "Department": new_department,
                            "SerialNumber": new_serial,
                            "Status": new_status,
                        })
                    st.cache_data.clear()
                    st.success("✅ เพิ่มข้อมูลเรียบร้อย บันทึกลง Google Sheet แล้ว")
                    st.rerun()

        # ---------- ลบข้อมูล ----------
        st.subheader("🗑️ ลบข้อมูล")
        if df.empty:
            st.info("ยังไม่มีอุปกรณ์ให้ลบ")
        else:
            delete_asset_id = st.selectbox("เลือก Asset ID ที่ต้องการลบ", df["Asset ID"].astype(str).unique(), key="delete_select")
            confirm_delete = st.checkbox(f"ยืนยันการลบ Asset ID: {delete_asset_id}")
            if st.button("❌ ลบข้อมูล", use_container_width=True, disabled=not confirm_delete):
                with st.spinner("กำลังลบออกจาก Google Sheet..."):
                    sh.delete_asset(delete_asset_id)
                st.cache_data.clear()
                st.success(f"✅ ลบ Asset ID {delete_asset_id} เรียบร้อย")
                st.rerun()

        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 ดาวน์โหลด CSV", csv, "it_asset.csv", "text/csv", use_container_width=True)

        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.05); padding:15px; border-radius:15px; margin-top:10px; border:1px solid rgba(255,255,255,0.1);">
            📊 จำนวนทรัพย์สินทั้งหมด : <b>{len(df)}</b> รายการ
        </div>
        """, unsafe_allow_html=True)

    # ---------------- TAB 2: ตั๋วซ่อม (ใหม่) ----------------
    with tab_repair:
        st.subheader("🔧 ตั๋วแจ้งซ่อมทั้งหมด")

        with st.spinner("กำลังโหลดตั๋วซ่อม..."):
            tickets = sh.get_all_tickets()

        if not tickets:
            st.info("ยังไม่มีตั๋วแจ้งซ่อม")
        else:
            tdf = pd.DataFrame(tickets)

            status_filter = st.multiselect(
                "กรองตามสถานะ",
                options=tdf["Status"].unique().tolist(),
                default=tdf["Status"].unique().tolist()
            )
            tdf_show = tdf[tdf["Status"].isin(status_filter)].sort_values("ReportedAt", ascending=False)
            st.dataframe(tdf_show, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("🔄 อัปเดตสถานะตั๋ว")
            ticket_ids = tdf["Ticket ID"].tolist()
            selected_ticket = st.selectbox("เลือกตั๋ว", ticket_ids)
            new_status = st.selectbox("สถานะใหม่", sh.STATUS_OPTIONS)
            if st.button("💾 บันทึกสถานะ", use_container_width=True):
                with st.spinner("กำลังอัปเดต..."):
                    sh.update_ticket_status(selected_ticket, new_status)
                st.success("✅ อัปเดตสถานะเรียบร้อย")
                st.rerun()


# =========================================================
# ROUTER: อ่าน query param เพื่อเลือกว่าจะแสดงหน้าไหน
# QR code จะลิงก์มาที่ ?view=repair&asset_id=XXX หรือ ?view=history&asset_id=XXX
# ถ้าไม่มี query param เลย จะแสดง dashboard ตามปกติ
# =========================================================
def main():
    qp = st.query_params
    view = qp.get("view", "dashboard")
    asset_id = qp.get("asset_id", None)

    df = load_data()

    if view == "repair":
        show_repair_form(asset_id, df)
    elif view == "history":
        show_repair_history(asset_id, df)
    else:
        show_dashboard()


if __name__ == "__main__":
    main()
