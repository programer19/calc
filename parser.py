import tkinter as tk
from xml.dom import minidom
import json

class UIParser:
    def __init__(self, fileName, signals):
        self._signals = signals
        self._widgetsConfig = {}
        self._dom = minidom.parse(fileName).childNodes[0]
        self._recursiveParse(self._dom)
        self._widgets = {}
        self._createWidgets()
        
    def _signalFunc(self, signalName):
        return lambda:self._signals[signalName](self)
        
    def _parseJson(self, jsonStr, signals):
        jsonArr = json.loads(jsonStr)
        res = None
        if isinstance(jsonArr, dict):
            res = {k:jsonArr[k] if jsonArr[k] not in signals else signals[jsonArr[k]] for k in jsonArr}
        else:
            res = [val if val not in signals else signals[val] for val in jsonArr]
        return res
        
    def _recursiveParse(self, element):
        for c in element.childNodes:
            if c.nodeType != 1: continue 
            attrs = c.attributes
            signals = {attrs[attr].localName:self._signalFunc(attrs[attr].value) for attr in attrs.keys() if attrs[attr].prefix == 'signal'}
            attributes = {attr:attrs[attr].value if attrs[attr].value not in signals else signals[attrs[attr].value] for attr in attrs.keys() if attrs[attr].prefix == None}
            packAttrs = {attrs[attr].localName:attrs[attr].value for attr in attrs.keys() if attrs[attr].prefix == 'pack'}
            gridAttrs = {attrs[attr].localName:attrs[attr].value for attr in attrs.keys() if attrs[attr].prefix == 'grid'}
            gSize = {attrs[attr].localName:self._parseJson(attrs[attr].value, {}) for attr in attrs.keys() if attrs[attr].prefix == 'gsize'}
            runs = {attrs[attr].localName:self._parseJson(attrs[attr].value, signals) for attr in attrs.keys() if attrs[attr].prefix == 'run'}
            binds = {'<'+attrs[attr].localName+'>':self._signals[attrs[attr].value] for attr in attrs.keys() if attrs[attr].prefix == 'bind'}
            self._widgetsConfig[attributes['id']] = {
                'type': c.tagName, 
                'parent': element.attributes['id'].value if element.tagName != 'xml' else None, 
                'attributes': attributes,
                'pack': packAttrs,
                'runs': runs,
                'grid': gridAttrs,
                'binds': binds,
                'gSize': gSize,
            }
            del self._widgetsConfig[attributes['id']]['attributes']['id']
            self._recursiveParse(c)
    
    def _createWidgets(self):
        for elId in self._widgetsConfig:
            elementFunc = getattr(tk, self._widgetsConfig[elId]['type'])
            if self._widgetsConfig[elId]['parent'] is not None:
                self._widgets[elId] = elementFunc(self._widgets[self._widgetsConfig[elId]['parent']], **self._widgetsConfig[elId]['attributes'])
                if len(self._widgetsConfig[elId]['pack']) > 0:
                    pack = getattr(self._widgets[elId], 'pack')
                    pack(**self._widgetsConfig[elId]['pack'])
                if len(self._widgetsConfig[elId]['grid']) > 0:
                    grid = getattr(self._widgets[elId], 'grid')
                    grid(**self._widgetsConfig[elId]['grid'])
            else:
                self._widgets[elId] = elementFunc(**self._widgetsConfig[elId]['attributes'])
                
            for run in self._widgetsConfig[elId]['runs']:
                func = getattr(self._widgets[elId], run)
                params = self._widgetsConfig[elId]['runs'][run]
                if isinstance(params, dict):
                    func(**params)
                else:
                    func(*params)
                
            for bind in self._widgetsConfig[elId]['binds']:
                bindFunc = getattr(self._widgets[elId], 'bind')
                bindFunc(bind, self._widgetsConfig[elId]['binds'][bind])
                
            if 'row' in self._widgetsConfig[elId]['gSize']:
                confFunc = getattr(self._widgets[elId], 'rowconfigure')
                for row in self._widgetsConfig[elId]['gSize']['row']:
                    confFunc(row, weight=self._widgetsConfig[elId]['gSize']['row'][row])
                    
            if 'column' in self._widgetsConfig[elId]['gSize']:
                confFunc = getattr(self._widgets[elId], 'columnconfigure')
                for column in self._widgetsConfig[elId]['gSize']['column']:
                    confFunc(column, weight=self._widgetsConfig[elId]['gSize']['column'][column])
        
    def getWidget(self, elId):
        return self._widgets[elId]



