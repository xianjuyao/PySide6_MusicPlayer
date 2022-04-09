# 格式化歌曲的时间
# 2022/3/22
class TimeFormat(object):
    # 将int类型的时间转换成str
    @staticmethod
    def format_int_to_str_time(duration: int):
        s_format_time = ""
        # 四舍五入取整拿到总的秒数
        dr = int(duration / 1000)
        # 拿到分钟数
        min = dr // 60
        # 秒
        sec = dr % 60
        # 补0
        if min < 10:
            s_format_time += "0"
        s_format_time += str(min)
        s_format_time += ":"
        # 补0
        if sec < 10:
            s_format_time += "0"
        s_format_time += str(sec)
        return s_format_time

    @staticmethod
    def format_str_to_int_time(duration: str):
        duration_list = duration.split(":")
        # 前半部分如 03 时长为 3*60 直接加上后半部分
        time = int(duration_list[0]) * 60
        time += int(duration_list[1])
        time *= 1000
        return time
