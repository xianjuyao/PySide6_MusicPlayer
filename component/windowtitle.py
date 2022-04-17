# 窗口的标题栏内容部分
# 最左边 logo 中间搜索框 右边一个最小化按钮和一个关闭按钮
# 2022/3/18
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton


class WindowTitle(QWidget):
    close_window = Signal()
    mini_window = Signal()
    search_content = Signal(str)

    def __init__(self, window):
        super(WindowTitle, self).__init__()
        self.w = window
        # 鼠标的位置
        self.mouse_x = None
        self.mouse_y = None
        # 窗口的位置
        self.w_x = None
        self.w_y = None
        # 位移
        self.move_x = None
        self.move_y = None
        self.setup_ui()

    def setup_ui(self):
        # 水平布局
        main_layout = QHBoxLayout()
        # logo
        logo = QLabel("cw", self)
        logo.setObjectName("logo")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedSize(60, 50)
        # 搜索框
        self.search_line = QLineEdit(self)
        self.search_line.setContentsMargins(20, 0, 0, 0)
        self.search_line.setFixedSize(340, 28)
        self.search_line.setObjectName("search_line")
        self.search_line.setPlaceholderText("Search for something")
        self.search_line.returnPressed.connect(self.search_content_btn)
        # 设置图标
        search_btn = QPushButton(icon=QIcon("./icons/search.png"))
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.setObjectName("search_btn")
        # 按下回车键去搜索内容
        search_btn.clicked.connect(self.search_content_btn)
        search_container = QHBoxLayout()
        search_container.setContentsMargins(0, 0, 0, 0)
        search_container.setSpacing(0)
        search_container.addStretch()
        search_container.addWidget(search_btn, alignment=Qt.AlignCenter | Qt.AlignCenter)
        self.search_line.setLayout(search_container)
        # 最小化按钮
        mini_bt = QPushButton(self)
        mini_bt.setFixedSize(46, 30)
        mini_bt.setProperty("name", "mini_window")
        mini_bt.setIcon(QIcon("./icons/mini.png"))
        mini_bt.setToolTip("最小化")
        # 关闭按钮信号
        mini_bt.clicked.connect(lambda: self.mini_window.emit())
        # 最小化按钮
        close_bt = QPushButton(self)
        close_bt.setProperty("name", "close_window")
        close_bt.setFixedSize(46, 30)
        close_bt.setIcon(QIcon("./icons/close.png"))
        close_bt.setToolTip("关闭")
        # 关闭按钮信号
        close_bt.clicked.connect(lambda: self.close_window.emit())
        # 添加控件至布局中
        main_layout.addWidget(logo)
        main_layout.addWidget(self.search_line)
        main_layout.addStretch()
        # 必须同时指定水平和垂直两个方向才能生效
        main_layout.addWidget(mini_bt, alignment=Qt.AlignRight | Qt.AlignTop)
        main_layout.addWidget(close_bt, alignment=Qt.AlignRight | Qt.AlignTop)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        # 设置布局
        self.setLayout(main_layout)

    def search_content_btn(self):
        if len(str.lstrip(self.search_line.text())) == 0:
            return
        self.search_content.emit(self.search_line.text())

    def mousePressEvent(self, event):
        # 鼠标的位置
        self.mouse_x = event.globalPosition().x()
        self.mouse_y = event.globalPosition().y()
        # 窗口的位置
        self.w_x = self.w.x()
        self.w_y = self.w.y()

    def mouseMoveEvent(self, event):
        # 移动后的鼠标位置-移动前鼠标位置
        self.move_x = event.globalPosition().x() - self.mouse_x
        self.move_y = event.globalPosition().y() - self.mouse_y
        # 窗口移动相同位置
        self.w.move(self.w_x + self.move_x, self.w_y + self.move_y)
