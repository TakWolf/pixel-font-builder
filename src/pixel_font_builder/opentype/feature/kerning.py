from __future__ import annotations

from collections.abc import Mapping

from fontTools.feaLib import ast


def create_kern_feature(kerning_values: Mapping[tuple[str, str], int], px_to_units: int) -> ast.FeatureBlock:
    feature = ast.FeatureBlock('kern')
    feature.statements.append(ast.ScriptStatement('DFLT'))
    feature.statements.append(ast.LanguageStatement('dflt'))

    for (left_glyph_name, right_glyph_name), offset in kerning_values.items():
        feature.statements.append(ast.PairPosStatement(
            ast.GlyphName(left_glyph_name),
            ast.ValueRecord(xAdvance=offset * px_to_units),
            ast.GlyphName(right_glyph_name),
            None,
        ))

    return feature
