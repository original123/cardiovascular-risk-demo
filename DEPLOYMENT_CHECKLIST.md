# 部署文档

---

## 一、Docker Compose 生产部署（推荐）

### 架构说明

```
用户浏览器
    │
    ▼  :4000
[nginx 容器 / frontend]
    │  /api/* 反向代理
    ▼  :8000 (仅内部)
[uvicorn 容器 / backend]
```

- frontend 容器：nginx 静态服务 + 反向代理，对外暴露 **4000** 端口。
- backend 容器：FastAPI + uvicorn，仅内部可达，不对外暴露。

### 前提

- 服务器已安装 Docker（≥ 24）和 Docker Compose（≥ v2）。
- 服务器可访问 GitHub 或已提前克隆代码。

### 部署步骤

```bash
git clone https://github.com/original123/cardiovascular-risk-demo.git
cd cardiovascular-risk-demo
docker compose up -d --build
```

访问 `http://<服务器IP>:4000` 即可使用。

### 更新部署

```bash
cd cardiovascular-risk-demo
git pull
docker compose up -d --build
```

### 查看日志 / 状态

```bash
docker compose ps
docker compose logs backend --tail=50
docker compose logs frontend --tail=50
```

---

## 二、踩坑记录（AI 部署经验）

### 坑 1：前端硬编码 API 地址

**现象：** 提交表单报 `Failed to fetch`。

**原因：** `App.vue` 中 `API_BASE` 默认值为 `http://127.0.0.1:8000`，在服务器的 nginx 容器内 `127.0.0.1:8000` 不可达。

**修复：** 将默认值改为空字符串，让请求走相对路径 `/api/...`，由 nginx 代理到 `backend:8000`。

```js
// 修复前
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
// 修复后
const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
```

---

### 坑 2：模型文件未打包进容器

**现象：** 提交表单报 `Unexpected token 'I', "Internal S"... is not valid JSON`（后端 500）。

**原因：** `lifetime.py` 中 `MODEL_PATH` 使用 `Path(__file__).resolve().parents[2] / "docs" / "research" / "lifetime_poly2_model.json"` 计算路径。容器内 `__file__` 为 `/app/app/lifetime.py`，往上两层为根目录 `/`，因此模型文件需要在 `/docs/research/` 下。原 Dockerfile 只 `COPY app/`，没有包含 `docs/`。

**修复：**
1. 将 backend 的 build context 改为项目根目录（在 `docker-compose.yml` 中指定 `context: .`）。
2. Dockerfile 中将 `docs` 目录复制到容器根路径：

```dockerfile
# 修复后的关键行
COPY docs/ /docs/
```

---

## 三、本地开发（不使用 Docker）

### 环境要求

- Python：建议 3.12 或兼容版本。
- Node.js：建议 22.x 或兼容 Vite 7 的版本。
- 后端端口：默认 `8000`。
- 前端端口：Vite dev 默认 `5173`；生产部署使用 `frontend/dist` 静态产物。

## 安装

后端：

```bash
cd backend
python -m pip install -r requirements.txt
```

前端：

```bash
cd frontend
npm install
npm run build
```

## 启动

后端：

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

前端开发：

```bash
cd frontend
VITE_API_BASE_URL=http://127.0.0.1:8000 npm run dev
```

生产部署：

```bash
cd frontend
npm run build
```

将 `frontend/dist` 发布到静态服务器，并配置 API 地址指向 Python 后端。

## 验证

后端测试：

```bash
cd backend
python -m pytest -q
```

健康检查：

```bash
curl http://127.0.0.1:8000/api/health
```

指南样例 API 检查：

```bash
curl -X POST http://127.0.0.1:8000/api/risk/evaluate \
  -H 'Content-Type: application/json' \
  -d '{"sex":1,"age":40,"region":1,"area":1,"waist":80,"tc_unit":2,"tc":5.2,"hdlc_unit":2,"hdlc":1.3,"sbp":145,"dbp":80,"drug":0,"dm":0,"csmoke":0,"fh_ascvd":1}'
```

期望：

- `tenYearRisk.percent` 约为 `4.7`
- `idealTenYearRisk.percent` 约为 `1.1`
- `lifetimeRisk.level` 为 `高危`
- 建议包含终生高危和高血压提示

## 限制说明

- 终生风险为工程拟合近似模型，非原始 China-PAR 终生风险公式。
- 正式医学或核保决策场景，需要补齐权威公式或官方服务授权。
- 当前版本不包含登录、历史记录、打印、分享和审计日志。
