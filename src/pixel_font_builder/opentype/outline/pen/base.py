from abc import abstractmethod
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class OutlinesPen(Protocol):
    @abstractmethod
    def move_to(self, point: tuple[float, float]):
        raise NotImplementedError()

    @abstractmethod
    def line_to(self, point: tuple[float, float]):
        raise NotImplementedError()

    @abstractmethod
    def cubic_curve_to(
            self,
            control_point_1: tuple[float, float],
            control_point_2: tuple[float, float],
            end_point: tuple[float, float],
    ):
        raise NotImplementedError()

    @abstractmethod
    def quadratic_curve_to(
            self,
            control_point: tuple[float, float],
            end_point: tuple[float, float],
    ):
        raise NotImplementedError()

    @abstractmethod
    def end_path(self):
        raise NotImplementedError()

    @abstractmethod
    def close_path(self):
        raise NotImplementedError()

    @abstractmethod
    def to_glyph(self) -> Any:
        raise NotImplementedError()
