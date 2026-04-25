# 工地考勤工资自动计算系统

创新智成-西安东站项目，工地考勤数据处理与工资自动计算。

---

## 架构概览

```
                    ┌──────────────┐
                    │   浏览器      │
                    └──────┬───────┘
                           │ :8080
                    ┌──────▼───────┐
                    │    Nginx     │  静态文件 + 反向代理
                    │   :8080      │
                    └──┬───────┬───┘
               静态文件  │       │ /api/*
                   ┌────▼───┐   │
                   │ Vue 3  │   │  项目选择器 + 数据看板/考勤计算双Tab
                   │ 前端SPA│   │
                   └────────┘   │
                           ┌────▼─────┐
                           │ FastAPI  │  计算API + 项目管理
                           │ :8000    │
                           └──┬───┬───┘
                              │   │
               ┌──────────────┘   └──────────────┐
               │ volume :ro                       │
          ┌────▼─────┐                     ┌──────▼──────┐
          │attendance│  核心计算模块(零修改)  │  SQLite DB  │  按项目隔离持久化
          │_core.py  │                     │  data/      │  (月度汇总+完整计算结果)
          └──────────┘                     └─────────────┘

独立服务:
                    ┌──────────────┐
                    │  Streamlit   │  备用界面(旧版)
                    │   :8501      │
                    └──────────────┘
```

---

## 目录结构

```
Abay/
├── docker-compose.yml           # 容器编排（3个服务）
├── README.md
│
├── attendance/                  # 核心计算模块 + Streamlit 备用前端
│   ├── Dockerfile               # python:3.12-slim，pip install
│   ├── requirements.txt         # streamlit, pandas, openpyxl, xlrd, plotly
│   ├── .dockerignore
│   ├── attendance_core.py       # ★ 核心计算逻辑（所有前端共用，零修改）
│   ├── app.py                   # Streamlit 前端（备用）
│   ├── generate_report.py       # 独立报表生成脚本
│   ├── start.sh                 # streamlit run app.py --server.port 8501
│   ├── mock_data/               # 测试数据
│   │   ├── 创新智成-西安东站-花名册-2026.4.xlsx
│   │   ├── 员工刷卡记录表*.xls
│   │   └── 工资台账2026（超）.xlsx
│   └── file/                    # 历史输出文件
│
├── backend/                     # FastAPI 后端 API
│   ├── Dockerfile               # python:3.12-slim
│   ├── requirements.txt         # fastapi, uvicorn, python-multipart, pandas, openpyxl, xlrd, numpy
│   ├── .dockerignore
│   ├── main.py                  # FastAPI 入口，CORS，生命周期，项目管理 + 年度汇总端点
│   ├── config.py                # 端口/会话过期/上传限制等常量
│   ├── database.py              # ★ SQLite 持久化：项目CRUD/月度汇总/完整计算结果/种子导入
│   ├── routers/
│   │   ├── upload.py            # 文件上传端点（台账上传时按项目 seed 历史月份）
│   │   ├── calculate.py         # 触发核心计算（计算后写入 DB 月度汇总 + 完整结果）
│   │   ├── results.py           # 查询计算结果 + 历史结果从 DB 加载
│   │   └── download.py          # 下载 Excel 文件
│   ├── services/
│   │   └── session_manager.py   # 内存会话管理，UUID，自动过期清理，绑定 project_id
│   ├── schemas/
│   │   └── models.py            # Pydantic 响应模型
│   └── data/                    # ★ SQLite 数据库文件目录（运行时生成）
│       └── attendance.db
│
├── frontend/                    # Vue 3 前端
│   ├── package.json
│   ├── vite.config.ts           # @ 别名 + dev proxy /api → :8000
│   ├── index.html
│   └── src/
│       ├── main.ts              # 入口：注册 ElementPlus + Pinia + 导入全局样式
│       ├── App.vue              # 主布局：顶部栏(项目选择+双Tab) + 可折叠深色侧边栏 + 内容区
│       ├── api/
│       │   └── client.ts        # Axios 实例，自动附加 session_id + project_id
│       ├── styles/
│       │   ├── variables.css    # ★ CSS 设计令牌（配色/间距/阴影/圆角/过渡/布局尺寸）
│       │   └── global.css       # ★ 全局样式（字体/动画/Element Plus 微调/响应式断点）
│       ├── stores/
│       │   └── attendance.ts    # Pinia 状态管理（项目CRUD/全生命周期/年度汇总按项目拉取）
│       ├── types/
│       │   └── index.ts         # TypeScript 接口定义（含 AnnualMonth, Project）
│       └── components/
│           ├── DashboardView.vue     # ★ 数据看板：年度工资总览（KPI+柱状图+月度表）
│           ├── FileUploadPanel.vue   # 3个上传项（步骤编号圆圈 + 深色适配）
│           ├── ConfigPanel.vue       # 晚班容差滑块（深色适配 + 放大数值显示）
│           ├── AlertBanner.vue       # 异常告警（左边框彩色卡片 + 折叠展开）
│           ├── OverviewCards.vue     # 4色 KPI 统计卡片
│           ├── JobCharts.vue         # 水平柱状图（工种人数 + 工种工资）
│           ├── SalaryTable.vue       # 工资汇总表（搜索/排序/分页/高亮）
│           ├── DailyAttendance.vue   # 每日考勤明细（Tab+Badge/搜索/分页/共享列定义）
│           ├── DownloadPanel.vue     # 3个下载卡片
│           └── YearSummaryChart.vue  # (保留) 年度工资汇总组件
│
└── nginx/                       # Nginx 反向代理
    ├── Dockerfile               # 多阶段：node构建前端 + nginx服务
    └── nginx.conf               # SPA fallback + /api/ proxy + gzip
```

