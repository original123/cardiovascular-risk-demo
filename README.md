# 心血管风险评估 Demo

本目录用于整理并实现 China-PAR 心脑血管病风险评估 demo。

## 目录结构

- `docs/references/`：原始指南、论文、补充材料等引用资料。
- `docs/research/`：官网黑盒反推、公式整理、规则说明。
- `src/`：后续 demo 源码目录。
- `tests/`：后续测试用例目录。

## 当前资料

- `docs/references/中国心血管病风险评估和管理指南.pdf`
- `docs/research/官网规则反推.md`
- `docs/research/可实现规则清单.md`
- `docs/research/lifetime_poly2_model.json`
- `docs/research/lifetime_fit_samples.jsonl`
- `docs/research/ideal_risk_samples.jsonl`
- `docs/research/valid_input_cases.jsonl`

## 当前结论

官网 `https://www.cvdrisk.com.cn/ASCVD/Eval/` 的核心计算不在前端完成。前端只做表单输入、基础范围校验和提交，实际风险值、分层和建议由后端接口返回。

当前已经整理出：

- 10 年 ASCVD 风险的工程近似公式。
- 终生风险的工程近似模型。
- 10 年风险和终生风险的分层规则。
- 理想风险的具体替换值。
- 官网“温馨建议”的主要触发规则。
- 后端输入校验和边界规则。
- 仍未完全公开的终生风险原始精确公式缺口。

后续实现 demo 时，建议先实现：

1. 问卷字段和输入校验。
2. 10 年风险计算。
3. 风险分层。
4. 温馨建议生成。
5. 终生风险先使用 `lifetime_poly2_model.json` 做 demo 近似，后续继续补齐原始公式。

## 本地运行

### 后端

```bash
cd /Users/zhaoleiguang/project/temp/心血管demo/backend
/Users/zhaoleiguang/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pip install -r requirements.txt
/Users/zhaoleiguang/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

健康检查：

```bash
curl http://127.0.0.1:8000/api/health
```

### 前端

```bash
cd /Users/zhaoleiguang/project/temp/心血管demo/frontend
npm install
npm run dev
```

如后端不是 `http://127.0.0.1:8000`，启动前端时设置：

```bash
VITE_API_BASE_URL=http://后端地址 npm run dev
```

## 测试

后端测试：

```bash
cd /Users/zhaoleiguang/project/temp/心血管demo/backend
/Users/zhaoleiguang/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest -q
```

前端构建：

```bash
cd /Users/zhaoleiguang/project/temp/心血管demo/frontend
npm run build
```

## 关键限制

- 10 年风险为按 China-PAR 论文结构和官网输出拟合的工程公式。
- 终生风险使用 `docs/research/lifetime_poly2_model.json` 工程近似模型，不是原始公开 Fine-Gray 公式。
- 若用于正式医学或核保决策，应替换为权威原始公式或获得官方计算服务授权。
