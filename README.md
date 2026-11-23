# Mini-MES

> 一个用 **FastAPI + React** 写的迷你 MES（制造执行系统）示例：登录鉴权、生产工单增删改查、分页筛选，以及带状态机约束的工单流转。

适合拿来当全栈练手项目或后端分层 / 前端组件化的参考，不追求产线级功能。

## 功能特性

- **JWT 登录鉴权**：`/auth/login` 签发 Token，前端自动附加 `Authorization: Bearer`，401 自动跳回登录页
- **工单 CRUD**：创建、列表、详情、更新、删除
- **分页与筛选**：按页码 / 每页条数分页，支持按状态筛选、按标题关键字搜索
- **状态机流转**：`pending → processing → done`，非法跳转直接返回 `409 CONFLICT`
- **角色权限**：`admin` / `operator`；仅创建者或管理员可修改，仅管理员可删除
- **统一错误格式**：所有异常统一为 `{"error": {"code", "message", "details?"}}`
- **数据库迁移**：Alembic 管理表结构，启动时自动 `upgrade head`
- **一键部署**：Docker Compose 同时拉起 PostgreSQL、后端、前端

## 技术栈

| 层 | 选型 |
| --- | --- |
| 后端 | FastAPI · SQLAlchemy 2.0 · Alembic · Pydantic v2 |
| 认证 | PyJWT · pwdlib（Argon2） |
| 数据库 | PostgreSQL 16 |
| 前端 | React 19 · TypeScript · Vite · TanStack Query · React Router · Axios |
| 部署 | Docker Compose · Nginx · uv |

## 架构

```mermaid
flowchart LR
    subgraph browser["浏览器"]
        SPA["React SPA<br/>登录页 / 工单列表 / 详情抽屉"]
    end

    subgraph compose["Docker Compose"]
        NG["Nginx :80<br/>静态资源 + /api 反向代理"]
        API["FastAPI :8000<br/>JWT 鉴权 · 统一错误处理<br/>路由 → Service → ORM"]
        DB[("PostgreSQL 16<br/>users · tickets")]
    end

    SPA -->|HTTP| NG
    NG -->|"/api/v1/*"| API
    API -->|SQLAlchemy| DB
    API -.->|"启动时 Alembic 迁移 + seed"| DB
```

**工单状态机**（`app/services/ticket.py`）：

```mermaid
stateDiagram-v2
    [*] --> pending: 新建工单
    pending --> processing: 开始处理
    processing --> done: 完成
    done --> [*]
```

任何跨状态跳转（如 `pending → done`）都会被拒绝并返回 `409`，避免绕过流程。

## 快速开始

### 前置条件

- Docker 与 Docker Compose（v2）

### 1. 准备环境变量

```bash
cp .env.example .env
```

编辑 `.env`，至少设置 `SECRET_KEY`（生产环境请使用随机值）：

```bash
openssl rand -hex 32
```

### 2. 启动

```bash
docker compose up --build -d
```

首次启动会自动完成：

1. 等待 PostgreSQL 健康检查通过
2. `alembic upgrade head` 建表
3. `scripts/seed` 写入演示账号
4. 启动 FastAPI 与 Nginx

### 3. 访问

| 服务 | 地址 |
| --- | --- |
| 前端 | <http://localhost> |
| API 文档（Swagger） | <http://localhost:8000/docs> |
| 健康检查 | <http://localhost:8000/api/v1/health> |
| PostgreSQL（宿主机端口） | `localhost:5433` |

### 演示账号

| 用户名 | 密码 | 角色 |
| --- | --- | --- |
| `admin` | `admin123` | admin（可删除工单） |
| `operator` | `operator123` | operator（只能操作自己的工单） |

> 以上账号由 `scripts/seed.py` 写入。`seed` 是幂等的，每次启动会重置这两个账号的密码和角色，但不会清空工单数据。

### 常用命令

```bash
docker compose ps                 # 查看容器状态
docker compose logs -f backend    # 跟踪后端日志
docker compose down               # 停止并保留数据
docker compose down -v            # 停止并清空数据库卷
```

## 截图

### 登录

![登录页](./loginPage.png)

### 工单列表 · 新建与详情

