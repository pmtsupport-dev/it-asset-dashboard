"""
sheets_helper.py
โมดูลสำหรับเขียน/อ่านข้อมูล "ตั๋วแจ้งซ่อม" กลับเข้า Google Sheet เดิม
(แท็บใหม่ชื่อ RepairTickets จะถูกสร้างอัตโนมัติในครั้งแรกที่ใช้งาน)

ต้องตั้งค่า Service Account ก่อนใช้งาน — ดูขั้นตอนใน SETUP.md
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import uuid

# ต้องตรงกับ Google Sheet ที่ dashboard ใช้อยู่
SHEET_ID = "19t2bqMYMBi_nmHJlZbSCHILG8-mDqssb-v3rTpUI2gY"
REPAIR_SHEET_NAME = "RepairTickets"

REPAIR_HEADERS = [
    "Ticket ID", "Asset ID", "Device", "Brand", "User",
    "Department", "Problem", "ReportedBy", "ReportedAt", "Status"
]

ASSET_STATUS_OPTIONS = ["Active", "Spare", "Repair"]

STATUS_OPTIONS = ["รอดำเนินการ", "กำลังซ่อม", "เสร็จแล้ว"]


@st.cache_resource
def get_client():
    """สร้าง gspread client จาก Service Account ที่เก็บใน st.secrets"""
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    return gspread.authorize(creds)


def get_repair_worksheet():
    """คืนค่า worksheet RepairTickets — สร้างใหม่พร้อม header ถ้ายังไม่มี"""
    client = get_client()
    sh = client.open_by_key(SHEET_ID)
    try:
        ws = sh.worksheet(REPAIR_SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(
            title=REPAIR_SHEET_NAME, rows=2000, cols=len(REPAIR_HEADERS)
        )
        ws.append_row(REPAIR_HEADERS)
    return ws


def add_repair_ticket(asset_id, device, brand, user, department, problem, reported_by):
    """เพิ่มตั๋วแจ้งซ่อมใหม่ 1 แถว คืนค่า ticket_id ที่สร้าง"""
    ws = get_repair_worksheet()
    ticket_id = f"TCK-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
    row = [
        ticket_id,
        str(asset_id),
        str(device),
        str(brand),
        str(user),
        str(department),
        str(problem),
        str(reported_by),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        STATUS_OPTIONS[0],
    ]
    ws.append_row(row)
    return ticket_id


def get_all_tickets():
    """คืนค่าตั๋วแจ้งซ่อมทั้งหมด เป็น list ของ dict"""
    ws = get_repair_worksheet()
    return ws.get_all_records()


def get_tickets_by_asset(asset_id):
    """คืนค่าตั๋วแจ้งซ่อมของอุปกรณ์เครื่องเดียว"""
    records = get_all_tickets()
    return [r for r in records if str(r.get("Asset ID", "")).strip() == str(asset_id).strip()]


def update_ticket_status(ticket_id, new_status):
    """อัปเดตสถานะของตั๋ว ระบุด้วย Ticket ID"""
    ws = get_repair_worksheet()
    values = ws.get_all_values()
    headers = values[0]
    id_col = headers.index("Ticket ID")
    status_col = headers.index("Status")

    for i, row in enumerate(values[1:], start=2):  # แถวที่ 1 = header
        if row[id_col] == ticket_id:
            ws.update_cell(i, status_col + 1, new_status)
            return True
    return False


# =========================================================
# ASSET SHEET — รายการอุปกรณ์ (แผ่นแรกสุดของไฟล์ Google Sheet)
# =========================================================

def get_asset_worksheet():
    """
    คืนค่า worksheet ของรายการอุปกรณ์ (แผ่นแรกสุด/index 0 ของไฟล์)
    สมมติว่าเป็นแผ่นเดิมที่ dashboard ใช้อยู่แต่แรก (สร้างก่อนแผ่น RepairTickets)
    """
    client = get_client()
    workbook = client.open_by_key(SHEET_ID)
    return workbook.get_worksheet(0)


def get_all_assets():
    """คืนค่ารายการอุปกรณ์ทั้งหมด เป็น list ของ dict"""
    ws = get_asset_worksheet()
    return ws.get_all_records()


def add_asset(new_asset: dict):
    """
    เพิ่มอุปกรณ์ใหม่ 1 แถว
    new_asset: dict เช่น {"Asset ID": "IT-0050", "Device": "Notebook", ...}
    ลำดับคอลัมน์จะเรียงตาม header แถวแรกของชีตจริง (ไม่ต้องตรงกับ dict)
    """
    ws = get_asset_worksheet()
    headers = ws.row_values(1)
    row = [str(new_asset.get(h, "")) for h in headers]
    ws.append_row(row)


def update_asset(asset_id, updated_fields: dict):
    """
    แก้ไขข้อมูลอุปกรณ์ที่มีอยู่ ระบุด้วย Asset ID (แก้ไขได้เฉพาะฟิลด์ใน updated_fields)
    คืนค่า True ถ้าเจอและแก้ไขสำเร็จ, False ถ้าไม่เจอ Asset ID นี้
    """
    ws = get_asset_worksheet()
    values = ws.get_all_values()
    headers = values[0]
    id_col = headers.index("Asset ID")

    for i, row in enumerate(values[1:], start=2):
        if row[id_col] == str(asset_id):
            new_row = row.copy()
            for key, val in updated_fields.items():
                if key in headers:
                    new_row[headers.index(key)] = str(val)
            ws.update(f"A{i}", [new_row])
            return True
    return False


def delete_asset(asset_id):
    """ลบอุปกรณ์ 1 แถว ระบุด้วย Asset ID — คืนค่า True ถ้าเจอและลบสำเร็จ"""
    ws = get_asset_worksheet()
    values = ws.get_all_values()
    headers = values[0]
    id_col = headers.index("Asset ID")

    for i, row in enumerate(values[1:], start=2):
        if row[id_col] == str(asset_id):
            ws.delete_rows(i)
            return True
    return False
