from __future__ import annotations

from io import BytesIO
from os import PathLike
from typing import BinaryIO

from fontTools.ttLib import TTFont


class DFontBuilder:
    font: TTFont
    is_monospaced: bool

    def __init__(
            self,
            font: TTFont,
            is_monospaced: bool,
    ):
        self.font = font
        self.is_monospaced = is_monospaced

    def dump(self, stream: BinaryIO):
        # TODO
        pass

    def dump_to_bytes(self) -> bytes:
        stream = BytesIO()
        self.dump(stream)
        return stream.getvalue()

    def save(self, file_path: str | PathLike[str]):
        with open(file_path, 'wb') as file:
            self.dump(file)
