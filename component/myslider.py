from PySide6.QtWidgets import QSlider


# 重写slider使得能够跟随鼠标移动
# 2022/3/23

class MySlider(QSlider):
    def __init__(self, orientation):
        super(MySlider, self).__init__(orientation)
        self.is_user_moved = False

    def mousePressEvent(self, ev) -> None:
        super().mousePressEvent(ev)
        s = ev.position().x() / self.width()
        val = s * (self.maximum() - self.minimum()) + self.minimum()
        self.is_user_moved = True
        self.setValue(val)
