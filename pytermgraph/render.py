import pygraphviz as pgv
import numpy as np

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

    def __add__(self, other: "Position"):
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Position"):
        return Position(self.x - other.x, self.y - other.y)


class Object:
    def __init__(self, position) -> None:
        self.position = position


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

    def draw_edge(self, box1, box2):
        assert box1.canvas == self
        assert box2.canvas == self

        first_anchor = box1.position + box1.center()
        first_anchor.x += box1.center().x - 2

        # 1. Select anchor point

        second_anchor = box2.position + box2.center()
        second_anchor.x -= box2.center().x

        # for i in range(first_anchor.x, second_anchor.x):
        #     self.array[box1.center().y][i] = edge_hori

        self.array[first_anchor.y][first_anchor.x] = edge_conn_right
        self.array[second_anchor.y][second_anchor.x] = edge_conn_left

    def to_string(self):
        return "".join([item for row in self.array for item in row])


class Edge:
    def __init__(self, start: Position, end: Position):
        self.start = start
        self.end = end


class Box(Object):
    def __init__(
        self,
        canvas: Canvas,
        width: int,
        height: int,
        position: Position = Position(0, 0),
        text: str = "",
    ):
        self.width = width + 1
        self.height = height + 1
        self.text = text
        self.canvas = canvas
        super().__init__(position)

        self.render()

    def render(self):
        for i in range(1, self.width - 1 - 1):
            for j in range(1, self.height - 1):
                self.canvas.array[j + self.position.y][i + self.position.x] = " "

        # Top + bottom edges
        for i in range(1, self.width - 1 - 1):
            self.canvas.array[0 + self.position.y][i + self.position.x] = edge_hori
            self.canvas.array[self.height - 1 + self.position.y][
                i + self.position.x
            ] = edge_hori

        # left + right edges
        for i in range(1, self.height - 1):
            self.canvas.array[i + self.position.y][0 + self.position.x] = edge_vert
            self.canvas.array[i + self.position.y][self.width - 2 + self.position.x] = (
                edge_vert
            )

        # Corners
        self.canvas.array[0 + self.position.y][0 + self.position.x] = corner_tl
        self.canvas.array[0 + self.position.y][self.width - 2 + self.position.x] = (
            corner_tr
        )
        self.canvas.array[self.height - 1 + self.position.y][0 + self.position.x] = (
            corner_bl
        )
        self.canvas.array[self.height - 1 + self.position.y][
            self.width - 2 + self.position.x
        ] = corner_br

        if self.text:
            center = self.center()
            offset_x = int(center.x - (len(self.text) / 2))

            self.canvas.array[center.y + self.position.y][
                offset_x + self.position.x : offset_x + self.position.x + len(self.text)
            ] = [c for c in self.text]

    def center(self) -> Position:
        return Position(int(self.width / 2), int(self.height / 2))
