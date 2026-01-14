from fastapi import FastAPI
from app.routers import content
from app.routers import approval
from app.api import auth
from app.integrations.linkedin.oauth import router as linkedin_router
from dotenv import load_dotenv
from app.routers import brand_profiles
load_dotenv()

app = FastAPI(title="AI Social Automation System", debug=True)

app.include_router(content.router, prefix="/content")
app.include_router(approval.router, prefix="/approval", tags=["approval"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(linkedin_router)   # 👈 ONLY ONCE

@app.get("/")
def root():
    return {"status": "AI Social Automation System Running"}

app.include_router(brand_profiles.router)
