from copy import copy, deepcopy
from pathlib import Path

import pytest
from fontTools.feaLib import ast
from fontTools.feaLib.error import FeatureLibError

from pixel_font_builder.opentype import FeatureFile
from pixel_font_builder.opentype.feature.source.parser import parse_feature_inputs


def test_parse(tmp_path: Path) -> None:
    feature_path = tmp_path.joinpath('main.fea')
    feature_path.write_text('feature salt { sub a by b; } salt;', 'utf-8')

    feature_ast = parse_feature_inputs(
        FeatureFile(feature_path).create_inputs(),
        ['a', 'b'],
    )

    assert len(feature_ast.statements) == 1
    assert isinstance(feature_ast.statements[0], ast.FeatureBlock)
    assert feature_ast.statements[0].name == 'salt'


def test_parse_relative_include_from_entry_directory(tmp_path: Path) -> None:
    tmp_path.joinpath('classes.fea').write_text('@Letters = [a];', 'utf-8')
    feature_path = tmp_path.joinpath('main.fea')
    feature_path.write_text('include(classes.fea); feature salt { sub @Letters by b; } salt;', 'utf-8')

    feature_ast = parse_feature_inputs(
        FeatureFile(feature_path).create_inputs(),
        ['a', 'b'],
    )

    feature_names = [
        statement.name
        for statement in feature_ast.statements
        if isinstance(statement, ast.FeatureBlock)
    ]
    assert feature_names == ['salt']


def test_parse_nested_include_from_entry_directory(tmp_path: Path) -> None:
    tmp_path.joinpath('classes.fea').write_text('@Letters = [a];', 'utf-8')
    sub_dir = tmp_path.joinpath('sub')
    sub_dir.mkdir()
    sub_dir.joinpath('salt.fea').write_text('include(classes.fea); feature salt { sub @Letters by b; } salt;', 'utf-8')
    feature_path = tmp_path.joinpath('main.fea')
    feature_path.write_text('include(sub/salt.fea);', 'utf-8')

    feature_ast = parse_feature_inputs(
        FeatureFile(feature_path).create_inputs(),
        ['a', 'b'],
    )

    feature_names = [
        statement.name
        for statement in feature_ast.statements
        if isinstance(statement, ast.FeatureBlock)
    ]
    assert feature_names == ['salt']


def test_parse_error_uses_entry_file_path(tmp_path: Path) -> None:
    feature_path = tmp_path.joinpath('main.fea')
    feature_path.write_text('feature salt { sub a by; } salt;', 'utf-8')

    with pytest.raises(FeatureLibError) as info:
        parse_feature_inputs(
            FeatureFile(feature_path).create_inputs(),
            ['a', 'b'],
        )

    assert info.value.location is not None
    assert info.value.location.file == str(feature_path)


def test_copy() -> None:
    feature_file_1 = FeatureFile(Path('test.fea'))
    feature_file_2 = copy(feature_file_1)
    feature_file_3 = deepcopy(feature_file_1)

    assert feature_file_1 == feature_file_2
    assert feature_file_1 == feature_file_3
    assert feature_file_1 is not feature_file_2
    assert feature_file_1 is not feature_file_3


def test_eq() -> None:
    feature_file_1 = FeatureFile(Path('test.fea'))
    feature_file_2 = FeatureFile(Path('test.fea'))
    assert feature_file_1 == feature_file_2