---

## Docker 服务

### 服务与 Profile

所有服务都通过 Docker Compose Profile 隔离，默认不启动任何服务。

| 服务 | Profile | 镜像 | 端口 | 用途 |
|------|---------|------|------|------|
| `backend` | `web` | `./backend` | 8000 | FastAPI API 服务 |
| `nginx` | `web` | `nginx/Dockerfile` | 8080 | **主入口**：Vue 前端 + API 反代 |
| `yt-worker` | `old` | `./attendance` | 8501 | Streamlit 备用（旧版） |

### Volume 挂载

```
yt-worker:  ./attendance → /app                        # Streamlit 代码
backend:    ./backend    → /app                        # API 代码（热更新）
            ./attendance → /app/attendance:ro           # 核心模块只读挂载
            # SQLite DB 文件位于 backend/data/，随代码目录自动持久化
nginx:      无（构建时内嵌前端静态文件）
```

### 启动命令

```bash
# 构建镜像
docker compose build backend nginx          # 只构建新前端（推荐）
docker compose --profile old build          # 只构建 Streamlit
docker compose --profile web --profile old build  # 构建全部

# 启动新前端（backend + nginx） → http://localhost:8080
docker compose --profile web up -d

# 启动 Streamlit 备用 → http://localhost:8501
docker compose --profile old up -d

# 启动全部3个服务
docker compose --profile web --profile old up -d

# 停止服务
docker compose --profile web down
docker compose --profile old down
docker compose --profile web --profile old down

# 查看日志
docker compose logs -f backend
docker compose logs -f nginx
```

---

## 核心计算模块 attendance_core.py

**这是整个系统的核心**，被 Streamlit 和 FastAPI 共同调用，**零修改约束**。

### 常量

```python
EXCLUDED_JOB_TYPES = {'管理', '安全员', '资料员', '技术员', '安全', '资料', '材料', '分包老板'}
DEFAULT_LATE_TOLERANCE = 10          # 晚班弹性补齐容差(分钟)
DEFAULT_OVERTIME_CUTOVER = time(16, 30)  # 加班分界时间
```

### 函数签名与数据流

```
                              输入文件
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
          ▼                     ▼                     ▼
   花名册.xlsx           考勤文件*.xls           工资台账.xlsx
          │                     │                     │
          ▼                     ▼                     │
  parse_xdz_roster()    parse_attendance()            │
  (file_path)           (file_paths)                  │
          │                     │                     │
          ▼                     ▼                     │
  Dict[str, dict]        DataFrame                   │
  {姓名: {               [姓名,工号,                  │
    工种,                  部门,日期,                  │
    工日工资,              打卡时间]                   │
    工时工资,                  │                       │
    备注,                     │                       │
    性别,身份证,              │                       │
    电话,地址,                │                       │
    合同编号                  │                       │
  }}                         │                       │
          │                   │                       │
          │         get_attendance_date_range()       │
          │         (file_paths)                      │
          │                → ((年,月,日),(年,月,日))  │
          │                   │                       │
          │         format_date_range_sheet_name()    │
          │                → "3月11日-4月10日工资表"   │
          │                   │                       │
          └───────┬───────────┘                       │
                  ▼                                   │
         process_xdz_data()                           │
         (attendance_df, roster_dict)                  │
                  │                                   │
          ┌───────┴───────┐                           │
          ▼               ▼                           │
    salary_df        daily_df                         │
    (工资汇总)       (每日明细)                        │
          │               │                           │
          ▼               ▼                           │
  ┌─────────────┐ ┌───────────────┐ ┌──────────────┐ │
  │ generate_   │ │ generate_     │ │ generate_    │ │
  │ attendance_ │ │ ledger_sheet()│ │ report_      │ │
  │ summary()   │ │               │ │ format()     │ │
  └──────┬──────┘ └──────┬────────┘ └──────┬───────┘ │
         ▼               ▼                  ▼         │
  考勤记录汇总.xlsx  工资台账(新Sheet)  上报表.xlsx  ◄─┘
  (单sheet)         (含年度汇总回写)   (花名册+考勤表)
```

