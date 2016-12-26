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
