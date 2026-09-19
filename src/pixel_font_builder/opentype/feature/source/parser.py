from __future__ import annotations

from collections.abc import Iterable, Iterator
from io import StringIO
from os import fspath
from typing import Any

from fontTools.feaLib import ast
from fontTools.feaLib.lexer import IncludingLexer
from fontTools.feaLib.parser import Parser

from pixel_font_builder.opentype.feature.source.input import FeatureInput, FeatureTextInput, FeatureFileInput


class _SequentialLexer:
    _lexers: Iterator[IncludingLexer]
    _active: IncludingLexer | None

    def __init__(self, lexers: Iterable[IncludingLexer]) -> None:
        self._lexers = iter(lexers)
        self._active = None

    def __iter__(self) -> _SequentialLexer:
        return self

    def __next__(self) -> tuple[str, str, Any]:
        while True:
            if self._active is None:
                self._active = next(self._lexers)

            try:
                return next(self._active)
            except StopIteration:
                self._active = None

    def scan_anonymous_block(self, tag: str) -> tuple[str, str, Any]:
        if self._active is None:
            raise RuntimeError('cannot scan anonymous block without an active lexer')

        return self._active.scan_anonymous_block(tag)


class _FeatureParser(Parser):
    def __init__(
            self,
            lexer: _SequentialLexer,
            glyph_names: Iterable[str],
    ) -> None:
        super().__init__(StringIO(), glyph_names, followIncludes=False)
        self.lexer_ = lexer
        self.cur_token_type_ = None
        self.cur_token_ = None
        self.cur_token_location_ = None
        self.next_token_type_ = None
        self.next_token_ = None
        self.next_token_location_ = None

        self.cur_comments_.clear()
        self.advance_lexer_(comments=True)


def _create_lexer(feature_input: FeatureInput) -> IncludingLexer:
    include_dir = (
        fspath(feature_input.include_dir)
        if feature_input.include_dir is not None
        else None
    )

    if isinstance(feature_input, FeatureTextInput):
        feature_file = StringIO(feature_input.text)
        if feature_input.filename is not None:
            feature_file.name = fspath(feature_input.filename)

        return IncludingLexer(feature_file, includeDir=include_dir)

    if isinstance(feature_input, FeatureFileInput):
        return IncludingLexer(fspath(feature_input.path), includeDir=include_dir)

    raise TypeError(f'unsupported feature input: {type(feature_input).__name__!r}')


def parse_feature_inputs(
        feature_inputs: Iterable[FeatureInput],
        glyph_names: Iterable[str],
) -> ast.FeatureFile:
    lexers = (_create_lexer(feature_input) for feature_input in feature_inputs)
    return _FeatureParser(_SequentialLexer(lexers), glyph_names).parse()