### 函数详细说明

#### `parse_xdz_roster(file_path: str) -> Dict[str, dict]`

解析花名册 Excel，读取含"班组花名册"的 sheet。

- 读取起始行：第3行
- 列映射：C=姓名, D=身份证号, E=性别, F=工种, G=电话, H=地址, I=工日工资, J=工时工资, P=合同编号
- 特殊处理："15000元/月" → daily_wage=None, 备注标记为月薪制
- 返回：`{姓名: {工种, 工日工资, 工时工资, 备注, 性别, 身份证号码, 电话号码, 身份证地址, 合同编号}}`

#### `parse_attendance(file_paths: List[str]) -> pd.DataFrame`

解析员工刷卡记录表（支持多文件合并）。

- 自定义格式：扫描"工号：X 姓名：XXX 部门：XXX"行，下一行为日期表头(1-31)，后续行为打卡数据
- 多次打卡以换行符分隔
- 按 (姓名, 日期, 打卡时间) 去重
- 返回：DataFrame[姓名, 工号, 部门, 日期, 打卡时间]

#### `process_xdz_data(attendance_df, roster_dict) -> Tuple[pd.DataFrame, pd.DataFrame]`

**核心计算引擎**，按个人工资标准匹配计算。

- 按姓名分组，每日打卡数据计算工时
- 工时计算规则：
  - `<2次打卡 → 异常，工时=0`
  - 最早打卡 `≤07:40 → 按07:30计`（早班进位）
  - 最晚打卡距整点/半点 `≤10分钟 → 补齐`（晚班补齐，容差可配）
  - 基本工时 = 打卡→16:30（扣除12:00-13:00午休）
  - 加班工时 = 16:30→最晚打卡
  - 按半小时向下取整
- 工资计算：`基本工资 = (基本工时/8) × 工日工资`，`加班工资 = 加班工时 × 工时工资`
- 异常处理：花名册无此人/排除工种/无工资标准 → 保留考勤，不计算工资

**salary_df 列**：序号, 姓名, 工种, 出勤工日, 日工资, 加班工时, 加班工资, 工资总额, 未支付数, 备注

**daily_df 列**：日期, 姓名, 工种, 上班打卡时间, 下班打卡时间, 当日工时, 基本工时, 加班工时, 当日基本工资, 当日加班工资, 当日总工资, 备注

#### `get_attendance_date_range(file_paths) -> Tuple[tuple, tuple]`

从考勤文件中提取日期范围。扫描"考勤日期：YYYY-MM-DD～YYYY-MM-DD"行，多文件取最早和最晚。返回 `((年,月,日), (年,月,日))` 或 `(None, None)`。

#### `format_date_range_sheet_name(start_date, end_date) -> str`

生成 sheet 名称，如 `"3月11日-4月10日工资表"`。

#### `generate_attendance_summary(daily_df, output_path) -> str`

生成考勤记录汇总 Excel（单 sheet "每日考勤明细"，按姓名+日期排序，蓝色表头+边框）。

#### `generate_ledger_sheet(ledger_path, output_path, salary_df, sheet_name, start_date, end_date)`

在现有台账文件中新增工资发放 sheet。

- 复制模板 sheet 的格式（标题行/列宽/合并单元格/字体）
- 18列：序号,班组,姓名,工种,出勤工日,日工资,加班工时,加班工资,路费,工资总额,预支费,罚款,其它,项目部代付,吴超付,未支付数,领款人签字,备注
- 自动调用 `_update_annual_summary()` 回写年度汇总台账
- 列映射规则：N月工资 = Col(8 + 2×N)

#### `generate_report_format(daily_df, roster_path, output_path, attendance_paths, ...)`

生成上报格式 Excel（2个 sheet）：

- Sheet1 "花名册(N月)"：编号,姓名,性别,工种,家庭地址,身份证号,联系电话,劳动合同编号
- Sheet2 "考勤表(YYYY.N月)"：每人2行（出勤√行+加班工时行），支持跨月合并

---

## FastAPI 后端 API

Base URL: `http://localhost:8000`（开发）或 `http://localhost:8080/api`（通过 Nginx）

### 公共端点（无需 session）

```
GET    /api/health                                      → 健康检查
GET    /api/annual-summary?project_id=1&year=2026       → 年度月度工资汇总（按项目隔离）
```

**GET /api/annual-summary**

从 SQLite 数据库读取指定项目、指定年度的所有月度汇总数据，无需会话。

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `project_id` | 1 | 项目 ID |
| `year` | 2026 | 年度 |

