# 音乐播放器
# pyside6
# 2022/3/18
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from component.WindowTitle import WindowTitle
from component.ContentWidget import ContentWidget
from utils.commonhelper import CommonHelper


# 音乐播放器主界面
class MusicPlayer(QMainWindow):
    def __init__(self):
        # 设置无窗口标题
        super().__init__(flags=Qt.FramelessWindowHint)
        # 设置窗口尺寸为1000*640
        self.resize(1000, 640)
        # 设置窗口标题
        self.setWindowTitle("Music Player")
        # 设置窗口图标
        self.setWindowIcon(QIcon("./icons/icon.png"))
        # 窗口上半部分控件
        self.win_title = WindowTitle(self)
        # 下半部分内容
        self.content_widget = ContentWidget()
        self.setup_ui()
        # 设置app样式
        self.setStyleSheet(CommonHelper.read_file("qss/app.qss"))
        self.show()

    def setup_ui(self):
        self.setContentsMargins(0, 0, 0, 0)
        # 中心控件
        center_widget = QWidget()
        # 中心控件布局 分为上下两个部分
        center_layout = QVBoxLayout()
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        # 绑定信号
        self.connect_signal()
        center_layout.addWidget(self.win_title)
        center_layout.addWidget(self.content_widget)
        # 设置中心控件布局
        center_widget.setLayout(center_layout)
        # 设置中心控件
        self.setCentralWidget(center_widget)

    # 连接信号
    def connect_signal(self):
        # 关闭窗口
        self.win_title.close_window.connect(lambda: self.close())
        # 最小化窗口
        self.win_title.mini_window.connect(lambda: self.showMinimized())
        # 搜索信号
        self.win_title.search_content.connect(lambda keys: self.content_widget.start_search_content.emit(keys))


if __name__ == '__main__':
    app = QApplication()
    player = MusicPlayer()
    sys.exit(app.exec())
