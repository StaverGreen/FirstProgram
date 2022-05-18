import os

from PIL import ImageTk, Image
from tkinter import Button, Tk, Label, DISABLED, NORMAL, Text, WORD, INSERT, END


class Vr(Tk):
    def __init__(self, value=1, bul=False):
        super().__init__()
        self.value = value
        self.bul = bul
        self.lis = []
        self.NOS = 2  # number of stories
        self.np = 6   # upper limit of pics in album
        self.image_number = 1
        self.attributes('-fullscreen', True)
        self.title('Select')
        self.matt = []
        self.start = True

    def list_pic(self):
        path = os.getcwd()
        for y in range(self.NOS + 1):
            name = 'bonus' if y == self.NOS else str(y+1) + 'a'
            os.chdir(os.path.join(path, name))
            vek = [os.path.join(path, name, str(x+1)+'.jpg') for x
                   in range(len([str(x+1) + '.jpg' for x in range(self.np)
                                 if os.path.isfile(str(x+1) + '.jpg')]))]
            self.matt.append(vek)

        os.chdir(os.path.join(path, 'respic'))
        self.lis = self.matt[0]
        self.main()
            
    def bonus(self):
        self.label.grid_forget()
        self.lis = self.matt[self.value] if self.bul else self.matt[self.NOS]
        self.bul = False if self.bul else True
        self.image_number = 1
        self.main()

    def change_story(self, delta):
        self.label.grid_forget()
        self.value += delta
        self.lis = self.matt[self.value]
        self.image_number = 1
        self.main()

    def change_pic(self, move):
        self.label.grid_forget()
        self.image_number += move
        self.main()

    def text_add(self, text_start, text_end=str(), height_con=17, width_con=30,
                 row_con=0, column_con=0, columnspan_var=4, rowspan_var=4):
        text = Text(self, height=height_con, width=width_con, font=("Arial", 30), wrap=WORD)
        text.insert(INSERT, text_start)
        text.insert(END, text_end)
        text.grid(row=row_con, column=column_con, columnspan=columnspan_var, rowspan=rowspan_var)
        
    def activate(self):
        start_text = 'You have chosen part ' + str(self.image_number) + ' of '
        end_text = 'bonus chapter.' if self.bul else 'chapter: ' + str(self.value) + '.'
        self.text_add(start_text + end_text)

    def description(self):
        txt = 'textb.txt' if self.bul else 'text' + str(self.value) + '.txt'
        with open(txt) as description_file:
            lines_file = description_file.readlines()
        self.text_add(lines_file[self.image_number - 1],)

        txt = 'pic: ' + str(self.image_number) + '   '
        start_text = txt if self.bul else txt + 'cha: ' + str(self.value) + '   '
        end_text = 'bonus: Yes' if self.bul else 'bonus: No'
        self.text_add(start_text, text_end=end_text, height_con=1, row_con=7)

    def main(self):
        self.label = MyLabel(self.lis[self.image_number - 1])
        self.label.grid(row=0, column=5, rowspan=8)

        if self.start:
            self.button_forward = MyButton(lambda: self.change_pic(1), ">>", ['d', '<Right>'])
            self.button_forward.grid(row=5, column=2)
            self.button_back = MyButton(lambda: self.change_pic(-1), "<<", ['a', '<Left>'])
            self.button_back.grid(row=5, column=0)
            self.button_next = MyButton(lambda: self.change_story(1), ">>>", ['<Shift-Right>', '<Shift-D>'])
            self.button_next.grid(row=6, column=2)
            self.button_last = MyButton(lambda: self.change_story(-1), "<<<", ['<Shift-Left>', '<Shift-A>'])
            self.button_last.grid(row=6, column=0)
            self.button_bonus = MyButton(lambda: self.bonus(), "Bonus", ['<Shift-space>'])
            self.button_bonus.grid(row=6, column=1)
            self.button_enter = MyButton(lambda: self.activate(), "Start", ['<space>', '<Return>'])
            self.button_enter.grid(row=5, column=1)
            self.start = False

        self.button_forward.set_enabled(self.image_number != len(self.lis), lambda _: self.change_pic(1))
        self.button_back.set_enabled(self.image_number != 1, lambda _: self.change_pic(-1))
        self.button_next.set_enabled(self.value != self.NOS and not self.bul, lambda _: self.change_story(1))
        self.button_last.set_enabled(self.value != 1 and not self.bul, lambda _: self.change_story(-1))
        self.button_bonus.set_enabled(True, lambda _: self.bonus())
        self.button_enter.set_enabled(True, lambda _: self.activate())
        self.bind('<Escape>', lambda _: self.destroy())
        self.description()


class MyButton(Button, Vr):
    def __init__(self, callback, text, shortcuts):
        super().__init__(root, text=text, width=10, height=5,
                         command=callback)
        self._shorcuts = shortcuts
        
    def set_enabled(self, enabled, call):
        if root.start:
            for shortcut in self._shorcuts:
                root.bind(shortcut, call)
                self['state'] = NORMAL
        if self['state'] == DISABLED and not enabled or self['state'] == NORMAL and enabled:
            pass
        if not enabled:
            self['state'] = DISABLED
            for shortcut in self._shorcuts:
                root.unbind(shortcut)
        else:
            self['state'] = NORMAL
            for shortcut in self._shorcuts:
                root.bind(shortcut, call)

    def test(self):
        pass


class MyLabel(Label, Vr):
    def __init__(self, slika):
        self.pic = Image.open(slika)
        self.tab_horizontal = int(0.653*float(root.winfo_screenwidth()))
        self.tab_vertical = int(0.8*float(root.winfo_screenheight()))
        self.wide = int((float(self.pic.size[0]) * float((self.tab_vertical / float(self.pic.size[1])))))
        if float(self.wide) > float(self.tab_horizontal):
            self.length_size = int((float(self.pic.size[1]) * float((self.tab_horizontal / float(self.pic.size[0])))))
            self.res_pic = self.pic.resize((self.tab_horizontal, self.length_size))
        else:
            self.res_pic = self.pic.resize((self.wide, self.tab_vertical))
        self.picture = ImageTk.PhotoImage(self.res_pic)
        super().__init__(image=self.picture)


root = Vr()

root.list_pic()
root.mainloop()
