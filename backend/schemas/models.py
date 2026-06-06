"""Pydantic response models."""

from typing import Optional
from pydantic import BaseModel


class SessionResponse(BaseModel):
    session_id: str


class UploadStatus(BaseModel):
    roster: bool = False
    attendance: bool = False
    ledger: bool = False
    attendance_count: int = 0


class ConfigUpdate(BaseModel):
    late_tolerance: int = 10
    work_start_time: str = "07:30"
    work_end_time: str = "17:30"
    break_start: str = "12:00"
    break_end: str = "13:00"


class OverviewStats(BaseModel):
    total_people: int = 0
    total_salary: float = 0
    total_workdays: int = 0
    total_overtime: float = 0


class SalaryRecord(BaseModel):
    序号: int = 0
    姓名: str = ""
    工种: str = ""
    出勤工日: int = 0
    日工资: float = 0
    加班工时: float = 0
    加班工资: float = 0
    工资总额: float = 0
    未支付数: float = 0
    备注: str = ""


class DailyRecord(BaseModel):
    日期: int = 0
    姓名: str = ""
    工种: str = ""
    上班打卡时间: Optional[str] = None
    下班打卡时间: Optional[str] = None
    当日工时: float = 0
    基本工时: float = 0
    加班工时: float = 0
    当日基本工资: float = 0
    当日加班工资: float = 0
    当日总工资: float = 0
    备注: str = ""


class SalaryResponse(BaseModel):
    overview: OverviewStats
    records: list[SalaryRecord]
    sheet_name: str = ""


class DailyResponse(BaseModel):
    records: list[DailyRecord]


class CalculateResponse(BaseModel):
    overview: OverviewStats
    sheet_name: str = ""
    abnormal_count: int = 0
