from __future__ import annotations

from os import PathLike, fspath
from typing import Iterable

from fontTools.feaLib import ast
from fontTools.feaLib.parser import Parser

from pixel_font_builder.opentype.feature.source.base import FeatureSource


class FeatureFile(FeatureSource):
    """A FEA program loaded from a real entry file.

    Relative ``include()`` paths use the entry file's directory as one common
    root. Nested includes keep using that root instead of the directory of the
    file containing the nested ``include()`` statement.
    """

    path: str | PathLike[str]

    def __init__(self, path: str | PathLike[str]) -> None:
        self.path = path

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FeatureFile):
            return NotImplemented
        return self.path == other.path

    def parse(self, glyph_names: Iterable[str]) -> ast.FeatureFile:
        return Parser(fspath(self.path), glyph_names).parse()

    def copy(self) -> FeatureFile:
        return FeatureFile(self.path)

    def deepcopy(self) -> FeatureFile:
        return self.copy()
