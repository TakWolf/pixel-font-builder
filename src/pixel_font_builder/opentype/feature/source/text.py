from __future__ import annotations

from collections.abc import Iterable
from os import PathLike

from pixel_font_builder.opentype.feature.source.input import FeatureInput, FeatureTextInput
from pixel_font_builder.opentype.feature.source.source import FeatureSource


class FeatureText(FeatureSource):
    """A FEA source backed by text held in memory.

    ``filename`` is an optional logical path used for diagnostics and does not
    need to exist. ``include_dir`` optionally defines the common root for
    relative ``include()`` paths, including nested includes. Without it,
    FontTools uses the filename's directory, or the current working directory
    when no filename is provided.
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FeatureText):
            return NotImplemented
        return (self.text == other.text and
                self.filename == other.filename and
                self.include_dir == other.include_dir)

    def create_inputs(self) -> Iterable[FeatureInput]:
        yield FeatureTextInput(
            self.text,
            self.filename,
            self.include_dir,
        )

    def copy(self) -> FeatureText:
        return FeatureText(
            self.text,
            self.filename,
            self.include_dir,
        )

    def deepcopy(self) -> FeatureText:
        return self.copy()
