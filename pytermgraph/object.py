from enum import Enum
from typing import Dict, List
from .support import Direction, Position, Step, opposite

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
edge_conn_top = "┴"


# Forward declaration
class Canvas:
    width: int
    height: int

    def draw(self, string: str, position: Position, offset: Position = Position(1, 0)):
        pass

    def draw_line(self, start: Position, end: Position, line_symbol: str):
        pass

    def to_canvas_pos(self, obj: "RenderObject", pos: Position):
        pass


class RenderObject:
    def __init__(self, position: Position, canvas: Canvas) -> None:
        self.position = position
        self.canvas = canvas

    def render(self):
        """Render the object into the parent canvas, based on its position"""
        pass


class Anchor:
    def __init__(
        self,
        position,
        obj: RenderObject,  # Parent object
    ) -> None:
        self.position = position
        self.obj = obj
        # self.edge = edge
        pass


class Corner(Enum):
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"


class Edge(RenderObject):
    def __init__(
        self,
        canvas,
        start: Position,
        end: Position,
        start_direction=Direction.HORIZONTAL,
        end_direction=Direction.VERTICAL,
        start_object: RenderObject | None = None,
        end_object: RenderObject | None = None,
    ) -> None:
        super().__init__(start, canvas)
        self.start = start
        self.end = end
        self.start_direction = start_direction
        self.end_direction = end_direction
        self.start_object = start_object
        self.end_object = end_object

    def render(self):
        self.path = self.generate_manhattan_path()
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
            if p == self.path[-1]:
                self.canvas.draw(arrow_head_b, p.position)
                pass

    def generate_manhattan_path(self) -> List[Step]:
        current = Step(self.start, self.start_direction)
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
                case _:
                    raise RuntimeError
            assert 0 <= next.position.x <= self.canvas.width
            assert 0 <= next.position.y <= self.canvas.height

            return next

        if self.start_direction != self.end_direction:
            # Move in one direction, then the other
            for direction in [self.start_direction, self.end_direction]:
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
            mid = Position.midpoint(self.start, self.end)

            for direction in [self.start_direction, opposite(self.start_direction)]:
                while (
                    direction == Direction.HORIZONTAL and current.position.x != mid.x
                ) or (direction == Direction.VERTICAL and current.position.y != mid.y):
                    current = move(current, direction)
                    path.append(current)
            for direction in [opposite(self.end_direction), self.end_direction]:
                while (
                    direction == Direction.HORIZONTAL
                    and current.position.x != self.end.x
                ) or (
                    direction == Direction.VERTICAL and current.position.y != self.end.y
                ):
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
        self.anchors: Dict[Direction, List[Anchor]] = {}

        self.anchors[Direction.UP] = []
        self.anchors[Direction.DOWN] = []
        self.anchors[Direction.LEFT] = []
        self.anchors[Direction.RIGHT] = []

        self.center = Position(self.width // 2, self.height // 2)

        self.corners[Corner.TOP_LEFT] = Position(0, 0)
        self.corners[Corner.TOP_RIGHT] = Position(self.width - 1, 0)
        self.corners[Corner.BOTTOM_LEFT] = Position(0, self.height - 1)
        self.corners[Corner.BOTTOM_RIGHT] = Position(self.width - 1, self.height - 1)

        # self.anchors["left"].insert(Position())
        super().__init__(position, canvas)

    def render(self):
        for i in range(1, self.width - 1):
            for j in range(1, self.height - 1):
                self.canvas.draw(" ", self.position, Position(i, j))

        # Top + bottom edges
        self.canvas.draw_line(
            self.canvas.to_canvas_pos(self, Position(0, 0)),
            self.canvas.to_canvas_pos(self, Position(self.width - 1, 0)),
            line_symbol=edge_hori,
        )

        self.canvas.draw_line(
            self.canvas.to_canvas_pos(self, Position(0, self.height - 1)),
            self.canvas.to_canvas_pos(self, Position(self.width - 1, self.height - 1)),
            line_symbol=edge_hori,
        )

        self.canvas.draw_line(
            self.canvas.to_canvas_pos(self, Position(0, 0)),
            self.canvas.to_canvas_pos(self, Position(0, self.height - 1)),
            line_symbol=edge_vert,
        )

        self.canvas.draw_line(
            self.canvas.to_canvas_pos(self, Position(self.width - 1, 0)),
            self.canvas.to_canvas_pos(self, Position(self.width - 1, self.height - 1)),
            line_symbol=edge_vert,
        )

        # for i in range(1, self.width - 1):
        #     self.canvas.draw(edge_hori, self.position, Position(i, 0))
        #     self.canvas.draw(edge_hori, self.position, Position(i, self.height - 1))

        # left + right edges
        # for i in range(1, self.height - 1):
        #     self.canvas.draw(edge_vert, self.position, Position(0, i))
        #     self.canvas.draw(edge_vert, self.position, Position(self.width - 1, i))

        self.canvas.draw(corner_tl, self.position, self.corners[Corner.TOP_LEFT])
        self.canvas.draw(corner_tr, self.position, self.corners[Corner.TOP_RIGHT])
        self.canvas.draw(corner_bl, self.position, self.corners[Corner.BOTTOM_LEFT])
        self.canvas.draw(corner_br, self.position, self.corners[Corner.BOTTOM_RIGHT])

        if self.text:
            self.canvas.draw(self.text, self.position, self.get_label_pos(self.text))

    def create_anchor(self, direction: Direction) -> Anchor:
        anchors_dir = self.anchors[direction]

        size = len(anchors_dir)

        step_x = self.width // (size + 2)
        step_y = self.height // (size + 2)
        match direction:
            case Direction.DOWN:
                offset_x = step_x
                offset_y = self.height - 1
            case Direction.UP:
                offset_x = step_x
                offset_y = 0

        # 1. Adjust anchor positions
        for idx in range(size):
            anchors_dir[idx].position.x = offset_x
            anchors_dir[idx].position.y = offset_y

            match direction:
                case Direction.DOWN:
                    offset_x += step_x
                case Direction.UP:
                    offset_x += step_x

        new_anchor = Anchor(Position(offset_x, offset_y), self)
        anchors_dir.append(new_anchor)
        # print(anchors_dir)
        # print(offset_x)

        return new_anchor

        # Readjust
        # return anchors_dir[size - 1]

    def get_label_pos(self, label: str) -> Position:
        # Offset from the left edge
        label_x = self.center.x - (len(label) // 2)
        label_y = self.center.y
        return Position(label_x, label_y)
