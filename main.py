from pytermgraph.render import Canvas, Position

canvas = Canvas(30, 10, fill="a")
box1 = canvas.draw_box(9, 4, Position(3, 2), "hello")
# print(canvas.to_string())
box2 = canvas.draw_box(9, 4, Position(16, 2), "world!")
canvas.draw_edge(box1, box2)
print(canvas.to_string())
