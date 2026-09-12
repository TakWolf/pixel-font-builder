from copy import copy, deepcopy
from pathlib import Path

import pytest
from fontTools.feaLib import ast
from fontTools.feaLib.error import FeatureLibError

from pixel_font_builder.opentype import FeatureIncludes


def test_parse_multiple_files_in_order_with_shared_glyph_class(tmp_path: Path) -> None:
    tmp_path.joinpath('classes.fea').write_text('@Letters = [a];', 'utf-8')
    tmp_path.joinpath('salt.fea').write_text('feature salt { sub @Letters by b; } salt;', 'utf-8')
    tmp_path.joinpath('ss01.fea').write_text('feature ss01 { sub b by a; } ss01;', 'utf-8')

    feature_ast = FeatureIncludes(
        paths=['classes.fea', 'salt.fea', 'ss01.fea'],
        include_dir=tmp_path,
    ).parse(['a', 'b'])

    feature_names = [
        statement.name
        for statement in feature_ast.statements
        if isinstance(statement, ast.FeatureBlock)
    ]
    assert feature_names == ['salt', 'ss01']


def test_parse_nested_include_from_common_include_directory(tmp_path: Path) -> None:
    tmp_path.joinpath('classes.fea').write_text('@Letters = [a];', 'utf-8')
    sub_dir = tmp_path.joinpath('sub')
    sub_dir.mkdir()
    sub_dir.joinpath('salt.fea').write_text('include(classes.fea); feature salt { sub @Letters by b; } salt;', 'utf-8')

    feature_ast = FeatureIncludes(
        paths=['sub/salt.fea'],
        include_dir=tmp_path,
    ).parse(['a', 'b'])

    feature_names = [
        statement.name
        for statement in feature_ast.statements
        if isinstance(statement, ast.FeatureBlock)
    ]
    assert feature_names == ['salt']


def test_parse_relative_paths_from_current_working_directory(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath('salt.fea').write_text('feature salt { sub a by b; } salt;', 'utf-8')

    feature_ast = FeatureIncludes(['salt.fea']).parse(['a', 'b'])

    feature_names = [
        statement.name
        for statement in feature_ast.statements
        if isinstance(statement, ast.FeatureBlock)
    ]
    assert feature_names == ['salt']


def test_parse_absolute_path_ignores_include_directory(tmp_path: Path) -> None:
    source_dir = tmp_path.joinpath('source')
    source_dir.mkdir()
    feature_path = source_dir.joinpath('salt.fea')
    feature_path.write_text('feature salt { sub a by b; } salt;', 'utf-8')
    other_dir = tmp_path.joinpath('other')
    other_dir.mkdir()

    feature_ast = FeatureIncludes(
        [feature_path],
        include_dir=other_dir,
    ).parse(['a', 'b'])

    feature_names = [
        statement.name
        for statement in feature_ast.statements
        if isinstance(statement, ast.FeatureBlock)
    ]
    assert feature_names == ['salt']


@pytest.mark.parametrize(
    'invalid_path',
    [
        'invalid).fea',
        'invalid\r.fea',
        'invalid\n.fea',
    ],
)
def test_parse_rejects_unrepresentable_include_path(invalid_path: str) -> None:
    with pytest.raises(ValueError, match='invalid feature include path'):
        FeatureIncludes([invalid_path]).parse(['a', 'b'])


def test_parse_error_uses_included_file_path(tmp_path: Path) -> None:
    feature_path = tmp_path.joinpath('invalid.fea')
    feature_path.write_text('feature salt { sub a by; } salt;', 'utf-8')

    with pytest.raises(FeatureLibError) as info:
        FeatureIncludes([feature_path]).parse(['a', 'b'])

    assert info.value.location is not None
    assert info.value.location.file == str(feature_path)


def test_copy() -> None:
    feature_includes_1 = FeatureIncludes(
        paths=[
            Path('test-1.fea'),
            Path('test-2.fea'),
        ],
        include_dir=Path('fea'),
    )
    feature_includes_2 = copy(feature_includes_1)

    assert feature_includes_1 == feature_includes_2
    assert feature_includes_1 is not feature_includes_2
    assert feature_includes_1.paths is feature_includes_2.paths


def test_deepcopy() -> None:
    feature_includes_1 = FeatureIncludes(
        paths=[
            Path('test-1.fea'),
            Path('test-2.fea'),
        ],
        include_dir=Path('fea'),
    )
    feature_includes_2 = deepcopy(feature_includes_1)

    assert feature_includes_1 == feature_includes_2
    assert feature_includes_1 is not feature_includes_2
    assert feature_includes_1.paths is not feature_includes_2.paths


def test_eq() -> None:
    feature_includes_1 = FeatureIncludes(
        paths=[
            Path('test-1.fea'),
            Path('test-2.fea'),
        ],
        include_dir=Path('fea'),
    )
    feature_includes_2 = FeatureIncludes(
        paths=[
            Path('test-1.fea'),
            Path('test-2.fea'),
        ],
        include_dir=Path('fea'),
    )
    assert feature_includes_1 == feature_includes_2
