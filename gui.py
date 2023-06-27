import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import configparser

# the class is a frame within the main window, not the main window itself
class GUI(tb.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.pack(fill=BOTH, expand=True)
    
    def create_widgets(self):
        

if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('./config/config.ini')

    title = config['GUI']['WINDOW_TITLE']
    width = int(config['GUI']['WINDOW_WIDTH'])
    height = int(config['GUI']['WINDOW_HEIGHT'])

    # app is the main window and is the "master" object
    app = tb.Window(
        title=title, 
        size=(width, height), 
        themename='darkly',
        resizable=(False,False)
        )
    
    GUI(app)
    app.mainloop()
