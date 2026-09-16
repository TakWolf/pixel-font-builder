from __future__ import annotations

from collections.abc import Iterable
from io import StringIO
from os import PathLike, fspath

from fontTools.feaLib import ast
from fontTools.feaLib.parser import Parser

from pixel_font_builder.opentype.feature.source.base import FeatureSource


class FeatureText(FeatureSource):
    """A complete FEA program stored in memory.

    ``filename`` is a logical source path and does not need to exist. Its
    directory is the common root for relative ``include()`` paths and its value
    is used in diagnostics. Without it, relative includes use the process's
    current working directory. Nested includes do not change the common root.
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

    def parse(self, glyph_names: Iterable[str]) -> ast.FeatureFile:
        stream = StringIO(self.text)
        if self.filename is not None:
            stream.name = fspath(self.filename)
        return Parser(stream, glyph_names).parse()

    def copy(self) -> FeatureText:
        return FeatureText(
            self.text,
            self.filename,
        )

    def deepcopy(self) -> FeatureText:
        return self.copy()
