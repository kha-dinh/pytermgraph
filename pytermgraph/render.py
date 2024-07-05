from typing import List
import numpy as np
from enum import Enum

# ASCI art characters for creating diagrams
#
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

arrow_head_t = "▲"
arrow_head_b = "▼"
arrow_head_l = "◀"
arrow_head_r = "▶"

corner_tr = "┐"
corner_tl = "┌"
corner_br = "┘"
corner_bl = "└"

edge_hori = "─"
edge_vert = "│"

edge_conn_right = "├"
edge_conn_left = "┤"
edge_conn_bot = "┬"
edge_conn_top = "┬"


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, Position):
            return Position(self.x + other.x, self.y + other.y)
        if isinstance(other, int):
            return Position(self.x + other, self.y + other)
        else:
            return Position(0, 0)

    def __sub__(self, other):
        if isinstance(other, Position):
            return Position(self.x - other.x, self.y - other.y)
        if isinstance(other, int):
            return Position(self.x - other, self.y - other)
        else:
            return Position(0, 0)


class Object:
    def __init__(self, position) -> None:
        self.position = position


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    HORIZONTAL = 5
    VERTICAL = 6


class Step(Position):
    def __init__(
        self, position: Position, is_horizontal: bool, previous: "Step | None" = None
    ):
        self.previous = previous
        self.is_horizontal = is_horizontal
        if self.is_horizontal:
            self.direction = Direction.HORIZONTAL
        else:
            self.direction = Direction.VERTICAL

        super().__init__(position.x, position.y)

        if previous:
            diff = self - previous
            assert not (diff.x == 0 ^ diff.y == 0)
            if diff.x > 0:
                self.direction = Direction.RIGHT
            elif diff.x < 0:
                self.direction = Direction.LEFT
            elif diff.y > 0:
                self.direction = Direction.DOWN
            elif diff.y < 0:
                self.direction = Direction.UP

            # self.direction =


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

    def draw_box(
        self, width: int, height: int, position: Position, label: str
    ) -> "Box":
        assert position.x + width <= self.width
        assert position.y + height <= self.height

        box = Box(self, width, height, position, label)
        return box

    def generate_manhattan_path(
        self, start: Position, end: Position, start_horizontal=True, end_horizontal=True
    ) -> List[Step]:
        path = [Step(start, start_horizontal)]
        current = Step(start, start_horizontal)
        dx, dy = end.x - start.x, end.y - start.y

        def move(is_horizontal):
            nonlocal current
            if is_horizontal:
                step = 1 if dx > 0 else -1
                current = Step(
                    Position(current.x + step, current.y), is_horizontal, current
                )
            else:
                step = 1 if dy > 0 else -1
                current = Step(
                    Position(current.x, current.y + step),
                    is_horizontal,
                    current,
                )
            path.append(current)

        if start_horizontal == end_horizontal:
            # Move in one direction, then the other
            for is_horizontal in [start_horizontal, not start_horizontal]:
                while (is_horizontal and current.x != end.x) or (
                    not is_horizontal and current.y != end.y
                ):
                    move(is_horizontal)
        else:
            # Move to midpoint, then change direction
            mid_x, mid_y = start.x + dx // 2, start.y + dy // 2
            for is_horizontal in [start_horizontal, not start_horizontal]:
                while (is_horizontal and current.x != mid_x) or (
                    not is_horizontal and current.y != mid_y
                ):
                    move(is_horizontal)

            # Complete the path
            for is_horizontal in [not start_horizontal, start_horizontal]:
                while (is_horizontal and current.x != end.x) or (
                    not is_horizontal and current.y != end.y
                ):
                    move(is_horizontal)

        return path

    def draw_edge(
        self, start: Position, end: Position, start_horizontal=True, end_horizontal=True
    ):
        path = self.generate_manhattan_path(
            start, end, start_horizontal, end_horizontal
        )

        for p in path:
            if (
                p.direction == Direction.LEFT
                or p.direction == Direction.RIGHT
                or p.direction == Direction.HORIZONTAL
            ):
                self.draw(edge_hori, p)
            if (
                p.direction == Direction.UP
                or p.direction == Direction.DOWN
                or p.direction == Direction.VERTICAL
            ):
                self.draw(edge_vert, p)

            prev = p.previous
            if not prev:
                continue

            # NoticeChange in direction
            if prev.direction != p.direction:
                if prev.direction == Direction.RIGHT and p.direction == Direction.DOWN:
                    self.draw(corner_tr, prev)
                if prev.direction == Direction.RIGHT and p.direction == Direction.UP:
                    self.draw(corner_br, prev)
                if prev.direction == Direction.LEFT and p.direction == Direction.DOWN:
                    self.draw(corner_tl, prev)
                if prev.direction == Direction.LEFT and p.direction == Direction.UP:
                    self.draw(corner_bl, prev)

                if prev.direction == Direction.DOWN and p.direction == Direction.RIGHT:
                    self.draw(corner_bl, prev)
                if prev.direction == Direction.DOWN and p.direction == Direction.LEFT:
                    self.draw(corner_br, prev)
                if prev.direction == Direction.UP and p.direction == Direction.RIGHT:
                    self.draw(corner_tr, prev)
                if prev.direction == Direction.UP and p.direction == Direction.RIGHT:
                    self.draw(corner_tl, prev)

    def draw_edge_boxes(self, box1: "Box", box2: "Box"):
        assert box1.canvas == self
        assert box2.canvas == self

        center1 = self.to_canvas_pos(box1, box1.center)
        center2 = self.to_canvas_pos(box2, box2.center)
        self.draw_edge(center1, center2)

    def to_canvas_pos(self, obj: Object, pos: Position):
        return obj.position + pos

    def draw(self, string: str, position: Position, offset: Position = Position(0, 0)):
        assert 0 <= position.x + offset.x <= self.width
        assert 0 <= position.y + offset.y <= self.height

        self.array[position.y + offset.y][
            position.x + offset.x : position.x + offset.x + len(string)
        ] = [c for c in string]

    def to_string(self):
        return "".join([item for row in self.array for item in row])


