from __future__ import annotations

from collections.abc import Iterable
from os import PathLike, fspath
from pathlib import Path

from pixel_font_builder.opentype.feature.source.input import FeatureInput, FeatureTextInput
from pixel_font_builder.opentype.feature.source.source import FeatureSource


class FeatureIncludes(FeatureSource):
    """A virtual FEA entry that includes multiple files in order.

    Absolute paths are preserved. Relative paths are resolved against
    ``include_dir`` when provided and against the current working directory
    otherwise. The resulting entry paths are absolute, while ``include_dir``
    remains the common root for relative includes inside every included file.
    Without it, nested relative includes use the current working directory.

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

    def create_inputs(self) -> Iterable[FeatureInput]:
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

        yield FeatureTextInput(text, include_dir=include_dir)

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
