# # 音乐播放器
# # pyside6
# # 2022/3/18
# # xianjuyao
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QApplication, QSystemTrayIcon, QMessageBox, QMenu
from component.windowtitle import WindowTitle
from component.contentwidget import ContentWidget
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
        # 托盘部分
        self._minimize_action = None
        self._restore_action = None
        self._quit_action = None

        self._tray_icon = None
        self._tray_icon_menu = None
        self.setup_ui()
        # 设置app样式
        self.setStyleSheet(CommonHelper.read_file("qss/app.qss"))
        self.show()

    def setup_ui(self):
        self.setContentsMargins(0, 0, 0, 0)
        # 创建托盘
        self.create_actions()
        self.create_tray_icon()
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

    def create_actions(self):
        self._minimize_action = QAction("最小化", self)
        self._minimize_action.triggered.connect(self.hide)

        self._restore_action = QAction("显示主界面", self)
        self._restore_action.triggered.connect(self.showNormal)

        self._quit_action = QAction("退出", self)
        self._quit_action.triggered.connect(qApp.quit)

    def create_tray_icon(self):
        self._tray_icon_menu = QMenu(self)
        self._tray_icon_menu.addAction(self._minimize_action)
        self._tray_icon_menu.addAction(self._restore_action)
        self._tray_icon_menu.addSeparator()
        self._tray_icon_menu.addAction(self._quit_action)

        self._tray_icon = QSystemTrayIcon(self)
        self._tray_icon.setIcon(QIcon("icons/heart.png"))
        self._tray_icon.setContextMenu(self._tray_icon_menu)
        # 在系统托盘显示此对象
        self._tray_icon.show()

    # 连接信号
    def connect_signal(self):
        # 关闭窗口
        self.win_title.close_window.connect(lambda: self.close())
        # 最小化窗口
        self.win_title.mini_window.connect(lambda: self.showMinimized())
        # 搜索信号
        self.win_title.search_content.connect(lambda keys: self.content_widget.start_search_content.emit(keys))

    def closeEvent(self, event) -> None:
        if self._tray_icon.isVisible():
            QMessageBox.information(self, "系统托盘",
                                    "系统将会在系统托盘中保持运行 "
                                    "如果想结束程序, 请在系统托盘右键退出")
            self.hide()
            event.ignore()



if __name__ == '__main__':
    app = QApplication()
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "系统托盘", "本系统检测不出系统托盘")
        sys.exit(1)
    QApplication.setQuitOnLastWindowClosed(False)
    player = MusicPlayer()
    sys.exit(app.exec())
