"""Calculate API route - core computation endpoint."""

import asyncio
import os
import sys

from fastapi import APIRouter, Query, HTTPException

from services.session_manager import session_manager
from database import upsert_month, save_calculation
from config import ATTENDANCE_CORE_DIR

router = APIRouter(prefix="/api", tags=["calculate"])


def _run_calculation(session):
    """Synchronous calculation function running in a thread."""
    # Ensure attendance module is importable
    if ATTENDANCE_CORE_DIR not in sys.path:
        sys.path.insert(0, ATTENDANCE_CORE_DIR)

    from attendance_core import (
        parse_xdz_roster,
        parse_attendance,
        process_xdz_data,
        generate_attendance_summary,
        generate_ledger_sheet,
        generate_report_format,
        get_attendance_date_range,
        format_date_range_sheet_name,
    )

    output_dir = session.temp_dir
    project_id = getattr(session, "project_id", 1)

    # 1. Parse roster
    roster_dict = parse_xdz_roster(session.roster_path)

    # 2. Parse attendance
    attendance_df = parse_attendance(session.attendance_paths)

    # 3. Get date range
    start_date, end_date = get_attendance_date_range(session.attendance_paths)
    if not start_date or not end_date:
        raise ValueError("无法从考勤文件中读取日期范围")

    sheet_name = format_date_range_sheet_name(start_date, end_date)

    # 4. Process data
    salary_df, daily_df = process_xdz_data(attendance_df, roster_dict)

    # 5. Generate output files
    # A. Attendance summary
    att_summary_path = os.path.join(output_dir, "考勤记录汇总.xlsx")
    generate_attendance_summary(daily_df, att_summary_path)

    # B. Ledger sheet
    import shutil
    ledger_output_path = os.path.join(output_dir, "工资台账2026（超）.xlsx")
    shutil.copy2(session.ledger_path, ledger_output_path)
    generate_ledger_sheet(
        ledger_path=ledger_output_path,
        output_path=ledger_output_path,
        salary_df=salary_df,
        sheet_name=sheet_name,
        start_date=start_date,
        end_date=end_date,
    )

    # C. Report
    sy, sm, sd = start_date
    ey, em, ed = end_date
    report_path = os.path.join(output_dir, f"上报三表{ey}.xlsx")
    generate_report_format(
        daily_df=daily_df,
        roster_path=session.roster_path,
        output_path=report_path,
        attendance_paths=session.attendance_paths,
    )

    # Convert DataFrames to JSON-safe dicts
    import numpy as np

    def _safe(val):
        if isinstance(val, float) and (np.isnan(val) if isinstance(val, float) else False):
            return None
        return val

    def _df_to_records(df):
        result = []
        for _, row in df.iterrows():
            record = {}
            for col in df.columns:
                val = row[col]
                if val is None:
                    record[col] = None
                elif hasattr(val, "item"):  # numpy scalar
                    record[col] = val.item()
                elif isinstance(val, float) and np.isnan(val):
                    record[col] = None
                elif hasattr(val, "strftime"):  # datetime.time
                    record[col] = val.strftime("%H:%M")
                else:
                    record[col] = val
            result.append(record)
        return result

    salary_records = _df_to_records(salary_df)
    daily_records = _df_to_records(daily_df)

    # Overview stats
    overview = {
        "total_people": len(salary_df),
        "total_salary": float(salary_df["工资总额"].sum()),
        "total_workdays": int(salary_df["出勤工日"].sum()),
        "total_overtime": round(float(salary_df["加班工时"].sum()), 1),
    }

    abnormal_count = len(salary_df[salary_df["备注"] != ""])

    # Store in session
    session.salary_records = salary_records
    session.daily_records = daily_records
    session.overview = overview
    session.sheet_name = sheet_name
    session.abnormal_count = abnormal_count
    session.att_summary_path = att_summary_path
    session.ledger_output_path = ledger_output_path
    session.report_path = report_path

    # Persist to SQLite
    sy, sm, _ = start_date

    # 1) Monthly summary
    upsert_month(
        project_id=project_id,
        year=sy,
        month=sm,
        sheet_name=sheet_name,
        people=overview["total_people"],
        total_salary=overview["total_salary"],
        total_workdays=overview["total_workdays"],
        total_overtime=overview["total_overtime"],
    )

    # 2) Full calculation results (salary + daily JSON)
    save_calculation(
        project_id=project_id,
        year=sy,
        month=sm,
        sheet_name=sheet_name,
        salary_records=salary_records,
        daily_records=daily_records,
        overview=overview,
        abnormal_count=abnormal_count,
        output_paths={
            "att_summary": att_summary_path,
            "ledger": ledger_output_path,
            "report": report_path,
        },
    )

    return {
        "overview": overview,
        "sheet_name": sheet_name,
        "abnormal_count": abnormal_count,
    }


@router.post("/calculate")
async def calculate(session_id: str = Query(...)):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")

    if not session.roster_path:
        raise HTTPException(400, "请先上传花名册")
    if not session.attendance_paths:
        raise HTTPException(400, "请先上传考勤记录")
    if not session.ledger_path:
        raise HTTPException(400, "请先上传工资台账")

    try:
        result = await asyncio.to_thread(_run_calculation, session)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"计算出错: {str(e)}")
