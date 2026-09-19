from __future__ import annotations

from pathlib import Path

import pytest
from fontTools.feaLib import ast
from fontTools.feaLib.error import FeatureLibError

from pixel_font_builder.opentype import FeatureTextInput, FeatureFileInput
from pixel_font_builder.opentype.feature.source.parser import parse_feature_inputs


def test_parse_single_input() -> None:
    feature_ast = parse_feature_inputs([
        FeatureTextInput('feature salt { sub a by b; } salt;'),
    ], ['a', 'b'])

    assert len(feature_ast.statements) == 1
    assert isinstance(feature_ast.statements[0], ast.FeatureBlock)
    assert feature_ast.statements[0].name == 'salt'


def test_parse_multiple_inputs_in_order_with_shared_glyph_class() -> None:
    feature_ast = parse_feature_inputs([
        FeatureTextInput('@Letters = [a];'),
        FeatureTextInput('feature salt { sub @Letters by b; } salt;'),
        FeatureTextInput('feature ss01 { sub b by a; } ss01;'),
    ], ['a', 'b'])

    feature_names = [
        statement.name
        for statement in feature_ast.statements
        if isinstance(statement, ast.FeatureBlock)
    ]
    assert feature_names == ['salt', 'ss01']


def test_parse_multiple_inputs_with_shared_lookup() -> None:
    feature_ast = parse_feature_inputs([
        FeatureTextInput('lookup Shared { sub a by b; } Shared;'),
        FeatureTextInput('feature salt { lookup Shared; } salt;'),
    ], ['a', 'b'])

    assert len(feature_ast.statements) == 2
    assert isinstance(feature_ast.statements[0], ast.LookupBlock)
    assert isinstance(feature_ast.statements[1], ast.FeatureBlock)
    assert feature_ast.statements[1].name == 'salt'


def test_parse_inputs_with_independent_include_directories(tmp_path: Path) -> None:
    first_dir = tmp_path.joinpath('first')
    first_dir.mkdir()
    first_dir.joinpath('feature.fea').write_text('feature salt { sub a by b; } salt;', 'utf-8')
    second_dir = tmp_path.joinpath('second')
    second_dir.mkdir()
    second_dir.joinpath('feature.fea').write_text('feature ss01 { sub b by a; } ss01;', 'utf-8')

    feature_ast = parse_feature_inputs([
        FeatureTextInput('include(feature.fea);', include_dir=first_dir),
        FeatureTextInput('include(feature.fea);', include_dir=second_dir),
    ], ['a', 'b'])

    feature_names = [
        statement.name
        for statement in feature_ast.statements
        if isinstance(statement, ast.FeatureBlock)
    ]
    assert feature_names == ['salt', 'ss01']


def test_parse_file_and_text_inputs_with_shared_glyph_class(tmp_path: Path) -> None:
    feature_path = tmp_path.joinpath('classes.fea')
    feature_path.write_text('@Letters = [a];', 'utf-8')

    feature_ast = parse_feature_inputs([
        FeatureFileInput(feature_path),
        FeatureTextInput('feature salt { sub @Letters by b; } salt;'),
    ], ['a', 'b'])

    assert len(feature_ast.statements) == 2
    assert isinstance(feature_ast.statements[0], ast.GlyphClassDefinition)
    assert isinstance(feature_ast.statements[1], ast.FeatureBlock)
    assert feature_ast.statements[1].name == 'salt'


def test_parse_empty_inputs() -> None:
    feature_ast = parse_feature_inputs([], ['a', 'b'])

    assert feature_ast.statements == []


def test_parse_inputs_can_be_repeated() -> None:
    feature_inputs = [
        FeatureTextInput('feature salt { sub a by b; } salt;'),
    ]

    first_ast = parse_feature_inputs(feature_inputs, ['a', 'b'])
    second_ast = parse_feature_inputs(feature_inputs, ['a', 'b'])

    assert len(first_ast.statements) == 1
    assert len(second_ast.statements) == 1


def test_parse_error_uses_text_input_filename(tmp_path: Path) -> None:
    filename = tmp_path.joinpath('invalid.fea')

    with pytest.raises(FeatureLibError) as info:
        parse_feature_inputs([
            FeatureTextInput(
                'feature salt { sub a by; } salt;',
                filename=filename,
            ),
        ], ['a', 'b'])
    assert info.value.location is not None
    assert info.value.location.file == str(filename)
