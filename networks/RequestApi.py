# 开启多线程请求后台数据
# 2022/3/22
import requests
from PySide6.QtCore import QThread, Signal, QObject, QRunnable, QThreadPool
from Entity.Music import Music


class RequestAPI(QThread):
    test = Signal(str)
    # 更新table_view
    update_table_view = Signal(dict)
    # 获取歌曲播放url
    get_song_url = Signal(str)
    # 获取专辑图片
    get_pic_content = Signal(bytes)
    # 请求出错
    req_error = Signal()
    # 关键词搜索
    SEARCH_CONTENT = 0
    # 获取音乐播放url
    GET_URL = 1
    # 获取专辑图
    GET_IMAGE_CONTENT = 2

    # req_type:区分是关键词搜索还是获取音乐播放url请求
    def __init__(self, req_url, req_type=SEARCH_CONTENT):
        super().__init__()
        self.url = req_url
        self.req_type = req_type
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        }

    def run(self) -> None:
        if self.req_type == self.SEARCH_CONTENT:
            self.search_content()
        elif self.req_type == self.GET_URL:
            self.get_music_url()
        elif self.req_type == self.GET_IMAGE_CONTENT:
            self.get_real_img_url()

    def search_content(self):
        try:
            response = requests.get(self.url, headers=self.headers)
            if response.status_code == 200:
                results = response.json()["result"]
                songCount = results["songCount"]
                songs = results["songs"]
                music_list = []
                for song in songs:
                    s_id = song["id"]
                    song_name = song["name"]
                    artists = ""
                    for ar in song["ar"]:
                        artists += ar["name"] + "、"
                    artists = artists[:-1]
                    album = song["al"]["name"]
                    al_img = song["al"]["picUrl"]
                    duration = song["dt"]
                    music = Music(s_id, song_name, artists, album, al_img, duration)
                    music_list.append(music)
                dic = {
                    "music_list": music_list,
                    "songCount": songCount
                }
                self.update_table_view.emit(dic)
            else:
                self.req_error.emit()
        except Exception as e:
            print(e)
            self.req_error.emit()

    def get_music_url(self):
        response = requests.get(self.url, headers=self.headers)
        if response.status_code == 200:
            result = response.json()
            # 获取歌曲的播放url
            url = result["data"][0]["url"]
            self.get_song_url.emit(url)
        else:
            self.req_error.emit()

    def get_real_img_url(self):
        response = requests.get(self.url, headers=self.headers)
        if response.status_code == 200:
            self.get_pic_content.emit(response.content)
        else:
            self.req_error.emit()
#################pyside6 线程池版本###########################
# class RequestAPI(QObject):
#     test = Signal(str)
#     # 更新table_view
#     update_table_view = Signal(dict)
#     # 获取歌曲播放url
#     get_song_url = Signal(str)
#     # 获取专辑图片
#     get_pic_content = Signal(bytes)
#     # 请求出错
#     req_error = Signal()
#
#     # req_type:区分是关键词搜索还是获取音乐播放url请求
#     def __init__(self):
#         super().__init__()
#         # 创建线程池最大线程数量为20个
#         self.executor = ThreadPoolExecutor(max_workers=10)
#         self.lock = Lock()
#         self.headers = {
#             "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
#         }
#
#     def start(self, fun, url) -> None:
#         self.executor.submit(fun, url)
#
#     def search_content(self, url):
#         response = requests.get(url, headers=self.headers)
#         if response.status_code == 200:
#             results = response.json()["result"]
#             songCount = results["songCount"]
#             songs = results["songs"]
#             music_list = []
#             for song in songs:
#                 s_id = song["id"]
#                 song_name = song["name"]
#                 artists = ""
#                 for ar in song["ar"]:
#                     artists += ar["name"] + "、"
#                 artists = artists[:-1]
#                 album = song["al"]["name"]
#                 al_img = song["al"]["picUrl"]
#                 duration = song["dt"]
#                 music = Music(s_id, song_name, artists, album, al_img, duration)
#                 music_list.append(music)
#             dic = {
#                 "music_list": music_list,
#                 "songCount": songCount
#             }
#             self.update_table_view.emit(dic)
#         else:
#             self.req_error.emit()
#
#     def get_music_url(self, url):
#         response = requests.get(url, headers=self.headers)
#         if response.status_code == 200:
#             result = response.json()
#             # 获取歌曲的播放url
#             url = result["data"][0]["url"]
#             self.get_song_url.emit(url)
#         else:
#             self.req_error.emit()
#
#     def get_real_img_url(self, url):
#         response = requests.get(url, headers=self.headers)
#         if response.status_code == 200:
#             self.get_pic_content.emit(response.content)
#         else:
#             self.req_error.emit()
#
#     def destroyed_thread_pool_executor(self):
#         self.executor.shutdown()
