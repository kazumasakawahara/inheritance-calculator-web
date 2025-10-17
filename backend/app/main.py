"""FastAPI Main Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Inheritance Calculator API",
    description="日本の民法に基づく相続計算のWeb API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS設定（開発環境用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js開発サーバー
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Inheritance Calculator API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy"}


# TODO: APIルーターの追加
# from app.api import auth, cases, calculate
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(cases.router, prefix="/api/cases", tags=["cases"])
# app.include_router(calculate.router, prefix="/api/calculate", tags=["calculate"])
