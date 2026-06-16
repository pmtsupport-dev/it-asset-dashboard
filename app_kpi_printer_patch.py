# แก้ไขในไฟล์ app.py ของคุณ

# ค้นหาส่วน KPI เดิม แล้วแทนที่ด้วยโค้ดนี้

total_asset = len(df)

notebook_count = (
    df["Device"]
    .astype(str)
    .str.contains("Notebook|Laptop", case=False, na=False)
    .sum()
)

computer_count = (
    df["Device"]
    .astype(str)
    .str.contains("Computer|Desktop|PC", case=False, na=False)
    .sum()
)

printer_count = (
    df["Device"]
    .astype(str)
    .str.contains("Printer|Brother|Canon|HP", case=False, na=False)
    .sum()
)

repair_count = (
    df["Status"]
    .astype(str)
    .str.contains("Repair", case=False, na=False)
    .sum()
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("📦 Asset", total_asset)
c2.metric("💻 Notebook", notebook_count)
c3.metric("🖥️ Computer", computer_count)
c4.metric("🖨️ Printer", printer_count)
c5.metric("🔧 Repair", repair_count)
