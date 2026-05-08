from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .service import evaluate
from .validation import ValidationError

app = FastAPI(title="心血管风险评估 Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/risk/evaluate")
async def evaluate_risk(request: Request):
    try:
        payload = await request.json()
        return {"success": True, "result": evaluate(payload)}
    except ValidationError as exc:
        return JSONResponse(
            status_code=422,
            content={"success": False, "message": str(exc), "errors": [{"message": str(exc)}]},
        )
