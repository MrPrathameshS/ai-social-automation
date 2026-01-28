from fastapi import FastAPI

from app.routers import content, approval, brands, brand_profiles, topics, brand_rules
from app.api import auth

from app.integrations.linkedin.routers import router as linkedin_router
from workers.scheduler import start_scheduler
app = FastAPI(title="AI Social Automation System", debug=True)

app.include_router(auth.router, tags=["auth"])   # 🔹 IMPORTANT

app.include_router(content.router, prefix="/content", tags=["content"])
app.include_router(approval.router, prefix="/approval", tags=["approval"])

app.include_router(brand_profiles.router, tags=["brand_profiles"])
app.include_router(brands.router, tags=["brands"])
app.include_router(topics.router, tags=["topics"])
app.include_router(
    brand_rules.router,
    prefix="/rules",
    tags=["brand_rules"]
)


app.include_router(linkedin_router)


@app.get("/")
def root():
    return {"status": "AI Social Automation System Running"}

from fastapi.routing import APIRoute

@app.get("/__debug/routes")
def debug_routes():
    return [
        {
            "path": route.path,
            "methods": list(route.methods),
            "name": route.name,
        }
        for route in app.routes
        if isinstance(route, APIRoute)
    ]

from workers.scheduler import start_scheduler

@app.on_event("startup")
def startup_event():
    print("🚀 App startup event triggered")
    start_scheduler()