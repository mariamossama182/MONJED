from fastapi import FastAPI

from app.api.flood import router as flood_router

from app.api.community_reports import router as community_reports_router
    
app = FastAPI(
    title="MONJED API",
    description="Disaster risk interpretation and action support platform",
    version="0.1.0"
)


app.include_router(flood_router)
app.include_router(community_reports_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to MONJED API"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "MONJED API"
    }