from typing import List
import numpy as np
from enum import Enum
from .render_object import Direction, Position, Box, Edge, RenderObject

# ASCI art characters for creating diagrams
# ## Characters:
#
# ### Single line
#
# * ASCII code 191 = ┐ ( Box drawing character single line upper right corner )
# * ASCII code 192 = └ ( Box drawing character single line lower left corner )
# * ASCII code 193 = ┴ ( Box drawing character single line horizontal and up )
# * ASCII code 194 = ┬ ( Box drawing character single line horizontal down )
# * ASCII code 195 = ├ ( Box drawing character single line vertical and right )
# * ASCII code 196 = ─ ( Box drawing character single horizontal line )
# * ASCII code 197 = ┼ ( Box drawing character single line horizontal vertical )
# * ASCII code 217 = ┘ ( Box drawing character single line lower right corner )
# * ASCII code 218 = ┌ ( Box drawing character single line upper left corner )
# * ASCII code 179 = │ ( Box drawing character single vertical line )
# * ASCII code 180 = ┤ ( Box drawing character single vertical and left line )
#
# ### Double line
#
# * ASCII code 185 = ╣ ( Box drawing character double line vertical and left )
# * ASCII code 186 = ║ ( Box drawing character double vertical line )
# * ASCII code 187 = ╗ ( Box drawing character double line upper right corner )
# * ASCII code 188 = ╝ ( Box drawing character double line lower right corner )
# * ASCII code 200 = ╚ ( Box drawing character double line lower left corner )
# * ASCII code 201 = ╔ ( Box drawing character double line upper left corner )
# * ASCII code 202 = ╩ ( Box drawing character double line horizontal and up )
# * ASCII code 203 = ╦ ( Box drawing character double line horizontal down )
# * ASCII code 204 = ╠ ( Box drawing character double line vertical and right )
# * ASCII code 205 = ═ ( Box drawing character double horizontal line )
# * ASCII code 206 = ╬ ( Box drawing character double line horizontal vertical )
#
# ### Shading
#
# * ASCII code 176 = ░ ( Graphic character, low density dotted )
# * ASCII code 177 = ▒ ( Graphic character, medium density dotted )
# * ASCII code 178 = ▓ ( Graphic character, high density dotted )
# * ASCII code 219 = █ ( Block, graphic character )
# * ASCII code 220 = ▄ ( Bottom half block )
# * ASCII code 223 = ▀ ( Top half block )
# * ASCII code 254 = ■ ( black square )
# G = pgv.AGraph()
# G.add_edge("a", "b")
# G.layout()


class Canvas:
    def __init__(self, width, height, fill=" "):
        self.width = width
        self.height = height
        self.fill = fill

        # +1 for the newline char
        self.array = np.array(
            [[self.fill for x in range(self.width + 1)] for _ in range(self.height)]
        )

        for i in range(self.height):
            self.array[i][self.width] = "\n"

    def add_box(self, width: int, height: int, position: Position, label: str) -> "Box":
        assert position.x + width <= self.width
        assert position.y + height <= self.height

        box = Box(self, width, height, position, label)
        return box

    def draw_edge(
        self,
        start: Position,
        end: Position,
        start_direction: Direction = Direction.HORIZONTAL,
        end_direction: Direction = Direction.VERTICAL,
    ) -> Edge:
        edge = Edge(self, start, end, start_direction, end_direction)
        return edge

    def draw_edge_boxes(
        self,
        box1: Box,
        box2: Box,
        start_direction: Direction = Direction.HORIZONTAL,
        end_direction: Direction = Direction.VERTICAL,
    ) -> Edge:
        assert box1.canvas == self
        assert box2.canvas == self

        center1 = self.to_canvas_pos(box1, box1.create_anchor(Direction.DOWN))
        center2 = self.to_canvas_pos(box2, box2.create_anchor(Direction.UP))
        return self.draw_edge(center1, center2, start_direction, end_direction)

    def to_canvas_pos(self, obj: RenderObject, pos: Position):
        return obj.position + pos

    def draw(self, string: str, position: Position, offset: Position = Position(0, 0)):
        assert 0 <= position.x + offset.x <= self.width
        assert 0 <= position.y + offset.y <= self.height

        self.array[position.y + offset.y][
            position.x + offset.x : position.x + offset.x + len(string)
        ] = [c for c in string]

    def to_string(self):
        return "".join([item for row in self.array for item in row])
