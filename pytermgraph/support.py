from enum import Enum

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
    def __init__(self, x: int, y: int, z: int = 0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        if isinstance(other, Position):
            return Position(self.x + other.x, self.y + other.y)
        if isinstance(other, int):
            return Position(self.x + other, self.y + other)
        else:
            raise TypeError

    def __sub__(self, other):
        if isinstance(other, Position):
            return Position(self.x - other.x, self.y - other.y)
        if isinstance(other, int):
            return Position(self.x - other, self.y - other)
        else:
            raise TypeError

    def __floordiv__(self, other):
        if isinstance(other, Position):
            return Position(self.x // other.x, self.y // other.y)
        if isinstance(other, int):
            return Position(self.x // other, self.y // other)
        else:
            raise TypeError

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __mul__(self, other):
        if isinstance(other, Position):
            return Position(self.x * other.x, self.y * other.y)
        if isinstance(other, int):
            return Position(self.x * other, self.y * other)
        else:
            raise TypeError

    def norm(self):
        dx = 0
        dy = 0
        if self.x != 0:
            dx = 1 if self.x > 0 else -1
        if self.y != 0:
            dy = 1 if self.y > 0 else -1
        return Position(dx, dy)

    @classmethod
    def midpoint(cls, a, b):
        return (a + b) // 2


class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

    UP_RIGHT = "up_right"
    UP_LEFT = "up_left"
    DOWN_RIGHT = "down_right"
    DOWN_LEFT = "down_left"

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


def opposite(direction: Direction):
    match direction:
        case Direction.UP:
            return Direction.DOWN
        case Direction.DOWN:
            return Direction.UP
        case Direction.LEFT:
            return Direction.RIGHT
        case Direction.RIGHT:
            return Direction.LEFT
        case Direction.VERTICAL:
            return Direction.HORIZONTAL
        case Direction.HORIZONTAL:
            return Direction.VERTICAL


class Step:
    def __init__(
        self,
        position: Position,
        direction: Direction = Direction.HORIZONTAL,
        previous: "Step | None" = None,
    ):
        self.previous = previous
        self.position = position
        self.direction = direction

        if previous:
            diff = self.position - previous.position
            assert not (diff.x == 0 ^ diff.y == 0)
            if diff.x > 0:
                self.direction = Direction.RIGHT
            elif diff.x < 0:
                self.direction = Direction.LEFT
            elif diff.y > 0:
                self.direction = Direction.DOWN
            elif diff.y < 0:
                self.direction = Direction.UP


# def get_next_char(current, next, direction) -> str:
#     if current == edge_hori and and next == direction == Direction.DOWN:
#         pass
