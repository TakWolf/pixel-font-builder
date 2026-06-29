from __future__ import annotations

from typing import Any


class Config:
    is_monospaced: bool

    def __init__(
            self,
            is_monospaced: bool = False,
    ):
        self.is_monospaced = is_monospaced

    def __copy__(self) -> Config:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> Config:
        return self.deepcopy()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Config):
            return NotImplemented
        return self.is_monospaced == other.is_monospaced

    def copy(self) -> Config:
        return Config(
            self.is_monospaced,
        )

    def deepcopy(self) -> Config:
        return self.copy()
