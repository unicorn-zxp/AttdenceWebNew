"""
工地考勤工资自动计算系统 - Streamlit前端
适配创新智成-西安东站项目
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import sys
import tempfile
import os

# 导入核心计算模块
from attendance_core import (
    parse_xdz_roster,
    parse_attendance,
    process_xdz_data,
    generate_attendance_summary,
    generate_ledger_sheet,
    generate_report_format,
    get_attendance_date_range,
    format_date_range_sheet_name,
    DEFAULT_LATE_TOLERANCE,
    DEFAULT_WORK_START,
    DEFAULT_WORK_END,
    DEFAULT_BREAK_START,
    DEFAULT_BREAK_END,
    compute_rated_hours,
)


# ============================================================
# 主计算函数
# ============================================================

def run_calculation(
    roster_path: str,
    attendance_paths: list,
    ledger_path: str,
    output_dir: str,
    work_start=None,
    work_end=None,
    break_start=None,
    break_end=None,
    late_tolerance=None,
):
    """执行考勤工资计算，返回三个输出文件路径"""
    # 1. 解析花名册
    roster_dict = parse_xdz_roster(roster_path)

    # 2. 解析刷卡记录
    attendance_df = parse_attendance(attendance_paths)

    # 3. 获取日期范围
    start_date, end_date = get_attendance_date_range(attendance_paths)
    if not start_date or not end_date:
        raise ValueError("无法从考勤文件中读取日期范围")

    sheet_name = format_date_range_sheet_name(start_date, end_date)

    # 4. 计算工时和工资
    from datetime import time as dt_time
    kwargs = {}
    if work_start: kwargs['work_start'] = work_start
    if work_end: kwargs['work_end'] = work_end
    if break_start: kwargs['break_start'] = break_start
    if break_end: kwargs['break_end'] = break_end
    if late_tolerance: kwargs['late_tolerance'] = late_tolerance
    salary_df, daily_df = process_xdz_data(attendance_df, roster_dict, **kwargs)

    # 5. 生成三个输出文件
    # A. 考勤记录汇总
    att_summary_path = os.path.join(output_dir, '考勤记录汇总.xlsx')
    generate_attendance_summary(daily_df, att_summary_path)

    # B. 工资台账更新（新增Sheet）
    ledger_output_path = os.path.join(output_dir, '工资台账2026（超）.xlsx')
    # 复制原台账文件
    import shutil
    shutil.copy2(ledger_path, ledger_output_path)
    generate_ledger_sheet(
        ledger_path=ledger_output_path,
        output_path=ledger_output_path,
        salary_df=salary_df,
        sheet_name=sheet_name,
        start_date=start_date,
        end_date=end_date,
    )

    # C. 上报表
    sy, sm, sd = start_date
    ey, em, ed = end_date
    report_path = os.path.join(output_dir, f'上报三表{ey}.xlsx')
    generate_report_format(
        daily_df=daily_df,
        roster_path=roster_path,
        output_path=report_path,
        attendance_paths=attendance_paths,
    )

    return salary_df, daily_df, roster_dict, att_summary_path, ledger_output_path, report_path, sheet_name


# ============================================================
# 页面配置
# ============================================================

st.set_page_config(
    page_title="工地考勤工资自动计算系统",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 侧边栏 - 文件上传
# ============================================================

st.sidebar.title("📁 数据上传")

# 花名册上传
roster_file = st.sidebar.file_uploader(
    "1. 劳务人员花名册 (xlsx)",
    type=['xlsx'],
    help='创新智成-西安东站花名册，需包含"班组花名册"sheet'
)

# 刷卡记录上传（支持多文件）
attendance_files = st.sidebar.file_uploader(
    "2. 员工刷卡记录表 (xls/xlsx，可多选)",
    type=['xls', 'xlsx'],
    accept_multiple_files=True,
    help="可选择多个文件"
)

# 台账模板上传
ledger_file = st.sidebar.file_uploader(
    "3. 工资台账 (xlsx)",
    type=['xlsx'],
    help="现有的工资台账文件，系统将在此基础上新增Sheet"
)

# 容差配置
st.sidebar.markdown("### ⚙️ 计算配置")

work_start_str = st.sidebar.text_input("上班时间", value=DEFAULT_WORK_START.strftime("%H:%M"))
work_end_str = st.sidebar.text_input("下班时间", value=DEFAULT_WORK_END.strftime("%H:%M"))
break_start_str = st.sidebar.text_input("休息开始", value=DEFAULT_BREAK_START.strftime("%H:%M"))
break_end_str = st.sidebar.text_input("休息结束", value=DEFAULT_BREAK_END.strftime("%H:%M"))

late_tolerance = st.sidebar.slider(
    "晚班弹性补齐容差（分钟）",
    min_value=1,
    max_value=15,
    value=DEFAULT_LATE_TOLERANCE,
    help="距整点/半点≤此分钟数则补齐"
)

def _parse_time_str(s: str):
    parts = s.strip().split(":")
    from datetime import time as dt_time
    return dt_time(int(parts[0]), int(parts[1]))

work_start_cfg = _parse_time_str(work_start_str)
work_end_cfg = _parse_time_str(work_end_str)
break_start_cfg = _parse_time_str(break_start_str)
break_end_cfg = _parse_time_str(break_end_str)
rated_h = compute_rated_hours(work_start_cfg, work_end_cfg, break_start_cfg, break_end_cfg)

st.sidebar.markdown(f"""
**当前规则**：
- 额定工时: {rated_h} 小时
- 早班进位: ≤ 上班时间+10分钟 按 {work_start_str} 计
- 晚班补齐: 距整点/半点 ≤ {late_tolerance}分钟 则补齐
- 工时取整: 按半小时向下取整
- 加班分界: {work_end_str} 后算加班
""")


# ============================================================
# 主页面
# ============================================================

st.markdown('<h1 class="main-title">🏗️ 工地考勤工资自动计算系统</h1>', unsafe_allow_html=True)


# ============================================================
# 检查文件是否完整
# ============================================================

if not roster_file or not attendance_files or not ledger_file:
    st.info("👈 请在侧边栏上传所需文件")

    with st.expander("📖 使用说明", expanded=True):
        st.markdown("""
        ### 数据文件要求

        1. **劳务人员花名册** (.xlsx)
           - 需包含「创新智成 (班组花名册)」sheet
           - 含个人工资标准：工日工资、工时工资

        2. **员工刷卡记录表** (.xls/.xlsx)
           - 可选择多个文件
           - 自动识别并合并打卡数据

        3. **工资台账** (.xlsx)
           - 现有工资台账文件
           - 系统将自动新增一个工资发放表Sheet

        ### 计算规则
        - **排除工种**: 管理、安全员、资料员、技术员、安全、资料、材料、分包老板
        - **异常判定**: 每日仅有一次打卡视为异常，不计入报表
        - **早班进位**: 打卡时间 ≤ 上班时间+10分钟，按上班时间计算；早到不算工时
        - **晚班补齐**: 距整点/半点 ≤ {late_tolerance}分钟则补齐（可配置）
        - **工时取整**: 按半小时向下取整（如 7.25h → 7.0h, 7.5h → 7.5h）
        - **额定工时**: 根据上下班时间和休息时间自动推导
        - **工资公式**: 额定内按 (日工资+时薪)/额定工时 × 实际工时，超出部分按时薪计算

        ### 异常处理
        - 考勤有但花名册无此人的 → 保留考勤记录，不计算工资，备注说明
        - 花名册中无工资标准的 → 保留考勤记录，不计算工资，备注说明
        """.format(late_tolerance=late_tolerance))

    st.stop()


# ============================================================
# 计算按钮
# ============================================================

st.sidebar.markdown("---")

if st.sidebar.button("🚀 开始计算", type="primary", width='stretch', key="btn_calculate"):
    with st.spinner("正在处理数据..."):
        try:
            temp_dir = tempfile.mkdtemp()

            # 保存花名册
            roster_path = os.path.join(temp_dir, "roster.xlsx")
            with open(roster_path, 'wb') as f:
                f.write(roster_file.read())

            # 保存刷卡记录
            attendance_paths = []
            for i, af in enumerate(attendance_files):
                ext = 'xlsx' if af.name.endswith('.xlsx') else 'xls'
                path = os.path.join(temp_dir, f"员工刷卡记录表{i+1}.{ext}")
                with open(path, 'wb') as f:
                    f.write(af.read())
                attendance_paths.append(path)

            # 保存台账
            ledger_path = os.path.join(temp_dir, "工资台账.xlsx")
            with open(ledger_path, 'wb') as f:
                f.write(ledger_file.read())

            # 执行计算
            (salary_df, daily_df, roster_dict,
             att_summary_path, ledger_output_path, report_path,
             sheet_name) = run_calculation(
                roster_path=roster_path,
                attendance_paths=attendance_paths,
                ledger_path=ledger_path,
                output_dir=temp_dir,
                work_start=work_start_cfg,
                work_end=work_end_cfg,
                break_start=break_start_cfg,
                break_end=break_end_cfg,
                late_tolerance=late_tolerance,
            )

            # 保存到session
            st.session_state.salary_df = salary_df
            st.session_state.daily_df = daily_df
            st.session_state.roster_dict = roster_dict
            st.session_state.att_summary_path = att_summary_path
            st.session_state.ledger_output_path = ledger_output_path
            st.session_state.report_path = report_path
            st.session_state.sheet_name = sheet_name
            st.session_state.calculated = True
            st.session_state.temp_dir = temp_dir

            st.success("✅ 计算完成！")
            st.rerun()

        except Exception as e:
            st.error(f"❌ 计算出错: {str(e)}")
            st.exception(e)


# ============================================================
# 显示结果
# ============================================================

if st.session_state.get('calculated', False):
    if st.sidebar.button("🔄 重置", width='stretch', key="btn_reset"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.sidebar.markdown("---")

    salary_df = st.session_state.salary_df
    daily_df = st.session_state.daily_df
    roster_dict = st.session_state.roster_dict
    sheet_name = st.session_state.sheet_name

    # ==================== 异常人员提示 ====================
    st.subheader("⚠️ 异常人员提示")

    no_wage = salary_df[salary_df['备注'] != '']
    if not no_wage.empty:
        with st.expander(f"共 {len(no_wage)} 人存在异常（点击展开）", expanded=False):
            st.dataframe(
                no_wage[['序号', '姓名', '工种', '出勤工日', '加班工时', '备注']],
                width='stretch',
                hide_index=True,
            )
    else:
        st.success("所有人员均有工资标准，无异常")

    # ==================== 概览统计 ====================
    st.subheader("📊 概览统计")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("结算人数", len(salary_df))

    with col2:
        wage_total = salary_df['工资总额'].sum()
        st.metric("工资总额", f"¥{wage_total:,.2f}")

    with col3:
        st.metric("总出勤工日", int(salary_df['出勤工日'].sum()))

    with col4:
        st.metric("总加班工时", round(salary_df['加班工时'].sum(), 1))

    # ==================== 工种分布 ====================
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("👥 工种人数分布")
        job_count = salary_df['工种'].value_counts().reset_index()
        job_count.columns = ['工种', '人数']

        fig_pie = px.pie(
            job_count,
            values='人数',
            names='工种',
            title='工种人数占比',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_layout(height=300)
        st.plotly_chart(fig_pie, width='stretch')

    with col_right:
        st.subheader("💰 工种工资总额")
        job_salary = salary_df.groupby('工种')['工资总额'].sum().reset_index().sort_values('工资总额', ascending=False)

        fig_bar = px.bar(
            job_salary,
            x='工资总额',
            y='工种',
            orientation='h',
            title='各工种工资总额',
            color='工资总额',
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(height=300, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bar, width='stretch')

    # ==================== 工资汇总表 ====================
    st.subheader("📋 工资汇总表")

    search_name = st.text_input("🔍 搜索员工姓名", "", key="search_name_summary")

    if search_name:
        display_df = salary_df[salary_df['姓名'].str.contains(search_name, na=False)]
    else:
        display_df = salary_df

    st.dataframe(
        display_df,
        width='stretch',
        hide_index=True,
        column_config={
            '序号': st.column_config.NumberColumn(width='small'),
            '姓名': st.column_config.TextColumn(width='small'),
            '工种': st.column_config.TextColumn(width='small'),
            '出勤工日': st.column_config.NumberColumn(width='small'),
            '日工资': st.column_config.NumberColumn(format='¥%.0f', width='medium'),
            '加班工时': st.column_config.NumberColumn(width='small'),
            '加班工资': st.column_config.NumberColumn(format='¥%.0f', width='medium'),
            '工资总额': st.column_config.NumberColumn(format='¥%.2f', width='medium'),
            '备注': st.column_config.TextColumn(width='large'),
        }
    )

    # ==================== 每日考勤明细 ====================
    st.subheader("📅 每日考勤明细")

    tab1, tab2, tab3 = st.tabs(["全部记录", "搜索员工", "异常记录"])

    with tab1:
        st.dataframe(
            daily_df.head(500),
            width='stretch',
            hide_index=True,
            column_config={
                '日期': st.column_config.NumberColumn(width='small'),
                '姓名': st.column_config.TextColumn(width='small'),
                '工种': st.column_config.TextColumn(width='small'),
                '上班打卡时间': st.column_config.TextColumn(width='small'),
                '下班打卡时间': st.column_config.TextColumn(width='small'),
                '当日工时': st.column_config.NumberColumn(width='small'),
                '基本工时': st.column_config.NumberColumn(width='small'),
                '加班工时': st.column_config.NumberColumn(width='small'),
                '当日总工资': st.column_config.NumberColumn(format='¥%.2f', width='medium'),
                '备注': st.column_config.TextColumn(width='large'),
            }
        )

    with tab2:
        search_name_daily = st.text_input("🔍 搜索员工姓名", "", key="search_name_daily")
        if search_name_daily:
            daily_search = daily_df[daily_df['姓名'].str.contains(search_name_daily, na=False)]
            st.dataframe(daily_search, width='stretch', hide_index=True)

    with tab3:
        abnormal_df = daily_df[daily_df['备注'].notna() & (daily_df['备注'] != '')]
        st.write(f"📌 共 {len(abnormal_df)} 条异常记录")
        st.dataframe(
            abnormal_df,
            width='stretch',
            hide_index=True,
            column_config={
                '日期': st.column_config.NumberColumn(width='small'),
                '姓名': st.column_config.TextColumn(width='small'),
                '工种': st.column_config.TextColumn(width='small'),
                '当日工时': st.column_config.NumberColumn(width='small'),
                '当日总工资': st.column_config.NumberColumn(format='¥%.2f', width='medium'),
                '备注': st.column_config.TextColumn(width='extra large'),
            }
        )

    # ==================== 下载按钮 ====================
    st.markdown("---")
    st.subheader("📥 下载结果")

    col1, col2, col3 = st.columns(3)

    with col1:
        with open(st.session_state.att_summary_path, 'rb') as f:
            st.download_button(
                label="📋 考勤记录汇总",
                data=f,
                file_name="考勤记录汇总.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                width='stretch',
            )

    with col2:
        with open(st.session_state.ledger_output_path, 'rb') as f:
            st.download_button(
                label="📊 工资台账（含新增Sheet）",
                data=f,
                file_name=f"工资台账2026（超）.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                width='stretch',
            )

    with col3:
        with open(st.session_state.report_path, 'rb') as f:
            st.download_button(
                label="📄 上报表",
                data=f,
                file_name=os.path.basename(st.session_state.report_path),
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                width='stretch',
            )

    # 显示新增的Sheet名
    st.info(f"💡 工资台账已新增Sheet: **{sheet_name}**")
