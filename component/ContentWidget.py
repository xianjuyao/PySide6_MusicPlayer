from PySide6.QtCore import QSize, Signal, QItemSelectionModel, QPoint, QThread
from PySide6.QtGui import QIcon, QStandardItemModel, QStandardItem, Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTableView, QAbstractItemView, \
    QHeaderView, QStackedLayout, QMessageBox, QLineEdit, QLabel

from Entity.Music import Music
from networks.RequestApi import RequestAPI
from utils.commonhelper import CommonHelper
from utils.db_utils import DB_Utils
from utils.timeformart import TimeFormat
from component.Settings import Settings
from component.MusicPlayer import MusicPlayer
from math import ceil


# 内容部分
# 2022/3/19
class ContentWidget(QWidget):
    # 开始搜索内容信号
    start_search_content = Signal(str)
    # 每一页返回的数量
    MAX_COUNT = 30

    def __init__(self):
        super(ContentWidget, self).__init__()
        # 初始化数据库内容
        self.db = DB_Utils("./db/my_list.db", "my_list")
        # 歌曲总量
        self.song_count = 0
        # 初始化请求第一页
        self.cur_page = 1
        # 总页数
        self.total_page_count = 0
        self.keys = ""
        # 为了防止用户多次快速点击
        self.is_clicked = False
        # 是否是添加歌曲
        self.is_add = False
        # 是否删除歌曲
        self.is_delete = True
        # 搜索歌曲列表
        self.music_list = None
        # 试听列表内容
        self.my_music_list = None
        # 试听列表表格
        self.my_list_table = None
        # 试听列表模型
        self.my_list_model = None
        # 搜索内容表格
        self.search_table = None
        # 搜索内容表格模型
        self.search_model = None
        # 当前播放的index
        self.cur_play_index = None
        # 当前播放的id
        self.cur_play_id = None
        # 添加列表歌曲id
        self.add_list_id = None
        self.req_api = None
        # 显示的表头
        self.labels = ["id", "歌曲名", "艺术家", "专辑名", "时长", "操作"]
        # ui初始化
        self.setup_ui()

    # ui
    def setup_ui(self):
        # 查询完成信号
        # 必须在创建ui之前连接信号，否则第一次加载数据会不触发
        self.db.select_complete.connect(self.handle_select_complete)
        # sql语句完成信号
        self.db.exec_sql_complete.connect(self.handle_exec_sql_complete)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.create_left_block())
        main_layout.addWidget(self.create_right_block())
        self.setLayout(main_layout)
        # 点击搜索信号
        self.start_search_content.connect(self.handle_start_search_content)
        # 播放上一曲信号
        self.player.play_prev_song.connect(self.handle_play_prev_song)
        # 播放下一曲信号
        self.player.play_next_song.connect(self.handle_play_next_song)

    ################# 左侧区域开始#################################
    def create_left_block(self):
        left_widget = QWidget()
        left_widget.setObjectName("left_widget")
        left_layout = QVBoxLayout()
        left_layout.setSpacing(0)
        left_layout.setContentsMargins(0, 0, 0, 0)
        # 搜索侧边栏按钮
        self.search_tab_btn = QPushButton(icon=QIcon("./icons/search.png"))
        self.search_tab_btn.setIconSize(QSize(24, 24))
        self.search_tab_btn.setFixedSize(60, 60)
        self.search_tab_btn.setObjectName("search_tab_btn")
        self.search_tab_btn.setProperty("selected", "true")
        self.search_tab_btn.clicked.connect(self.handle_search_tab_click)
        # 设置鼠标指针为手指
        self.search_tab_btn.setCursor(Qt.PointingHandCursor)
        self.search_tab_btn.setToolTip("搜索")
        # 我的列表侧边栏按钮
        self.my_list_tab_btn = QPushButton(icon=QIcon("./icons/wodexihuan.png"))
        self.my_list_tab_btn.setIconSize(QSize(24, 24))
        self.my_list_tab_btn.setFixedSize(60, 60)
        self.my_list_tab_btn.setProperty("selected", "false")
        self.my_list_tab_btn.clicked.connect(self.handle_my_list_tab_click)
        self.my_list_tab_btn.setCursor(Qt.PointingHandCursor)
        self.my_list_tab_btn.setToolTip("我的列表")
        # 设置页面侧边栏按钮
        self.setting_tab_btn = QPushButton(icon=QIcon("./icons/shezhi.png"))
        self.setting_tab_btn.setIconSize(QSize(24, 24))
        self.setting_tab_btn.setFixedSize(60, 60)
        self.setting_tab_btn.setProperty("selected", "false")
        self.setting_tab_btn.clicked.connect(self.handle_setting_tab_click)
        self.setting_tab_btn.setToolTip("设置")
        self.setting_tab_btn.setCursor(Qt.PointingHandCursor)
        # 添加至布局
        left_layout.addWidget(self.search_tab_btn)
        left_layout.addWidget(self.my_list_tab_btn)
        left_layout.addWidget(self.setting_tab_btn)
        left_layout.addStretch()
        left_widget.setLayout(left_layout)
        return left_widget

    # 创建右侧内容区域
    def create_content_layout(self):
        self.s_layout = QStackedLayout()
        self.s_layout.setContentsMargins(0, 0, 0, 0)
        self.s_layout.setSpacing(0)
        self.s_layout.addWidget(self.create_search_content_table())
        self.s_layout.addWidget(self.create_my_list_table())
        self.s_layout.addWidget(self.create_settings_content())

    ###################右侧区域开始################################
    def create_right_block(self):
        right_widget = QWidget()
        right_main_layout = QVBoxLayout()
        self.create_content_layout()
        right_main_layout.setSpacing(0)
        right_main_layout.setContentsMargins(0, 0, 0, 0)
        right_main_layout.addLayout(self.s_layout)
        self.player = MusicPlayer()
        right_main_layout.addWidget(self.player)
        right_widget.setLayout(right_main_layout)
        return right_widget

    # 创建搜索内容表格
    def create_search_content_table(self):
        content_widget = QWidget(self)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        model = self.create_search_table_model([])
        self.search_table = self.create_table(model, 0)
        self.search_table.horizontalHeader().setVisible(False)  # 隐藏表头
        self.search_table.doubleClicked.connect(self.handle_search_table_double_clicked)
        content_layout.addWidget(self.search_table)
        content_layout.addWidget(self.create_search_table_page_layout())
        content_widget.setLayout(content_layout)
        return content_widget

    # 创建搜索表格数据模型
    def create_search_table_model(self, data):
        self.search_model = self.create_model(data)
        return self.search_model

    # 创建tableview中的操作控件
    def create_search_table_item_operation(self, model):
        icon1 = QIcon("icons/shouting.png")
        icon2 = QIcon("icons/tianjia.png")
        self.create_table_operation(model,
                                    self.search_table, icon1, icon2,
                                    self.handle_play_btn_clicked,
                                    self.handle_add_btn_clicked,
                                    "播放音乐",
                                    "添加至我的列表")

    # 下方分页部分
    def create_search_table_page_layout(self):
        self.page_widget = QWidget()
        self.page_widget.setVisible(False)
        self.page_widget.setObjectName("page_widget")
        page_layout = QHBoxLayout()
        page_layout.setSpacing(3)
        page_layout.setContentsMargins(0, 0, 0, 2)
        # 上一页按钮
        pre_page_btn = QPushButton("上一页")
        pre_page_btn.clicked.connect(self.handle_pre_page)
        pre_page_btn.setCursor(Qt.PointingHandCursor)
        # 跳转单行文本框
        self.page_to_btn = QLineEdit("1")
        self.page_to_btn.setFixedSize(30, 25)
        self.page_to_btn.returnPressed.connect(self.handle_page_to)
        self.total_page_label = QLabel("/1")
        # 下一页按钮
        next_page_btn = QPushButton("下一页")
        next_page_btn.clicked.connect(self.handle_next_page)
        next_page_btn.setCursor(Qt.PointingHandCursor)
        # 添加控件至布局
        page_layout.addStretch()
        page_layout.addWidget(pre_page_btn)
        page_layout.addWidget(self.page_to_btn)
        page_layout.addWidget(self.total_page_label)
        page_layout.addWidget(next_page_btn)
        page_layout.addStretch()
        self.page_widget.setLayout(page_layout)
        return self.page_widget

    # 右侧试听列表表格
    def create_my_list_table(self):
        model = self.create_my_list_table_model()
        self.my_list_table = self.create_table(model, 0)
        # 绑定双击事件
        self.my_list_table.doubleClicked.connect(self.handle_my_list_table_double_clicked)
        return self.my_list_table

    # 创建试听列表模型
    def create_my_list_table_model(self):
        # 查询音乐列表
        self.db.exec_select("select * from my_list order by insert_time desc")
        return self.create_model([])

    # 创建试听列表的操作控件
    def create_my_list_table_item_operation(self, model):
        icon1 = QIcon("icons/shouting.png")
        icon2 = QIcon("icons/shanchu.png")
        self.create_table_operation(model,
                                    self.my_list_table, icon1, icon2,
                                    self.handle_my_list_play_btn_clicked,
                                    self.handle_my_list_remove_btn_clicked,
                                    "播放音乐",
                                    "删除音乐")

    # 右侧设置
    def create_settings_content(self):
        return Settings(self)

    ###################通用部分开始############################
    # 创建模型
    def create_model(self, data):
        row = len(data)  # 行
        col = len(self.labels)  # 列
        model = QStandardItemModel(row, col)
        model.setHorizontalHeaderLabels(self.labels)
        sel = QItemSelectionModel(model)
        for index, item in enumerate(data):
            s_id = QStandardItem(str(item.s_id))
            model.setItem(index, 0, s_id)
            s_name = QStandardItem(item.song_name)
            s_name.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            model.setItem(index, 1, s_name)
            s_artists = QStandardItem(item.artists)
            s_artists.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            model.setItem(index, 2, s_artists)
            s_album = QStandardItem(item.album)
            s_album.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            model.setItem(index, 3, s_album)
            if type(item.duration) == int:
                s_duration = QStandardItem(TimeFormat.format_int_to_str_time(item.duration))
            else:
                s_duration = QStandardItem(item.duration)
            s_duration.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            model.setItem(index, 4, s_duration)
            item = QStandardItem()
            model.setItem(index, 5, item)
        return model

    # 创建表格
    def create_table(self, model, hidden_col):
        table = QTableView(self)
        # 设置选择整行
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置均分表头
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        # 不可编辑
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 不展示表格线
        table.setShowGrid(False)
        # 设置默认模型
        table.setModel(model)
        # 设置单行选择
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        # 隐藏Id列
        table.setColumnHidden(hidden_col, True)
        return table

    # 创建表格操作按钮部分
    def create_table_operation(self, model, table, icon1, icon2, fun1, fun2, tip1, tip2):
        for i in range(model.rowCount()):
            # 添加表格中的操作列
            operation_widget = QWidget()
            operation_widget.setProperty("operation_widget", "true")
            # 播放
            play_btn = QPushButton()
            play_btn.setIcon(icon1)
            play_btn.setFixedSize(30, 30)
            play_btn.setCursor(Qt.PointingHandCursor)
            play_btn.setToolTip(tip1)
            play_btn.clicked.connect(fun1)
            # 添加列表
            add_btn = QPushButton()
            add_btn.setIcon(icon2)
            add_btn.setFixedSize(30, 30)
            add_btn.setCursor(Qt.PointingHandCursor)
            add_btn.setToolTip(tip2)
            add_btn.clicked.connect(fun2)
            # 操作区域部分布局
            o_layout = QHBoxLayout()
            o_layout.setSpacing(0)
            o_layout.setContentsMargins(0, 0, 0, 0)
            o_layout.addStretch()
            o_layout.addWidget(play_btn)
            o_layout.addWidget(add_btn)
            o_layout.addStretch()
            operation_widget.setLayout(o_layout)
            table.setIndexWidget(model.index(i, 5), operation_widget)

    # 获取表格控件的mode index
    def get_model_index(self, table):
        # 在表格中获取控件的行号
        push_btn = self.sender()
        if push_btn is None: return
        # 获取按钮的父控件的x坐标和y坐标
        x = push_btn.parentWidget().frameGeometry().x()
        y = push_btn.parentWidget().frameGeometry().y()
        # 根据按钮的父控件x和y坐标来定位对应的单元格
        index = table.indexAt(QPoint(x, y))
        return index

    # 获取模型数据
    def get_model_data(self, model, row, data_list):
        # 获取数据
        s_id = model.data(model.index(row, 0))
        s_name = model.data(model.index(row, 1))
        s_artists = model.data(model.index(row, 2))
        s_album = model.data(model.index(row, 3))
        s_duration = model.data(model.index(row, 4))
        album_img_url = data_list[row].album_img_url
        # 封装成一个对象
        return Music(s_id, s_name, s_artists, s_album, album_img_url, s_duration)

    # 选中表格中播放的行
    def selected_table_row_by_id(self, table, data_list, id):
        for index, item in enumerate(data_list):
            if str(item.s_id) == id:
                # 选中播放的行
                table.selectRow(index)
                # 设置播放的index
                self.cur_play_index = index
                break

    # 根据音乐id请求歌曲
    def request_music_by_id(self):
        url = f"https://autumnfish.cn/song/url?id={self.cur_play_id}"
        self.req_api = RequestAPI(url, RequestAPI.GET_URL)
        self.req_api.get_song_url.connect(self.handle_play_music)
        self.req_api.req_error.connect(self.handle_request_error)
        # 线程任务完成的时候有空就删除线程对象
        self.req_api.finished.connect(self.req_api.deleteLater)
        self.req_api.start()

    #####################槽函数处理部分开始#############################
    # 搜索点击事件
    def handle_search_tab_click(self):
        if self.s_layout.currentIndex() != 0:
            self.s_layout.setCurrentIndex(0)
            # 选中设置样式
            self.search_tab_btn.setProperty("selected", "true")
            self.my_list_tab_btn.setProperty("selected", "false")
            self.setting_tab_btn.setProperty("selected", "false")
            self.setStyleSheet(CommonHelper.read_file("qss/app.qss"))

    # 我的列表点击事件
    def handle_my_list_tab_click(self):
        if self.s_layout.currentIndex() != 1:
            self.s_layout.setCurrentIndex(1)
            # 选中设置样式
            self.search_tab_btn.setProperty("selected", "false")
            self.my_list_tab_btn.setProperty("selected", "true")
            self.setting_tab_btn.setProperty("selected", "false")
            self.setStyleSheet(CommonHelper.read_file("qss/app.qss"))

    # 设置按钮点击事件
    def handle_setting_tab_click(self):
        if self.s_layout.currentIndex() != 2:
            self.s_layout.setCurrentIndex(2)
            # 选中设置样式
            self.search_tab_btn.setProperty("selected", "false")
            self.my_list_tab_btn.setProperty("selected", "false")
            self.setting_tab_btn.setProperty("selected", "true")
            self.setStyleSheet(CommonHelper.read_file("qss/app.qss"))

    # 开启多线程请求api槽
    def handle_start_search_content(self, keys):
        if keys is not None:
            # 保存上一次的关键词
            self.keys = keys
            # 重置当前页为1
            self.cur_page = 1
            self.page_to_btn.setText(str(self.cur_page))
        if not self.is_clicked:
            self.is_clicked = True
            req_url = f"https://autumnfish.cn/cloudsearch?keywords={self.keys}&offset={(self.cur_page - 1) * self.MAX_COUNT}"
            self.req_api = RequestAPI(req_url)
            self.req_api.finished.connect(self.req_api.deleteLater)
            self.req_api.req_error.connect(self.handle_request_error)
            # 请求成功后更新tableview model
            self.req_api.update_table_view.connect(self.handle_update_search_table_model)
            # 开启多线程请求数据
            self.req_api.start()

    # 请求错误槽
    def handle_request_error(self):
        QMessageBox.warning(self, "错误", "网络错误,请稍后重试", QMessageBox.Ok, QMessageBox.No)

    # 请求成功后更新tableView model
    def handle_update_search_table_model(self, dic):
        # 设置搜索表头显示
        self.search_table.horizontalHeader().setVisible(True)
        # 设置搜索分页显示
        self.page_widget.setVisible(True)
        # 获取歌曲总数
        self.song_count = dic["songCount"]
        # 计算总页数向上取整
        self.total_page_count = ceil(self.song_count / self.MAX_COUNT)
        # 设置总页数
        self.total_page_label.setText(f"/{self.total_page_count}")
        # 是否是用户点击
        self.is_clicked = False
        self.music_list = dic["music_list"]
        # 根据list来创建模型
        model = self.create_search_table_model(self.music_list)
        # tableview 显示数据
        self.search_table.setModel(model)
        # 隐藏Id列
        self.search_table.setColumnHidden(0, True)
        # 创建table中的操作列
        self.create_search_table_item_operation(model)

    # 处理搜索表格的双击事件
    def handle_search_table_double_clicked(self, model_index):
        if not self.is_clicked:
            self.is_clicked = True
            # 播放的是第几行
            row = model_index.row()
            mc = self.get_model_data(self.search_table.model(), row, self.music_list)
            self.cur_play_id = mc.s_id
            # 根据id请求歌曲
            self.request_music_by_id()
            sql = f"insert into my_list(s_id,song_name,song_artists,song_album,album_img_url,song_duration) values('{mc.s_id}','{mc.song_name}','{mc.artists}','{mc.album}','{mc.album_img_url}','{mc.duration}')"
            # 保存数据库
            self.db.exec_sql(sql)

    # 处理我的列表表格的双击事件
    def handle_my_list_table_double_clicked(self, model_index):
        if not self.is_clicked:
            self.is_clicked = True
            # 获取model对象
            model = self.my_list_table.model()
            # 获取播放id
            self.cur_play_id = model.data(model.index(model_index.row(), 0))
            self.selected_table_row_by_id(self.my_list_table, self.my_music_list, self.cur_play_id)
            # 根据id请求播放数据
            self.request_music_by_id()

    # 处理播放音乐
    def handle_play_music(self, song_url):
        # 是否是用户点击
        self.is_clicked = False
        if len(self.my_music_list) > 0:
            music = None
            for item in self.my_music_list:
                if item.s_id == self.cur_play_id:
                    music = item
                    break
            if music is not None:
                music.set_real_url(song_url)
                self.player.set_play_data(music)
                self.player.start_play()

    # 处理播放上一曲
    def handle_play_prev_song(self):
        if len(self.my_music_list) > 0 and not self.is_clicked:
            self.is_clicked = True
            # 索引-1 如果超过第一个就跳转到最后一首
            self.cur_play_index -= 1
            if self.cur_play_index <= -1:
                self.cur_play_index = self.my_list_model.rowCount() - 1
            # 根据当前播放的index获取播放的id
            index = self.my_list_model.index(self.cur_play_index, 0)
            self.cur_play_id = self.my_list_model.data(index)
            # 请求歌曲数据
            self.request_music_by_id()
            self.my_list_table.selectRow(self.cur_play_index)  # 设置选中的行

    # 处理播放下一曲
    def handle_play_next_song(self):
        if len(self.my_music_list) > 0 and not self.is_clicked:
            self.is_clicked = True
            self.cur_play_index += 1
            # 索引+1 如果超过最后一个就跳转到第一首
            if self.cur_play_index >= self.my_list_model.rowCount():
                self.cur_play_index = 0
            index = self.my_list_model.index(self.cur_play_index, 0)
            self.cur_play_id = self.my_list_model.data(index)
            self.request_music_by_id()
            self.my_list_table.selectRow(self.cur_play_index)  # 设置选中的行

    # 处理请求下一页
    def handle_next_page(self):
        if self.music_list is not None:
            self.cur_page += 1
            if self.cur_page > self.total_page_count:
                self.cur_page = self.total_page_count
            self.handle_start_search_content(None)
            self.page_to_btn.setText(str(self.cur_page))

    # 处理请求上一页
    def handle_pre_page(self):
        if self.music_list is not None:
            self.cur_page -= 1
            if self.cur_page < 1:
                self.cur_page = 1
            self.handle_start_search_content(None)
            self.page_to_btn.setText((str(self.cur_page)))

    # 处理跳转
    def handle_page_to(self):
        if self.music_list is not None:
            text = self.page_to_btn.text()
            if text.isdigit():
                t = int(text)
                if self.total_page_count >= t >= 1:
                    self.cur_page = t
                    self.handle_start_search_content(None)

    # 添加按钮点击事件
    def handle_add_btn_clicked(self):
        self.is_add = True
        index = self.get_model_index(self.search_table)
        mc = self.get_model_data(self.search_table.model(), index.row(), self.music_list)
        self.add_list_id = mc.s_id
        sql = f"insert into my_list(s_id,song_name,song_artists,song_album,album_img_url,song_duration) values('{mc.s_id}','{mc.song_name}','{mc.artists}','{mc.album}','{mc.album_img_url}','{mc.duration}')"
        # 保存数据库
        self.db.exec_sql(sql)

    # 搜索界面播放按钮点击事件
    def handle_play_btn_clicked(self):
        index = self.get_model_index(self.search_table)
        self.search_table.doubleClicked.emit(index)

    # 我的列表界面按钮播放事件
    def handle_my_list_play_btn_clicked(self):
        index = self.get_model_index(self.my_list_table)
        self.my_list_table.doubleClicked.emit(index)

    # 我的列表删除按钮事件
    def handle_my_list_remove_btn_clicked(self):
        if self.is_delete:
            model = self.my_list_model
            index = self.get_model_index(self.my_list_table)
            row = index.row()
            s_id = model.data(model.index(row, 0))
            s_name = model.data(model.index(row, 1))
            # 提示用户是否确定删除
            res = QMessageBox.information(self, "提示", f"是否真要删除【{s_name}】", QMessageBox.Ok, QMessageBox.No)
            if res == QMessageBox.Ok:
                self.is_delete = False
                sql = f"delete from my_list where s_id='{s_id}'"
                # 保存数据库
                self.db.exec_sql(sql)
                # 当前播放的index不为None且删除的是当前播放的行
                if self.cur_play_index is not None and self.cur_play_index == row:
                    self.handle_play_next_song()

    # 处理查询数据库完成事件
    def handle_select_complete(self, music_list):
        # 没有数据，且点击了删除按钮
        if len(music_list) == 0 and self.is_delete:
            self.player.reset_player()
        self.my_music_list = music_list
        self.my_list_model = self.create_model(self.my_music_list)
        self.my_list_table.setModel(self.my_list_model)
        self.create_my_list_table_item_operation(self.my_list_model)
        # 选中播放表格的行号
        self.selected_table_row_by_id(self.my_list_table, self.my_music_list, self.cur_play_id)

    # 处理执行sql语句数据库完成事件
    def handle_exec_sql_complete(self):
        # 如果执行成功更新数据模型
        self.is_delete = True
        self.create_my_list_table_model()

    # 关闭数据库连接
    def destroy(self, destroyWindow: bool = ..., destroySubWindows: bool = ...) -> None:
        # 在关闭数据库之前，必须使用QSqlQuery.finish()或QSqlQuery.clear。
        # 否则，Query对象中会遗漏剩余内存。文档中提到Query对象可用于多个查询。
        # 当您查询10,000条记录时，您会注意到“内存泄漏”。内存使用率急剧上升。
        self.db.close_query()
        self.db.close_db()
