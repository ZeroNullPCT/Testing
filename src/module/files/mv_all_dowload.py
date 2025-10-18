import os
import re
import shutil
from datetime import datetime, timedelta

# Define base directories
downloads_folder = "/home/zeronull/Downloads"
db_vietstock_base = "/home/zeronull/Desktop/Workspace/stock/data/db_vietstock"
db_hsx_en_base = "/home/zeronull/Desktop/Workspace/stock/data/db_hsx/en"
db_hsx_vn_foreign = "/home/zeronull/Desktop/Workspace/stock/data/db_hsx/vn/foreign"
db_hsx_vn_proprietary = "/home/zeronull/Desktop/Workspace/stock/data/db_hsx/vn/proprietary"
db_hsx_vn_summary = "/home/zeronull/Desktop/Workspace/stock/data/db_hsx/vn/summary"

def get_week_start_end(date_str):
    """Calculate the start (Monday) and end (Friday) of the given week's date."""
    file_date = datetime.strptime(date_str, "%Y%m%d")  # Convert YYYYMMDD to date
    weekday = file_date.weekday()  # Get the weekday (Monday=0, Friday=4, Sunday=6)

    # Calculate Monday (start of the week)
    monday = file_date - timedelta(days=weekday)

    # Calculate Friday (end of the week)
    friday = monday + timedelta(days=4)

    # Format MMDDMMDD
    week_range = f"{monday.strftime('%m%d')}{friday.strftime('%m%d')}"
    
    return f"w{monday.isocalendar()[1]:02d}_{week_range}"

def create_week_folder(base_path, date_str):
    """Create a folder for the given week (wXX_MMDDMMDD) inside the specified base path."""
    week_folder_name = get_week_start_end(date_str)
    week_folder_path = os.path.join(base_path, week_folder_name)

    if not os.path.exists(week_folder_path):
        os.makedirs(week_folder_path)
        print(f"Created week folder: {week_folder_path}")

    return week_folder_path

# Process all files in Downloads
for filename in os.listdir(downloads_folder):
    old_filepath = os.path.join(downloads_folder, filename)

    # Handle TradingStatistic XLS files
    match_xls = re.match(
        r"TradingStatistic-(HSX|HNX|UPCoM)-(Foreign|Order|Price|Proprietary|PutForeign)-(\d{4})(\d{2})(\d{2})(?:-2)?-\d{4}\.xls",
        filename
    )

    if match_xls:
        market = match_xls.group(1).lower()
        file_type = match_xls.group(2).lower()
        date_part = match_xls.group(3) + match_xls.group(4) + match_xls.group(5)
        mmdd = match_xls.group(4) + match_xls.group(5)

        category_folder = os.path.join(db_vietstock_base, file_type)
        
        if not os.path.exists(category_folder):
            os.makedirs(category_folder)

        week_folder = create_week_folder(category_folder, date_part)
        
        new_filename = f"{market}_{file_type}_{mmdd}.xls"
        new_filepath = os.path.join(week_folder, new_filename)

        shutil.move(old_filepath, new_filepath)
        print(f"Moved: {filename} → {new_filepath}")
        continue

    # Handle Foreign & Proprietary Trading PDFs
    match_pdf = re.match(r"(\d{8})_.*(Foreign Investors|Proprietary Trading).*\.pdf", filename, re.IGNORECASE)

    if match_pdf:
        date_part = match_pdf.group(1)
        mmdd = date_part[4:8]
        pdf_type = match_pdf.group(2).lower()

        if "foreign" in pdf_type:
            target_folder = os.path.join(db_hsx_en_base, "foreign")
            new_filename = f"foreign_{mmdd}.pdf"
        elif "proprietary" in pdf_type:
            target_folder = os.path.join(db_hsx_en_base, "proprietary")
            new_filename = f"proprietary_{mmdd}.pdf"
        else:
            print(f"Skipping (Unknown PDF Type): {filename}")
            continue

        week_folder = create_week_folder(target_folder, date_part)
        new_filepath = os.path.join(week_folder, new_filename)
        shutil.move(old_filepath, new_filepath)
        print(f"Moved: {filename} → {new_filepath}")
        continue

    # Handle "Thong ke Giao Dich Tu doanh" PDFs → Move to /foreign/
    match_thongke_pdf = re.match(r"(\d{8})_.*Thong ke Giao Dich Tu doanh\.pdf", filename, re.IGNORECASE)

    if match_thongke_pdf:
        date_part = match_thongke_pdf.group(1)
        
        target_folder = db_hsx_vn_foreign
        week_folder = create_week_folder(target_folder, date_part)

        new_filename = f"{date_part}.pdf"
        new_filepath = os.path.join(week_folder, new_filename)

        shutil.move(old_filepath, new_filepath)
        print(f"Moved: {filename} → {new_filepath}")
        continue

    # Handle "ho.pdf" (Proprietary Trading in DDMMYYYY format)
    match_ho_pdf = re.match(r"(\d{8})_(\d{2})(\d{2})(\d{4}) ho\.pdf", filename, re.IGNORECASE)

    if match_ho_pdf:
        date_part = match_ho_pdf.group(1)
        mmdd = match_ho_pdf.group(2) + match_ho_pdf.group(3)

        target_folder = db_hsx_vn_proprietary
        week_folder = create_week_folder(target_folder, date_part)

        new_filename = f"vn_proprietary_{mmdd}.pdf"
        new_filepath = os.path.join(week_folder, new_filename)

        shutil.move(old_filepath, new_filepath)
        print(f"Moved: {filename} → {new_filepath}")
        continue

    # Handle Summary PDFs
    match_summary_pdf = re.match(r"(\d{8})_.*\.pdf", filename)

    if match_summary_pdf:
        date_part = match_summary_pdf.group(1)
        mmdd = date_part[4:8]

        summary_folder = db_hsx_vn_summary
        week_folder = create_week_folder(summary_folder, date_part)

        new_filename = f"summary_{mmdd}.pdf"
        new_filepath = os.path.join(week_folder, new_filename)

        shutil.move(old_filepath, new_filepath)
        print(f"Moved: {filename} → {new_filepath}")
        continue

    print(f"Skipping: {filename} (No matching pattern)")
