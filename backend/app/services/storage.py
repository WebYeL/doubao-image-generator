"""
历史记录存储模块 - 持久化存储
"""
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from threading import Lock

from ..models import ImageInfo

logger = logging.getLogger(__name__)


class HistoryStorage:
    """历史记录持久化存储"""

    def __init__(self, storage_path: str = "./data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.history_file = self.storage_path / "image_history.json"
        self.lock = Lock()
        self._history: List[dict] = []
        self._load()

    def _load(self):
        """从文件加载历史记录"""
        try:
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self._history = json.load(f)
                logger.info(f"Loaded {len(self._history)} history records")
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            self._history = []

    def _save(self):
        """保存历史记录到文件"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self._history, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def add(self, image_info: ImageInfo):
        """添加记录"""
        with self.lock:
            record = {
                "id": image_info.id,
                "prompt": image_info.prompt,
                "size": image_info.size,
                "style": image_info.style,
                "created_at": image_info.created_at.isoformat(),
                "url": image_info.url,
                "local_path": image_info.local_path,
                "width": image_info.width,
                "height": image_info.height,
                "size_bytes": image_info.size_bytes
            }
            self._history.insert(0, record)
            self._save()

    def get(self, image_id: str) -> Optional[ImageInfo]:
        """获取单条记录"""
        with self.lock:
            for record in self._history:
                if record["id"] == image_id:
                    return self._to_image_info(record)
        return None

    def list(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[ImageInfo], int]:
        """获取分页列表"""
        with self.lock:
            total = len(self._history)
            start = (page - 1) * page_size
            end = start + page_size
            records = self._history[start:end]
            return [self._to_image_info(r) for r in records], total

    def delete(self, image_id: str) -> bool:
        """删除记录"""
        with self.lock:
            for i, record in enumerate(self._history):
                if record["id"] == image_id:
                    self._history.pop(i)
                    self._save()
                    return True
        return False

    def clear(self) -> int:
        """清空所有记录"""
        with self.lock:
            count = len(self._history)
            self._history.clear()
            self._save()
            return count

    def _to_image_info(self, record: dict) -> ImageInfo:
        """将字典转换为ImageInfo对象"""
        return ImageInfo(
            id=record["id"],
            prompt=record["prompt"],
            size=record["size"],
            style=record.get("style"),
            created_at=datetime.fromisoformat(record["created_at"]),
            url=record["url"],
            local_path=record.get("local_path"),
            width=record.get("width", 0),
            height=record.get("height", 0),
            size_bytes=record.get("size_bytes")
        )


# 全局实例
history_storage = HistoryStorage()
