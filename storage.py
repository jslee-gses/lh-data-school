from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class StorageError(RuntimeError):
    """User-facing storage error."""


class GalleryStorage:
    """Read gallery data generated and committed by GitHub Actions."""

    def __init__(self, base_dir: Path) -> None:
        self.data_path = base_dir / "data" / "projects.json"
        self.sample_path = base_dir / "data" / "sample_projects.json"
        self.is_persistent = True

    def get_projects(self) -> list[dict[str, Any]]:
        source = self.data_path if self.data_path.exists() else self.sample_path
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError("갤러리 데이터 파일을 읽지 못했습니다.") from exc

        if not isinstance(payload, list):
            raise StorageError("갤러리 데이터 형식이 올바르지 않습니다.")
        return payload
