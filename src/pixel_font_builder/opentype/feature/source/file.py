from __future__ import annotations

from collections.abc import Iterable
from os import PathLike

from pixel_font_builder.opentype.feature.source.input import FeatureInput, FeatureFileInput
from pixel_font_builder.opentype.feature.source.source import FeatureSource


class FeatureFile(FeatureSource):
    """A FEA source backed by one real entry file.

    ``include_dir`` optionally defines the common root for relative
    ``include()`` paths, including nested includes. Without it, FontTools uses
    the entry file's directory.
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FeatureFile):
            return NotImplemented
        return (self.path == other.path and
                self.include_dir == other.include_dir)

    def create_inputs(self) -> Iterable[FeatureInput]:
        yield FeatureFileInput(
            self.path,
            self.include_dir,
        )

    def copy(self) -> FeatureFile:
        return FeatureFile(
            self.path,
            self.include_dir,
        )

    def deepcopy(self) -> FeatureFile:
        return self.copy()
