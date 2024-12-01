import tkinter
from vars import HEIGHT, WIDTH, VSTEP, SCROLL_STEP, SIDE_STEP
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
        self.side_scroll = 0
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
        """
        Draws the canvas (what's inside the window)
        """
        cur_width = self.canvas.winfo_width()
        cur_height =  self.canvas.winfo_height()
        self.canvas.delete("all")
        x = self.display_list[-1][1] - cur_height
        fact = x / SIDE_STEP
        y = cur_height-fact
        a = self.canvas.create_rectangle(cur_width-10, self.side_scroll, cur_width, y+self.side_scroll, fill='blue')
        self.canvas.move(a, 0, 0)

        for x, y, c in self.display_list:
            if y > self.scroll + height: continue
            if y + VSTEP < self.scroll : continue
            self.canvas.create_text(x, y - self.scroll, text=c)

    def scrolldown(self, e) : 
        """
        Handles the scroll down behaviour (with the downside key)
        """
        cur_height = self.canvas.winfo_height()
        if self.scroll + cur_height < self.display_list[-1][1]:
            self.scroll += SCROLL_STEP
            self.side_scroll += SIDE_STEP
            self.draw(cur_height)
    
    def scrollup(self, e):
        """
        Handles the scroll up behaviour (with the upside key)
        """
        cur_height = self.canvas.winfo_height()
        if self.scroll > 0 :
            self.scroll -= SCROLL_STEP
            self.side_scroll -= SIDE_STEP
            self.draw(cur_height)

    def mousewheel(self, e):
        """
        Handles mousewheel scrolling for the canvas
        """
        cur_height = self.canvas.winfo_height()
        if e.num == 5 or e.delta == -120 : 
            if self.scroll + cur_height < self.display_list[-1][1]:
                self.scroll += SCROLL_STEP
                self.side_scroll += SIDE_STEP
                self.draw(cur_height)
        if e.num == 4 or e.delta == 120 : 
            if self.scroll > 0 :
                self.scroll -= SCROLL_STEP
                self.side_scroll -= SCROLL_STEP
                self.draw(cur_height)

    def on_configure(self, e):
        """
        Reconfigures the content for when the sizes of 
        the height or width of the window is changed.
        """
        new_width = e.width
        new_height = e.height
        self.display_list = layout(self.text, new_width)
        self.draw(new_height)