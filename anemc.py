# -----------------------------------------------------------------------------
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

freeRegs = [1,2,3,4,5,6,7,8,9,10,11,12]
tempText = ''

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

def p_function(t):
    '''function : TYPE VARIABLE LPAREN RPAREN block
                | TYPE VARIABLE LPAREN declarations RPAREN block'''
    global tempText
    functions[t[2]] = CFunction(t[1])
    functions[t[2]].block = t[6] if len(t)==7 else t[5]
    print('//%s function "%s"' % (t[1],t[2]))
    print '%s:\t%s'%(t[2],tempText)
    tempText = ''

def p_declarations(t):
    '''declarations : declarations declaration
                   | declaration'''
    pass

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
    print 'block'

def p_commandlist(t):
    '''commandlist : commandlist command
                   | command'''
    print 'commandlist'

def p_command(t):
    '''command : declaration
               | statement
               | RETURNCOMMAND expression END
               | ifblock
               | whileblock
               | forblock
               | funcall'''
    if t[1]==t_RETURNCOMMAND:
        print 'return'

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
    t[0] = freeRegs.pop()
    print 'function returns on reg %d'%t[0]
    tempText = tempText +('JAL %s\nPOP $%d\n'%(t[1],t[0]))

def p_vallist(t):
    '''vallist : vallist LISTSEP expression
               | expression'''
    global tempText
    if len(t) == 2:
        reg = t[1]
    else:
        reg = t[3]
    tempText = tempText +('PUSH $%d\n'%reg)
    freeRegs.append(reg)

def p_ifblock(t):
    '''ifblock : IFCOMMAND LPAREN condition RPAREN block ELSECOMMAND block
               | IFCOMMAND LPAREN condition RPAREN block'''
    print 'if'

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

print('Functions:')
for function in functions:
    print function

print('Variables:')
for variable in variables:
    print variable
