# 数据库操作类
# 2022/3/27
from PySide6.QtCore import Signal, QObject, QThread, QMutex
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from Entity.Music import Music


class DB_Utils(QObject):
    select_complete = Signal(list)
    exec_sql_complete = Signal(bool)

    # 数据库文件路径
    def __init__(self, save_path, table_name):
        super().__init__()
        self.lock = QMutex()
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.query = self.create_connection(save_path)
        self.create_table(table_name)
        self.db_thread = None

    # 创建链接
    def create_connection(self, save_path):
        self.con.setDatabaseName(save_path)
        if not self.con.open():
            print("open database fail")
            return None
        query = QSqlQuery()
        return query

    # 创建表
    def create_table(self, table_name):
        if self.query is not None:
            self.query.exec(f"create table if not exists {table_name}("
                            "s_id varchar(60)primary key,"
                            "song_name varchar(100),"
                            "song_artists varchar(60),"
                            "song_album varchar(60),"
                            "album_img_url varchar(255),"
                            "song_duration varchar(30),"
                            "insert_time TimeStamp DEFAULT CURRENT_TIMESTAMP)")

    # 添加数据或者删除数据
    def exec_sql(self, sql):
        self.db_thread = DBThread(self.exec_sql_task, sql)
        # 线程任务完成后稍后删除该对象
        self.db_thread.finished.connect(self.db_thread.deleteLater)
        self.db_thread.start()

    # 查询数据
    def exec_select(self, sql):
        self.db_thread = DBThread(self.select_task, sql)
        # 线程任务完成后稍后删除该对象
        self.db_thread.finished.connect(self.db_thread.deleteLater)
        self.db_thread.start()

    # 查询任务
    def select_task(self, sql):
        # 加锁
        self.lock.lock()
        try:
            # 需要保证线程安全的代码
            if self.query is not None:
                self.query.exec(sql)
                music_list = []
                while self.query.next():
                    s_id = self.query.value(0)
                    song_name = self.query.value(1)
                    song_artists = self.query.value(2)
                    song_album = self.query.value(3)
                    album_img_url = self.query.value(4)
                    song_duration = self.query.value(5)
                    music = Music(s_id, song_name, song_artists, song_album, album_img_url, song_duration)
                    music_list.append(music)
                self.select_complete.emit(music_list)
            else:
                self.select_complete.emit([])
        except Exception as e:
            print(e)
        # 使用finally 块来保证释放锁
        finally:
            # 修改完成，释放锁
            self.lock.unlock()
            self.db_thread.quit()

    # 更新任务
    def exec_sql_task(self, sql):
        # 加锁
        self.lock.lock()
        try:
            # 需要保证线程安全的代码
            if self.query is not None:
                self.exec_sql_complete.emit(self.query.exec(sql))
        except Exception as e:
            print(e)
        finally:
            # 修改完成，释放锁
            self.lock.unlock()
            self.db_thread.quit()

    # 关闭数据库
    def close_db(self):
        self.con.close()

    def close_query(self):
        self.query.clear()
        self.query.finish()


class DBThread(QThread):
    def __init__(self, fun, sql):
        super(DBThread, self).__init__()
        self.fun = fun
        self.sql = sql

    def run(self) -> None:
        self.fun(self.sql)
