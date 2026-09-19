from copy import copy, deepcopy
from pathlib import Path

from fontTools.feaLib import ast

from pixel_font_builder.opentype import FeatureProgram, FeatureText, FeatureFile
from pixel_font_builder.opentype.feature.source.parser import parse_feature_inputs


def test_parse_sources_in_order_with_shared_glyph_class() -> None:
    feature_ast = parse_feature_inputs(
        FeatureProgram([
            FeatureText('@Letters = [a];'),
            FeatureText('feature salt { sub @Letters by b; } salt;'),
            FeatureText('feature ss01 { sub b by a; } ss01;'),
        ]).create_inputs(),
        ['a', 'b'],
    )

    feature_names = [
        statement.name
        for statement in feature_ast.statements
        if isinstance(statement, ast.FeatureBlock)
    ]
    assert feature_names == ['salt', 'ss01']


def test_parse_sources_with_shared_lookup() -> None:
    feature_ast = parse_feature_inputs(
        FeatureProgram([
            FeatureText('lookup Shared { sub a by b; } Shared;'),
            FeatureText('feature salt { lookup Shared; } salt;'),
        ]).create_inputs(),
        ['a', 'b'],
    )

    assert len(feature_ast.statements) == 2
    assert isinstance(feature_ast.statements[0], ast.LookupBlock)
    assert isinstance(feature_ast.statements[1], ast.FeatureBlock)
    assert feature_ast.statements[1].name == 'salt'


def test_parse_sources_with_independent_include_directories(tmp_path: Path) -> None:
    first_dir = tmp_path.joinpath('first')
    first_dir.mkdir()
    first_dir.joinpath('feature.fea').write_text('feature salt { sub a by b; } salt;', 'utf-8')
    second_dir = tmp_path.joinpath('second')
    second_dir.mkdir()
    second_dir.joinpath('feature.fea').write_text('feature ss01 { sub b by a; } ss01;', 'utf-8')

    feature_ast = parse_feature_inputs(
        FeatureProgram([
            FeatureText('include(feature.fea);', first_dir.joinpath('main.fea')),
            FeatureText('include(feature.fea);', second_dir.joinpath('main.fea')),
        ]).create_inputs(),
        ['a', 'b'],
    )

    feature_names = [
        statement.name
        for statement in feature_ast.statements
        if isinstance(statement, ast.FeatureBlock)
    ]
    assert feature_names == ['salt', 'ss01']


def test_parse_mixed_sources(tmp_path: Path) -> None:
    feature_path = tmp_path.joinpath('classes.fea')
    feature_path.write_text('@Letters = [a];', 'utf-8')

    feature_ast = parse_feature_inputs(
        FeatureProgram([
            FeatureFile(feature_path),
            FeatureText('feature salt { sub @Letters by b; } salt;'),
        ]).create_inputs(),
        ['a', 'b'],
    )

    assert len(feature_ast.statements) == 2
    assert isinstance(feature_ast.statements[0], ast.GlyphClassDefinition)
    assert isinstance(feature_ast.statements[1], ast.FeatureBlock)


def test_parse_nested_program() -> None:
    feature_ast = parse_feature_inputs(
        FeatureProgram([
            FeatureProgram([
                FeatureText('@Letters = [a];'),
            ]),
            FeatureText('feature salt { sub @Letters by b; } salt;'),
        ]).create_inputs(),
        ['a', 'b'],
    )

    assert len(feature_ast.statements) == 2
    assert isinstance(feature_ast.statements[0], ast.GlyphClassDefinition)
    assert isinstance(feature_ast.statements[1], ast.FeatureBlock)


def test_parse_empty_program() -> None:
    feature_ast = parse_feature_inputs(
        FeatureProgram([]).create_inputs(),
        ['a', 'b'],
    )

    assert feature_ast.statements == []


def test_parse_can_be_repeated() -> None:
    feature_program = FeatureProgram([
        FeatureText('feature salt { sub a by b; } salt;'),
    ])

    first_ast = parse_feature_inputs(
        feature_program.create_inputs(),
        ['a', 'b'],
    )
    second_ast = parse_feature_inputs(
        feature_program.create_inputs(),
        ['a', 'b'],
    )

    assert len(first_ast.statements) == 1
    assert len(second_ast.statements) == 1


def test_copy() -> None:
    feature_program_1 = FeatureProgram([
        FeatureFile(Path('test-1.fea')),
        FeatureFile(Path('test-2.fea')),
    ])
    feature_program_2 = copy(feature_program_1)

    assert feature_program_1 == feature_program_2
    assert feature_program_1 is not feature_program_2
    assert feature_program_1.sources is feature_program_2.sources


def test_deepcopy() -> None:
    feature_program_1 = FeatureProgram([
        FeatureFile(Path('test-1.fea')),
        FeatureFile(Path('test-2.fea')),
    ])
    feature_program_2 = deepcopy(feature_program_1)

    assert feature_program_1 == feature_program_2
    assert feature_program_1 is not feature_program_2
    assert feature_program_1.sources is not feature_program_2.sources

    for source_1, source_2 in zip(feature_program_1.sources, feature_program_2.sources):
        assert source_1 is not source_2


def test_eq() -> None:
    feature_program_1 = FeatureProgram([
        FeatureFile(Path('test-1.fea')),
        FeatureFile(Path('test-2.fea')),
    ])
    feature_program_2 = FeatureProgram([
        FeatureFile(Path('test-1.fea')),
        FeatureFile(Path('test-2.fea')),
    ])
    assert feature_program_1 == feature_program_2