Response:
```json
{
  "year": 2026,
  "project_id": 1,
  "months": [
    { "month": 2, "sheet_name": "2月11日-3月10日工资表", "people": 45, "total_salary": 125000.00, "total_workdays": 900, "total_overtime": 120.5 },
    { "month": 3, "sheet_name": "3月11日-4月10日工资表", "people": 48, "total_salary": 132000.00, "total_workdays": 960, "total_overtime": 135.0 }
  ]
}
```

### 会话管理

```
POST   /api/session                        → 创建会话
DELETE /api/session/{session_id}            → 删除会话（重置）
PUT    /api/config?session_id=&late_tolerance=  → 更新容差配置
```

**POST /api/session**

Response:
```json
{"session_id": "a1b2c3d4e5f6..."}
```

### 项目管理

```
GET    /api/projects                       → 列出所有项目
POST   /api/projects?name=xxx              → 新建项目
DELETE /api/projects/{project_id}          → 删除项目及所有关联数据
```

**GET /api/projects**

Response:
```json
{
  "projects": [
    { "id": 1, "name": "默认项目", "created_at": "2026-04-25 09:00:00" },
    { "id": 2, "name": "西安北站", "created_at": "2026-04-25 09:05:00" }
  ]
}
```

**POST /api/projects**

参数：`name`（项目名称，必填）

Response: 新创建的项目对象

**DELETE /api/projects/{project_id}**

级联删除该项目的所有 monthly_summary 和 calculation_result 记录。

### 文件上传

```
POST   /api/upload/roster?session_id=              → 上传花名册（单个 .xlsx）
POST   /api/upload/attendance?session_id=          → 上传考勤（多个 .xls/.xlsx）
POST   /api/upload/ledger?session_id=&project_id=  → 上传台账（单个 .xlsx）★ 按项目种子历史月份
GET    /api/upload/status?session_id=              → 查询上传状态（含 project_id）
```

**POST /api/upload/roster**

Request: `multipart/form-data`，字段名 `file`

Response: `{"status": "ok", "filename": "花名册.xlsx"}`

**POST /api/upload/attendance**

Request: `multipart/form-data`，字段名 `files`（多文件）

Response: `{"status": "ok", "count": 3}`

**POST /api/upload/ledger**

上传台账时，后端自动读取原始 Excel 中所有 `*工资表` sheet，提取人数/工资总额/出勤工日/加班工时等数据写入 SQLite 数据库（种子操作，按 `project_id` 隔离）。

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `session_id` | 必填 | 会话ID |
| `project_id` | 1 | 绑定到的项目ID |

Request: `multipart/form-data`，字段名 `file`

Response: `{"status": "ok", "filename": "工资台账.xlsx", "seeded_months": 2}`

**GET /api/upload/status**

Response:
```json
{
  "roster": true,
  "attendance": true,
  "ledger": false,
  "attendance_count": 2,
  "project_id": 1
}
```

### 计算触发

```
POST   /api/calculate?session_id=           → 执行计算（核心端点）
```

前置条件：三个文件均已上传。内部通过 `asyncio.to_thread()` 调用 `attendance_core.py` 的同步函数，避免阻塞事件循环。

调用链：
```
POST /api/calculate
  → parse_xdz_roster(roster_path)
  → parse_attendance(attendance_paths)
  → get_attendance_date_range(attendance_paths)
  → process_xdz_data(attendance_df, roster_dict)
  → generate_attendance_summary(daily_df, ...)
  → generate_ledger_sheet(ledger_path, ..., salary_df, ...)
  → generate_report_format(daily_df, roster_path, ...)
  → 将 DataFrame 转为 JSON-safe dict 存入会话
  → ★ upsert_month() 将当月汇总写入 SQLite（按 project_id 隔离）
  → ★ save_calculation() 将完整工资+考勤 JSON 永久保存到 SQLite
```

Response:
```json
{
  "overview": {
    "total_people": 176,
    "total_salary": 1180417.48,
    "total_workdays": 3245,
    "total_overtime": 456.5
  },
  "sheet_name": "3月11日-4月10日工资表",
  "abnormal_count": 12
}
```

Error: `400` 文件未上传/日期范围读取失败，`500` 计算异常

### 结果查询

```
GET    /api/results/salary?session_id=              → 工资汇总 JSON（从会话内存）
GET    /api/results/daily?session_id=               → 每日明细 JSON（从会话内存）
GET    /api/results/history?project_id=&year=&month= → ★ 从 DB 加载历史计算结果
GET    /api/results/history-list?project_id=         → ★ 列出某项目所有历史计算
```

**GET /api/results/salary**

Response:
```json
{
  "overview": { "total_people": 176, "total_salary": 1180417.48, "total_workdays": 3245, "total_overtime": 456.5 },
  "records": [
    { "序号": 1, "姓名": "张三", "工种": "木工", "出勤工日": 22, "日工资": 350, "加班工时": 12.5, "加班工资": 43.75, "工资总额": 10093.75, "未支付数": 10093.75, "备注": "" }
  ],
  "sheet_name": "3月11日-4月10日工资表"
}
```

