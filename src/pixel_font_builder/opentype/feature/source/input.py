from __future__ import annotations

from os import PathLike
from typing import Any


class FeatureTextInput:
    """An in-memory FEA input with source-location and include-root metadata.

    ``filename`` is an optional logical path used for diagnostics. Unless
    ``include_dir`` is provided, its directory is used as the common root for
    relative ``include()`` paths. Without either value, relative includes use
    the process's current working directory.
    """

    text: str
    filename: str | PathLike[str] | None
    include_dir: str | PathLike[str] | None

    def __init__(
            self,
            text: str,
            filename: str | PathLike[str] | None = None,
            include_dir: str | PathLike[str] | None = None,
    ) -> None:
        self.text = text
        self.filename = filename
        self.include_dir = include_dir

    def __copy__(self) -> FeatureTextInput:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> FeatureTextInput:
        return self.deepcopy()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FeatureTextInput):
            return NotImplemented
        return (self.text == other.text and
                self.filename == other.filename and
                self.include_dir == other.include_dir)

    def copy(self) -> FeatureTextInput:
        return FeatureTextInput(
            self.text,
            self.filename,
            self.include_dir,
        )

    def deepcopy(self) -> FeatureTextInput:
        return self.copy()


class FeatureFileInput:
    """A FEA input backed by a real entry file.

    ``path`` identifies the file read by FontTools. Unless ``include_dir`` is
    provided, the entry file's directory is used as the common root for
    relative ``include()`` paths.
    """

    path: str | PathLike[str]
    include_dir: str | PathLike[str] | None

    def __init__(
            self,
            path: str | PathLike[str],
            include_dir: str | PathLike[str] | None = None,
    ) -> None:
        self.path = path
        self.include_dir = include_dir

    def __copy__(self) -> FeatureFileInput:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> FeatureFileInput:
        return self.deepcopy()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FeatureFileInput):
            return NotImplemented
        return (self.path == other.path and
                self.include_dir == other.include_dir)

    def copy(self) -> FeatureFileInput:
        return FeatureFileInput(
            self.path,
            self.include_dir,
        )

    def deepcopy(self) -> FeatureFileInput:
        return self.copy()


FeatureInput = FeatureTextInput | FeatureFileInput
