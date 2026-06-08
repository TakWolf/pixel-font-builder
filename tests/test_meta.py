from copy import copy, deepcopy
from datetime import datetime

from pixel_font_builder import WeightName, SerifStyle, SlantStyle, WidthStyle, MetaInfo


def test_copy():
    meta_info_1 = MetaInfo(
        version='1.2.3',
        created_time=datetime.fromisoformat('2000-01-01T00:00:00Z'),
        modified_time=datetime.fromisoformat('9999-12-31T23:59:59Z'),
        family_name='Demo Font',
        weight_name=WeightName.REGULAR,
        serif_style=SerifStyle.SANS_SERIF,
        slant_style=SlantStyle.NORMAL,
        width_style=WidthStyle.MONOSPACED,
        manufacturer='Pixel Font Studio',
        designer='TakWolf',
        description='A pixel font',
        copyright_info='Copyright (c) TakWolf',
        license_info='This Font Software is licensed under the SIL Open Font License, Version 1.1',
        vendor_url='https://github.com/TakWolf/pixel-font-builder',
        designer_url='https://takwolf.com',
        license_url='https://openfontlicense.org',
        sample_text='Hello World!',
    )
    meta_info_2 = copy(meta_info_1)
    meta_info_3 = deepcopy(meta_info_1)

    assert meta_info_1 == meta_info_2
    assert meta_info_1 == meta_info_3
    assert meta_info_1 is not meta_info_2
    assert meta_info_1 is not meta_info_3


def test_eq():
    meta_info_1 = MetaInfo(
        version='1.2.3',
        created_time=datetime.fromisoformat('2000-01-01T00:00:00Z'),
        modified_time=datetime.fromisoformat('9999-12-31T23:59:59Z'),
        family_name='Demo Font',
        weight_name=WeightName.REGULAR,
        serif_style=SerifStyle.SANS_SERIF,
        slant_style=SlantStyle.NORMAL,
        width_style=WidthStyle.MONOSPACED,
        manufacturer='Pixel Font Studio',
        designer='TakWolf',
        description='A pixel font',
        copyright_info='Copyright (c) TakWolf',
        license_info='This Font Software is licensed under the SIL Open Font License, Version 1.1',
        vendor_url='https://github.com/TakWolf/pixel-font-builder',
        designer_url='https://takwolf.com',
        license_url='https://openfontlicense.org',
        sample_text='Hello World!',
    )
    meta_info_2 = MetaInfo(
        version='1.2.3',
        created_time=datetime.fromisoformat('2000-01-01T00:00:00Z'),
        modified_time=datetime.fromisoformat('9999-12-31T23:59:59Z'),
        family_name='Demo Font',
        weight_name=WeightName.REGULAR,
        serif_style=SerifStyle.SANS_SERIF,
        slant_style=SlantStyle.NORMAL,
        width_style=WidthStyle.MONOSPACED,
        manufacturer='Pixel Font Studio',
        designer='TakWolf',
        description='A pixel font',
        copyright_info='Copyright (c) TakWolf',
        license_info='This Font Software is licensed under the SIL Open Font License, Version 1.1',
        vendor_url='https://github.com/TakWolf/pixel-font-builder',
        designer_url='https://takwolf.com',
        license_url='https://openfontlicense.org',
        sample_text='Hello World!',
    )
    assert meta_info_1 == meta_info_2
