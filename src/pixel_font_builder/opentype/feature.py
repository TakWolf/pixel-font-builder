from __future__ import annotations

from io import StringIO
from os import PathLike


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
    ):
        self.text = text
        self.file_path = file_path


def build_kern_feature(pairs: dict[tuple[str, str], int], px_to_units: int) -> str:
    text = StringIO()
    text.write('languagesystem DFLT dflt;\n')
    text.write('languagesystem latn dflt;\n')
    text.write('\n')
    text.write('feature kern {\n')
    for (left_glyph_name, right_glyph_name), offset in sorted(pairs.items()):
        text.write(f'    position {left_glyph_name} {right_glyph_name} {offset * px_to_units};\n')
    text.write('} kern;\n')
    return text.getvalue()
