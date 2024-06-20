from parser import UIParser

def clickClear(parser):
    parser.getWidget('textField').config(text='')
    
def clickDigit(parser, digit):
    label = parser.getWidget('textField')
    label.config(text = label.cget('text') + str(digit))

def clickPoint(parser):
    label = parser.getWidget('textField')
    label = parser.getWidget('textField')
    text = label.cget('text')
    
    if len(text) > 0 and text[-1].isdigit():
        label.config(text = label.cget('text') + '.')
    
def clickOperation(parser, operation):
    operationSymbols = {'Mult': '*', 'Add': '+', 'Div': '/', 'Sub': '-', 'Equal': ''}
    label = parser.getWidget('textField')
    text = label.cget('text')
    
    if (len(text) == 0): return None
    if text[-1] in ['*', '/', '+', '-']: text = text[:-1:]
    
    operations = {
        '*': lambda a, b: a * b, 
        '/': lambda a, b: a / b, 
        '+': lambda a, b: a + b, 
        '-': lambda a, b: a - b
    }
    
    for sym in ['*', '/', '+', '-']:
        if sym in text:
            pos = text.find(sym)
            text = '%.10f' % operations[text[pos]](float(text[:pos:]), float(text[pos+1::]))
            break
        
    while '.' in text and len(text) > 0 and (text[-1] == '0' or text[-1] == '.'):
        text = text[:-1:]
            
    if len(text) == 0:
        text = '0'
    
    label.config(text = text + operationSymbols[operation])
    
def clickOperationFactory(operation):
    return lambda parser, operation=operation: clickOperation(parser, operation)
    
def clickDigitFactory(digit):
    return lambda parser, digit=digit: clickDigit(parser, digit)
    
digitSignals = {'click'+str(digit): clickDigitFactory(digit) for digit in range(10)}
operationSignals = {'click'+operation: clickOperationFactory(operation) for operation in ['Mult', 'Add', 'Div', 'Sub', 'Equal']}

parser = UIParser('win.ui', {
    **digitSignals,
    **operationSignals,
    'clickClear': clickClear,
    'clickPoint': clickPoint,
})
parser.getWidget('mainWindow').mainloop()
