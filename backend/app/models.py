"""
数据模型定义
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ImageSize(str, Enum):
    """支持的图片尺寸"""
    SIZE_1K = "1K"
    SIZE_2K = "2K"
    SIZE_4K = "4K"
    PORTRAIT_1K = "竖图1K"
    PORTRAIT_2K = "竖图2K"


class ImageGenerateRequest(BaseModel):
    """图片生成请求模型"""
    prompt: str = Field(..., min_length=1, max_length=2000, description="图片描述提示词")
    size: ImageSize = Field(default=ImageSize.SIZE_2K, description="图片尺寸")
    n: int = Field(default=1, ge=1, le=4, description="生成图片数量")
    style: Optional[str] = Field(default=None, description="风格预设")
    negative_prompt: Optional[str] = Field(default=None, max_length=500, description="负向提示词")
    watermark: bool = Field(default=True, description="是否添加水印")
    response_format: str = Field(default="url", description="返回格式: url或b64_json")


class ImageToImageRequest(ImageGenerateRequest):
    """图生图请求模型"""
    image_url: Optional[str] = Field(default=None, description="输入图片URL")
    image_base64: Optional[str] = Field(default=None, description="输入图片Base64数据")

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()


class ImageData(BaseModel):
    """单张图片数据"""
    id: str = Field(..., description="图片唯一标识")
    url: str = Field(..., description="图片URL")
    local_path: Optional[str] = Field(default=None, description="本地存储路径")
    width: int = Field(default=0, description="图片宽度")
    height: int = Field(default=0, description="图片高度")
    size_bytes: Optional[int] = Field(default=None, description="文件大小(字节)")


class ImageGenerateResponse(BaseModel):
    """图片生成响应模型"""
    success: bool = Field(..., description="是否成功")
    data: List[ImageData] = Field(default_factory=list, description="图片数据列表")
    message: str = Field(default="", description="响应消息")
    task_id: Optional[str] = Field(default=None, description="任务ID")


class ImageInfo(BaseModel):
    """图片信息模型"""
    id: str
    prompt: str
    size: str
    style: Optional[str] = None
    created_at: datetime
    url: str
    local_path: Optional[str] = None
    width: int = 0
    height: int = 0
    size_bytes: Optional[int] = None


class ImageHistoryItem(BaseModel):
    """历史记录项"""
    id: str
    prompt: str
    size: str
    thumbnail_url: Optional[str] = None
    created_at: datetime
    width: int = 0
    height: int = 0


class ImageHistoryResponse(BaseModel):
    """历史记录响应"""
    success: bool = True
    data: List[ImageHistoryItem] = Field(default_factory=list)
    total: int = Field(default=0, description="总数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页数量")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "healthy"
    version: str = "1.0.0"
    api_key_configured: bool = False


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = False
    error: str
    error_code: Optional[str] = None
    detail: Optional[str] = None


# ==================== 视频生成相关模型 ====================

class VideoResolution(str, Enum):
    """支持的视频分辨率"""
    RES_480P = "480p"
    RES_720P = "720p"
    RES_1080P = "1080p"


class VideoAspectRatio(str, Enum):
    """支持的视频宽高比"""
    RATIO_16_9 = "16:9"
    RATIO_4_3 = "4:3"
    RATIO_1_1 = "1:1"
    RATIO_3_4 = "3:4"
    RATIO_9_16 = "9:16"
    RATIO_21_9 = "21:9"
    RATIO_ADAPTIVE = "adaptive"


class VideoGenerateRequest(BaseModel):
    """视频生成请求模型"""
    prompt: str = Field(..., min_length=1, max_length=2000, description="视频描述提示词")
    resolution: VideoResolution = Field(default=VideoResolution.RES_720P, description="视频分辨率")
    aspect_ratio: VideoAspectRatio = Field(default=VideoAspectRatio.RATIO_16_9, description="视频宽高比")
    duration: int = Field(default=5, ge=2, le=12, description="视频时长(秒)")
    watermark: bool = Field(default=True, description="是否添加水印")

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()


class VideoFromImageRequest(BaseModel):
    """图生视频请求模型"""
    prompt: str = Field(..., min_length=1, max_length=2000, description="视频描述提示词")
    image_url: Optional[str] = Field(default=None, description="输入图片URL")
    image_base64: Optional[str] = Field(default=None, description="输入图片Base64数据")
    resolution: VideoResolution = Field(default=VideoResolution.RES_720P, description="视频分辨率")
    aspect_ratio: VideoAspectRatio = Field(default=VideoAspectRatio.RATIO_16_9, description="视频宽高比")
    duration: int = Field(default=5, ge=2, le=12, description="视频时长(秒)")
    watermark: bool = Field(default=True, description="是否添加水印")

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()


class VideoData(BaseModel):
    """单条视频数据"""
    id: str = Field(..., description="视频唯一标识")
    url: str = Field(..., description="视频URL")
    local_path: Optional[str] = Field(default=None, description="本地存储路径")
    duration: int = Field(default=0, description="视频时长(秒)")
    width: int = Field(default=0, description="视频宽度")
    height: int = Field(default=0, description="视频高度")
    size_bytes: Optional[int] = Field(default=None, description="文件大小(字节)")


class VideoGenerateResponse(BaseModel):
    """视频生成响应模型"""
    success: bool = Field(..., description="是否成功")
    data: Optional[VideoData] = Field(default=None, description="视频数据")
    message: str = Field(default="", description="响应消息")
    task_id: Optional[str] = Field(default=None, description="任务ID")


class VideoInfo(BaseModel):
    """视频信息模型"""
    id: str
    prompt: str
    resolution: str
    aspect_ratio: str
    duration: int
    created_at: datetime
    url: str
    local_path: Optional[str] = None
    width: int = 0
    height: int = 0
    size_bytes: Optional[int] = None


class VideoHistoryItem(BaseModel):
    """历史记录项"""
    id: str
    prompt: str
    resolution: str
    aspect_ratio: str
    duration: int
    thumbnail_url: Optional[str] = None
    created_at: datetime
    width: int = 0
    height: int = 0


class VideoHistoryResponse(BaseModel):
    """视频历史记录响应"""
    success: bool = True
    data: List[VideoHistoryItem] = Field(default_factory=list)
    total: int = Field(default=0, description="总数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页数量")


class VideoTaskStatusResponse(BaseModel):
    """视频任务状态响应"""
    task_id: str
    status: str  # pending / processing / completed / failed
    progress: int = Field(default=0, ge=0, le=100, description="进度百分比")
    video_url: Optional[str] = None
    error: Optional[str] = None
    message: str = Field(default="")
