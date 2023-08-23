from tkinter import ttk, filedialog
from tkinter.messagebox import showinfo
from tkinter import *
from PIL import Image, ImageTk
import sqlite3
import PIL.Image
from io import BytesIO


class GUI:
    def __init__(self, database):
        self.db = database

        self.root = Tk()
        w, h = 800, 600
        l, t = (self.root.winfo_screenwidth() - w) // 2, (self.root.winfo_screenheight() - h) // 2
        self.root.title("Знаменитые конструктора России")
        self.root.geometry(f"{w}x{h}+{l}+{t}")
        self.root.resizable(0, 0)

        self.listbox = Listbox(font=("Arial", 10))
        self.canvas = Canvas()
        self.text = Text(wrap="word", font=("Arial", 11), state=DISABLED)
        self.label = Label(text=" F1 - Справка | Ctrl+N - Добавить | Ctrl+D - Удалить | "
                                "Ctrl+E - Изменить | F10 - меню программы",
                           bg='#003296', fg='#ffffff', font=("Arial", 13), anchor='w')
        self.id = 0
        self.file_path = ""
        self.image_handler = ImageHandler(None)
        self.create_widgets()

        self.root.mainloop()

    def exit_app(self):
        self.root.protocol("WM_DELETE_WINDOW", self.root.quit())
        self.root.quit()

    def select_image(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.image_handler.image_data = self.file_path
            image = self.image_handler.get_image((100, 100))
            self.image_path_label.configure(image=image)
            self.image_path_label.image = image

    def create_widgets(self):
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Фонд", menu=file_menu)
        file_menu.add_command(label="Добавить", command=self.add_konstructor_window, accelerator="Ctrl+N")
        file_menu.add_command(label="Удалить", command=lambda: self.delete_konstructor(self.id), accelerator="Ctrl+D")
        file_menu.add_command(label="Изменить", accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.exit_app, accelerator="Ctrl+X")

        self.root.bind("<F10>", lambda event: menu_bar)
        self.root.bind("<Control-Key-n>", lambda event: self.add_konstructor_window())
        self.root.bind("<Control-Key-d>", lambda event: self.delete_konstructor(self.id))
        self.root.bind("<Control-Key-x>", lambda event: self.exit_app())
        self.root.bind("<F1>", lambda event: self.show_help_window())

        info_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Справка", menu=info_menu)
        info_menu.add_command(label="Содержание", command=self.show_help_window)
        info_menu.add_separator()
        info_menu.add_command(label="О программе", command=self.show_info_window)

        def get_description_and_picture(m):
            d_konstructors = self.get_dict_konstructors()
            self.id = list(d_konstructors.keys())[list(d_konstructors.values()).index
                                (self.listbox.get(self.listbox.curselection()))]

            description = db.get_konstructor_by_id(self.id)[2]
            self.text.configure(state=NORMAL)
            self.text.delete("1.0", END)
            self.text.insert(END, description)
            self.text.configure(state=DISABLED)

            blob_img = db.get_konstructor_by_id(self.id)[3]
            img = PhotoImage(data=blob_img, format='png').subsample(2, 2)
            self.canvas.create_image(0, 0, image=img, anchor=NW)
            self.canvas.image = img

        self.listbox.place(x=0, y=0, width=150, height=570)
        self.canvas.place(x=150, y=85, width=400, height=400)
        self.text.place(x=550, y=0, width=250, height=570)
        self.label.place(x=0, y=570, width=800, height=30)

        self.fill_listbox()
        self.listbox.bind("<<ListboxSelect>>", get_description_and_picture)

    def get_dict_konstructors(self):
        l_konstructors = list(self.db.get_all_konstructors())
        d_konstructors = dict()
        for konstructor in l_konstructors:
            d_konstructors[konstructor[0]] = konstructor[1]
        return d_konstructors

    def fill_listbox(self):
        d_konstructors = self.get_dict_konstructors()

        print(d_konstructors)

        names = list(d_konstructors.values())
        for i in range(len(d_konstructors)):
            self.listbox.insert(i, names[i])

    def refresh_listbox(self):
        self.listbox.delete(0, 'end')
        self.fill_listbox()

    def add_konstructor_window(self):
        self.add_window = Toplevel(self.root)
        self.add_window.title("Добавить конструктора")
        self.add_window.resizable(0, 0)

        input_frame = ttk.Frame(self.add_window, padding=10)
        input_frame.grid(row=0, column=0)

        def close_and_refresh():
            self.add_window.destroy()
            self.refresh_listbox()

        name_label = ttk.Label(input_frame, text="Имя:")
        name_label.grid(row=0, column=0, sticky=W)

        self.name_entry = ttk.Entry(input_frame, width=60)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        desc_label = ttk.Label(input_frame, text="Описание:")
        desc_label.grid(row=1, column=0, sticky=W)

        self.desc_var = StringVar()
        self.desc_var.set("")
        self.desc_entry = ttk.Entry(input_frame, width=60, textvariable=self.desc_var)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5)

        image_label = ttk.Label(input_frame, text="Изображение:")
        image_label.grid(row=2, column=0, sticky=W)

        self.image_path = StringVar()
        self.image_path.set("")
        canvas = Canvas(input_frame, width=10, height=10)
        canvas.grid(row=2, column=2, padx=5, pady=5)
        self.image_path_label = ttk.Label(input_frame, textvariable=self.image_path)
        self.image_path_label.grid(row=2, column=1, padx=5, pady=5)

        image_button = ttk.Button(input_frame, text="Добавить изображение",
                                  command=self.select_image)
        image_button.grid(row=3, column=1, padx=5, pady=5)

        buttons_frame = ttk.Frame(self.add_window, padding=10)
        buttons_frame.grid(row=1, column=0, sticky=E)

        commit_button=ttk.Button(input_frame, text="Применить",
                    command=lambda: self.db.add_konstructor(self.name_entry.get(),
                                                       self.desc_entry.get(),
                                                       self.db.image_to_blob(self.file_path)))
        commit_button.grid(row=4, column=0, padx=5, pady=5)
        cancel_button = ttk.Button(input_frame, text="Закрыть", command=close_and_refresh)
        cancel_button.grid(row=4, column=2, padx=5, pady=5)

        self.add_window.grab_set()
        self.root.wait_window(self.add_window)

    def delete_konstructor(self, id):
        db.delete_konstructor(id)
        self.refresh_listbox()

    def show_help_window(self):
        global f_view_help
        def close_help_window():
            global f_view_help
            f_view_help = False
            help_window.destroy()
        if not (f_view_help):
            help_window = Toplevel(self.root)
            w, h = 430, 200
            l, t = (help_window.winfo_screenwidth() - w) // 2,\
                (help_window.winfo_screenheight() - h) // 2
            help_window.geometry(f"{w}x{h}+{l}+{t}")
            help_window.title("Справка")
            help_window.resizable(0, 0)
            help_window.protocol("WM_DELETE_WINDOW", close_help_window)
            help_label = ttk.Label(help_window,
                                    text="База данных 'Знаменитые конструктора России'\n"
                                         "Позволяет: добавлять / изменять / удалять информацию\n"
                                         "Клавиши программы:\n"
                                         "F1 - вызов справки по программе;\n"
                                         "Ctrl+N - добавить запись в Базу Данных;\n"
                                         "Ctrl+D - удалить запись из Базы Данных;\n"
                                         "Ctrl+E - изменить запись в Базе Данных;\n"
                                         "Ctrl+X - выход из программы\n"
                                         "F10 - Меню программы", font=("Calibri", 12))
            help_label.pack(pady=5, padx=5, expand=True)
            help_button = ttk.Button(help_window, text="Закрыть", command=close_help_window)
            help_button.place(x=340, y=165)
            f_view_help = True

    def show_info_window(self):
        showinfo('О программе', 'База данных "Знаменитые конструктора России"\n(с) Molyakov D.N., Russia, 2023\nПочта: Molyakov.dima@mail.ru')

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('AmDB.db')
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS konstructors (id INTEGER PRIMARY KEY, name TEXT, description TEXT, image BLOB)")
        self.conn.commit()

    def add_konstructor(self, name, description, image_blob):
        print(image_blob)
        self.cur.execute("INSERT INTO konstructors (name, description, image) VALUES (?, ?, ?)",
                         (name, description, image_blob))
        self.conn.commit()
        print(f'{name} был успешно добавлен в БД')

    def delete_konstructor(self, id):
        self.cur.execute("DELETE FROM konstructors WHERE id=?", (id,))
        self.conn.commit()
        print('Удаление выполнено')

    def get_all_konstructors(self):
        self.cur.execute("SELECT * FROM konstructors")
        return self.cur.fetchall()

    def get_konstructor_by_id(self, id):
        self.cur.execute("SELECT * FROM konstructors WHERE id=?", (id,))
        return self.cur.fetchone()

    def close_connection(self):
        self.conn.close()

    def image_to_blob(self, image_path):
        try:
            with open(image_path, 'rb') as f:
                img_bytes = f.read()
            return sqlite3.Binary(img_bytes)
        except FileNotFoundError as e:
            print("Файл не найден")

    def blob_to_image(self, blob):
        try:
            type(blob)
            file_like = BytesIO(blob)
            image = PIL.Image.open(file_like)
            return image
        except Exception as e:
            print(f"Error blob_to_image: {e}")

class ImageHandler:
    def __init__(self, image_data):
        self.image_data = image_data

    def get_image(self, size):
        img = Image.open(self.image_data)
        img = img.resize(size, Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(img)
        return photo

if __name__ == "__main__":
    f_view_info = False
    f_view_help = False
    db = Database()
    app = GUI(db)
