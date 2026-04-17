"""
API路由 - 图片和视频生成相关接口
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional
import os
import logging

from ..models import (
    ImageGenerateRequest,
    ImageGenerateResponse,
    ImageToImageRequest,
    ImageInfo,
    ImageHistoryResponse,
    VideoGenerateRequest,
    VideoGenerateResponse,
    VideoFromImageRequest,
    VideoInfo,
    VideoHistoryResponse,
    VideoTaskStatusResponse,
    ErrorResponse
)
from ..services.image_service import image_service
from ..services.video_service import video_service
from ..config import settings

logger = logging.getLogger(__name__)


# ==================== 图片相关路由 ====================

images_router = APIRouter(prefix="/images", tags=["images"])


@images_router.post(
    "/generate",
    response_model=ImageGenerateResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="生成图片",
    description="使用AI模型生成图片"
)
async def generate_images(request: ImageGenerateRequest):
    """
    生成图片接口

    - **prompt**: 图片描述提示词（必填）
    - **size**: 图片尺寸（1K/2K/4K/竖图1K/竖图2K）
    - **n**: 生成数量（1-4张）
    - **style**: 风格预设（可选）
    - **negative_prompt**: 负向提示词（可选）
    - **watermark**: 是否添加水印
    """
    try:
        if len(request.prompt) < settings.MIN_PROMPT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Prompt must be at least {settings.MIN_PROMPT_LENGTH} characters"
            )

        if len(request.prompt) > settings.MAX_PROMPT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Prompt must not exceed {settings.MAX_PROMPT_LENGTH} characters"
            )

        if request.n > settings.MAX_IMAGES_PER_REQUEST:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot generate more than {settings.MAX_IMAGES_PER_REQUEST} images at once"
            )

        response = await image_service.generate_images(request)

        if not response.success:
            raise HTTPException(
                status_code=500,
                detail=response.message
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@images_router.post(
    "/generate-from-image",
    response_model=ImageGenerateResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="图生图",
    description="根据输入图片生成新图片"
)
async def generate_images_from_image(request: ImageToImageRequest):
    """
    图生图接口

    - **prompt**: 图片描述提示词（必填）
    - **image_url**: 输入图片URL(与image_base64二选一)
    - **image_base64**: 输入图片base64数据(与image_url二选一)
    - **size**: 图片尺寸（1K/2K/4K/竖图1K/竖图2K）
    - **n**: 生成数量（1-4张）
    - **style**: 风格预设（可选）
    - **negative_prompt**: 负向提示词（可选）
    - **watermark**: 是否添加水印
    """
    try:
        if len(request.prompt) < settings.MIN_PROMPT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Prompt must be at least {settings.MIN_PROMPT_LENGTH} characters"
            )

        if len(request.prompt) > settings.MAX_PROMPT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Prompt must not exceed {settings.MAX_PROMPT_LENGTH} characters"
            )

        if request.n > settings.MAX_IMAGES_PER_REQUEST:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot generate more than {settings.MAX_IMAGES_PER_REQUEST} images at once"
            )

        if not request.image_url and not request.image_base64:
            raise HTTPException(
                status_code=400,
                detail="Either image_url or image_base64 must be provided"
            )

        response = await image_service.generate_images_from_image(request)

        if not response.success:
            raise HTTPException(
                status_code=500,
                detail=response.message
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_images_from_image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@images_router.get(
    "/{image_id}",
    response_model=ImageInfo,
    responses={404: {"model": ErrorResponse}},
    summary="获取图片详情",
    description="根据图片ID获取详细信息"
)
async def get_image(image_id: str):
    """获取单张图片的详细信息"""
    image_info = await image_service.get_image_info(image_id)

    if not image_info:
        raise HTTPException(
            status_code=404,
            detail=f"Image {image_id} not found"
        )

    return image_info


@images_router.get(
    "/history/list",
    response_model=ImageHistoryResponse,
    summary="获取生成历史",
    description="获取图片生成历史记录"
)
async def get_image_history(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量")
):
    """获取图片生成历史"""
    return await image_service.get_history(page, page_size)


@images_router.delete(
    "/{image_id}",
    responses={
        200: {"description": "删除成功"},
        404: {"model": ErrorResponse}
    },
    summary="删除图片",
    description="删除指定ID的图片"
)
async def delete_image(image_id: str):
    """删除指定的图片"""
    success = await image_service.delete_image(image_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Image {image_id} not found"
        )

    return {"success": True, "message": "Image deleted successfully"}


@images_router.delete(
    "/history/clear",
    summary="清空历史",
    description="清空所有生成历史"
)
async def clear_image_history():
    """清空所有生成历史"""
    count = await image_service.clear_history()

    return {
        "success": True,
        "message": f"Cleared {count} records",
        "count": count
    }


@images_router.get(
    "/download/{image_id}",
    responses={
        200: {"content": {"image/png": {}}},
        404: {"model": ErrorResponse}
    },
    summary="下载图片",
    description="下载指定ID的图片文件"
)
async def download_image(image_id: str):
    """下载图片到本地"""
    image_info = await image_service.get_image_info(image_id)

    if not image_info:
        raise HTTPException(
            status_code=404,
            detail=f"Image {image_id} not found"
        )

    if not image_info.local_path or not os.path.exists(image_info.local_path):
        raise HTTPException(
            status_code=404,
            detail="Local file not found"
        )

    return FileResponse(
        path=image_info.local_path,
        filename=f"{image_id}.png",
        media_type="image/png"
    )


@images_router.get(
    "/serve/{image_id}",
    summary="获取图片",
    description="通过API获取图片（可用于前端展示）"
)
async def serve_image(image_id: str):
    """获取图片（用于前端展示）"""
    image_info = await image_service.get_image_info(image_id)

    if not image_info:
        raise HTTPException(
            status_code=404,
            detail=f"Image {image_id} not found"
        )

    if image_info.local_path and os.path.exists(image_info.local_path):
        return FileResponse(path=image_info.local_path)

    if image_info.url:
        return {"url": image_info.url}

    raise HTTPException(
        status_code=404,
        detail="Image file not found"
    )


# ==================== 视频相关路由 ====================

videos_router = APIRouter(prefix="/videos", tags=["videos"])


@videos_router.post(
    "/generate",
    response_model=VideoGenerateResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="文生视频",
    description="使用AI模型根据文本描述生成视频"
)
async def generate_video(request: VideoGenerateRequest):
    """
    文生视频接口

    - **prompt**: 视频描述提示词（必填）
    - **resolution**: 视频分辨率（480p/720p/1080p）
    - **aspect_ratio**: 宽高比（16:9/4:3/1:1/3:4/9:16/21:9/adaptive）
    - **duration**: 视频时长（2-12秒）
    - **watermark**: 是否添加水印
    """
    try:
        if len(request.prompt) < settings.MIN_PROMPT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Prompt must be at least {settings.MIN_PROMPT_LENGTH} characters"
            )

        if len(request.prompt) > settings.MAX_PROMPT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Prompt must not exceed {settings.MAX_PROMPT_LENGTH} characters"
            )

        response = await video_service.generate_video(request)

        if not response.success:
            raise HTTPException(
                status_code=500,
                detail=response.message
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@videos_router.post(
    "/generate-from-image",
    response_model=VideoGenerateResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="图生视频",
    description="根据输入图片生成视频"
)
async def generate_video_from_image(request: VideoFromImageRequest):
    """
    图生视频接口

    - **prompt**: 视频描述提示词（必填）
    - **image_url**: 输入图片URL(与image_base64二选一)
    - **image_base64**: 输入图片base64数据(与image_url二选一)
    - **resolution**: 视频分辨率（480p/720p/1080p）
    - **aspect_ratio**: 宽高比（16:9/4:3/1:1/3:4/9:16/21:9/adaptive）
    - **duration**: 视频时长（2-12秒）
    - **watermark**: 是否添加水印
    """
    try:
        if len(request.prompt) < settings.MIN_PROMPT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Prompt must be at least {settings.MIN_PROMPT_LENGTH} characters"
            )

        if len(request.prompt) > settings.MAX_PROMPT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Prompt must not exceed {settings.MAX_PROMPT_LENGTH} characters"
            )

        if not request.image_url and not request.image_base64:
            raise HTTPException(
                status_code=400,
                detail="Either image_url or image_base64 must be provided"
            )

        response = await video_service.generate_video_from_image(request)

        if not response.success:
            raise HTTPException(
                status_code=500,
                detail=response.message
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_video_from_image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@videos_router.get(
    "/{video_id}",
    response_model=VideoInfo,
    responses={404: {"model": ErrorResponse}},
    summary="获取视频详情",
    description="根据视频ID获取详细信息"
)
async def get_video(video_id: str):
    """获取单条视频的详细信息"""
    video_info = await video_service.get_video_info(video_id)

    if not video_info:
        raise HTTPException(
            status_code=404,
            detail=f"Video {video_id} not found"
        )

    return video_info


@videos_router.get(
    "/status/{task_id}",
    response_model=VideoTaskStatusResponse,
    summary="查询任务状态",
    description="查询视频生成任务的状态"
)
async def get_video_task_status(task_id: str):
    """查询视频生成任务状态"""
    return await video_service.get_task_status(task_id)


@videos_router.get(
    "/history/list",
    summary="获取视频历史",
    description="获取视频生成历史记录"
)
async def get_video_history(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量")
):
    """获取视频生成历史"""
    return await video_service.get_history(page, page_size)


@videos_router.delete(
    "/{video_id}",
    responses={
        200: {"description": "删除成功"},
        404: {"model": ErrorResponse}
    },
    summary="删除视频",
    description="删除指定ID的视频"
)
async def delete_video(video_id: str):
    """删除指定的视频"""
    success = await video_service.delete_video(video_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Video {video_id} not found"
        )

    return {"success": True, "message": "Video deleted successfully"}


@videos_router.delete(
    "/history/clear",
    summary="清空视频历史",
    description="清空所有视频生成历史"
)
async def clear_video_history():
    """清空所有视频生成历史"""
    count = await video_service.clear_history()

    return {
        "success": True,
        "message": f"Cleared {count} records",
        "count": count
    }


@videos_router.get(
    "/download/{video_id}",
    summary="下载视频",
    description="下载指定ID的视频文件"
)
async def download_video(video_id: str):
    """下载视频到本地"""
    video_info = await video_service.get_video_info(video_id)

    if not video_info:
        raise HTTPException(
            status_code=404,
            detail=f"Video {video_id} not found"
        )

    if not video_info.local_path or not os.path.exists(video_info.local_path):
        raise HTTPException(
            status_code=404,
            detail="Local file not found"
        )

    def iterfile():
        with open(video_info.local_path, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                yield chunk

    return StreamingResponse(
        iterfile(),
        media_type="video/mp4",
        headers={
            "Content-Disposition": f'attachment; filename="{video_id}.mp4"'
        }
    )


@videos_router.get(
    "/serve/{video_id}",
    summary="获取视频",
    description="通过API获取视频（可用于前端播放）"
)
async def serve_video(video_id: str):
    """获取视频（用于前端播放）"""
    video_info = await video_service.get_video_info(video_id)

    if not video_info:
        raise HTTPException(
            status_code=404,
            detail=f"Video {video_id} not found"
        )

    if video_info.url:
        return {"url": video_info.url}

    raise HTTPException(
        status_code=404,
        detail="Video URL not available"
    )
