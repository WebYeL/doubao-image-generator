"""
配置管理模块
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# 加载环境变量
load_dotenv()


class Settings(BaseSettings):
    """应用配置"""

    # API配置
    ARK_API_KEY: str = ""
    ARK_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"
    ARK_MODEL_NAME: str = "doubao-seedream-5-0-260128"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # 图片存储配置
    IMAGE_STORAGE_PATH: str = "./generated_images"
    IMAGE_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_PROMPT_LENGTH: int = 2000
    MIN_PROMPT_LENGTH: int = 1

    # 请求限制
    MAX_IMAGES_PER_REQUEST: int = 4
    MAX_REQUESTS_PER_MINUTE: int = 10
    MAX_REQUESTS_PER_DAY: int = 100

    # 视频生成配置
    VIDEO_MODEL_NAME: str = "doubao-seedance-2-0-pro-260416"
    VIDEO_STORAGE_PATH: str = "./generated_videos"
    VIDEO_POLL_INTERVAL: int = 10  # 轮询间隔(秒)
    VIDEO_MAX_POLL_TIME: int = 600  # 最大轮询时间(秒)

    # CORS配置
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


def get_storage_path() -> Path:
    """获取图片存储路径"""
    path = Path(settings.IMAGE_STORAGE_PATH)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_video_storage_path() -> Path:
    """获取视频存储路径"""
    path = Path(settings.VIDEO_STORAGE_PATH)
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_api_key() -> bool:
    """验证API Key是否配置"""
    if not settings.ARK_API_KEY:
        raise ValueError("ARK_API_KEY environment variable is not set")
    return True
