from pytermgraph.canvas import Canvas
from pytermgraph.support import Position
from pytermgraph.render_object import Direction

# import pygraphviz as pgv
# A = pgv.AGraph()
# # add some edges
# A.add_edge(1, 2)
# A.add_edge(2, 3)
# A.add_edge(1, 3)
# A.add_edge(3, 4)
# A.add_edge(3, 5)
# A.add_edge(3, 6)
# A.add_edge(4, 6)
#
# print(A.string())
# A.layout(prog="dot")
# print(A.string())

canvas = Canvas(100, 15, fill="░")

box1 = canvas.add_box(9, 5, Position(3, 1), "hello")
box2 = canvas.add_box(11, 5, Position(3, 9), "world!")
box3 = canvas.add_box(11, 5, Position(30, 9), "ASCII!")

edge1 = canvas.draw_edge_boxes(box1, box2, start_direction=Direction.VERTICAL)
edge2 = canvas.draw_edge_boxes(box1, box3, start_direction=Direction.VERTICAL)

canvas.render()

# box1.render()
# box2.render()
# box3.render()
#
# edge1.render()
# edge2.render()

# edge2 = canvas.draw_edge_boxes(
#     box2, box3, start_direction=Direction.VERTICAL, end_direction=Direction.HORIZONTAL
# )
# edge3 = canvas.draw_edge_boxes(box1, box3, start_direction=Direction.VERTICAL)
# edge3.render()

print(canvas.to_string())
