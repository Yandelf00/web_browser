"""
    variable = ["browzie.py", "data:/idk mlsd" ,"dslmj"]
    print(variable[1:])
"""


variabletwo = "<div>sdlfkj &lt; qlskqdf &lt;div&gt;ljf</div>"

in_tag = False
entity = False
new_entity="&"
for c in variabletwo:
    if c == "<" :
        in_tag = True
    elif c == ">" :
        in_tag = False
    elif c == "&":
        entity = True
    elif entity:
        new_entity += c
        if len(new_entity) == 4:
            if new_entity == "&lt;":
                print("<", end="") 
                entity = False
                new_entity = "&"
            elif new_entity == "&gt;":
                print(">", end="")
                entity = False
                new_entity = "&"
            else : 
                print(new_entity, end="")
                entity = False
                new_entity = "&"

    elif not in_tag and not entity: 
            print(c, end="")



"""
url = "file:///Users/surfa/OneDrive/Bureau/git_repos/web_browser/file_to_open.txt"

scheme, url = url.split("://", 1)




print(scheme)
print(url)
print("C:" + url)
f = open("C:/Users/surfa/OneDrive/Bureau/git_repos/web_browser/file_to_open.txt", "r")

print(f.read())
"""