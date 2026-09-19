from __future__ import annotations

from collections.abc import Iterable
from os import PathLike

from pixel_font_builder.opentype.feature.source.input import FeatureInput, FeatureTextInput
from pixel_font_builder.opentype.feature.source.source import FeatureSource


class FeatureText(FeatureSource):
    """A FEA source backed by text held in memory.

    ``filename`` is an optional logical path and does not need to exist.
    FontTools uses it in diagnostics and uses its directory as the common root
    for relative ``include()`` paths, including nested includes. Without a
    filename, relative includes use the current working directory.
    """

    text: str
    filename: str | PathLike[str] | None

    def __init__(
            self,
            text: str,
            filename: str | PathLike[str] | None = None,
    ) -> None:
        self.text = text
        self.filename = filename

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FeatureText):
            return NotImplemented
        return (self.text == other.text and
                self.filename == other.filename)

    def create_inputs(self) -> Iterable[FeatureInput]:
        yield FeatureTextInput(self.text, self.filename)

    def copy(self) -> FeatureText:
        return FeatureText(
            self.text,
            self.filename,
        )

    def deepcopy(self) -> FeatureText:
        return self.copy()
