"""
视频生成服务 - 封装Doubao Seedance API调用
"""
import os
import uuid
import logging
import asyncio
import time
import httpx
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from volcenginesdkarkruntime import Ark

from ..config import settings, get_video_storage_path
from ..models import (
    VideoGenerateRequest,
    VideoFromImageRequest,
    VideoData,
    VideoGenerateResponse,
    VideoInfo,
    VideoTaskStatusResponse
)
from .storage import video_history_storage

logger = logging.getLogger(__name__)

# 后台任务状态存储
_background_tasks: Dict[str, Dict[str, Any]] = {}
_task_lock = threading.Lock()
_executor = ThreadPoolExecutor(max_workers=3)


class VideoService:
    """视频生成服务类"""

    def __init__(self):
        self.client = None
        self.storage_path = get_video_storage_path()
        self._init_client()

    def _init_client(self) -> None:
        """初始化Doubao API客户端"""
        try:
            self.client = Ark(
                base_url="https://ark.cn-beijing.volces.com/api/v3",
                api_key=settings.ARK_API_KEY
            )
            logger.info("Doubao API client initialized for video service")
        except Exception as e:
            logger.error(f"Failed to initialize Doubao API client: {e}")
            raise

    def _generate_video_id(self) -> str:
        """生成唯一的视频ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"vid_{timestamp}_{unique_id}"

    def _store_task_status(self, task_id: str, status: str, video_url: str = None,
                           error: str = None, video_data = None):
        """存储任务状态"""
        with _task_lock:
            _background_tasks[task_id] = {
                "status": status,
                "video_url": video_url,
                "error": error,
                "video_data": video_data,
                "updated_at": datetime.now()
            }
            logger.info(f"[{task_id}] Status updated: {status}")

    def _get_task_status_local(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        with _task_lock:
            return _background_tasks.get(task_id)

    def _background_generate_video(self, task_id: str, api_task_id: str,
                                   prompt: str, ratio: str, resolution: str, duration: int,
                                   watermark: bool, video_type: str,
                                   image_url: str = None, image_base64: str = None):
        """后台生成视频"""
        try:
            logger.info(f"[{task_id}] Background task started, API task: {api_task_id}")
            self._store_task_status(task_id, "running")

            # 轮询任务状态
            video_url = self._poll_api_status(api_task_id)

            if video_url:
                # 下载视频到本地
                local_result = self._download_video(video_url, task_id)

                video_data = VideoData(
                    id=task_id,
                    url=video_url,
                    local_path=local_result["path"] if local_result else None,
                    duration=duration,
                    width=local_result.get("width", 0) if local_result else 0,
                    height=local_result.get("height", 0) if local_result else 0,
                    size_bytes=local_result.get("size") if local_result else None
                )

                # 保存到历史记录
                video_info = VideoInfo(
                    id=task_id,
                    prompt=prompt or "Video generation",
                    resolution=resolution,
                    aspect_ratio=ratio,
                    duration=duration,
                    created_at=datetime.now(),
                    url=video_url,
                    local_path=local_result["path"] if local_result else None,
                    width=local_result.get("width", 0) if local_result else 0,
                    height=local_result.get("height", 0) if local_result else 0,
                    size_bytes=local_result.get("size") if local_result else None
                )
                try:
                    video_history_storage.add(video_info)
                    logger.info(f"[{task_id}] Saved to history")
                except Exception as e:
                    logger.error(f"[{task_id}] Failed to save to history: {e}")

                self._store_task_status(task_id, "succeeded", video_url=video_url,
                                       video_data=video_data)
                logger.info(f"[{task_id}] Video generation completed: {video_url}")
            else:
                self._store_task_status(task_id, "failed", error="Video generation failed or timed out")
                logger.error(f"[{task_id}] Video generation failed")

        except Exception as e:
            logger.error(f"[{task_id}] Background task error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self._store_task_status(task_id, "failed", error=str(e))

    def _poll_api_status(self, task_id: str) -> Optional[str]:
        """轮询API任务状态"""
        status_url = f"https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}"
        headers = {"Authorization": f"Bearer {settings.ARK_API_KEY}"}

        max_polls = settings.VIDEO_MAX_POLL_TIME // settings.VIDEO_POLL_INTERVAL
        poll_count = 0

        logger.info(f"[API] Polling status for: {task_id}")

        while poll_count < max_polls:
            try:
                with httpx.Client(timeout=60.0) as client:
                    response = client.get(status_url, headers=headers)
                    response.raise_for_status()

                result = response.json()
                logger.info(f"[API {task_id}] Response: {result}")

                # 解析状态 - API直接返回任务对象，不是 {data: {...}}
                task_data = result.get("data", result)

                # 处理可能的对象结构
                if hasattr(task_data, 'status'):
                    status = task_data.status
                    content = task_data.content if hasattr(task_data, 'content') else None
                    if content and hasattr(content, 'video_url'):
                        video_url = content.video_url
                    else:
                        video_url = None
                else:
                    # 字典结构
                    status = task_data.get("status")
                    content = task_data.get("content", {})
                    if isinstance(content, dict):
                        video_url = content.get("video_url")
                    else:
                        video_url = None

                logger.info(f"[API {task_id}] Status: {status}")

                if status == "succeeded":
                    if video_url:
                        logger.info(f"[API {task_id}] Video URL: {video_url}")
                        return video_url
                    # content可能在task_data顶层
                    for key in ["video_url", "content.video_url", "output.video_url"]:
                        if key in task_data:
                            return task_data[key]
                    # 尝试其他位置
                    if hasattr(task_data, 'video_url'):
                        return task_data.video_url
                    logger.warning(f"[API {task_id}] Succeeded but no video URL found")
                    return None

                elif status == "failed":
                    logger.error(f"[API {task_id}] Task failed")
                    return None

                # 继续等待
                poll_count += 1
                logger.info(f"[API {task_id}] Waiting... ({poll_count}/{max_polls})")
                time.sleep(settings.VIDEO_POLL_INTERVAL)

            except Exception as e:
                logger.error(f"[API {task_id}] Error: {e}")
                poll_count += 1
                time.sleep(settings.VIDEO_POLL_INTERVAL)

        logger.warning(f"[API {task_id}] Polling timed out")
        return None

    def _download_video(self, url: str, video_id: str) -> Optional[Dict[str, Any]]:
        """下载视频到本地"""
        try:
            logger.info(f"[{video_id}] Downloading video from: {url}")
            with httpx.Client(timeout=120.0) as client:
                response = client.get(url)
                response.raise_for_status()

            content = response.content
            size_bytes = len(content)

            filename = f"{video_id}.mp4"
            filepath = self.storage_path / filename

            with open(filepath, "wb") as f:
                f.write(content)

            logger.info(f"[{video_id}] Downloaded to {filepath}, size: {size_bytes}")

            return {"path": str(filepath), "size": size_bytes}

        except Exception as e:
            logger.error(f"[{video_id}] Download failed: {e}")
            return None

    async def generate_video(self, request: VideoGenerateRequest) -> VideoGenerateResponse:
        """生成视频（异步模式）"""
        try:
            if not settings.ARK_API_KEY:
                return VideoGenerateResponse(success=False, message="API key not configured")

            task_id = self._generate_video_id()
            logger.info(f"[{task_id}] Starting video generation")

            ratio = request.aspect_ratio.value if request.aspect_ratio else "16:9"
            duration = min(max(request.duration, 5), 15)
            # resolution 使用 1080p 格式
            resolution = "1080p" if ratio in ["16:9", "9:16"] else "720p"

            content = [{"type": "text", "text": request.prompt}]

            # 创建API任务
            try:
                create_result = self.client.content_generation.tasks.create(
                    model=settings.VIDEO_MODEL_NAME,
                    content=content,
                    ratio=ratio,
                    duration=duration,
                    watermark=request.watermark if hasattr(request, 'watermark') else True,
                    generate_audio=True
                )
                api_task_id = create_result.id
                logger.info(f"[{task_id}] API task created: {api_task_id}")
            except Exception as e:
                logger.error(f"[{task_id}] Failed to create API task: {e}")
                return VideoGenerateResponse(success=False, message=f"Failed to create task: {str(e)}")

            self._store_task_status(task_id, "pending")

            _executor.submit(
                self._background_generate_video,
                task_id, api_task_id, request.prompt, ratio, resolution, duration,
                request.watermark if hasattr(request, 'watermark') else True,
                "text2video"
            )

            return VideoGenerateResponse(
                success=True,
                message="Video generation task submitted",
                task_id=task_id
            )

        except Exception as e:
            logger.error(f"[{task_id}] Error: {e}")
            return VideoGenerateResponse(success=False, message=f"Error: {str(e)}")

    async def generate_video_from_image(self, request: VideoFromImageRequest) -> VideoGenerateResponse:
        """图生视频（异步模式）"""
        try:
            if not settings.ARK_API_KEY:
                return VideoGenerateResponse(success=False, message="API key not configured")

            if not request.image_url and not request.image_base64:
                return VideoGenerateResponse(
                    success=False,
                    message="Either image_url or image_base64 must be provided"
                )

            task_id = self._generate_video_id()
            logger.info(f"[{task_id}] Starting image-to-video generation")

            ratio = request.aspect_ratio.value if request.aspect_ratio else "16:9"
            duration = min(max(request.duration, 5), 15)
            # resolution 使用 1080p 格式
            resolution = "1080p" if ratio in ["16:9", "9:16"] else "720p"

            # 构建提示词（包含参数）
            prompt_text = f"{request.prompt} --resolution {resolution} --duration {duration} --watermark {request.watermark if hasattr(request, 'watermark') else True}"

            content = [
                {"type": "text", "text": prompt_text}
            ]
            if request.image_url:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": request.image_url}
                })
            elif request.image_base64:
                # base64 转 data URI
                data_uri = request.image_base64 if request.image_base64.startswith('data:') else f"data:image/png;base64,{request.image_base64}"
                content.append({
                    "type": "image_url",
                    "image_url": {"url": data_uri}
                })

            try:
                create_result = self.client.content_generation.tasks.create(
                    model=settings.VIDEO_MODEL_NAME,
                    content=content
                )
                api_task_id = create_result.id
                logger.info(f"[{task_id}] API task created: {api_task_id}")
            except Exception as e:
                logger.error(f"[{task_id}] Failed to create API task: {e}")
                return VideoGenerateResponse(success=False, message=f"Failed to create task: {str(e)}")

            self._store_task_status(task_id, "pending")

            _executor.submit(
                self._background_generate_video,
                task_id, api_task_id, request.prompt, ratio, resolution, duration,
                request.watermark if hasattr(request, 'watermark') else True,
                "image2video",
                request.image_url if hasattr(request, 'image_url') else None,
                request.image_base64 if hasattr(request, 'image_base64') else None
            )

            return VideoGenerateResponse(
                success=True,
                message="Video generation task submitted",
                task_id=task_id
            )

        except Exception as e:
            logger.error(f"[{task_id}] Error: {e}")
            return VideoGenerateResponse(success=False, message=f"Error: {str(e)}")

    async def get_task_status(self, task_id: str) -> VideoTaskStatusResponse:
        """查询任务状态"""
        try:
            task_info = self._get_task_status_local(task_id)
            logger.info(f"[{task_id}] get_task_status called, found: {task_info is not None}")

            if not task_info:
                return VideoTaskStatusResponse(
                    task_id=task_id,
                    status="not_found",
                    error="Task not found",
                    message="Task not found"
                )

            status = task_info["status"]

            if status == "succeeded":
                video_data = task_info.get("video_data")
                if video_data:
                    video_info = VideoInfo(
                        id=video_data.id,
                        prompt="Video generation",
                        resolution="720p",
                        aspect_ratio="16:9",
                        duration=video_data.duration,
                        created_at=datetime.now(),
                        url=video_data.url,
                        local_path=video_data.local_path,
                        width=video_data.width,
                        height=video_data.height,
                        size_bytes=video_data.size_bytes
                    )
                    video_history_storage.add(video_info)

                return VideoTaskStatusResponse(
                    task_id=task_id,
                    status="succeeded",
                    progress=100,
                    video_url=task_info.get("video_url"),
                    message="Video generation completed"
                )

            elif status == "failed":
                return VideoTaskStatusResponse(
                    task_id=task_id,
                    status="failed",
                    error=task_info.get("error"),
                    message="Video generation failed"
                )

            else:  # pending, running
                return VideoTaskStatusResponse(
                    task_id=task_id,
                    status=status,
                    progress=0 if status == "pending" else 50,
                    message="Video generation in progress"
                )

        except Exception as e:
            logger.error(f"[{task_id}] get_task_status error: {e}")
            return VideoTaskStatusResponse(
                task_id=task_id,
                status="failed",
                error=str(e),
                message="Failed to get task status"
            )

    async def get_video_info(self, video_id: str) -> Optional[VideoInfo]:
        """获取视频信息"""
        return video_history_storage.get(video_id)

    async def get_history(self, page: int = 1, page_size: int = 20):
        """获取生成历史"""
        videos, total = video_history_storage.list(page, page_size)

        items = []
        for video in videos:
            items.append({
                "id": video.id,
                "prompt": video.prompt[:50] + "..." if len(video.prompt) > 50 else video.prompt,
                "resolution": video.resolution,
                "aspect_ratio": video.aspect_ratio,
                "duration": video.duration,
                "thumbnail_url": video.url,
                "created_at": video.created_at,
                "width": video.width,
                "height": video.height
            })

        return {
            "success": True,
            "data": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def delete_video(self, video_id: str) -> bool:
        """删除视频"""
        video = await self.get_video_info(video_id)
        if not video:
            return False

        if video.local_path and os.path.exists(video.local_path):
            try:
                os.remove(video.local_path)
                logger.info(f"Deleted local file: {video.local_path}")
            except Exception as e:
                logger.error(f"Failed to delete file: {e}")

        return video_history_storage.delete(video_id)

    async def clear_history(self) -> int:
        """清空所有历史记录"""
        videos, _ = video_history_storage.list(page=1, page_size=10000)

        for video in videos:
            if video.local_path and os.path.exists(video.local_path):
                try:
                    os.remove(video.local_path)
                except Exception as e:
                    logger.error(f"Failed to delete file: {e}")

        count = video_history_storage.clear()
        logger.info(f"Cleared {count} video records")

        return count

    def check_health(self) -> Dict[str, Any]:
        """健康检查"""
        _, total = video_history_storage.list(page=1, page_size=10000)

        return {
            "status": "healthy",
            "api_key_configured": bool(settings.ARK_API_KEY),
            "video_model_configured": bool(settings.VIDEO_MODEL_NAME),
            "video_count": total,
            "storage_path": str(self.storage_path)
        }


# 全局单例
video_service = VideoService()
