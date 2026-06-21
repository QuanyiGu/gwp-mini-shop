"""FastAPI 应用入口 - TDD GREEN阶段"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime


def create_app() -> FastAPI:
    """创建并配置FastAPI应用"""
    app = FastAPI(
        title="GWP的小店 API",
        description="自然好味，从田间到舌尖",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    from app.api.routes import router
    app.include_router(router)

    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat()
        }

    return app


app = create_app()