| 新建工单 | 工单详情 |
| --- | --- |
| ![工单列表与新建](./mainPage_and_createPage.png) | ![工单列表与详情](./mainPage_and_editPage.png) |

## 本地开发（不用 Docker）

### 后端

```bash
# 1. 安装依赖
uv sync

# 2. 准备一个 PostgreSQL；可直接复用 Compose 里的 db（宿主机端口 5433）
docker compose up -d db

# 3. 在 .env 里配置 DATABASE_URL，例如：
#    DATABASE_URL=postgresql+psycopg://mes:mes@localhost:5433/mini_mes

# 4. 建表 + 种子数据
uv run alembic upgrade head
uv run python -m scripts.seed

# 5. 启动（热重载）
uv run uvicorn app.main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

开发服务器在 <http://localhost:5173>，Vite 会把 `/api` 代理到 `http://localhost:8000`（见 `frontend/vite.config.ts`）。

## 测试

测试使用**独立的 PostgreSQL 数据库**，不会碰开发库。首次运行前先创建测试库：

```bash
# 复用 Compose 的数据库实例
docker compose up -d db
docker compose exec db createdb -U mes mini_mes_test
```

在 `.env` 中配置测试库（注意 Compose 的宿主机端口是 `5433`）：

```bash
TEST_DATABASE_URL=postgresql+psycopg://mes:mes@localhost:5433/mini_mes_test
```

然后运行：

```bash
uv sync
uv run pytest -v
```

当前覆盖 10 个用例：

- `tests/test_health.py`：健康检查
- `tests/test_auth.py`：登录成功 / 密码错误
- `tests/test_ticket.py`：创建、分页、按状态筛选、404、非法状态流转、权限、未登录拦截

测试隔离方式（`tests/conftest.py`）：会话开始时 `create_all` 建表、结束时 `drop_all`；每个用例前 `TRUNCATE ... RESTART IDENTITY CASCADE`；通过 FastAPI 的 `dependency_overrides` 把 `get_db` 换成测试库 Session。

代码检查：

```bash
uv run ruff check
cd frontend && npm run lint
```

## API 一览

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| `POST` | `/api/v1/auth/login` | 登录（`application/x-www-form-urlencoded`） | 公开 |
| `GET` | `/api/v1/auth/me` | 当前用户 | 登录 |
| `GET` | `/api/v1/health` | 健康检查 | 公开 |
| `GET` | `/api/v1/tickets` | 工单列表，支持 `page` / `size` / `status` / `q` | 登录 |
| `POST` | `/api/v1/tickets` | 创建工单 | 登录 |
| `GET` | `/api/v1/tickets/{id}` | 工单详情 | 公开 |
| `PATCH` | `/api/v1/tickets/{id}` | 更新工单 / 流转状态 | 创建者或 admin |
| `DELETE` | `/api/v1/tickets/{id}` | 删除工单 | admin |

## 项目结构

```text
mini-mes/
├── app/
│   ├── main.py              # FastAPI 入口、异常处理器
│   ├── db.py                # Engine / Session / Base
│   ├── api/
│   │   ├── router.py        # /api/v1 路由汇总
│   │   ├── deps.py          # 当前用户、admin 校验
│   │   └── routes/          # auth / tickets / health
│   ├── core/                # 配置、JWT、密码哈希、业务异常
│   ├── models/              # SQLAlchemy ORM 模型
│   ├── schemas/             # Pydantic 入参 / 出参
│   └── services/            # 业务逻辑（含状态机）
├── frontend/
│   ├── src/pages/           # 登录页、工单列表页
│   ├── src/components/      # 新建工单弹窗、详情抽屉
│   ├── src/api/             # Axios 封装与接口
│   └── nginx.conf           # 静态资源 + /api 代理 + SPA 回退
├── migrations/              # Alembic 迁移
├── scripts/seed.py          # 演示账号
├── tests/                   # pytest
├── docker-compose.yml
└── Dockerfile
```

## 说明

- 这是一个演示项目：示例账号、默认 JWT 密钥、`DEBUG` 日志等配置**不要直接用于生产**。
- 数据库里的 `status` 用 `String(20)` + 应用层约束，而不是 PostgreSQL 原生 ENUM，便于用 Alembic 增删状态值。
- 分页接口的 `size` 上限被限制在 100，避免一次拉取全表。
