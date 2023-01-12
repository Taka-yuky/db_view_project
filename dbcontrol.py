import sqlite3
import tkinter.messagebox as mb
import tkinter as tk
import tkinter.ttk as ttk
from view import DbView
import os

class DbRepository():
    """
    PythonでSqlite3に接続しデータを操作するためのクラス
    """

    def __init__(self):
        self.header = []
        self.data = []
    
    def read_table(self, data_path, table_name):
        ret = True
        header = []
        data = []
        try :
            with sqlite3.connect(data_path) as conn:
                cursor = conn.cursor()
                sql = f"""SELECT * FROM {table_name}"""
                result = cursor.execute(sql)
                #print(list(result))
                for name in cursor.description:
                    header.append(name[0])
                for record in result:
                    data.append(record)
        except IOError as e:
            ret = False
        self.header = header
        self.data = data
        return ret
    
class DbControl():
    def __init__(self):
        self.view = DbView()
        self.repo = DbRepository()
        self.view.bind_readbutton(self.update_view)
        self.view.mainloop()
    
    def update_view(self):
        columns, data = self.read_db()
        self.view.set_newcolumn_records(columns, data)
    
    def read_db(self):
        ret = False
        file_path = self.view.get_filepath()
        if os.path.exists(file_path):
            ret = self.repo.read_table(file_path, "t_task_progress")
        
        if ret:
            mb.showinfo("readcsv", "Succeed")
        else:
            mb.showerror("readcsv", "failed")
        
        #print(self.repo.header, self.repo.data)
        return self.repo.header, self.repo.data

if __name__ == "__main__":
    control = DbControl()