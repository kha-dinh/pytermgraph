from pytermgraph.render import Canvas, Position

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

canvas = Canvas(30, 12, fill="_")

box1 = canvas.draw_box(9, 5, Position(3, 1), "hello")
box2 = canvas.draw_box(11, 5, Position(17, 3), "world!")
box3 = canvas.draw_box(11, 5, Position(3, 6), "ASCII!")


canvas.draw_edge_boxes(box1, box2)
canvas.draw_edge_boxes(box2, box3)

box1.render()
box2.render()
box3.render()

# print(canvas.to_string())
