# -*- coding: utf-8 -*- -----------------------------------------------------------------------------
# anemc.py
#
# A compiler for the ANEM microcontroller.
# -----------------------------------------------------------------------------

tokens = (
    'TYPE', 'RETURNCOMMAND',
    'IFCOMMAND', 'WHILECOMMAND', 'FORCOMMAND', 'ELSECOMMAND',
    'VARIABLE', 'VALUE',
    'RECEIVES', 'PLUSOP', 'MULOP', 'SIGN',
    'LOR', 'LAND', 'LNOT', 'COMPOP',
    'LPAREN', 'RPAREN', 'LWHISKERS', 'RWHISKERS',
    'LISTSEP', 'END'
    )

t_TYPE      = r'(bool)|(int)|(char)|(uint)|(schar)|(void)'
t_IFCOMMAND = r'if'
t_ELSECOMMAND = r'else'
t_WHILECOMMAND = r'while'
t_FORCOMMAND = r'for'
t_RETURNCOMMAND = r'return'
t_VARIABLE  = r'(?!((return)|(bool)|(int)|(char)|(uint)|(schar)|(void)|(if)|(else)|(while)|(for)))[a-zA-Z_][a-zA-Z0-9_]*'
t_VALUE     = r'(0x)?\d+'
t_RECEIVES  = r'=(?![=\!><])'
t_PLUSOP    = r'\+|-|(\|(?!\|))'
t_MULOP     = r'\*|/|(&(?!&))'
t_SIGN      = r'\+|-|~'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LOR       = r'\|\|'
t_LAND      = r'&&'
t_LNOT       = r'\!(?!=)'
t_COMPOP    = r'(==)|(>=)|(<=)|(<)|(>)|(\!=)'
t_LWHISKERS = r'{'
t_RWHISKERS = r'}'
t_LISTSEP   = r','
t_END       = r';'

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lexer = lex.lex()

variables = {}
freeAddress = 0
functions = {}

# Definição dos registradores
# $0 -> 0, $1 -> 1
# $2,$3,$4,$5,$6,$7, -> área de troca de informações com subrotinas (argumentos e retorno): "temporários"
# $8 -> endereços contantes
# $9,$10,$11,$12 -> "super registrador" (devem ser preservados pela chamada de uma função)
# $13 -> stack pointer, "saved"
# $14 -> data pointer, "saved"
# $15 -> return address, "empilhável"

freeRegs = [2,3,4,5,6,7,8,13,14,16,17,18,20,22,23,24,1,1,1,1,1,1,1]
paramRegs = (9,10,11,12)
tempText = ''
ifCounter = 0;
forCounter = 0;
whileCounter = 0;

# Object Variable, to store type and value
class Variable:
    def __init__(self,varType):
        self.type  = varType
        self.value = 0
        self.address = 0

class CFunction:
    def __init__(self,varType):
        self.type = varType
        self.block = ''
        self.inputs = []

def p_program(t):
    '''program : program declaration
               | program function
               | declaration
               | function'''
    pass

execfile("function.py")

def p_declaration(t):
    '''declaration : TYPE VARIABLE END
                   | TYPE VARIABLE RECEIVES VALUE END'''
    global freeAddress
    variables[t[2]] = Variable(t[1])
    if len(t)==6:
        variables[t[2]].value = t[4]
    else:
        variables[t[2]].value = '0'
    register = 8 # Usado para armazenar constantes de enderecos
    print('.constant %s = %d -- type %s' %(t[2],freeAddress,t[1]))
    print('LIW $%d, %s'%(register,variables[t[2]].value))
    print('SW $%d,%d'%(register,freeAddress))
    freeAddress = freeAddress + 1

def p_block(t):
    '''block : command
             | LWHISKERS commandlist RWHISKERS
             | LWHISKERS RWHISKERS'''
    if len(t)==4:
        t[0] = 'comandos\n'
    else:
        t[0] = 'vazio\n'

def p_commandlist(t):
    '''commandlist : commandlist command
                   | command'''
    pass

def p_command(t):
    '''command : declaration
               | statement
               | return
               | ifblock
               | whileblock
               | forblock
               | funcall'''
    pass

def p_return(t):
    '''return : RETURNCOMMAND expression END'''
    global tempText
    tempText = tempText +('MV $9,$%d\nRET\n'%(t[2]))

def p_statement(t):
    '''statement  : VARIABLE RECEIVES expression END'''
    global tempText
    tempText = tempText +('SW %s,r$%d\n' %(t[1],t[3]))
    freeRegs.append(t[3])

