import os

from PIL import ImageTk, Image
from tkinter import Button, Tk, Label, DISABLED, NORMAL, Text, WORD, INSERT, END, Canvas, Scale, HORIZONTAL


class LevelSelectScreen(Tk):
    def __init__(self, stories=2, limit=6, step=0.75):
        super().__init__()
        self.start = True
        self.attributes('-fullscreen', True)
        self.title('Select')
        self.bonus_active = False
        self.number_of_stories = stories  
        self.upper_limit = limit   # upper limit of pics in album
        self.max_zoom_window = 4  # 5 is entire screen
        self.zoomcycle_max = 10
        self.picture = None  # picture on screen
        self.pic = None  # original image
        self.res_pic = None  # original picture resized to fit the screen
        self.mag_image = None
        self.zoom_image = None
        self.zoom_window_image = None  # image on the magnifier
        self.zoom_image_part = None
        self.magnifier_active = True
        self.zoom_active = False
        self.start_zoom = False  # turns on when first zoom is activated
        self.zoom_step = step
        self.zoom_width = int()
        self.zoom_height = int()
        self.zoomcycle = 0
        self.album_value = 0
        self.possition_x = 0
        self.possition_y = 0
        self.x_last = 0
        self.y_last = 0
        self.image_number = 1
        self.magnifier_size = 1
        self.lis = []
        self.matt = []
        self.tab_horizontal = int(0.653*float(self.winfo_screenwidth()))
        self.tab_vertical = int(0.8*float(self.winfo_screenheight()))
        self.canvas = Canvas(self, width=self.tab_horizontal, height=self.tab_vertical)
        self.canvas.bind("<MouseWheel>", self.change_zoom_level)
        self.canvas.bind("<Motion>", self.crop)
        self.bind("<Shift-MouseWheel>", self.zoom_window)
        self.bind("<Shift_L>", lambda _: self.disable_zoom())
        self.bind("z", lambda _: self.change_active_mode())
        self.bind("<Button-1>", lambda _: self.mouse_clicked())
        self.bind("<ButtonRelease-1>", lambda _: self.rebind())
        self.bind("r", lambda _: self.refresh())
        with open("text\disc.txt") as shortcut_file:
            self.shortcut_file = shortcut_file.read()
        path = os.getcwd()
        
        for y in range(self.number_of_stories + 1):
            name = 'bonus' if y == self.number_of_stories else str(y+1) + 'a'
            list_of_pic = [os.path.join(path, name, str(x+1)+'.jpg')
                          for x in range(len([str(x+1) + '.jpg' for x in range(self.upper_limit)
                                              if os.path.isfile(os.path.join(path, name,
                                                                             str(x+1) + '.jpg'))]))]
            self.matt.append(list_of_pic)
        os.chdir(os.path.join(path, 'text'))
        self.lis = self.matt[0]

        self.button_forward = MyButton(lambda: self.change_pic(1), ">>", ['d', '<Right>'],
                                       lambda _: self.change_pic(1), self)
        self.button_forward.grid(row=5, column=5)
        self.button_back = MyButton(lambda: self.change_pic(-1), "<<", ['a', '<Left>'],
                                    lambda _: self.change_pic(-1), self)
        self.button_back.grid(row=5, column=0)
        self.button_next = MyButton(lambda: self.change_story(1), ">>>", ['<Shift-Right>', '<Shift-D>'],
                                    lambda _: self.change_story(1), self)
        self.button_next.grid(row=7, column=5)
        self.button_last = MyButton(lambda: self.change_story(-1), "<<<", ['<Shift-Left>', '<Shift-A>'],
                                    lambda _: self.change_story(-1), self)
        self.button_last.grid(row=7, column=0)
        self.button_bonus = MyButton(lambda: self.change_bonus_state(), "Bonus", ['<Shift-space>'],
                                     lambda _: self.change_bonus_state(), self)
        self.button_bonus.grid(row=7, column=2)
        self.button_enter = MyButton(lambda: self.activate_level(), "Start", ['<space>', '<Return>'],
                                     lambda _: self.activate_level(), self)
        self.button_enter.grid(row=5, column=2)
        self.button_activate_magnifier = Button(self, command=lambda: self.activate_mode('magnifier'),
                                                width=10, height=5, text='On \n (magnifier)')
        self.button_activate_magnifier.grid(row=5, column=1)
        self.button_activate_zoom = Button(self, command=lambda: self.activate_mode('zoom'),
                                           width=10, height=5, text='Off \n (zoom)')
        self.button_activate_zoom.grid(row=5, column=3)    
        self.magnifier_size_scale = Scale(self, from_=1, to=self.max_zoom_window, orient=HORIZONTAL,
                                          command=lambda _: self.magnifier_slider())  
        self.magnifier_size_scale.grid(row=7, column=1)
        self.zoom_level_scale = Scale(self, from_=0, to=self.zoomcycle_max, orient=HORIZONTAL,
                                      command=lambda _: self.zoom_slider())
        self.zoom_level_scale.grid(row=7, column=3)
        self.slider_label = Label(self, text='Magnifier size', font=("Arial", 18))
        self.slider_label.grid(row=6, column=1)
        self.zoom_slider_label = Label(self, text='Zoom level', font=("Arial", 18))
        self.zoom_slider_label.grid(row=6, column=3)

        self.refresh()

    def refresh(self):
        self.canvas.grid(row=0, column=8, rowspan=8)
        self.pic = Image.open(self.lis[self.image_number - 1])
        width = int((float(self.pic.size[0]) * float((self.tab_vertical / float(self.pic.size[1])))))
        if float(width) > float(self.tab_horizontal):
            length_size = int((float(self.pic.size[1]) * float((self.tab_horizontal / float(self.pic.size[0])))))
            self.res_pic = self.pic.resize((self.tab_horizontal, length_size))
        else:
            self.res_pic = self.pic.resize((width, self.tab_vertical))
        self.picture = ImageTk.PhotoImage(self.res_pic)
        self.canvas.create_image(0, 0, image=self.picture, anchor="nw")

        self.button_forward.set_enabled(self.image_number != len(self.lis))
        self.button_back.set_enabled(self.image_number != 1)
        self.button_next.set_enabled(self.album_value+1 != self.number_of_stories and not self.bonus_active)
        self.button_last.set_enabled(self.album_value+1 != 1 and not self.bonus_active)
        self.button_bonus.set_enabled(True)
        self.button_enter.set_enabled(True)
        self.bind('<Escape>', lambda _: self.destroy())
        self.description()
        self.zoomcycle = 0
        self.zoom_level_scale.set(0)

    def zoom_window(self, event):
        if event.delta > 0 and self.magnifier_size != self.max_zoom_window:
            self.magnifier_size += 1
        elif event.delta < 0 and self.magnifier_size != 1:
            self.magnifier_size -= 1
        self.magnifier_size_scale.set(self.magnifier_size)
        self.crop(event)      
    
    def change_zoom_level(self, event):
        if event.delta > 0 and self.zoomcycle != self.zoomcycle_max:
            self.zoomcycle += 1
        elif event.delta < 0 and self.zoomcycle != 0:
            self.zoomcycle -= 1
        self.zoom_level_scale.set(self.zoomcycle)
        if not self.zoom_active:    
            self.crop(event)

    def crop(self, event):
        horizontal_ratio = float(self.pic.size[0])/float(self.res_pic.size[0])
        vertical_ratio = float(self.pic.size[1])/float(self.res_pic.size[1])
        if self.mag_image:
            self.canvas.delete(self.mag_image)
        if self.zoomcycle != 0:
            x, y = horizontal_ratio*event.x, vertical_ratio*event.y
            scale = self.magnifier_size*0.05*self.zoom_step**self.zoomcycle  # scale of zoom function
            x1, y1 = float(self.pic.size[0])*scale, float(self.pic.size[1])*scale
            tmp = self.pic.crop((x-x1, y-y1, x+x1, y+y1))
            self.zoom_width = int(0.2*self.magnifier_size*float(self.res_pic.size[0]))
            self.zoom_height = int(0.2*self.magnifier_size*float(self.res_pic.size[1]))
            size = self.zoom_width, self.zoom_height
            self.zoom_window_image = ImageTk.PhotoImage(tmp.resize(size))
            self.mag_image = self.canvas.create_image(event.x, event.y, image=self.zoom_window_image)

    def motion(self, event):
        x, y = event.x, event.y
        self.possition_x = x
        self.possition_y = y
        
    def zooming(self, event):
        horizontal_ratio = float(self.pic.size[0])/float(self.res_pic.size[0])
        vertical_ratio = float(self.pic.size[1])/float(self.res_pic.size[1])
        x_half = 1/2*float(self.res_pic.size[0])
        y_half = 1/2*float(self.res_pic.size[1])
        if event.delta < 0 and self.zoomcycle != 0 or event.delta > 0 and self.zoomcycle != self.zoomcycle_max:
            if self.zoomcycle == 0:
                self.start_zoom = True
            scale_before = float(self.zoom_step**self.zoomcycle)
            self.change_zoom_level(event)
            x, y = self.possition_x, self.possition_y
            scale = float(self.zoom_step**self.zoomcycle)
            self.zoom_width = int(float(self.res_pic.size[0]))
            self.zoom_height = int(float(self.res_pic.size[1]))
            size = self.zoom_width, self.zoom_height
            x1, y1 = float(self.pic.size[0])*scale/2, float(self.pic.size[1])*scale/2
            if self.start_zoom:
                x = horizontal_ratio*x - (x-x_half)*self.zoom_step*horizontal_ratio
                y = vertical_ratio * y - (y - y_half) * self.zoom_step * vertical_ratio
                tmp = self.pic.crop((x-x1, y-y1, x+x1, y+y1))
            else:
                dx = (self.possition_x-x_half)*scale_before*horizontal_ratio
                dy = (self.possition_y-y_half)*scale_before*vertical_ratio
                dx2 = (self.possition_x-x_half)*scale*horizontal_ratio
                dy2 = (self.possition_y-y_half)*scale*vertical_ratio
                x, y = self.x_last + dx - dx2, self.y_last + dy - dy2
                tmp = self.pic.crop((x-x1, y-y1, x+x1, y+y1))
            self.zoom_image_part = ImageTk.PhotoImage(tmp.resize(size))
            self.zoom_image = self.canvas.create_image(0, 0, image=self.zoom_image_part, anchor="nw")    
            self.x_last, self.y_last = x, y
            self.start_zoom = False
        
    def change_active_mode(self):
        if self.zoom_active:
            self.activate_mode('magnifier')
        elif self.magnifier_active:
            self.activate_mode('zoom')
        
    def activate_mode(self, mode):
        if self.zoom_active:
            self.zoom_active = False
            self.canvas.unbind("<MouseWheel>")
            self.canvas.unbind("<Motion>")
            self.button_activate_zoom['text'] = 'Off \n (zoom)'
        elif self.magnifier_active:
            self.magnifier_active = False
            self.button_activate_magnifier['text'] = 'Off \n (magnifier)'
            self.canvas.unbind("<MouseWheel>")
            self.canvas.unbind("<Motion>")
            self.unbind("<Shift-MouseWheel>")
            self.magnifier_size_scale['state'] = 'disabled'
        if mode == 'magnifier':
            if not self.magnifier_active:
                self.magnifier_active = True
                self.button_activate_magnifier['text'] = 'On \n (magnifier)'
                self.canvas.bind("<MouseWheel>", self.change_zoom_level)
                self.canvas.bind("<Motion>", self.crop)
                self.bind("<Shift-MouseWheel>", self.zoom_window)
                self.magnifier_size_scale['state'] = 'normal'
        elif mode == 'zoom':
            if not self.zoom_active:
                self.zoom_active = True
                self.canvas.bind("<MouseWheel>", self.zooming)
                self.canvas.bind("<Motion>", self.motion)
                self.button_activate_zoom['text'] = 'On \n (zoom)'
        self.refresh()

    def zoom_slider(self):
        self.zoomcycle = self.zoom_level_scale.get()
        
    def magnifier_slider(self):
        self.magnifier_size = self.magnifier_size_scale.get()
    
    def change_bonus_state(self):
        self.canvas.delete(self.zoom_image)
        self.lis = self.matt[self.album_value] if self.bonus_active else self.matt[self.number_of_stories]
        self.bonus_active = False if self.bonus_active else True
        self.image_number = 1
        self.refresh()

    def change_story(self, delta):
        self.canvas.delete(self.zoom_image)
        self.album_value += delta
        self.lis = self.matt[self.album_value]
        self.image_number = 1
        self.refresh()

    def change_pic(self, move):
        self.canvas.delete(self.zoom_image)
        self.image_number += move
        self.refresh()
        
    def activate_level(self):
        start_text = 'You have chosen part ' + str(self.image_number) + ' of '
        end_text = 'bonus chapter.' if self.bonus_active else 'chapter: ' + str(self.album_value+1) + '.'
        self.text_add(start_text + end_text)

    def description(self):
        txt = 'textb.txt' if self.bonus_active else 'text' + str(self.album_value+1) + '.txt'
        with open(txt) as description_file:
            lines_file = description_file.readlines()
        self.text_add(lines_file[self.image_number - 1], text_end=self.shortcut_file)

        txt = 'pic: ' + str(self.image_number) + '   '
        start_text = txt if self.bonus_active else txt + 'cha: ' + str(self.album_value+1) + '   '
        end_text = 'bonus: Yes' if self.bonus_active else 'bonus: No'
        self.text_add(start_text, text_end=end_text, height_con=1, row_con=8)

    def text_add(self, text_start, text_end=str(), height_con=17, width_con=30,
                 row_con=0, column_con=0, columnspan_var=7, rowspan_var=4):
        text = Text(self, height=height_con, width=width_con, font=("Arial", 30), wrap=WORD)
        text.insert(INSERT, text_start)
        text.insert(END, text_end)
        text.grid(row=row_con, column=column_con, columnspan=columnspan_var, rowspan=rowspan_var)

    def mouse_clicked(self):
        if self.magnifier_active:
            self.canvas.unbind("<MouseWheel>")
            self.bind("<MouseWheel>", self.zoom_window)     
        
    def rebind(self):
        self.unbind("<MouseWheel>")
        if self.zoom_active:
            self.canvas.bind("<MouseWheel>", self.zooming)
        elif self.magnifier_active:
            self.canvas.bind("<MouseWheel>", self.change_zoom_level)

    def disable_zoom(self):
        self.canvas.unbind("<MouseWheel>")
        self.canvas.after(1000, self.rebind)


class MyButton(Button):
    def __init__(self, callback, text, shortcuts, call, class_root):
        super().__init__(class_root, text=text, width=10, height=5,
                         command=callback)
        self._shorcuts = shortcuts
        for shortcut in self._shorcuts:
            class_root.bind(shortcut, call)
            self['state'] = NORMAL
        self.call = call
        self.root = class_root
        
    def set_enabled(self, enabled):
        if self['state'] == DISABLED and not enabled or self['state'] == NORMAL and enabled:
            pass
        if not enabled:
            self['state'] = DISABLED
            for shortcut in self._shorcuts:
                self.root.unbind(shortcut)
        else:
            self['state'] = NORMAL
            for shortcut in self._shorcuts:
                self.root.bind(shortcut, self.call)


if __name__ == "__main__":
    root = LevelSelectScreen()
