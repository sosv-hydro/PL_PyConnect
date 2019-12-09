
import ply.lex as lex

# Defining list of generic tokens in the language.
# NOTE: Ply's Lexer will use the list named "tokens" to tokenize
# automatically based on the regex rules they have.

#TODO: Add more tokens as necessary

tokens = [
    'IP',
    'INT',
    'FLOAT',
    'KEYWORD',
    'STRING',
    'ASSIGN',
    'COLON',
    'COMMA'
]

#TODO: Add more reserved words as necessary

# Defining dictionary of specific reserved words and their token values.
# NOTE: this is done to match all strings and identify keywords afterwards
# using a dictionary mapping.
reserved = {
    'address'       : 'ADDRESS',   
    'allow'         : 'ALLOW',
    'port'          : 'PORT',
    'connection'    : 'CONNECTION',
    'connect'       : 'CONNECT',
    'initiate'      : 'INITIATE',
    'info'          : 'INFO',
    'close'         : 'CLOSE',
    'clients'       : 'CLIENTS',
    'to'            : 'TO',
    'message'       : 'MESSAGE',
    'send'          : 'SEND',
    'show'          : 'SHOW', 
    'server'        : 'SERVER',
    'name'          : 'NAME',
    'in'            :  'IN'
}

tokens += reserved.values()
# =================================================================================
# Defining rules for lex to interpret tokens.

# Simple rules.
# NOTE: Ply's lexer maps the regex of anything preceded by "t_"
# to the token that follows it.

t_COMMA = ','
t_COLON = r':'
t_ASSIGN = r'='

# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


# Rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_BOOL(t):
    r'true|false'
    if  t.value == 'true':
        t.value = True
    elif t.value == 'false':
        t.value = False
    return t

def t_IP(t):
    r'\b((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\.)){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\b'
    return t

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_FLOAT(t):
    r'\d*\.\d+'
    t.value = float(t.value)
    return t

#TODO: Either modify definition or add a new on to influde Filepaths
def t_STRING(t):
    r'"(?:\\"|.)*?"'
    t.value = bytes(t.value.lstrip('"').rstrip('"'), "utf-8").decode("unicode_escape")
    return t

def t_KEYWORD(t):
    r'\w+'
    value = t.value.lower()
    if(reserved.get(value)):
        t.value = str(t.value)
        t.type = reserved.get(value, t.type)
    else:
        t.type = 'STRING'
    return t

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

