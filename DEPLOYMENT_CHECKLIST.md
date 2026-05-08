# 客户部署前检查清单

## 环境

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
