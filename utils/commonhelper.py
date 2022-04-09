# 工具类
# 2022/3/22

class CommonHelper:
    # 读取qss
    @staticmethod
    def read_file(file_path):
        with open(file_path, "r", encoding='utf-8') as f:
            return f.read()
