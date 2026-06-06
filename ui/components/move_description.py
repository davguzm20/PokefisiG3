from config.colors import Colors
from ui.components.placeholder import Placeholder


class MoveDescription(Placeholder):
    WIDTH = 350
    HEIGHT = 35

    def __init__(self, position_y: int, text: str):
        super().__init__(
            position_x=(640 - self.WIDTH) // 2,
            position_y=position_y,
            width=self.WIDTH,
            height=self.HEIGHT,
            asset="assets/ui/frames/cuadro-movimiento-description.png",
            text_color=Colors.WHITE,
            text_size=18,
            label=text,
        )