class Edge:
    def __init__(self, start: Position, end: Position):
        self.start = start
        self.end = end


class Corner(Enum):
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"


class Box(Object):
    def __init__(
        self,
        canvas: Canvas,
        width: int,
        height: int,
        position: Position,  # Position within the canvas
        text: str = "",
    ):
        # Note: winthin this Box class, *relative* positions are used
        self.width = width
        self.height = height
        self.text = text
        self.canvas = canvas
        self.corners = {}
        self.anchors = {}

        self.center = Position(round(self.width / 2), round(self.height / 2))

        self.corners[Corner.TOP_LEFT] = Position(0, 0)
        self.corners[Corner.TOP_RIGHT] = Position(self.width - 1, 0)
        self.corners[Corner.BOTTOM_LEFT] = Position(0, self.height - 1)
        self.corners[Corner.BOTTOM_RIGHT] = Position(self.width - 1, self.height - 1)

        self.anchors[Direction.LEFT] = []
        self.anchors[Direction.RIGHT] = []
        self.anchors[Direction.UP] = []
        self.anchors[Direction.DOWN] = []

        # self.anchors["left"].insert(Position())
        super().__init__(position)

    def render(self):
        for i in range(1, self.width - 1):
            for j in range(1, self.height - 1):
                self.canvas.draw(" ", self.position, Position(i, j))

        # Top + bottom edges
        for i in range(1, self.width - 1):
            self.canvas.draw(edge_hori, self.position, Position(i, 0))
            self.canvas.draw(edge_hori, self.position, Position(i, self.height - 1))

        # left + right edges
        for i in range(1, self.height - 1):
            self.canvas.draw(edge_vert, self.position, Position(0, i))
            self.canvas.draw(edge_vert, self.position, Position(self.width - 1, i))

        self.canvas.draw(corner_tl, self.position, self.corners[Corner.TOP_LEFT])
        self.canvas.draw(corner_tr, self.position, self.corners[Corner.TOP_RIGHT])
        self.canvas.draw(corner_bl, self.position, self.corners[Corner.BOTTOM_LEFT])
        self.canvas.draw(corner_br, self.position, self.corners[Corner.BOTTOM_RIGHT])

        if self.text:
            self.canvas.draw(self.text, self.position, self.get_label_pos(self.text))

    def get_label_pos(self, label: str) -> Position:
        label_x = self.center.x - round((len(label)) / 2)
        label_y = self.center.y
        return Position(label_x, label_y)
