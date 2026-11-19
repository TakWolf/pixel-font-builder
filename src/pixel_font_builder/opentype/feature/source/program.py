from collections.abc import Iterable
from typing import Any, Self, cast

from pixel_font_builder.opentype.feature.source.input import FeatureInput
from pixel_font_builder.opentype.feature.source.source import FeatureSource


class FeatureProgram(FeatureSource):
    """An ordered collection of feature sources parsed as one FEA program.

    Source inputs are flattened in order and parsed with one shared symbol
    scope, allowing later sources to reference definitions from earlier
    sources. Each source retains its own input and include-root behavior.
    """

    sources: list[FeatureSource]

    def __init__(self, sources: list[FeatureSource]) -> None:
        self.sources = sources

    def __copy__(self) -> Self:
        return cast(type[Self], type(self))(self.sources)

    def __deepcopy__(self, memo: dict[int, Any]) -> Self:
        return cast(type[Self], type(self))([source.deepcopy() for source in self.sources])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FeatureProgram):
            return NotImplemented
        return self.sources == other.sources

    def create_inputs(self) -> Iterable[FeatureInput]:
        for feature_source in self.sources:
            yield from feature_source.create_inputs()
