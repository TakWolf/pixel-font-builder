from __future__ import annotations

from typing import Any


class Config:
    resolution_x: int
    resolution_y: int
    only_basic_plane: bool

    def __init__(
            self,
            resolution_x: int = 75,
            resolution_y: int = 75,
            only_basic_plane: bool = False,
    ):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.only_basic_plane = only_basic_plane

    def __copy__(self) -> Config:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> Config:
        return self.deepcopy()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Config):
            return NotImplemented
        return (self.resolution_x == other.resolution_x and
                self.resolution_y == other.resolution_y and
                self.only_basic_plane == other.only_basic_plane)

    def copy(self) -> Config:
        return Config(
            self.resolution_x,
            self.resolution_y,
            self.only_basic_plane,
        )

    def deepcopy(self) -> Config:
        return self.copy()
