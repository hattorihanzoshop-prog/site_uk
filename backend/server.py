import os
import json
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Flow Consulting API - JSON DB Mode")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Путь к файлу с данными
DB_FILE = Path(__file__).parent / "db_dump.json"

# Глобальное хранилище данных
db_data = {
    "reports": [],
    "payment_transactions": [],
    "newsletter_signups": [],
    "custom_research_requests": [],
    "contact_submissions": [],
    "sample_downloads": []
}

# Загрузка данных из файла при старте
def load_db():
    global db_data
    if DB_FILE.exists():
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                # Объединяем загруженные данные с нашей структурой
                for key in db_data:
                    if key in loaded:
                        db_data[key] = loaded[key]
            print(f"Successfully loaded data from {DB_FILE}")
        except Exception as e:
            print(f"Error loading {DB_FILE}: {e}")

load_db()

# --- ЭНДПОИНТЫ ---

@app.get("/api/reports")
async def get_reports(industry: Optional[str] = None, search: Optional[str] = None):
    results = db_data["reports"]
    if industry:
        results = [r for r in results if r.get("industry") == industry]
    if search:
        s = search.lower()
        results = [r for r in results if s in r.get("title", "").lower() or s in r.get("description", "").lower()]
    return results

@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    # Ищем и по 'id', и по 'report_id' (зависит от того, как в JSON)
    report = next((r for r in db_data["reports"] if str(r.get("id")) == report_id or r.get("report_id") == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@app.get("/api/industries")
async def get_industries():
    counts = {}
    for r in db_data["reports"]:
        ind = r.get("industry", "Other")
        counts[ind] = counts.get(ind, 0) + 1
    return [{"name": name, "count": count} for name, count in counts.items()]

@app.post("/api/admin/login")
async def admin_login(data: dict):
    if data.get("password") == "flowadmin2025":
        return {"success": True, "token": "mock_token_123"}
    raise HTTPException(status_code=401, detail="Invalid password")

@app.get("/api/admin/stats")
async def get_admin_stats():
    # Считаем статистику на основе реальных данных из файла
    total_rev = sum(t.get("amount", 0) for t in db_data["payment_transactions"])
    return {
        "total_reports": len(db_data["reports"]),
        "total_revenue": total_rev,
        "paid_orders": len(db_data["payment_transactions"]),
        "active_subscriptions": len(db_data["newsletter_signups"]),
        "research_requests": len(db_data["custom_research_requests"])
    }

# Остальные эндпоинты (заглушки для работы интерфейса)
@app.post("/api/checkout")
async def create_checkout(data: dict):
    return {"url": "/success?session_id=mock_session"}
