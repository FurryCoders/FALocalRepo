def sigint_block():
    pass

def sigint_ublock():
    pass

def sigint_check():
    return False

def sigint_clear():
    while True:
        try:
            sigint_ublock()
            break
        except:
            pass
    sigint_block()
