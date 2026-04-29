from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Gallery:
    gallery_id: int
    name: str
    folder: Path
    images: list[str] = field(default_factory=list)


class GalleryStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self._next_id = 1
        self.galleries: dict[int, Gallery] = {}

    def create_gallery(self) -> Gallery:
        gid = self._next_id
        self._next_id += 1
        gname = f"Gallery_{gid}"
        folder = self.root / f"Folder_{gid}"
        folder.mkdir(parents=True, exist_ok=True)
        gallery = Gallery(gallery_id=gid, name=gname, folder=folder)
        self.galleries[gid] = gallery
        return gallery

    def rename_gallery(self, gid: int, new_name: str) -> None:
        if gid in self.galleries and new_name.strip():
            self.galleries[gid].name = new_name.strip()

    def get(self, gid: int) -> Gallery | None:
        return self.galleries.get(gid)


    def find_gallery_by_image(self, image_path: str) -> Gallery | None:
        for g in self.galleries.values():
            if image_path in g.images:
                return g
        return None
