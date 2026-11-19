from __future__ import annotations

from copy import copy, deepcopy
from typing import Any


class Config:
    resource_id: int
    is_fixed_width: bool

    def __init__(
            self,
            resource_id: int = 128,
            is_fixed_width: bool = False,
    ) -> None:
        self.resource_id = resource_id
        self.is_fixed_width = is_fixed_width

    def __copy__(self) -> Config:
        return Config(
            self.resource_id,
            self.is_fixed_width,
        )

    def __deepcopy__(self, memo: dict[int, Any]) -> Config:
        return copy(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Config):
            return NotImplemented
        return (self.resource_id == other.resource_id and
                self.is_fixed_width == other.is_fixed_width)

    def copy(self) -> Config:
        return copy(self)

    def deepcopy(self) -> Config:
        return deepcopy(self)
