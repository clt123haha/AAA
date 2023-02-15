cont = 0
id = 0
cont_down = 0
cont_down_list = []

def id_up():
    global id
    id += 1

def get_id():
    global id
    return id

def list_append(n):
    global cont_down_list
    cont_down_list.append(n)

def len_list():
    global cont_down_list
    return len(cont_down_list)

def cont_down_up():
    global cont_down
    cont_down += 1

def get_cont_down():
    global cont_down
    return  cont_down

def get_cont_down_list():
    global cont_down_list
    return cont_down_list[0]

def del_cont_down_list():
    global cont_down_list
    del cont_down_list[0]