def p_expression(t):
    '''expression : expression PLUSOP sfactor
                  | sfactor'''
    global tempText
    if len(t)==4:
        if (t[2] == '+'):
            menmonic = 'ADD'
        elif (t[2] == '-'):
            menmonic = 'SUB'
        elif (t[2] == '|'):
            menmonic = 'OR'
        tempText = tempText +('%s r$%d, r$%d\n'%(menmonic,t[1],t[3]))
        freeRegs.append(t[3])
    t[0] = t[1]

def p_sfactor(t):
    '''sfactor : SIGN factor
               | factor'''
    global tempText
    if len(t)==3:
        tempText = tempText +('INV r$%d'%t[2])
        t[0] = t[2]
    else:
        t[0] = t[1]

def p_factor(t):
    '''factor : factor MULOP term'''
    global tempText
    if (t[2] == '/'):
        menmonic = 'DIV'
    elif (t[2] == '*'):
        menmonic = 'MUL'
    elif (t[2] == '&'):
        menmonic = 'AND'
    tempText = tempText +('%s r$%d, r$%d\n'%(menmonic,t[1],t[3]))
    t[0] = t[1]
    freeRegs.append(t[3])

def p_factor_term(t):
    '''factor : term'''
    t[0] = t[1]

def p_term_var(t):
    '''term : VARIABLE'''
    global tempText
    t[0] = freeRegs.pop()
    tempText = tempText +('LW $r%d, %s\n'%(t[0],t[1]))

def p_term_val(t):
    '''term : VALUE'''
    global tempText
    t[0] = freeRegs.pop()
    tempText = tempText +('LIW $r%d, %s\n'%(t[0],t[1]))

def p_term_pars(t):
    '''term : LPAREN expression RPAREN'''
    t[0] = t[2]

def p_term_function(t):
    '''term : fcall'''
    t[0] = t[1]

def p_funcall(t):
    '''funcall : fcall END'''
    print "funcall"

items = []

def p_fcall(t):
    '''fcall : VARIABLE LPAREN vallist RPAREN'''
    global tempText
    tempText = tempText + '--Call to function "%s"\n' % (t[1])
    for idx,var in enumerate(t[3]): # each parameter goes in the heap
        tempText = tempText + 'MV $%d,$%d\n'%(paramRegs[idx],var)
        freeRegs.append(var)
    t[0] = freeRegs.pop()
    tempText = tempText +('JAL %s\nMV $%d,$9\n'%(t[1],t[0]))

def p_vallist(t):
    '''vallist : expression LISTSEP vallist
               | expression'''
    if len(t) == 2:
        t[0] = [t[1]]
    else:
        t[0] = t[3] + [t[1]]

def p_ifblock(t):
    '''ifblock : IFCOMMAND LPAREN condition RPAREN block ELSECOMMAND block
               | IFCOMMAND LPAREN condition RPAREN block'''
    global tempText
    global ifCounter
    if len(t) == 8:
        tempText = tempText + 'beq ${},$0,%else{}%\n'.format(t[3],ifCounter)
        tempText = tempText + t[5]
        tempText = tempText + 'J %endif{}%\n'.format(ifCounter)
        tempText = tempText + 'else{}:'.format(ifCounter)
        tempText = tempText + t[7]
        tempText = tempText + 'endif{}:'.format(ifCounter)
    else:
        tempText = tempText + 'beq ${},$0,%endif{}%\n'.format(t[3],ifCounter)
        tempText = tempText + t[5]
        tempText = tempText + 'endif{}:'.format(ifCounter)
    ifCounter = ifCounter + 1

def p_whileblock(t):
    '''whileblock : WHILECOMMAND LPAREN condition RPAREN block'''
    print 'while'

def p_forblock(t):
    '''forblock : FORCOMMAND LPAREN statement condition END statement RPAREN block
                | FORCOMMAND LPAREN declaration condition END statement RPAREN block'''
    print 'for'

def p_condition(t):
    '''condition : condition LOR lfactor
                 | lfactor'''
    print 'condition'

def p_lfactor(t):
    '''lfactor : lfactor LAND lterm
                 | lterm'''
    print 'lfactor'

def p_lterm(t):
    '''lterm : LNOT lterm
             | VARIABLE
             | VALUE
             | comparison
             | LPAREN condition RPAREN'''
    print 'lterm'

def p_comparison(t):
    '''comparison : expression COMPOP expression'''
    print('comparison type %s'%(t[2]))


def p_error(t):
    print("Syntax error at '%s'" % t.value)

import ply.yacc as yacc
parser = yacc.yacc()

try:
    programa = open('programa.txt','r')
except:
    print("File error")
texto = programa.read()
programa.close()
parser.parse(texto);

# print('Functions:')
# for function in functions:
#     print function
#
# print('Variables:')
# for variable in variables:
#     print variable
