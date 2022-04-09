# music class
# 2022/3/21
# entity
class Music(object):
    def __init__(self, s_id, song_name, artists, album, album_img_url, duration):
        self.s_id = s_id
        self.song_name = song_name
        self.artists = artists
        self.album = album
        self.album_img_url = album_img_url
        self.duration = duration
        self.real_play_url = None

    def set_real_url(self, url):
        self.real_play_url = url

    def __str__(self):
        return f"{self.s_id},{self.song_name},{self.artists},{self.album},{self.duration},{self.album_img_url}"
