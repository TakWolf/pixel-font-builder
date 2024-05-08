import datetime
from enum import StrEnum


class WeightName(StrEnum):
    LIGHT = 'Light'
    NORMAL = 'Normal'
    REGULAR = 'Regular'
    MEDIUM = 'Medium'
    BOLD = 'Bold'
    HEAVY = 'Heavy'


class SerifStyle(StrEnum):
    SERIF = 'Serif'
    SANS_SERIF = 'Sans Serif'


class SlantStyle(StrEnum):
    NORMAL = 'Normal'
    ITALIC = 'Italic'
    OBLIQUE = 'Oblique'
    REVERSE_ITALIC = 'Reverse Italic'
    REVERSE_OBLIQUE = 'Reverse Oblique'


class WidthMode(StrEnum):
    MONOSPACED = 'Monospaced'
    DUOSPACED = 'Duospaced'
    PROPORTIONAL = 'Proportional'


class MetaInfo:
    def __init__(
            self,
            version: str = '0.0.0',
            created_time: datetime.datetime = None,
            modified_time: datetime.datetime = None,
            family_name: str = None,
            weight_name: WeightName = None,
            serif_style: SerifStyle = None,
            slant_style: SlantStyle = None,
            width_mode: WidthMode = None,
            manufacturer: str = None,
            designer: str = None,
            description: str = None,
            copyright_info: str = None,
            license_info: str = None,
            vendor_url: str = None,
            designer_url: str = None,
            license_url: str = None,
            sample_text: str = None,
    ):
        self.version = version
        self.created_time = created_time
        self.modified_time = modified_time
        self.family_name = family_name
        self.weight_name = weight_name
        self.serif_style = serif_style
        self.slant_style = slant_style
        self.width_mode = width_mode
        self.manufacturer = manufacturer
        self.designer = designer
        self.description = description
        self.copyright_info = copyright_info
        self.license_info = license_info
        self.vendor_url = vendor_url
        self.designer_url = designer_url
        self.license_url = license_url
        self.sample_text = sample_text
