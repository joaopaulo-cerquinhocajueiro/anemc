Anem C
------

A subset of C for the ANEM microcontroller


## BNF

```
program : [declaration | function]*

declaration : TYPE VARIABLE [ RECEIVES expression ] END
function    : TYPE VARIABLE LPAREN declaration [ SEPARATOR declaration ]* RPAREN block

block : command | LWHISKERS [command]* RWHISKERS

command : declaration | statement | ifblock | whileblock | forblock | block | funcall

statement  : VARIABLE RECEIVES expression END
expression : sfactor [PLUSOP sfactor]*
sfactor    : [SIGN] factor
factor     : term [MULOP term]*
term       : VARIABLE | VALUE | LPAREN expression RPAREN | fcall

funcall : fcall END
fcall   : VARIABLE LPAREN [expression]* RPAREN

ifblock    : IFCOMMAND LPAREN condition RPAREN block [ELSECOMMAND block]
whileblock : WHILECOMMAND LPAREN condition RPAREN block
forcommand : FORCOMMAND LPAREN statement | declaration SEPARATOR condition SEPARATOR statement RPAREN block

condition : lfactor [LOR lfactor]*
lfactor   : lterm [LAND lterm]*
lterm     : [LNOT] [VARIABLE | VALUE | comparison | LPAREN condition RPAREN]

comparison : expression COMPOP expression
```

The types are a subset of the c types:

```python
TYPE = r'(bool)|(int)|(char)|(uint)|(schar)'
```

## Definition of the register functions# Definição dos registradores

- Register $0 is hard-coded to 0, register $1 is soft-coded to 1
- Registers $2,$3,$4,$5,$6,$7 are free registers, for arithmetic operations
- register $8 will be used to store addressess to variables, for load and store operations
- Registers $9,$10,$11,$12 -> are for parameter passing and function return
- Register $13 is the stack pointer, "saved"
- Register $14 is the data pointer, "saved"
- Register $15 is the return address, the JAL operation links here.
