from vars import NLINE, HSTEP, WIDTH, VSTEP


def lex(body): 
    if type(body)!= str:
        body = body.decode("utf8")
    
    text = ""
    in_tag = False
    is_entity =  False
    the_entity = ""
    for c in body: 
        if c == "<" :
            in_tag = True
        elif c == ">" :
            in_tag = False
        elif is_entity :
            the_entity+= c
            if len(the_entity) == 4:
                if the_entity== "&lt;":
                    text += "<"
                    is_entity = False
                    the_entity = ""
                elif the_entity == "&gt;":
                    text += ">"
                    is_entity = False
                    the_entity = ""
                else : 
                    text += the_entity
                    is_entity= False
                    the_entity= ""
        elif not in_tag and not is_entity: 
            if c == "&":
                is_entity = True
                the_entity = "&"
            else :
                text += c
    if len(the_entity)>0:
        text += the_entity

    return text


def layout(text, width=WIDTH):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text : 
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x > width - HSTEP: 
            cursor_y += VSTEP 
            cursor_x = HSTEP
        if c == '\n' : 
            cursor_x = HSTEP
            cursor_y += NLINE 
    return display_list 