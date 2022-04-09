# charset
# 设置方面
# 2022/04/07
from PySide6.QtGui import QFont
from PySide6.QtWidgets import *
from utils.commonhelper import CommonHelper


class Settings(QWidget):
    def __init__(self,parent):
        super(Settings, self).__init__(parent)
        self.license = CommonHelper.read_file(r"licenses/license.html")
        self.setup_ui()

    def setup_ui(self):
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(0)
        h_layout.addWidget(self.create_scroll_area())
        self.setLayout(h_layout)

    def create_scroll_area(self):
        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(0)
        s_area = QScrollArea(self)
        s_area.setLayout(v_layout)
        v_layout.addWidget(self.create_version_block(s_area))
        v_layout.addWidget(self.create_about_me_block(s_area))
        v_layout.addStretch(0)
        return s_area

    def create_group(self, parent, title, widget):
        v_layout = QVBoxLayout()
        v_layout.setSpacing(0)
        group = QGroupBox(title, parent)
        group.setFont(QFont("微软雅黑", 13))
        group.setLayout(v_layout)
        v_layout.addWidget(widget)
        return group

    # 关于我
    def create_about_me_block(self, parent):
        about_me_label = QLabel(parent)
        about_me_label.adjustSize()
        about_me_label.setFont(QFont("微软雅黑", 11))
        about_me_label.setOpenExternalLinks(True)
        about_me_label.setText(self.license)
        group = self.create_group(parent, "关于本软件", about_me_label)
        return group

    # 版本
    def create_version_block(self, parent):
        label = QLabel(parent)
        label.adjustSize()
        label.setFont(QFont("微软雅黑", 11))
        label.setText("当前版本:1.0")
        group = self.create_group(parent, "软件版本", label)
        return group


if __name__ == '__main__':
    app = QApplication()
    settings = Settings()
    settings.show()
    app.exec()
