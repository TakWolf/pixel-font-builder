from copy import copy, deepcopy

from pixel_font_builder import FontBuilder, FontCollectionBuilder


def test_copy():
    collection_builder_1 = FontCollectionBuilder([
        FontBuilder(),
        FontBuilder(),
    ])
    collection_builder_2 = copy(collection_builder_1)

    assert collection_builder_1 == collection_builder_2
    assert collection_builder_1 is not collection_builder_2

    for builder_1, builder_2 in zip(collection_builder_1, collection_builder_2):
        assert builder_1 is builder_2


def test_deepcopy():
    collection_builder_1 = FontCollectionBuilder([
        FontBuilder(),
        FontBuilder(),
    ])
    collection_builder_2 = deepcopy(collection_builder_1)

    assert collection_builder_1 == collection_builder_2
    assert collection_builder_1 is not collection_builder_2

    for builder_1, builder_2 in zip(collection_builder_1, collection_builder_2):
        assert builder_1 is not builder_2


def test_eq():
    collection_builder_1 = FontCollectionBuilder([
        FontBuilder(),
        FontBuilder(),
    ])
    collection_builder_2 = FontCollectionBuilder([
        FontBuilder(),
        FontBuilder(),
    ])
    assert collection_builder_1 == collection_builder_2
