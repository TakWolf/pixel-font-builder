from __future__ import annotations

from collections.abc import Iterable
from os import PathLike

from pixel_font_builder.opentype.feature.source.input import FeatureInput, FeatureFileInput
from pixel_font_builder.opentype.feature.source.source import FeatureSource


class FeatureFile(FeatureSource):
    """A FEA source backed by one real entry file.

    FontTools uses the entry file's directory as the common root for relative
    ``include()`` paths, including nested includes.
    """

    path: str | PathLike[str]

    def __init__(self, path: str | PathLike[str]) -> None:
        self.path = path

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FeatureFile):
            return NotImplemented
        return self.path == other.path

    def create_inputs(self) -> Iterable[FeatureInput]:
        yield FeatureFileInput(self.path)

    def copy(self) -> FeatureFile:
        return FeatureFile(self.path)

    def deepcopy(self) -> FeatureFile:
        return self.copy()
