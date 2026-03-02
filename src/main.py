from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.modules.reports.controllers.report_controller import router as reports_router

app = FastAPI(
    title="AegisAI Connectors - Reports API",
    description="Report generation and storage pipeline",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reports_router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "aegisai-connectors"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
