"""
FastAPI 主入口 - Doubao图片/视频生成服务
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.routes import images_router, videos_router
from .models import HealthResponse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Starting Doubao Image/Video Generation Service...")
    logger.info(f"Image storage path: {settings.IMAGE_STORAGE_PATH}")
    logger.info(f"Video storage path: {settings.VIDEO_STORAGE_PATH}")
    logger.info(f"API Key configured: {bool(settings.ARK_API_KEY)}")

    # 初始化存储目录
    os.makedirs(settings.IMAGE_STORAGE_PATH, exist_ok=True)
    os.makedirs(settings.VIDEO_STORAGE_PATH, exist_ok=True)

    yield

    logger.info("Shutting down Doubao Image/Video Generation Service...")


# 创建应用
app = FastAPI(
    title="Doubao Image/Video Generation API",
    description="""
    基于Doubao-Seedream-5.0-lite的AI图片生成服务和Seedance 2.0的视频生成服务

    ## 功能

    - AI图片生成（文生图、图生图）
    - AI视频生成（文生视频、图生视频）
    - 历史记录管理
    - 文件下载

    ## 使用说明

    1. 首先确保配置了ARK_API_KEY环境变量
    2. 图片生成: POST /api/v1/images/generate
    3. 视频生成: POST /api/v1/videos/generate
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# CORS中间件（处理实际请求的响应头）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
)


# 全局预检处理（兜底：确保所有 OPTIONS 请求返回正确 CORS 头）
@app.options("/{full_path:path}", include_in_schema=False)
async def preflight_handler(request: Request, full_path: str):
    origin = request.headers.get("origin", "*")
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Requested-With,Accept",
        }
    )


# 注册路由
app.include_router(images_router, prefix="/api/v1")
app.include_router(videos_router, prefix="/api/v1")


@app.get("/", tags=["root"])
async def root():
    """根路径 - 服务信息"""
    return {
        "service": "Doubao Image/Video Generation API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """健康检查接口"""
    from .services.image_service import image_service
    from .services.video_service import video_service

    image_health = image_service.check_health()
    video_health = video_service.check_health()

    return HealthResponse(
        status="healthy" if (image_health["api_key_configured"] and video_health["api_key_configured"]) else "degraded",
        version="2.0.0",
        api_key_configured=image_health["api_key_configured"]
    )


@app.get("/api/v1", tags=["root"])
async def api_v1_info():
    """API v1 信息"""
    return {
        "version": "v1",
        "features": ["image-generation", "video-generation"],
        "endpoints": {
            "images": {
                "generate": "/api/v1/images/generate",
                "generate-from-image": "/api/v1/images/generate-from-image",
                "history": "/api/v1/images/history/list",
                "download": "/api/v1/images/download/{image_id}"
            },
            "videos": {
                "generate": "/api/v1/videos/generate",
                "generate-from-image": "/api/v1/videos/generate-from-image",
                "status": "/api/v1/videos/status/{task_id}",
                "history": "/api/v1/videos/history/list",
                "download": "/api/v1/videos/download/{video_id}"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
