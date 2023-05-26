
class MetaInfos:
    def __init__(
            self,
            family_name: str,
            version: str,
            description: str = None,
            copyright_info: str = None,
            license_description: str = None,
            license_url: str = None,
            manufacturer: str = None,
            designer: str = None,
            designer_url: str = None,
            vendor_url: str = None,
    ):
        self.family_name = family_name
        self.version = version
        self.description = description
        self.copyright_info = copyright_info
        self.license_description = license_description
        self.license_url = license_url
        self.manufacturer = manufacturer
        self.designer = designer
        self.designer_url = designer_url
        self.vendor_url = vendor_url


class OpenTypeConfigs:
    def __init__(
            self,
            px_to_units: int = 100,
    ):
        self.px_to_units = px_to_units


class BdfConfigs:
    def __init__(
            self,
            resolution_x: int = 75,
            resolution_y: int = 75,
            px_to_points: int = 100,
    ):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.px_to_points = px_to_points
