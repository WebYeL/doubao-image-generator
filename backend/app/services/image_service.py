"""
图片生成服务 - 封装Doubao API调用
"""
import os
import uuid
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

import httpx
from PIL import Image
import io

from volcenginesdkarkruntime import Ark

from ..config import settings, get_storage_path
from ..models import (
    ImageGenerateRequest,
    ImageToImageRequest,
    ImageData,
    ImageGenerateResponse,
    ImageInfo,
    ImageHistoryItem,
    ImageHistoryResponse,
    ImageSize
)
from .storage import history_storage

logger = logging.getLogger(__name__)


class ImageService:
    """图片生成服务类"""

    def __init__(self):
        self.client = None
        self.storage_path = get_storage_path()
        self._executor = ThreadPoolExecutor(max_workers=3)
        self._init_client()

    def _init_client(self) -> None:
        """初始化Doubao API客户端"""
        try:
            self.client = Ark(
                base_url=settings.ARK_BASE_URL,
                api_key=settings.ARK_API_KEY
            )
            logger.info("Doubao API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Doubao API client: {e}")
            raise

    def _map_size(self, size: ImageSize) -> str:
        """映射尺寸参数到API期望的格式"""
        # API支持 "2K"、"3K" 或像素值如 "2048x2048"
        # 注意：doubao-seedream-5.0-lite 只支持 2K 和 3K
        size_mapping = {
            ImageSize.SIZE_1K: "2K",        # 1K 映射到 2K
            ImageSize.SIZE_2K: "2K",
            ImageSize.SIZE_4K: "3K",        # 4K 映射到 3K
            ImageSize.PORTRAIT_1K: "2K",    # 竖图也使用 2K
            ImageSize.PORTRAIT_2K: "2K"
        }
        return size_mapping.get(size, "2K")

    def _generate_image_id(self) -> str:
        """生成唯一的图片ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"img_{timestamp}_{unique_id}"

    async def generate_images(
        self,
        request: ImageGenerateRequest
    ) -> ImageGenerateResponse:
        """
        生成图片

        Args:
            request: 图片生成请求

        Returns:
            ImageGenerateResponse: 包含生成结果的响应
        """
        try:
            # 验证API Key
            if not settings.ARK_API_KEY:
                return ImageGenerateResponse(
                    success=False,
                    message="API key not configured"
                )

            task_id = self._generate_image_id()
            logger.info(f"Starting image generation task: {task_id}")
            logger.info(f"Prompt: {request.prompt[:100]}...")

            # 在线程池中执行同步API调用
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._executor,
                self._call_doubao_api,
                request
            )

            if result["success"]:
                # 保存到持久化存储
                for image_data in result["data"]:
                    image_info = ImageInfo(
                        id=image_data.id,
                        prompt=request.prompt,
                        size=request.size.value,
                        style=request.style,
                        created_at=datetime.now(),
                        url=image_data.url,
                        local_path=image_data.local_path,
                        width=image_data.width,
                        height=image_data.height,
                        size_bytes=image_data.size_bytes
                    )
                    history_storage.add(image_info)

                logger.info(f"Successfully generated {len(result['data'])} images")
                return ImageGenerateResponse(
                    success=True,
                    data=result["data"],
                    message=f"Successfully generated {len(result['data'])} images",
                    task_id=task_id
                )
            else:
                return ImageGenerateResponse(
                    success=False,
                    message=result.get("error", "Unknown error")
                )

        except Exception as e:
            logger.error(f"Error generating images: {e}")
            return ImageGenerateResponse(
                success=False,
                message=f"Error: {str(e)}"
            )

    async def generate_images_from_image(
        self,
        request: ImageToImageRequest
    ) -> ImageGenerateResponse:
        """
        图生图 - 根据输入图片生成新图片

        Args:
            request: 图生图请求

        Returns:
            ImageGenerateResponse: 包含生成结果的响应
        """
        try:
            # 验证API Key
            if not settings.ARK_API_KEY:
                return ImageGenerateResponse(
                    success=False,
                    message="API key not configured"
                )

            # 验证输入图片
            if not request.image_url and not request.image_base64:
                return ImageGenerateResponse(
                    success=False,
                    message="Either image_url or image_base64 must be provided"
                )

            task_id = self._generate_image_id()
            logger.info(f"Starting image-to-image generation task: {task_id}")
            logger.info(f"Prompt: {request.prompt[:100]}...")

            # 在线程池中执行同步API调用
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._executor,
                self._call_doubao_img2img_api,
                request
            )

            if result["success"]:
                # 保存到持久化存储
                for image_data in result["data"]:
                    image_info = ImageInfo(
                        id=image_data.id,
                        prompt=request.prompt,
                        size=request.size.value,
                        style=request.style,
                        created_at=datetime.now(),
                        url=image_data.url,
                        local_path=image_data.local_path,
                        width=image_data.width,
                        height=image_data.height,
                        size_bytes=image_data.size_bytes
                    )
                    history_storage.add(image_info)

                logger.info(f"Successfully generated {len(result['data'])} images from input image")
                return ImageGenerateResponse(
                    success=True,
                    data=result["data"],
                    message=f"Successfully generated {len(result['data'])} images from input image",
                    task_id=task_id
                )
            else:
                return ImageGenerateResponse(
                    success=False,
                    message=result.get("error", "Unknown error")
                )

        except Exception as e:
            logger.error(f"Error generating images from image: {e}")
            return ImageGenerateResponse(
                success=False,
                message=f"Error: {str(e)}"
            )

    def _call_doubao_api(
        self,
        request: ImageGenerateRequest
    ) -> Dict[str, Any]:
        """
        调用Doubao API文生图

        Args:
            request: 图片生成请求

        Returns:
            Dict containing success status and image data
        """
        try:
            # 构建API调用参数（使用images.generate方法）
            api_params = {
                "model": settings.ARK_MODEL_NAME,
                "prompt": request.prompt,
                "response_format": request.response_format,
                "size": self._map_size(request.size),
                "stream": False,
                "watermark": request.watermark
            }

            # 调用API（使用generate方法进行文生图）
            response = self.client.images.generate(**api_params)

            # 处理响应
            images = []
            for idx, image_data in enumerate(response.data):
                image_id = f"{self._generate_image_id()}_{idx}"

                # 下载图片到本地
                local_path = None
                width = 0
                height = 0
                size_bytes = None

                if request.response_format == "url" and image_data.url:
                    local_result = self._download_image(
                        image_data.url,
                        image_id
                    )
                    if local_result:
                        local_path = local_result["path"]
                        width = local_result["width"]
                        height = local_result["height"]
                        size_bytes = local_result["size"]

                images.append(ImageData(
                    id=image_id,
                    url=image_data.url or "",
                    local_path=local_path,
                    width=width,
                    height=height,
                    size_bytes=size_bytes
                ))

            return {"success": True, "data": images}

        except Exception as e:
            logger.error(f"Doubao API call failed: {e}")
            return {"success": False, "error": str(e)}

    def _call_doubao_img2img_api(
        self,
        request: ImageToImageRequest
    ) -> Dict[str, Any]:
        """
        调用Doubao图生图API

        Args:
            request: 图生图请求

        Returns:
            Dict containing success status and image data
        """
        try:
            # 构建API调用参数（使用images.generate方法的image参数）
            api_params = {
                "model": settings.ARK_MODEL_NAME,
                "prompt": request.prompt,
                "response_format": request.response_format,
                "size": self._map_size(request.size),
                "stream": False,
                "watermark": request.watermark
            }

            # 添加图片输入参数（使用image参数传递参考图片）
            if request.image_url:
                api_params["image"] = request.image_url
            elif request.image_base64:
                api_params["image"] = request.image_base64

            # 调用API（使用generate方法，image参数用于图生图）
            response = self.client.images.generate(**api_params)

            # 处理响应
            images = []
            for idx, image_data in enumerate(response.data):
                image_id = f"{self._generate_image_id()}_{idx}"

                # 下载图片到本地
                local_path = None
                width = 0
                height = 0
                size_bytes = None

                if request.response_format == "url" and image_data.url:
                    local_result = self._download_image(
                        image_data.url,
                        image_id
                    )
                    if local_result:
                        local_path = local_result["path"]
                        width = local_result["width"]
                        height = local_result["height"]
                        size_bytes = local_result["size"]

                images.append(ImageData(
                    id=image_id,
                    url=image_data.url or "",
                    local_path=local_path,
                    width=width,
                    height=height,
                    size_bytes=size_bytes
                ))

            return {"success": True, "data": images}

        except Exception as e:
            logger.error(f"Doubao image-to-image API call failed: {e}")
            return {"success": False, "error": str(e)}

    def _download_image(self, url: str, image_id: str) -> Optional[Dict[str, Any]]:
        """
        下载图片到本地

        Args:
            url: 图片URL
            image_id: 图片ID

        Returns:
            Dict containing image info or None if failed
        """
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url)
                response.raise_for_status()

                content = response.content
                size_bytes = len(content)

                # 获取图片尺寸
                img = Image.open(io.BytesIO(content))
                width, height = img.size

                # 生成文件名
                filename = f"{image_id}.png"
                filepath = self.storage_path / filename

                # 保存图片
                with open(filepath, "wb") as f:
                    f.write(content)

                logger.info(f"Downloaded image to {filepath}")

                return {
                    "path": str(filepath),
                    "width": width,
                    "height": height,
                    "size": size_bytes
                }

        except Exception as e:
            logger.error(f"Failed to download image {image_id}: {e}")
            return None

    async def get_image_info(self, image_id: str) -> Optional[ImageInfo]:
        """获取图片信息"""
        return history_storage.get(image_id)

    async def get_history(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> ImageHistoryResponse:
        """获取生成历史"""
        images, total = history_storage.list(page, page_size)

        items = []
        for image in images:
            items.append(ImageHistoryItem(
                id=image.id,
                prompt=image.prompt[:50] + "..." if len(image.prompt) > 50 else image.prompt,
                size=image.size,
                thumbnail_url=image.url,
                created_at=image.created_at,
                width=image.width,
                height=image.height
            ))

        return ImageHistoryResponse(
            success=True,
            data=items,
            total=total,
            page=page,
            page_size=page_size
        )

    async def delete_image(self, image_id: str) -> bool:
        """删除图片"""
        image = await self.get_image_info(image_id)
        if not image:
            return False

        # 删除本地文件
        if image.local_path and os.path.exists(image.local_path):
            try:
                os.remove(image.local_path)
                logger.info(f"Deleted local file: {image.local_path}")
            except Exception as e:
                logger.error(f"Failed to delete file: {e}")

        # 从存储中删除记录
        return history_storage.delete(image_id)

    async def clear_history(self) -> int:
        """清空所有历史记录"""
        # 获取所有图片信息
        images, _ = history_storage.list(page=1, page_size=10000)

        # 删除所有本地文件
        for image in images:
            if image.local_path and os.path.exists(image.local_path):
                try:
                    os.remove(image.local_path)
                except Exception as e:
                    logger.error(f"Failed to delete file: {e}")

        # 清空存储
        count = history_storage.clear()
        logger.info(f"Cleared {count} image records")

        return count

    def check_health(self) -> Dict[str, Any]:
        """健康检查"""
        images, count = history_storage.list(page=1, page_size=1)
        _, total = history_storage.list(page=1, page_size=10000)

        return {
            "status": "healthy",
            "api_key_configured": bool(settings.ARK_API_KEY),
            "history_count": total,
            "storage_path": str(self.storage_path)
        }


# 全局单例
image_service = ImageService()
