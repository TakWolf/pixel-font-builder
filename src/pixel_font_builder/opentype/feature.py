from __future__ import annotations

from io import StringIO
from os import PathLike
from typing import Any


class FeatureFile:
    @staticmethod
    def load(file_path: str | PathLike[str]) -> FeatureFile:
        with open(file_path, 'r', encoding='utf-8') as file:
            return FeatureFile(file.read(), file_path)

    text: str
    file_path: str | PathLike[str] | None

    def __init__(
            self,
            text: str,
            file_path: str | PathLike[str] | None = None,
    ) -> None:
        self.text = text
        self.file_path = file_path

    def __copy__(self) -> FeatureFile:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any]) -> FeatureFile:
        return self.deepcopy()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FeatureFile):
            return NotImplemented
        return (self.text == other.text and
                self.file_path == other.file_path)

    def copy(self) -> FeatureFile:
        return FeatureFile(
            self.text,
            self.file_path,
        )

    def deepcopy(self) -> FeatureFile:
        return self.copy()


def build_kern_feature(kerning_values: dict[tuple[str, str], int], px_to_units: int) -> str:
    text = StringIO()
    text.write('languagesystem DFLT dflt;\n')
    text.write('\n')
    text.write('feature kern {\n')
    for (left_glyph_name, right_glyph_name), offset in kerning_values.items():
        text.write(f'    position {left_glyph_name} {right_glyph_name} {offset * px_to_units};\n')
    text.write('} kern;\n')
    return text.getvalue()
