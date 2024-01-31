
class Config:
    def __init__(
            self,
            x_height: int = 0,
            cap_height: int = 0,
    ):
        self.x_height = x_height
        self.cap_height = cap_height

    def __mul__(self, other: int) -> 'Config':
        return Config(
            self.x_height * other,
            self.cap_height * other,
        )
