from __future__ import annotations

from io import StringIO
from os import PathLike, fspath
from pathlib import Path
from typing import Iterable

from fontTools.feaLib import ast
from fontTools.feaLib.parser import Parser

from pixel_font_builder.opentype.feature.source.base import FeatureSource


class FeatureIncludes(FeatureSource):
    """A virtual FEA entry program that includes multiple files in order.

    Absolute paths are used unchanged. Relative paths use ``include_dir`` when
    provided, otherwise the process's current working directory. The same
    ``include_dir`` is the common root for relative includes inside every
    included file. Without it, nested relative includes use the current working
    directory. They are never resolved relative to each included file.

    Paths containing ``)``, carriage returns, or line feeds are rejected because
    FontTools FEA ``include()`` syntax cannot represent them safely.
    """

    paths: list[str | PathLike[str]]
    include_dir: str | PathLike[str] | None

    def __init__(
            self,
            paths: list[str | PathLike[str]],
            include_dir: str | PathLike[str] | None = None,
    ) -> None:
        self.paths = paths
        self.include_dir = include_dir

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FeatureIncludes):
            return NotImplemented
        return (self.paths == other.paths and
                self.include_dir == other.include_dir)

    def parse(self, glyph_names: Iterable[str]) -> ast.FeatureFile:
        include_dir = Path(self.include_dir).absolute() if self.include_dir is not None else None
        paths = [
            path if path.is_absolute() else (
                include_dir.joinpath(path) if include_dir is not None else path.absolute()
            )
            for path in map(Path, self.paths)
        ]

        for path in paths:
            path_text = fspath(path)
            if ')' in path_text or '\r' in path_text or '\n' in path_text:
                raise ValueError(f'invalid feature include path: {path_text!r}')

        text = '\n'.join(f'include({fspath(path)});' for path in paths)

        return Parser(
            StringIO(text),
            glyph_names,
            includeDir=fspath(include_dir) if include_dir is not None else None,
        ).parse()

    def copy(self) -> FeatureIncludes:
        return FeatureIncludes(
            self.paths,
            self.include_dir,
        )

    def deepcopy(self) -> FeatureIncludes:
        return FeatureIncludes(
            self.paths.copy(),
            self.include_dir,
        )
