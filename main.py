from Browser import Browser
from URL import URL
import tkinter



if __name__ == "__main__":
    import sys
    path = "file:///Users/surfa/OneDrive/Bureau/git_repos/web_browser/file_to_open.txt"
    if len(sys.argv) < 2 : 
        Browser().load(URL(path))
    elif len(sys.argv) > 2 and sys.argv[1][:4]=="data": 
        new_url = []
        for el in sys.argv[1:]: 
            new_url.append(el)
        Browser().load(URL(new_url))
    else : 
        Browser().load(URL(sys.argv[1]))

    tkinter.mainloop()