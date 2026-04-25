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
                   │ Vue 3  │   │
                   │ 前端SPA│   │
                   └────────┘   │
                           ┌────▼─────┐
                           │ FastAPI  │  计算API
                           │ :8000    │
                           └────┬─────┘
                                │ volume :ro
                           ┌────▼─────┐
                           │attendance│  核心计算模块(零修改)
                           │_core.py  │
                           └──────────┘

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
│   ├── main.py                  # FastAPI 入口，CORS，生命周期
│   ├── config.py                # 端口/会话过期/上传限制等常量
│   ├── routers/
│   │   ├── upload.py            # 文件上传端点
│   │   ├── calculate.py         # 触发核心计算
│   │   ├── results.py           # 查询计算结果
│   │   └── download.py          # 下载 Excel 文件
│   ├── services/
│   │   └── session_manager.py   # 内存会话管理，UUID，自动过期清理
│   └── schemas/
│       └── models.py            # Pydantic 响应模型
│
├── frontend/                    # Vue 3 前端
│   ├── package.json
│   ├── vite.config.ts           # @ 别名 + dev proxy /api → :8000
│   ├── index.html
│   └── src/
│       ├── main.ts              # 入口：注册 ElementPlus + Pinia
│       ├── App.vue              # 主布局：左侧 sidebar + 右侧内容区
│       ├── api/
│       │   └── client.ts        # Axios 实例，自动附加 session_id
│       ├── stores/
│       │   └── attendance.ts    # Pinia 状态管理（全生命周期）
│       ├── types/
│       │   └── index.ts         # TypeScript 接口定义
│       └── components/
│           ├── FileUploadPanel.vue   # 3个上传按钮
│           ├── ConfigPanel.vue       # 晚班容差滑块
│           ├── AlertBanner.vue       # 异常人员告警
│           ├── OverviewCards.vue     # 4个统计卡片
│           ├── JobCharts.vue         # ECharts 工种饼图+柱状图
│           ├── SalaryTable.vue       # 工资汇总表（搜索/排序/高亮）
│           ├── DailyAttendance.vue   # 每日考勤明细（3个Tab）
│           └── DownloadPanel.vue     # 3个下载按钮
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

所有端点（除 `/api/session` 和 `/api/health`）需携带 `?session_id=xxx` 查询参数。

### 会话管理

```
POST   /api/session                        → 创建会话
DELETE /api/session/{session_id}            → 删除会话（重置）
GET    /api/health                          → 健康检查
PUT    /api/config?session_id=&late_tolerance=  → 更新容差配置
```

**POST /api/session**

Response:
```json
{"session_id": "a1b2c3d4e5f6..."}
```

### 文件上传

```
POST   /api/upload/roster?session_id=       → 上传花名册（单个 .xlsx）
POST   /api/upload/attendance?session_id=   → 上传考勤（多个 .xls/.xlsx）
POST   /api/upload/ledger?session_id=       → 上传台账（单个 .xlsx）
GET    /api/upload/status?session_id=       → 查询上传状态
```

**POST /api/upload/roster**

Request: `multipart/form-data`，字段名 `file`

Response: `{"status": "ok", "filename": "花名册.xlsx"}`

**POST /api/upload/attendance**

Request: `multipart/form-data`，字段名 `files`（多文件）

Response: `{"status": "ok", "count": 3}`

**POST /api/upload/ledger**

Request: `multipart/form-data`，字段名 `file`

Response: `{"status": "ok", "filename": "工资台账.xlsx"}`

**GET /api/upload/status**

