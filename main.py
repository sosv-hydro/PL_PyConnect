import parser

parser = Parser().parser
while True:
    try:
        msg = input('->')
        if msg == 'exit':
            sys.exit()
    except EOFError:
        break
    result = parser.parse(msg)