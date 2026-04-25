export interface SalaryRecord {
  序号: number
  姓名: string
  工种: string
  出勤工日: number
  日工资: number
  加班工时: number
  加班工资: number
  工资总额: number
  未支付数: number
  备注: string
}

export interface DailyRecord {
  日期: number
  姓名: string
  工种: string
  上班打卡时间: string | null
  下班打卡时间: string | null
  当日工时: number
  基本工时: number
  加班工时: number
  当日基本工资: number
  当日加班工资: number
  当日总工资: number
  备注: string
}

export interface OverviewStats {
  total_people: number
  total_salary: number
  total_workdays: number
  total_overtime: number
}

export interface UploadStatus {
  roster: boolean
  attendance: boolean
  ledger: boolean
  attendance_count: number
}

export interface SalaryResponse {
  overview: OverviewStats
  records: SalaryRecord[]
  sheet_name: string
}

export interface DailyResponse {
  records: DailyRecord[]
}

export interface CalculateResponse {
  overview: OverviewStats
  sheet_name: string
  abnormal_count: number
}
