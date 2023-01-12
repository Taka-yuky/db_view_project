import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
from collections.abc import Callable, Sequence

class FileOpenFrame(ttk.Frame):
    """
    ファイル読み込み用フレーム
    """
    def __init__(self, master:tk.Tk=None, file_entry_width=100):
        super().__init__(master)
        self.__filepath = tk.StringVar()
        self.create_widgets(file_entry_width)
    
    @property
    def filepath(self) -> tk.StringVar:
        return self.__filepath
    

    def create_widgets(self, entry_width):
        label = ttk.Label(self, text="FilePath")
        label.grid(column=0, row=0)
        entry = ttk.Entry(self, textvariable=self.filepath, width=entry_width)
        entry.grid(column=1, row=0)
        button  = ttk.Button(self, text="open", command=self.open_file_dialog)
        button.grid(column=2, row=0)
        self.readbutton = ttk.Button(self, text="read")
        self.readbutton.grid(column=3, row=0)
    
    def open_file_dialog(self):
        """
        ファイルダイアログを開く
        """
        file = filedialog.askopenfilename(filetypes=[("db", "*.db")])
        self.__filepath.set(file)
    
    def bind_readbutton(self, callback:Callable):
        self.readbutton.config(command=callback)

class TreeViewFrame(ttk.Frame):
    """
    取得したデータを表示するTreeView
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.tree = None
        self.selected_iid = None
        self.columns_name = []
        self.create_widgets()
        #self.pack() (これは呼び出し元のViewで行ったほうがよさそう)
        self.insert_sampledata()
    
    @property
    def columns_name(self) -> str:
        return self.__columns_name
    
    @columns_name.setter
    def columns_name(self, value):
        self.__columns_name = value
    
    def create_widgets(self):
        self.tree = ttk.Treeview(self)
        self.tree["show"] = "headings"
        self.tree.pack()
    
    def set_columns(self, columns:list|tuple):
        """
        TreeViewの列名を設定
        """
        self.columns_name = columns
        self.tree["columns"] = self.columns_name
        for col in columns:
            self.tree.heading(col, text=col)
    
    def insert_record(self, index="", row_data:list|tuple=[]):
        """
        新規レコードの挿入
        """
        self.tree.insert("", index="end", text=index, values=row_data)
    
    def insert_records(self, rows_data:list|tuple):
        """
        複数の新規レコードの挿入
        """
        for i, row_data in enumerate(rows_data):
            self.insert_record(index=i, row_data=row_data)
    
    def insert_sampledata(self):
        """
        起動時のサンプルデータ
        """
        column_data = ("Name", "Value")
        rows_data = [("None", "None")]
        self.delete_records()
        self.set_columns(column_data)
        self.insert_records(rows_data)
    
    def delete_records(self):
        """
        レコードの全件削除
        """
        children = self.tree.get_children("")
        for child in children:
            self.tree.delete(child)
        print("全件削除しました")

    def bind_selected_selection(self, callback:Callable):
        """
        レコードが選択されたときに呼ばれる関数をバインドする。
        """
        self.tree.bind("<<TreeviewSelect>>", callback)
    
    def get_selected_record(self) -> tuple | str:
        """
        現在選択されているレコードの取得を行う。
        """
        self.selected_iid = self.tree.focus()
        return self.tree.item(self.selected_iid, "values")
    
    def get_all_records(self) -> list:
        """
        全レコードの取得を行う。
        """
        records = []
        children = self.tree.get_children("")
        for child in children:
            record = self.tree.item(child, "values")
            records.append(record)
        return records
    
    def get_datamap(self) -> None|dict:
        """
        現在選択されているレコードの列名と値のマップを取得する。
        """
        record = self.get_selected_record()
        if len(self.columns_name) != len(record):
            return {"none": "none"}
        else:
            data_map = {}
            for i, column in enumerate(self.columns_name):
                data_map[column] = record[i]
            return data_map
    
    def update_record(self, iid, new_values):
        """
        指定されたiidのレコードの値を更新する。
        """
        self.tree.item(iid, values=new_values)

    def update(self,value_dict):
        """
        マップからリストに変更後
        値の更新
        """
        data =[]
        for column in self.columns:
            data.append(value_dict[column])
        self.update_record(data)

    def insert(self,value_dict):
        """
        マップからリストに変更後
        新規レコードの挿入
        """
        data =[]
        for column in self.columns:
            data.append(value_dict[column])
        children = self.tree.get_children("")
        index = len(children)
        self.insert_record(index = str(index), row_data=data)
    
class LabelEntryWidget(ttk.Frame):
    """
    labelとEntryを組み合わせたWdiget
    """
    def __init__(self, master, text="property"):
        super().__init__(master)
        self.value = tk.StringVar()
        self.create_widgets(text)

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        self.__value = value

    def create_widgets(self, text="property"):
        self.label = ttk.Label(self, text=text)
        self.label.pack(side="left")
        self.entry = ttk.Entry(self, textvariable=self.value)
        self.entry.pack()
    
    def set_label_option(self, key_dict:dict):
        """
        Labelのオプションを指定する
        """
        for k in key_dict.keys():
            self.label[k] = key_dict[k]

    def set_entry_option(self, key_dict:dict):
        """
        Entryのオプションを指定する
        """
        for k in key_dict.keys():
            self.entry[k] = key_dict[k]

class PropertyView(ttk.Frame):
    """
    選択されたレコードの内容を修正・新規レコードの挿入を操作するためのフレーム
    """
    def __init__(self, master):
        super().__init__(master)
        self.param_dict = {}
        #self.pack()
    
    def create_widgets(self, columns):
        self.clear_widgets()
        self.param_dict = {}
        for column in columns:
            option = {"width": 10}
            param = LabelEntryWidget(self, text=column)
            param.set_label_option(option)
            param.pack()
            self.param_dict[column] = param.value
        self.create_buttons_frame()
    
    def create_buttons_frame(self):
        """
        フレームに配置するボタンを生成する関数
        """
        button_frame = ttk.Frame(self)
        button_frame.pack(anchor="e")
        self.update_button = ttk.Button(button_frame, text="commit")
        self.insert_button = ttk.Button(button_frame, text="insert")
        self.save_button = ttk.Button(button_frame, text="save")
        self.update_button.pack(side="left")
        self.insert_button.pack(side="left")
        self.save_button.pack(side="left")
    
    def clear_widgets(self):
        """
        フレーム内に存在するウィジェットをすべて削除する。
        """
        children = self.winfo_children()
        for child in children:
            child.destroy()
    
    def bind_update_button(self, callback:Callable):
        self.update_button.config(command=callback)

    def bind_insert_button(self, callback:Callable):
        self.insert_button.config(command=callback)

    def bind_save_button(self, callback:Callable):
        self.save_button.config(command=callback)

    def set_parameter(self, param):
        print(self.param_dict)
        for key in self.param_dict.keys():
            self.param_dict[key] = param[key]
    
    def get_parameter(self):
        param_dict = {}
        for key, value in self.param_dict.items():
            param_dict[key] = value
        return param_dict

class DbView(tk.Tk):
    def __init__(self,master=None,borderwidth=10):
        super().__init__(master)
        self.title("DB Viewer")
        self.geometry("1200x700")
        self.tree = None
        self.create_widgets()
        self.set_action()
    
    def create_widgets(self):
        self.create_upper_frame()
        self.create_lower_frame()
    
    def create_upper_frame(self):
        upper_frame = ttk.Frame(self)
        upper_frame.pack()
        self.file_path_frame = FileOpenFrame(upper_frame)
        self.file_path_frame.pack()
    
    def create_lower_frame(self):
        lower_frame = ttk.Frame(self)
        lower_frame.pack()
        left_frame = ttk.LabelFrame(lower_frame, text="DBData")
        left_frame.pack(side="left")
        self.tree = TreeViewFrame(left_frame)
        self.tree.pack()
        self.tree.insert_sampledata()
        right_frame = ttk.LabelFrame(lower_frame, text="RecordData")
        right_frame.pack(side="right", anchor="n")

        self.property = PropertyView(right_frame)
        self.property.create_widgets(self.tree.columns_name)
        self.property.pack()
    
    def set_action(self):
        def _update_command():
            param = self.property.get_parameter()
            self.tree.update(param)
        
        def _insert_command():
            param = self.property.get_parameter()
            self.tree.insert(param)
        
        def _callback(event):
            self.property.set_parameter(self.tree.get_datamap())
            self.property.bind_update_button(_update_command)
            self.property.bind_insert_button(_insert_command)
        
        self.tree.bind_selected_selection(_callback)
    
    def get_filepath(self):
        return self.file_path_frame.filepath.get()
    
    def set_newcolumn_records(self, columns:list|tuple, rows:list|tuple):
        print(columns, rows)
        self.tree.delete_records()
        self.tree.set_columns(columns)
        self.tree.insert_records(rows)
        self.property.create_widgets(self.tree.columns_name)
    
    def get_columns(self):
        return self.tree.columns_name
    
    def get_all_records(self) -> list:
        return self.tree.get_all_records()
    
    def bind_readbutton(self, callback:Callable):
        self.file_path_frame.bind_readbutton(callback)

if __name__ == "__main__":
    app = DbView()
    app.mainloop()