Response:
```json
{
  "roster": true,
  "attendance": true,
  "ledger": false,
  "attendance_count": 2
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
GET    /api/results/salary?session_id=      → 工资汇总 JSON
GET    /api/results/daily?session_id=       → 每日明细 JSON
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

## 会话管理机制

`services/session_manager.py` 实现基于内存的 UUID 会话。

- 每个会话有独立 `tempfile.mkdtemp()` 临时目录，存放上传文件和输出文件
- 2小时自动过期（`SESSION_EXPIRE_HOURS=2`）
- 后台 asyncio 任务每小时清理过期会话
- 无 Redis/数据库（单用户内部工具）

### 会话生命周期

```
前端创建会话 → localStorage 存储 session_id
  → 上传3个文件到会话临时目录
  → POST /calculate 触发计算
  → GET /results/* 查询结果
  → GET /download/* 下载 Excel
  → DELETE /session 或 2小时后自动过期清理
```

---

## Vue 前端

### 技术栈

Vue 3 + TypeScript + Element Plus + Pinia + ECharts + Axios + Vite

### 状态管理 (Pinia store)

`stores/attendance.ts` 管理全部状态：

| 字段 | 类型 | 说明 |
|------|------|------|
| `sessionId` | `string` | 当前会话ID |
| `uploadStatus` | `UploadStatus` | 三个文件的上传状态 |
| `calculating` | `boolean` | 计算中标记 |
| `calculated` | `boolean` | 已完成计算 |
| `overview` | `OverviewStats` | 概览统计 |
| `salaryData` | `SalaryRecord[]` | 工资汇总数据 |
| `dailyData` | `DailyRecord[]` | 每日考勤数据 |
| `sheetName` | `string` | 新增Sheet名称 |
| `abnormalCount` | `number` | 异常人数 |
| `lateTolerance` | `number` | 晚班容差配置 |
| `error` | `string` | 错误信息 |

### API 客户端

`api/client.ts` 封装 Axios：

- `baseURL: '/api'`
- 请求拦截器：从 `localStorage` 读取 `session_id` 附加到查询参数
- 响应拦截器：提取 `response.data.detail` 作为错误信息
- 超时 120秒（计算可能耗时）

### 组件说明

| 组件 | Element Plus 组件 | 功能 |
|------|-------------------|------|
| `App.vue` | `el-container` | 主布局：320px侧边栏 + 弹性内容区 |
| `FileUploadPanel` | 3×`el-upload` | 花名册/考勤/台账上传，上传后按钮变绿并提示"点击重选"可覆盖重传 |
| `ConfigPanel` | `el-slider` | 晚班容差配置（1-15分钟） |
| `AlertBanner` | `el-alert` + `el-table` | 异常人员列表（可展开表格） |
| `OverviewCards` | 4×`el-card` + `el-statistic` | 结算人数/工资总额/出勤工日/加班工时 |
| `JobCharts` | `vue-echarts` | 环形饼图（工种人数）+ 水平柱状图（工种工资） |
| `SalaryTable` | `el-table` | 搜索/排序/金额格式化/异常行黄色高亮 |
| `DailyAttendance` | `el-tabs` + `el-table` | 3个Tab：全部/搜索/异常 |
| `DownloadPanel` | 3×`el-button` | 下载3个Excel文件 |

### 用户操作流程

```
1. 页面加载 → 自动创建会话（或恢复 localStorage 中的 session_id）
2. 侧边栏上传3个文件（按钮逐一变绿，提示"点击重选"可覆盖重传）
3. 调整容差配置（可选）
4. 点击"开始计算" → loading 状态
5. 计算完成 → 展示：异常告警 → 概览卡片 → 图表 → 工资表 → 考勤明细 → 下载按钮
6. 点击"重置" → 清除会话，回到上传界面
注：上传完毕后即可点击"重置"，无需等到计算完成
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

## 测试数据

`attendance/mock_data/` 目录含测试用文件：

| 文件 | 说明 |
|------|------|
| `创新智成-西安东站-花名册-2026.4.xlsx` | 花名册，含245人 |
| `员工刷卡记录表4-1.xls` + `4-2.xls` | 考勤记录，共6543条 |
| `工资台账2026（超）.xlsx` | 工资台账模板 |

E2E 测试结果：176条工资记录，工资总额 ¥1,180,417.48。

---

## 关键技术决策

| 决策 | 理由 |
|------|------|
| `attendance_core.py` 零修改 | 核心计算逻辑单一数据源，前端可替换 |
| 内存会话（无 Redis） | 单用户内部工具，无需额外中间件 |
| 无数据库 | 输入输出均为 Excel，无需持久化 |
| `asyncio.to_thread()` | `attendance_core.py` 是同步 pandas 代码 |
| ECharts 替代 Plotly | 中文支持好，与 Element Plus 风格统一 |
| 全量数据下发（无分页） | 典型 <200 人、<5000 条记录，前端过滤即可 |
| 单页应用（无 vue-router） | 线性工作流：上传→计算→结果 |
| Volume 挂载 attendance_core.py | 避免代码重复，保持单一数据源 |
