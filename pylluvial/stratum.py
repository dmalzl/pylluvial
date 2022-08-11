from matplotlib.patches import Polygon
from typing import Any, Union, Optional


class Stratum:
    def __init__(
        self,
        relative_height: float,
        x: float = 0,
        y: float = 0,
        label: Optional[Any] = None
):
        self.x = x
        self.y = y
        self.relative_height = relative_height
        self.lode_position = 0
        self.height = 0
        self.width = 0
        self.color = None
        self.label = label

    def __repr__(self) -> str:
        return f'Stratum(h = {self.height:.02f}, rh = {self.relative_height:.02f}, y = {self.y:.02f})'

    def set_width(self, width: float) -> None:
        self.width = width

    def set_color(self, color: Union[str, tuple[float, float, float, float]]) -> None:
        self.color = color

    def reset_lode_position(self) -> None:
        self.lode_position = self.height

    def get_left_bound(self, gap: float) -> float:
        return self.x - self.width / 2 - gap

    def get_right_bound(self, gap: float) -> float:
        return self.x + self.width / 2 + gap

    def get_flow_ycoords(self, relative_flow_width: float) -> tuple[float, float]:
        if not self.lode_position:
            self.lode_position = self.height

        flow_width = self.height * relative_flow_width
        top = self.lode_position + self.y
        bottom = top - flow_width
        self.lode_position -= flow_width

        return top, bottom

    def set_xy(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def set_height(self, scale, norm = None):
        height = self.relative_height * scale
        self.height = norm(height, scale) if norm else height

    def get_patch(
        self,
        color: Union[str, tuple[float, float, float, float]],
        alpha: float
    ) -> Polygon:
        if not self.color:
            self.color = color

        top_left = [self.x - self.width / 2, self.y + self.height]
        top_right = [self.x + self.width / 2, self.y + self.height]
        bottom_left = [self.x - self.width / 2, self.y]
        bottom_right = [self.x + self.width / 2, self.y]
        patch = Polygon(
            [
                top_left, top_right,
                bottom_right, bottom_left
            ],
            facecolor = color,
            edgecolor = 'white',
            alpha = alpha
        )
        return patch

    def get_label(self) -> tuple[float, float, str]:
        return self.x, self.y + self.height / 2, str(self.label)
