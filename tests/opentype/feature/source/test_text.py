from copy import copy, deepcopy
from pathlib import Path

import pytest
from fontTools.feaLib import ast
from fontTools.feaLib.error import FeatureLibError

from pixel_font_builder.opentype import FeatureText
from pixel_font_builder.opentype.feature.source.parser import parse_feature_inputs


def test_parse() -> None:
    feature_ast = parse_feature_inputs(
        FeatureText('feature salt { sub a by b; } salt;').create_inputs(),
        ['a', 'b'],
    )

    assert len(feature_ast.statements) == 1
    assert isinstance(feature_ast.statements[0], ast.FeatureBlock)
    assert feature_ast.statements[0].name == 'salt'


def test_parse_relative_include_from_virtual_filename(tmp_path: Path) -> None:
    tmp_path.joinpath('classes.fea').write_text('@Letters = [a];', 'utf-8')

    feature_ast = parse_feature_inputs(
        FeatureText(
            'include(classes.fea); feature salt { sub @Letters by b; } salt;',
            filename=tmp_path.joinpath('virtual-main.fea'),
        ).create_inputs(),
        ['a', 'b'],
    )

    feature_names = [
        statement.name
        for statement in feature_ast.statements
        if isinstance(statement, ast.FeatureBlock)
    ]
    assert feature_names == ['salt']


def test_parse_nested_include_from_virtual_filename_directory(tmp_path: Path) -> None:
    tmp_path.joinpath('classes.fea').write_text('@Letters = [a];', 'utf-8')
    sub_dir = tmp_path.joinpath('sub')
    sub_dir.mkdir()
    sub_dir.joinpath('salt.fea').write_text('include(classes.fea); feature salt { sub @Letters by b; } salt;', 'utf-8')

    feature_ast = parse_feature_inputs(
        FeatureText(
            'include(sub/salt.fea);',
            filename=tmp_path.joinpath('virtual-main.fea'),
        ).create_inputs(),
        ['a', 'b'],
    )

    feature_names = [
        statement.name
        for statement in feature_ast.statements
        if isinstance(statement, ast.FeatureBlock)
    ]
    assert feature_names == ['salt']


def test_parse_nested_include_from_explicit_include_directory(tmp_path: Path) -> None:
    include_dir = tmp_path.joinpath('features')
    include_dir.mkdir()
    include_dir.joinpath('classes.fea').write_text('@Letters = [a];', 'utf-8')
    sub_dir = include_dir.joinpath('sub')
    sub_dir.mkdir()
    sub_dir.joinpath('salt.fea').write_text('include(classes.fea); feature salt { sub @Letters by b; } salt;', 'utf-8')

    feature_ast = parse_feature_inputs(
        FeatureText(
            'include(sub/salt.fea);',
            filename=tmp_path.joinpath('virtual-main.fea'),
            include_dir=include_dir,
        ).create_inputs(),
        ['a', 'b'],
    )

    feature_names = [
        statement.name
        for statement in feature_ast.statements
        if isinstance(statement, ast.FeatureBlock)
    ]
    assert feature_names == ['salt']


def test_parse_relative_include_from_current_working_directory(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath('classes.fea').write_text('@Letters = [a];', 'utf-8')

    feature_ast = parse_feature_inputs(
        FeatureText('include(classes.fea); feature salt { sub @Letters by b; } salt;').create_inputs(),
        ['a', 'b'],
    )

    feature_names = [
        statement.name
        for statement in feature_ast.statements
        if isinstance(statement, ast.FeatureBlock)
    ]
    assert feature_names == ['salt']


def test_parse_error_uses_virtual_filename(tmp_path: Path) -> None:
    filename = tmp_path.joinpath('virtual-main.fea')

    with pytest.raises(FeatureLibError) as info:
        parse_feature_inputs(
            FeatureText(
                'feature salt { sub a by; } salt;',
                filename=filename,
            ).create_inputs(),
            ['a', 'b'],
        )
    assert info.value.location is not None
    assert info.value.location.file == str(filename)


def test_copy() -> None:
    feature_text_1 = FeatureText(
        text='test',
        filename=Path('test.fea'),
        include_dir=Path('fea'),
    )
    feature_text_2 = copy(feature_text_1)
    feature_text_3 = deepcopy(feature_text_1)

    assert feature_text_1 == feature_text_2
    assert feature_text_1 == feature_text_3
    assert feature_text_1 is not feature_text_2
    assert feature_text_1 is not feature_text_3


def test_eq() -> None:
    feature_text_1 = FeatureText(
        text='test',
        filename=Path('test.fea'),
        include_dir=Path('fea'),
    )
    feature_text_2 = FeatureText(
        text='test',
        filename=Path('test.fea'),
        include_dir=Path('fea'),
    )
    assert feature_text_1 == feature_text_2