**GET /api/results/daily**

Response:
```json
{
  "records": [
    { "日期": 11, "姓名": "张三", "工种": "木工", "上班打卡时间": "07:30", "下班打卡时间": "18:00", "当日工时": 9.5, "基本工时": 8.0, "加班工时": 1.5, "当日基本工资": 350.0, "当日加班工资": 65.63, "当日总工资": 415.63, "备注": "" }
  ]
}
```

### 文件下载

```
GET    /api/download/attendance-summary?session_id=  → 考勤记录汇总.xlsx
GET    /api/download/ledger?session_id=              → 工资台账（含新增Sheet）.xlsx
GET    /api/download/report?session_id=              → 上报表.xlsx
```

Response: 二进制 Excel 文件，`Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

---

## SQLite 持久化存储

`backend/database.py` 使用 SQLite 存储项目、月度工资汇总和完整计算结果，数据库文件位于 `backend/data/attendance.db`。所有数据按 `project_id` 隔离，支持多工地独立使用。

### 表结构

```sql
-- 项目表
CREATE TABLE project (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 月度工资汇总（按项目隔离）
CREATE TABLE monthly_summary (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id   INTEGER NOT NULL,
    year         INTEGER NOT NULL,
    month        INTEGER NOT NULL,
    sheet_name   TEXT    NOT NULL DEFAULT '',
    people       INTEGER NOT NULL DEFAULT 0,
    total_salary REAL    NOT NULL DEFAULT 0,
    total_workdays INTEGER NOT NULL DEFAULT 0,
    total_overtime  REAL NOT NULL DEFAULT 0,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project(id),
    UNIQUE(project_id, year, month)   -- 每个项目同年同月只保留最新一条
);

-- 完整计算结果（工资+考勤JSON永久保存）
CREATE TABLE calculation_result (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id        INTEGER NOT NULL,
    year              INTEGER NOT NULL,
    month             INTEGER NOT NULL,
    sheet_name        TEXT    NOT NULL DEFAULT '',
    salary_json       TEXT    NOT NULL DEFAULT '[]',   -- 工资汇总完整记录 JSON
    daily_json        TEXT    NOT NULL DEFAULT '[]',   -- 每日考勤完整记录 JSON
    overview_json     TEXT    NOT NULL DEFAULT '{}',   -- 概览统计 JSON
    abnormal_count    INTEGER NOT NULL DEFAULT 0,
    output_att_summary TEXT,                           -- 考勤汇总输出路径
    output_ledger     TEXT,                             -- 台账输出路径
    output_report     TEXT,                             -- 上报表输出路径
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project(id),
    UNIQUE(project_id, year, month)
);
```

### 数据写入时机

| 时机 | 触发方式 | 写入内容 |
|------|---------|---------|
| 上传台账 | `POST /api/upload/ledger` | 按项目自动读取台账中所有 `*工资表` sheet，提取并入库 monthly_summary |
| 计算完成 | `POST /api/calculate` | 写入 monthly_summary（当月汇总）+ calculation_result（完整 JSON） |

### 数据读取方式

| 场景 | 端点 | 说明 |
|------|------|------|
| 页面加载 | `GET /api/annual-summary?project_id=&year=` | 无需 session，按项目返回年度汇总 |
| 历史回看 | `GET /api/results/history?project_id=&year=&month=` | 从 DB 加载完整工资/考勤 JSON |
| 项目列表 | `GET /api/results/history-list?project_id=` | 列出某项目所有历史计算 |

---

## 会话管理机制

`services/session_manager.py` 实现基于内存的 UUID 会话。

- 每个会话有独立 `tempfile.mkdtemp()` 临时目录，存放上传文件和输出文件
- 每个会话绑定一个 `project_id`（默认为 1），上传台账时自动关联
- 2小时自动过期（`SESSION_EXPIRE_HOURS=2`）
- 后台 asyncio 任务每小时清理过期会话
- **月度汇总和完整计算结果存储在 SQLite 中，独立于会话生命周期**
- **历史计算结果可通过 `/api/results/history` 从 DB 加载，不依赖会话存活**

### 会话生命周期

```
前端创建会话 → localStorage 存储 session_id + project_id
  → 上传3个文件到会话临时目录（台账上传时按项目 seed 历史月份到 SQLite）
  → POST /calculate 触发计算（计算结果写入 SQLite monthly_summary + calculation_result）
  → GET /results/* 查询结果
  → GET /download/* 下载 Excel
  → DELETE /session 或 2小时后自动过期清理
  → SQLite 中的数据不受影响，下次页面加载仍然可见
  → 历史结果可通过 /api/results/history 永久回看
```

---

## Vue 前端

### 技术栈

Vue 3 + TypeScript + Element Plus + Pinia + ECharts + Axios + Vite

### 设计系统

`src/styles/variables.css` 定义全局 CSS 设计令牌：

| 类别 | 内容 |
|------|------|
| 配色 | 品牌色 Indigo `#4F46E5`，深色侧边栏 `#1E293B`，浅色内容区 `#F8FAFC` |
| KPI 卡片色 | 4 种独立配色：indigo / emerald / orange / red |
| 阴影 | xs / sm / md / lg 四级 |
| 间距 | 4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48 px |
| 字体 | 12-30px 层级 |
| 圆角 | 4 / 8 / 12 / 16px |
| 过渡 | 150ms / 250ms / 350ms |
| 布局 | 侧边栏 280px / 顶部栏 56px / 内容区 max-width 1400px |
| Element Plus | 覆盖 `--el-color-primary`、`--el-border-color` 等 |

### 状态管理 (Pinia store)

`stores/attendance.ts` 管理全部状态：

| 字段 | 类型 | 说明 |
|------|------|------|
| `projects` | `Project[]` | 所有项目列表 |
| `activeProjectId` | `number` | 当前选中项目ID（默认1） |
| `activeProject` | `Project` | 当前项目对象（computed） |
| `sessionId` | `string` | 当前会话ID |
| `uploadStatus` | `UploadStatus` | 三个文件的上传状态（含 project_id） |
| `calculating` | `boolean` | 计算中标记 |
| `calculated` | `boolean` | 已完成计算 |
| `overview` | `OverviewStats` | 概览统计 |
| `salaryData` | `SalaryRecord[]` | 工资汇总数据 |
| `dailyData` | `DailyRecord[]` | 每日考勤数据 |
| `sheetName` | `string` | 新增Sheet名称 |
| `abnormalCount` | `number` | 异常人数 |
| `lateTolerance` | `number` | 晚班容差配置 |
| `error` | `string` | 错误信息 |
| `annualData` | `AnnualMonth[]` | ★ 年度月度汇总（按项目从 SQLite 读取） |

### API 客户端

`api/client.ts` 封装 Axios：

- `baseURL: '/api'`
- 请求拦截器：从 `localStorage` 读取 `session_id` 和 `project_id` 附加到查询参数
- 响应拦截器：提取 `response.data.detail` 作为错误信息
- 超时 120秒（计算可能耗时）

年度汇总接口使用 `axios` 直接调用 `/api/annual-summary?project_id=X&year=2026`（无需 session），在 `fetchAnnual()` 中按项目独立拉取。

### 组件说明

| 组件 | 功能 |
|------|------|
| `App.vue` | 主布局：顶部栏(项目选择器+数据看板/考勤计算双Tab) + 可折叠深色侧边栏 280px + 可滚动内容区 |
| `DashboardView` | ★ 数据看板 Tab：年度工资总览（4色KPI卡片 + 柱状图 + 月度明细表），按项目加载 |
| `FileUploadPanel` | 3 个上传项，深色适配，步骤编号圆圈（完成变绿勾），等宽排列 |
| `ConfigPanel` | 晚班容差滑块，深色适配，容差值放大显示，规则放入半透明圆角卡片 |
| `AlertBanner` | 左边框彩色卡片（warning=amber / success=emerald），点击折叠展开异常表格 |
| `OverviewCards` | 4 色 KPI 卡片（indigo/emerald/orange/red），彩色图标圆圈 + 大号数值，hover 上移效果 |
| `YearSummaryChart` | ★ 年度工资汇总：4 张大号累计 KPI 卡片 + 柱状图 + 月度明细表，数据从 SQLite 加载 |
| `JobCharts` | 2 列水平柱状图（工种人数分布 + 工种工资总额），品牌色渐变填充 |
| `SalaryTable` | 工资汇总表，表头 flex 两端对齐（标题+人数标签+搜索框），工资总额品牌色强调，前端分页（20/50/100条） |
| `DailyAttendance` | 3 个 Tab（全部/异常）带 Badge 数量，搜索框内嵌，共享列定义 v-for 渲染，前端分页 |
| `DownloadPanel` | 3 个独立下载卡片（图标+标题+描述+按钮），Sheet 信息绿色 Tag |

### 用户操作流程

```
1. 页面加载 → 自动拉取项目列表 → 恢复上次选中项目（localStorage）
            → 按项目从 SQLite 拉取年度汇总
            → 同时创建会话（或恢复 localStorage 中的 session_id）
2. 顶部栏显示当前项目（下拉切换 / 新建 / 删除）
3. 两个 Tab 切换：
   a. 「数据看板」Tab — 全宽年度工资总览（KPI + 柱状图 + 月度表），侧边栏隐藏
   b. 「考勤计算」Tab — 侧边栏 + 计算流程
4. 切换项目 → 重置会话 → 重新拉取该项目年度数据
5. 侧边栏上传 3 个文件（按钮逐一变绿，台账上传时按项目 seed 历史月份到 DB）
6. 调整容差配置（可选）
7. 点击"开始计算" → loading 状态
8. 计算完成 → 自动切换到「考勤计算」Tab → fade 过渡到结果页面：
   异常告警 → 当月 KPI 卡片 → 工种图表 → 工资表 → 考勤明细 → 下载卡片
9. 点击"重置" → 清除会话，回到上传界面（SQLite 数据保留）
注：上传完毕后即可点击"重置"，无需等到计算完成
```

### 页面布局

```
┌──────────────────────────────────────────────────────────────┐
│  ┌──────────────────────────────────────────────────────────┐│
│  │ ≡  [数据看板] [考勤计算]   🏢 默认项目 ▼   [计算完成] 🗑││ ← 顶部栏 56px
│  │    └─ Tab 切换 ──┘        └─ 项目选择器 ──┘              ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ──「数据看板」Tab（无侧边栏，全宽）──                       │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  2026 年度工资总览 — 创新智成 · 西安东站项目             ││
│  │  ┌──────────┬──────────┬──────────┬──────────┐          ││
│  │  │ 累计工资  │ 人数峰值  │ 累计工日  │ 累计加班  │          ││ ← 4 色 KPI
│  │  │ ¥12.50万 │ 48人     │ 1860工日  │ 255.5h   │          ││
│  │  └──────────┴──────────┴──────────┴──────────┘          ││
│  │  ┌────────────────────────────────────────────┐          ││
│  │  │  月度工资趋势（柱状图）                      │          ││
│  │  └────────────────────────────────────────────┘          ││
│  │  ┌────────────────────────────────────────────┐          ││
│  │  │  月度明细表（月份/工资表/人数/工资/工日/加班）│          ││
│  │  └────────────────────────────────────────────┘          ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ──「考勤计算」Tab（侧边栏 + 内容区）──                      │
│  ┌──────────┐  ┌──────────────────────────────────────────┐│
│  │ 品牌 Logo │  │                                          ││
│  │──────────│  │  流程指引卡片 / 计算结果                   ││
│  │ ┌──────┐ │  │  ┌──────────────────────────────┐        ││
│  │ │数据  │ │  │  │  1 花名册 ✓ → 2 考勤 ✓ → 3 台账  │        ││
│  │ │上传  │ │  │  └──────────────────────────────┘        ││
│  │ └──────┘ │  │                                          ││
│  │ ┌──────┐ │  │  计算规则说明 (折叠面板)                  ││
│  │ │计算  │ │  │                                          ││
│  │ │配置  │ │  │  ── 计算后 fade 过渡到结果页 ──           ││
│  │ └──────┘ │  │  异常告警 → KPI卡片 → 工种图表 →          ││
│  │ ┌──────┐ │  │  工资表 → 考勤明细 → 下载卡片             ││
│  │ │开始  │ │  │                                          ││
│  │ │计算  │ │  │                                          ││
│  │ │重置  │ │  │                                          ││
│  │ └──────┘ │  │                                          ││
│  │  深色    │  │                                          ││
│  │  侧边栏  │  │                                          ││
│  │  280px  │  │                                          ││
│  └──────────┘  └──────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

---

## Nginx 配置

```
location /        → 静态文件，SPA fallback (try_files $uri /index.html)
location /api/    → proxy_pass http://backend:8000
client_max_body_size 50M    (Excel上传)
proxy_read_timeout 120s     (计算耗时)
gzip on                     (压缩静态资源)
```

Nginx Dockerfile 采用多阶段构建：
1. `node:20-alpine` 安装 pnpm，`pnpm build` 生成 dist
2. `nginx:alpine` 复制 dist + nginx.conf

---

## 本地开发

### 后端

```bash
cd backend
PYTHONPATH=../attendance:$PYTHONPATH uvicorn main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npx pnpm dev    # http://localhost:3000，Vite 自动代理 /api → :8000
```

### Docker

```bash
# 启动新前端 → http://localhost:8080
docker compose --profile web up -d

# 启动 Streamlit → http://localhost:8501
docker compose --profile old up -d

# 全部启动
docker compose --profile web --profile old up -d
```

---

## 公网部署（cpolar 内网穿透）

通过 cpolar 将本地服务暴露到公网，无需云服务器，其他人通过公网地址即可访问。

### 适用场景

- 多个工地负责人在不同网络环境下传考勤数据
- 大老板在办公室查看各项目工资汇总
- 2-3 个偶发用户，不需要 24 小时高可用

### 架构

```
A负责人(工地) ──┐
                │    公网                  内网
大老板(办公室) ──┼──→ cpolar.top ──→ 你的电脑:8080 ──→ Docker(Nginx+FastAPI+SQLite)
                │
B负责人(工地) ──┘
```

### 安装与配置

```bash
# 1. 安装 cpolar
curl -L https://www.cpolar.com/static/downloads/install-release-cpolar.sh | sudo bash

# 2. 注册账号（https://dashboard.cpolar.com/signup），获取 authtoken
sudo cpolar authtoken 你的authtoken

# 3. 启动 Docker 服务
cd ~/Documents/Abay/Web
docker compose --profile web up -d

# 4. 启动 cpolar 并设为开机自启
sudo systemctl enable cpolar
sudo systemctl start cpolar

# 5. 创建隧道（通过管理面板 API）
curl -X POST http://localhost:9200/api/tunnels \
  -H "Content-Type: application/json" \
  -d '{"addr":"8080","proto":"http","name":"attendance"}'
```

### 获取公网地址

```bash
# 方式1：创建隧道时返回
# 方式2：访问管理面板 http://localhost:9200 查看
# 方式3：查询 API
curl http://localhost:9200/api/tunnels
```

地址格式：`http://xxxxxxxx.r30.cpolar.top`（HTTP，不是 HTTPS）

### 使用方式

| 角色 | 操作 |
|------|------|
| 项目负责人 | 打开公网地址 → 选择项目 → 「考勤计算」上传文件并计算 |
| 大老板 | 打开公网地址 → 「数据看板」→ 顶部切换项目查看各工地汇总 |

### 注意事项

- 你的电脑必须保持开机，不能关机或休眠
- 免费 cpolar 隧道每次重启地址会变，需重新发送给他人
- 长期使用建议购买固定域名（9元/月）
- **必须用 HTTP 访问，不要用 HTTPS**（免费版不支持）
- cpolar 管理面板地址：`http://localhost:9200`

### 重新创建隧道（地址变了之后）

```bash
# 重启 cpolar
sudo systemctl restart cpolar
sleep 3

# 重新创建隧道
curl -X POST http://localhost:9200/api/tunnels \
  -H "Content-Type: application/json" \
  -d '{"addr":"8080","proto":"http","name":"attendance"}'
```

---

## 测试数据

`attendance/mock_data/` 目录含测试用文件：

| 文件 | 说明 |
|------|------|
| `创新智成-西安东站-花名册-2026.4.xlsx` | 花名册，含245人 |
| `员工刷卡记录表4-1.xls` + `4-2.xls` | 考勤记录，共6543条 |
| `工资台账2026（超）.xlsx` | 工资台账模板（含2月、3月已有工资表） |

E2E 测试结果：176条工资记录，工资总额 ¥1,180,417.48。

---

## 关键技术决策

| 决策 | 理由 |
|------|------|
| `attendance_core.py` 零修改 | 核心计算逻辑单一数据源，前端可替换 |
| 内存会话（无 Redis） | 单用户内部工具，无需额外中间件 |
| SQLite 持久化 + 项目隔离 | 跨会话保留数据，多工地互不冲突，零运维开销 |
| `project_id` 维度隔离 | 不同工地上传不同台账不会互相覆盖，数据完全独立 |
| 完整计算结果落库 | salary/daily JSON 永久保存，历史结果可随时回看 |
| 年度汇总读原始台账文件 | 避免 openpyxl 保存后丢失公式缓存值的问题 |
| `asyncio.to_thread()` | `attendance_core.py` 是同步 pandas 代码 |
| SQLite WAL + busy_timeout | 2-3 个偶发用户并发写入，无需引入 PostgreSQL |
| 顶部栏 Tab 导航 | 数据看板（全局）与考勤计算（工具）两个场景清晰分离 |
| ECharts 替代 Plotly | 中文支持好，与 Element Plus 风格统一 |
| 前端分页（20/50/100条） | 避免大量数据时表格过长，搜索时自动重置页码 |
| 单页应用（无 vue-router） | 线性工作流：选择项目→上传→计算→结果 |
| Volume 挂载 attendance_core.py | 避免代码重复，保持单一数据源 |
| CSS 设计令牌 (variables.css) | 统一配色/间距/阴影/圆角，全局一致且易于主题切换 |
| 移动端响应式适配 | 侧边栏右滑抽屉 + 遮罩关闭，KPI/表格/图表 640px 自适应，支持手机浏览器访问 |
| 年度汇总合计公式修复 | 新增人员时 SUM 范围需同时包含原有行和新增行，排除合计行自身 |
| seed_from_ledger 逐行累加 | 工资总额始终通过累加有名字行的 col10 值计算，不依赖合计行，更可靠 |
| 上传文件名显示 | 侧边栏上传后显示原始文件名，考勤支持多文件名展示，后端 SessionData 存储文件名 |
| 年度汇总工资合计公式 | col5（工资合计）统一为各月工资列累加公式，新增和已有人员均自动更新 |
| 工资汇总表限高滚动 | 表格 max-height=500px，配合分页避免页面过长，移动端体验改善 |
| 年度汇总写实际数值 | openpyxl 公式无缓存值导致手机端显示0，改为写入实际计算数值（双wb加载读取缓存） |
