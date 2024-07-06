from enum import Enum
from typing import List

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


class Canvas:
    def draw(self, string: str, position: Position, offset: Position = Position(1, 0)):
        pass


class RenderObject:
    def __init__(self, position: Position, canvas: Canvas) -> None:
        self.position = position
        self.canvas = canvas


class Anchor:
    def __init__(
        self,
        position,
        obj: RenderObject,  # Parent object
        edge: Edge,  # Parent object
    ) -> None:
        self.position = position
        self.obj = obj
        self.edge = edge
        pass


class Corner(Enum):
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    HORIZONTAL = 5
    VERTICAL = 6


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


class Edge(RenderObject):
    def __init__(
        self,
        canvas,
        start: Position,
        end: Position,
        start_direction=Direction.HORIZONTAL,
        end_direction=Direction.VERTICAL,
    ) -> None:
        super().__init__(start, canvas)
        self.start = start
        self.end = end
        self.path = self.generate_manhattan_path(start_direction, end_direction)

    def render(self):
        for p in self.path:
            if (
                p.direction == Direction.LEFT
                or p.direction == Direction.RIGHT
                or p.direction == Direction.HORIZONTAL
            ):
                self.canvas.draw(edge_hori, p.position)
            if (
                p.direction == Direction.UP
                or p.direction == Direction.DOWN
                or p.direction == Direction.VERTICAL
            ):
                self.canvas.draw(edge_vert, p.position)

            prev = p.previous
            if not prev:
                continue

            # NoticeChange in direction
            if prev.direction != p.direction:
                if prev.direction == Direction.RIGHT and p.direction == Direction.DOWN:
                    self.canvas.draw(corner_tr, prev.position)
                if prev.direction == Direction.RIGHT and p.direction == Direction.UP:
                    self.canvas.draw(corner_br, prev.position)
                if prev.direction == Direction.LEFT and p.direction == Direction.DOWN:
                    self.canvas.draw(corner_tl, prev.position)
                if prev.direction == Direction.LEFT and p.direction == Direction.UP:
                    self.canvas.draw(corner_bl, prev.position)

                if prev.direction == Direction.DOWN and p.direction == Direction.RIGHT:
                    self.canvas.draw(corner_bl, prev.position)
                if prev.direction == Direction.DOWN and p.direction == Direction.LEFT:
                    self.canvas.draw(corner_br, prev.position)
                if prev.direction == Direction.UP and p.direction == Direction.RIGHT:
                    self.canvas.draw(corner_tr, prev.position)
                if prev.direction == Direction.UP and p.direction == Direction.RIGHT:
                    self.canvas.draw(corner_tl, prev.position)

    def generate_manhattan_path(
        self, start_direction: Direction, end_direction: Direction
    ) -> List[Step]:
        current = Step(self.start, start_direction)
        path = [current]
        dx, dy = self.end.x - self.start.x, self.end.y - self.start.y

        # print(self.start.__dict__)
        # print(self.end.__dict__)

        def move(current: Step, direction) -> Step:
            match direction:
                case Direction.HORIZONTAL:
                    step = 1 if dx > 0 else -1
                    next = Step(
                        Position(current.position.x + step, current.position.y),
                        direction,
                        current,
                    )
                case Direction.VERTICAL:
                    step = 1 if dy > 0 else -1
                    next = Step(
                        Position(current.position.x, current.position.y + step),
                        direction,
                        current,
                    )
            assert next.position.x <= self.canvas.width
            assert next.position.y <= self.canvas.height

            return next

        if start_direction != end_direction:
            # Move in one direction, then the other
            for direction in [start_direction, end_direction]:
                while (
                    direction == Direction.HORIZONTAL
                    and current.position.x != self.end.x
                ) or (
                    direction == Direction.VERTICAL and current.position.y != self.end.y
                ):
                    current = move(current, direction)
                    path.append(current)
        else:
            # Move eto midpoint, then change direction
            midpoint = Position(self.start.x + dx // 2, self.start.y + dy // 2)

            for direction in [start_direction, opposite(start_direction)]:
                while (
                    direction == Direction.HORIZONTAL
                    and current.position.x != midpoint.x
                ) or (
                    direction == Direction.VERTICAL and current.position.y != midpoint.y
                ):
                    current = move(current, direction)
                    path.append(current)
            for direction in [opposite(end_direction), end_direction]:
                # print(direction)
                while (
                    direction == Direction.HORIZONTAL
                    and current.position.x != self.end.x
                ) or (
                    direction == Direction.VERTICAL and current.position.y != self.end.y
                ):
                    # print("Stepping")
                    # print(current.position.__dict__)
                    current = move(current, direction)
                    path.append(current)

        #
        #
        #     for is_horizontal in [start_horizontal, not start_horizontal]:
        #         while (is_horizontal and current.position.x != mid_x) or (
        #             not is_horizontal and current.position.y != mid_y
        #         ):
        #             move(is_horizontal)
        #
        #     # Complete the path
        #     for is_horizontal in [not start_horizontal, start_horizontal]:
        #         while (is_horizontal and current.x != self.end.x) or (
        #             not is_horizontal and current.y != self.end.y
        #         ):
        #             move(is_horizontal)

        return path


class Box(RenderObject):
    def __init__(
        self,
        canvas,
        width: int,
        height: int,
        position: Position,  # Position within the canvas
        text: str = "",
    ):
        # Note: winthin this Box class, *relative* positions are used
        self.width = width
        self.height = height
        self.text = text

        self.corners = {}
        self.anchors = {}

        self.center = Position(self.width // 2, self.height // 2)

        self.corners[Corner.TOP_LEFT] = Position(0, 0)
        self.corners[Corner.TOP_RIGHT] = Position(self.width - 1, 0)
        self.corners[Corner.BOTTOM_LEFT] = Position(0, self.height - 1)
        self.corners[Corner.BOTTOM_RIGHT] = Position(self.width - 1, self.height - 1)

        self.anchors[Direction.LEFT] = []
        self.anchors[Direction.RIGHT] = []
        self.anchors[Direction.UP] = []
        self.anchors[Direction.DOWN] = []

        # self.anchors["left"].insert(Position())
        super().__init__(position, canvas)

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

    def create_anchor(self, direction: Direction) -> Position:
        new_anchor = Position(0, 0)
        anchors_dir: List[Position] = self.anchors[direction]
        anchors_dir.append(new_anchor)

        print(anchors_dir)

        size = len(self.anchors[direction])

        offset_x = 0
        offset_y = 0

        step_x = self.width // (size + 1)
        step_y = self.height // (size + 1)

        print(step_x)
        print(size)
        print(self.width)
        for idx in range(size):
            if direction == Direction.DOWN:
                offset_x += step_x
                anchors_dir[idx] = Position(offset_x, self.height - 1)
            if direction == Direction.UP:
                offset_x += step_x
                anchors_dir[idx] = Position(offset_x, 0)
                print(self.position.__dict__)
                print(anchors_dir[idx].__dict__)

        # Readjust
        return anchors_dir[size - 1]

    def get_label_pos(self, label: str) -> Position:
        # Offset from the left edge
        label_x = self.center.x - (len(label) // 2)
        label_y = self.center.y
        return Position(label_x, label_y)
