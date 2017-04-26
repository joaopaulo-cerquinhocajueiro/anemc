def p_function(t):   # Definition of a function
    '''function : TYPE VARIABLE LPAREN RPAREN block
                | TYPE VARIABLE LPAREN varlist RPAREN block'''
    global tempText  # stores the object code
    global freeAddress # heap
    hasParams = (len(t)==7)
    # if there is a varlist (t[4]), then the function has parameters
    if hasParams:
        # each parameter goes in the heap
        for idx,var in enumerate(t[4]):
            # create a constant with the name of the variable at a free address
            varText = '.constant {} = {} -- type {}\n'.format(var[1],freeAddress,var[0])
            # load the address at register 8
            varText = varText + 'LIW $8,{}\n'.format(freeAddress)
            freeAddress = freeAddress + 1
            # Store the parameter at the given address
            varText = varText + 'SW $%d,0($8)\n'%(paramRegs[idx])
            tempText = varText + tempText
    functions[t[2]] = CFunction(t[1])
    functions[t[2]].block = t[6] if hasParams else t[5]
    print('--%s function "%s"' % (t[1],t[2]))
    print '%s:\n%s'%(t[2],tempText)
    tempText = ''
    if hasParams:
        freeAddress = freeAddress - len(t[4])

def p_varlist(t):
    '''varlist : vardecl LISTSEP varlist
               | vardecl'''
    if len(t) == 2:
        t[0] = [t[1]]
    else:
        t[0] = t[3] + [t[1]]

def p_vardecl(t):
    '''vardecl : TYPE VARIABLE'''
    t[0] = (t[1],t[2])
