import sys
from PySide6.QtCore import QUrl, Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QIcon, QColor
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import QWidget, QApplication, QPushButton, QHBoxLayout, QLabel, QVBoxLayout

from component.MySlider import MySlider
from networks.RequestApi import RequestAPI
from utils.timeformart import TimeFormat


# 实现音乐播放器功能和UI
# 2022/3/22
class MusicPlayer(QWidget):
    # 播放上一首歌曲
    play_prev_song = Signal()
    # 播放下一曲
    play_next_song = Signal()

    def __init__(self):
        super(MusicPlayer, self).__init__()
        self.img_label = None
        self.player = QMediaPlayer(self)
        self.out_put = QAudioOutput(self)
        self.player.setAudioOutput(self.out_put)
        self.out_put.setVolume(0.5)
        self.is_user_changed = False  # 是否使用改变的
        self.req_api = None
        self.task = None
        self.music = None
        # 注意这里有个问题
        # 在处理函数中会去调用slider的setValue进度条，
        # 会再次触发slider的valueChanged事件会导致重新设置音乐的位置，
        # 导致卡顿的问题
        # 解决方案就是在继承的类中存放一个变量用来判断是否是用户移动
        # 默认是false，当用户拖动时，设置成true
        self.player.positionChanged.connect(self.set_slider_position)
        # 这里也是同样的问题
        # playbackStateChanged 自动切换下一曲
        self.player.playbackStateChanged.connect(self.play_state_changed)
        self.play_song_name = None
        self.volume_slider = None
        self.play_slider = None
        self.cur_play_time = None
        self.total_play_time = None
        self.play_state_btn = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.create_left_image())
        main_layout.addLayout(self.create_center_slider())
        main_layout.addLayout(self.create_play_controller())
        self.setLayout(main_layout)

    # 设置播放的音乐文件
    def set_play_data(self, music):
        self.music = music
        self.is_user_changed = True
        self.player.setSource(QUrl(music.real_play_url))
        # 开启线程设置图片
        self.req_api = RequestAPI(music.album_img_url, RequestAPI.GET_IMAGE_CONTENT)
        self.req_api.get_pic_content.connect(self.handle_get_pic_content)
        self.req_api.start()
        # 设置正在播放的歌曲名称
        self.play_song_name.setText(music.song_name + "-" + music.artists)
        # 设置歌曲总时长
        self.total_play_time.setText("/" + music.duration)
        # 设置进度条的最大值
        self.play_slider.setMaximum(TimeFormat.format_str_to_int_time(music.duration))
        # 设置播放图标为
        self.play_state_btn.setIcon(QIcon("./icons/pause.png"))

    # 播放音乐
    def start_play(self):
        if self.player.playbackState() != QMediaPlayer.PlayingState:
            self.player.play()
            self.is_user_changed = False

    # 停止播放
    def stop_play(self):
        if self.player.playbackState() != QMediaPlayer.StoppedState:
            self.player.stop()

    # 暂停播放
    def pause_play(self):
        # 只有正在播放时才能暂停
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()

    # 重置播放器
    def reset_player(self):
        # 音乐为空
        self.music = None
        self.stop_play()
        # 设置正在播放的歌曲名称
        self.play_song_name.setText("")
        # 设置歌曲总时长
        self.total_play_time.setText("/00:00")
        # 设置进度条的最大值
        self.play_slider.setMaximum(100)
        # 设置播放图标为
        self.play_state_btn.setIcon(QIcon("./icons/play.png"))
        self.img_label.clear()

    # 设置进度条
    def set_slider_position(self):
        if not self.play_slider.isSliderDown():
            p_pos = self.player.position()
            self.play_slider.setValue(p_pos)
            self.cur_play_time.setText(TimeFormat.format_int_to_str_time(p_pos))

    # 更新播放状态
    def play_state_changed(self):
        # 如果处于停止状态并且不是用户改变的，播放下一曲
        if self.player.playbackState() == QMediaPlayer.StoppedState and not self.is_user_changed and self.music:
            # 直接发送信号与用户发送区别开
            self.play_next_song.emit()

    # 最左边歌曲图片
    def create_left_image(self):
        self.img_label = QLabel(self)
        self.img_label.setObjectName("img_url")
        self.img_label.setFixedSize(60, 60)
        return self.img_label

    # 中间的播放条等
    def create_center_slider(self):
        play_center = QVBoxLayout()
        play_center.setSpacing(0)
        play_center.setContentsMargins(0, 0, 0, 0)
        play_center_top_layout = QHBoxLayout()
        play_center_top_layout.setSpacing(0)
        play_center_top_layout.setContentsMargins(0, 0, 0, 0)

        # 上边歌曲名称以及音量控制条
        self.play_song_name = QLabel("")
        self.volume_slider = MySlider(orientation=Qt.Horizontal)
        self.volume_slider.setCursor(Qt.PointingHandCursor)
        self.volume_slider.valueChanged.connect(self.handle_volume_slider_change)
        # 设置最大值和最大小值(0-100)音量
        self.volume_slider.setMaximum(100)
        self.volume_slider.setMinimum(0)
        # 设置默认音量为50
        self.volume_slider.setValue(50)
        self.volume_slider.setToolTip(f"音量为:{self.volume_slider.value()}")
        play_center_top_layout.addWidget(self.play_song_name, alignment=Qt.AlignLeft | Qt.AlignBottom)
        play_center_top_layout.addWidget(self.volume_slider, alignment=Qt.AlignRight | Qt.AlignCenter)

        # 中间播放进度条
        self.play_slider = MySlider(orientation=Qt.Horizontal)
        # 设置鼠标指针
        self.play_slider.setCursor(Qt.PointingHandCursor)
        self.play_slider.setTracking(False)  # 关闭跟踪，只有当用户释放滑块才会进行进度更改
        self.play_slider.valueChanged.connect(self.handle_play_slider_move)

        # 下面播放时长显示
        play_center_bottom_layout = QHBoxLayout()
        self.cur_play_time = QLabel("00:00")
        self.cur_play_time.adjustSize()
        self.total_play_time = QLabel("/00:00")
        self.total_play_time.adjustSize()

        # 添加控件到下面的布局中
        play_center_bottom_layout.addStretch(0)
        play_center_bottom_layout.addWidget(self.cur_play_time, alignment=Qt.AlignRight | Qt.AlignTop)
        play_center_bottom_layout.addWidget(self.total_play_time, alignment=Qt.AlignRight | Qt.AlignTop)

        # 中间部分总布局
        play_center.addLayout(play_center_top_layout)
        play_center.addWidget(self.play_slider)
        play_center.addLayout(play_center_bottom_layout)
        return play_center

    # 右边的播放控制
    def create_play_controller(self):
        play_controller = QHBoxLayout()
        # 上一首
        pre_btn = QPushButton(icon=QIcon("./icons/prev.png"))
        pre_btn.setIconSize(QSize(24, 24))
        pre_btn.setCursor(Qt.PointingHandCursor)
        pre_btn.setProperty("play_controller", "true")
        pre_btn.clicked.connect(self.handle_play_prev)
        # 播放状态
        self.play_state_btn = QPushButton(icon=QIcon("./icons/play.png"))
        self.play_state_btn.setIconSize(QSize(24, 24))
        self.play_state_btn.setCursor(Qt.PointingHandCursor)
        self.play_state_btn.clicked.connect(self.handle_change_play_state)
        self.play_state_btn.setProperty("play_controller", "true")
        # 下一首
        next_btn = QPushButton(icon=QIcon("./icons/next.png"))
        next_btn.setCursor(Qt.PointingHandCursor)
        next_btn.setIconSize(QSize(24, 24))
        next_btn.setProperty("play_controller", "true")
        next_btn.clicked.connect(self.handle_play_next)
        # 添加子控件
        play_controller.addWidget(pre_btn)
        play_controller.addWidget(self.play_state_btn)
        play_controller.addWidget(next_btn)
        return play_controller

    # 处理滚动条值改变事件
    def handle_play_slider_move(self, value):
        # 是用户触发的就更改播放音乐位置
        if self.play_slider.is_user_moved and self.music:
            # 设置播放位置
            self.player.setPosition(value)
            # 设置进度条的位置并且更新UI
            self.cur_play_time.setText(TimeFormat.format_int_to_str_time(value))
            # 开始播放
            self.start_play()
            # 重置状态
            self.play_slider.is_user_moved = False

    # 处理音量滚动条改变事件
    def handle_volume_slider_change(self, value):
        # 音量的区间为[0,1]
        self.out_put.setVolume(value / 100)
        self.volume_slider.setToolTip(f"音量为:{self.volume_slider.value()}")

    # 处理获取图片内容并显示在界面上
    def handle_get_pic_content(self, content):
        pixmap = QPixmap()
        pixmap.loadFromData(content)
        self.img_label.setPixmap(pixmap)
        self.img_label.setScaledContents(True)  # 设置图片自适应
        # 没有音乐对象时候清除图片
        # 这里需要注意一下，如果不清除，
        # 会导致后面的图片字节会继续显示导致重置方法中的clear()失效
        if not self.music:
            self.img_label.clear()

    # 处理改变播放状态
    def handle_change_play_state(self):
        if self.music:
            # 处在播放状态 切换图片暂停
            if self.player.playbackState() == QMediaPlayer.PlayingState:
                self.play_state_btn.setIcon(QIcon("./icons/play.png"))
                self.pause_play()
            else:
                self.play_state_btn.setIcon(QIcon("./icons/pause.png"))
                self.start_play()

    # 处理上一曲
    def handle_play_prev(self):
        if self.music:
            # 是用户修改的歌曲
            self.is_user_changed = True
            self.play_prev_song.emit()

    # 处理上一曲
    def handle_play_next(self):
        if self.music:
            # 是用户修改的歌曲
            self.is_user_changed = True
            self.play_next_song.emit()


if __name__ == '__main__':
    app = QApplication()
    player = MusicPlayer()
    sys.exit(app.exec())
