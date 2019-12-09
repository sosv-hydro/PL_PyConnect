from intermediate_code.simple_client import * 
from intermediate_code.simple_server import *
import time

from pyCon_lexer import tokens
from ply import yacc

# ======================================================================================
# Defining parser methods

# NOTE: p[0] represents the non-terminal on the left of the colon ":"
# p[1->n] are the terminals/non-terminals to the right of the colon.
# these can have multiple values specified between "or"s "|".
# The idea is to pass up predicable tuples with predictable values inside them

# NOTE: will cause errors trying to build parser if grammar contains terminals/non-terminals
# that have not yet been implemented.
# =======================================================================================


# Global dictionary to hold all variables created or modified
global_vars = {}
connType = None
currentCon = None

def p_run_command(p):
    '''
    run_command : create_server
                | allow_conns
                | close_connection
                | show_clients
                | close_client_connection_in_server
                | create_client
                | send_message
                | send_spec_message
                | create_server_for_all
                | show_server_info
    '''
    p[0] = p[1]

# creates a server instance and stores it in the global_vars dictionary. 
# Any subsequent calls to the server have to be done through the provision of the name
def p_create_server(p):
    '''
    create_server : INITIATE SERVER COLON ADDRESS IP COMMA PORT INT COMMA NAME STRING
    '''
    p[0] = Server(p[5], p[8])
    global_vars[p[11]] = p[0]
    global_vars['conType'] = "s"


def p_create_server_for_all(p):
    '''
    create_server_for_all : INITIATE SERVER COLON PORT INT COMMA NAME STRING
    '''
    p[0] = Server("", port=p[5])
    global_vars[p[8]] = p[0]
    connType = "s"


def p_create_client(p):
    '''
    create_client : CONNECT TO SERVER COLON ADDRESS IP COMMA PORT INT
    '''
    p[0] = Client(p[6], p[9])
    connType = "c"
    time.sleep(.500)
    username = p[0].getUsername()
    global_vars[username] = p[0]
    global_vars['conType'] = "c"
    global_vars['activeUser'] = username
#  print(global_vars)

# changes the amount of connections the server will allow
def p_allow_conns(p):
    '''
    allow_conns : ALLOW CONNECTION IN STRING COLON INT
    '''
    server = global_vars[p[4]]
    if(server):
        server.changeClientLimit(p[6])
    else:
        print("server is not yet created")

# shows the clients in the server
def p_show_clients(p):
    '''
    show_clients : SHOW CLIENTS INFO IN STRING
    '''
    server = global_vars[p[5]]
    if(server):
        server.showClientsList()
    else:
        print("server is not yet created")

# provides server information
def p_show_server_info(p):
    '''
    show_server_info : SHOW STRING INFO
    '''
    server = global_vars[p[2]]
    if(server):
        server.showServerInfo()
    else:
        print("server is not yet created")

# closes the connection 
def p_close_connection(p):
    '''
    close_connection : CLOSE CONNECTION COLON STRING
    '''
    try:
        conn = global_vars[p[4]]
        conn.closeCon()
        sys.exit()
    except KeyError:
        print("object to close not found")
    except AttributeError:
        print("object to close is not of a connection type")
    
# Close a particular client connection in the server
def p_close_client_connection_in_server(p):
    '''
    close_client_connection_in_server : CLOSE CONNECTION COLON STRING IN STRING
    '''
    server = global_vars[p[6]]
    if(server):
        try:
            if(server.lookUpClient(p[4])):
                server.closeClientCon(p[4])
        except KeyError:
            print("client not connected to server")

def p_send_message(p):
    '''
    send_message : SEND MESSAGE COLON STRING
    '''
    if(global_vars['conType']  == "c"):
        username = global_vars['activeUser']
        global_vars[username].send_msg(p[4])
    elif(global_vars['conType']  == "s"):
        currentCon.msg_to_all_from_server(p[4])
    else:
        print("message was not sent")

def p_send_spec_message(p):
    '''
    send_spec_message : SEND MESSAGE TO STRING COLON STRING
    '''
    print("sending spec message")
    if(global_vars['conType']  == "c"):
        username = global_vars['activeUser']
        global_vars[username].send_msg("sendSpecMessage," + p[4] + "," + p[6])
    else:
        print("message was not sent")

def p_error(p):
     if p:
          print("Syntax error at token", p.type)
          # Just discard the token and tell the parser it's okay.
          parser.errok()
     else:
          print("Syntax error at EOF")

# Build the parser
parser = yacc.yacc()

while True:
    try:
        msg = input('->')
        if msg == 'exit':
            sys.exit()
    except EOFError:
        break
    result = parser.parse(msg)