import tkinter
from vars import HEIGHT, WIDTH, VSTEP, SCROLL_STEP
from Ofunctions import lex, layout

class Browser : 
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT,
        )
        self.canvas.pack(fill="both", expand=1)
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.mousewheel)
        self.window.bind("<Configure>", self.on_configure)

    def load(self, url):
        if url.scheme in ["http", "https"]:
            body = url.request()
            if body is not None :
                self.text = lex(body)
                self.display_list = layout(self.text)
                self.draw()
            else : 
                print("there is no body to show")
        elif url.scheme in ["view-source:http","view-source:https"]:
            body = url.request()
            if body is not None:
                print(body.decode("utf8"))
            else:
                print("there is no body to show")
        elif url.scheme == "file" : 
            f = open(url.path, 'r')
            body = f.read()
            if body is not None:
                print(lex(body))
            else:
                print("there is no body to show")
        elif url.scheme == "data" :
            body = url.path 
            if body is not None:
                self.text = lex(body)
                print(self.text)
            else:
                print("there is no body to show")
    
    def draw(self, height=HEIGHT):
        self.canvas.delete("all")
        a = self.canvas.create_rectangle(50, 0, 100, 50, fill='red')
        self.canvas.move(a, 20, 20)

        for x, y, c in self.display_list:
            if y > self.scroll + height: continue
            if y + VSTEP < self.scroll : continue
            self.canvas.create_text(x, y - self.scroll, text=c)

    def scrolldown(self, e) : 
        cur_height = self.canvas.winfo_height()
        if self.scroll + cur_height < self.display_list[-1][1]:
            self.scroll += SCROLL_STEP
            self.draw(cur_height)
    
    def scrollup(self, e):
        cur_height = self.canvas.winfo_height()
        if self.scroll > 0 :
            self.scroll -= SCROLL_STEP
            self.draw(cur_height)

    def mousewheel(self, e):
        cur_height = self.canvas.winfo_height()
        if e.num == 5 or e.delta == -120 : 
            if self.scroll + cur_height < self.display_list[-1][1]:
                self.scroll += SCROLL_STEP
                self.draw(cur_height)
        if e.num == 4 or e.delta == 120 : 
            if self.scroll > 0 :
                self.scroll -= SCROLL_STEP
                self.draw(cur_height)

    def on_configure(self, e):
        new_width = e.width
        new_height = e.height
        self.display_list = layout(self.text, new_width)
        self.draw(new_height)