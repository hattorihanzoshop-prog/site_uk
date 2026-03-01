import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Flow Consulting API - Mock Mode")

# Настройка CORS для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ДАННЫЕ ИЗ PRD И README ---
# Здесь те самые 15 отчетов, которые были зашиты в инициализацию
MOCK_REPORTS = [
    {
        "_id": "1",
        "title": "Global AI in Healthcare Market 2025",
        "industry": "Healthcare & Pharmaceuticals",
        "category": "Market Analysis",
        "description": "Comprehensive analysis of AI implementation in modern healthcare systems.",
        "prices": {"single": 2800, "multi": 4500, "enterprise": 7500},
        "featured": True,
        "image_url": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?q=80&w=2070",
        "key_insights": ["AI reduces diagnostics time by 40%", "Market growth at 25% CAGR"],
        "specifications": {"format": "PDF", "pages": "180", "published": "Jan 2026"}
    },
    {
        "_id": "2",
        "title": "Fintech Revolution: Digital Banking 2026",
        "industry": "Financial Services & Banking",
        "category": "Strategic Outlook",
        "description": "The shift from traditional to neobanking in emerging markets.",
        "prices": {"single": 3200, "multi": 5200, "enterprise": 8500},
        "featured": True,
        "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070",
        "key_insights": ["70% of users prefer mobile-first banking", "Blockchain security is top priority"],
        "specifications": {"format": "PDF", "pages": "220", "published": "Feb 2026"}
    },
    # Можно добавить остальные 13 отчетов аналогично...
]

# Хранилище для лидов (в памяти)
submissions = {
    "newsletter": [],
    "contact": [],
    "custom_research": []
}

# --- ЭНДПОИНТЫ (MOCK ЛОГИКА) ---

@app.get("/api/reports")
async def get_reports(
    industry: Optional[str] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None
):
    results = MOCK_REPORTS
    if industry:
        results = [r for r in results if r["industry"] == industry]
    if search:
        s = search.lower()
        results = [r for r in results if s in r["title"].lower() or s in r["description"].lower()]
    if featured is not None:
        results = [r for r in results if r["featured"] == featured]
    return results

@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    report = next((r for r in MOCK_REPORTS if r["_id"] == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@app.get("/api/industries")
async def get_industries():
    # Автоматический подсчет кол-ва отчетов по отраслям для секции Industries
    industries = {}
    for r in MOCK_REPORTS:
        industries[r["industry"]] = industries.get(r["industry"], 0) + 1
    return [{"name": name, "count": count} for name, count in industries.items()]

@app.post("/api/admin/login")
async def admin_login(data: dict):
    if data.get("password") == "flowadmin2025":
        return {"success": True, "token": "mock_token_123"}
    raise HTTPException(status_code=401, detail="Invalid password")

@app.get("/api/admin/stats")
async def get_admin_stats():
    return {
        "total_reports": len(MOCK_REPORTS),
        "total_revenue": 145200,
        "paid_orders": 24,
        "active_subscriptions": len(submissions["newsletter"]),
        "research_requests": len(submissions["custom_research"])
    }

# Заглушка для Stripe, чтобы не требовать ключи при просмотре
@app.post("/api/checkout")
async def create_checkout(data: dict):
    return {"url": "/success?session_id=mock_session"}

@app.get("/api/checkout/status/{session_id}")
async def check_status(session_id: str):
    return {"status": "paid"}
