from collections.abc import Iterable

from fontTools.feaLib import ast

from pixel_font_builder.opentype.feature.source.source import FeatureSource


def _claims_feature(feature_ast: ast.FeatureFile, name: str) -> bool:
    return any(
        isinstance(statement, (ast.FeatureBlock, ast.VariationBlock)) and statement.name == name
        for statement in feature_ast.statements
    )


def build_feature_ast(
        features: FeatureSource | None,
        glyph_names: Iterable[str],
        generated_kern_feature: ast.FeatureBlock | None = None,
) -> ast.FeatureFile:
    feature_ast = features.parse(glyph_names) if features is not None else ast.FeatureFile()
    if generated_kern_feature is not None and not _claims_feature(feature_ast, 'kern'):
        feature_ast.statements.append(generated_kern_feature)
    return feature_ast
