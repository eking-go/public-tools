#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
xml_to_dict_parser.py - convert XML to dict,
use only xml.parsers.expat - minimal dependenses, only for standard library.
For using with small utilites.
'''

import xml.parsers.expat

__author__ = 'Nikolay Gatilov'
__copyright__ = 'Nikolay Gatilov'
__license__ = 'GPL'
__version__ = '0.2.2017083009'
__maintainer__ = 'Nikolay Gatilov'
__email__ = 'eking.work@gmail.com'


class XMLToDictParser:
    def __init__(self, data, simplify=True):
        self.parsed = {}
        self.simplify = simplify
        self.current_dict = self.parsed
        self.up_list = []
        pxml = xml.parsers.expat.ParserCreate()
        pxml.StartElementHandler = self.start
        pxml.EndElementHandler = self.stop
        pxml.CharacterDataHandler = self.get_data
        pxml.Parse(data)

    def start(self, name, attr):
        '''try:
            self.current_dict['subs'][name] = {}
        except:
            self.current_dict['subs'] = {}
            self.current_dict['subs'][name] = {}
        if len(attr) != 0:
            self.current_dict['subs'][name]['attr'] = attr
        self.up_list.append(self.current_dict)
        self.current_dict = self.current_dict['subs'][name]'''
        try:
            self.current_dict['subs'].append({name: {}})
        except:
            self.current_dict['subs'] = []
            self.current_dict['subs'].append({name: {}})
        if len(attr) != 0:
            self.current_dict['subs'][-1][name]['attr'] = attr
        self.up_list.append(self.current_dict)
        self.current_dict = self.current_dict['subs'][-1][name]

    def stop(self, name):
        try:
            s = self.current_dict['subs']
            subs_present = True
        except:
            subs_present = False
        try:
            self.current_dict['attr']
            attr_present = True
        except:
            attr_present = False
        try:
            d = self.current_dict['data']
            data_present = True
        except:
            data_present = False
        self.current_dict = self.up_list.pop()
        if not subs_present and not attr_present and data_present and self.simplify:
            self.current_dict['subs'][-1][name] = d
        if subs_present and not attr_present and not data_present and self.simplify:
            self.current_dict['subs'][-1][name] = s

    def get_data(self, data):
        dat = data.lstrip()
        dat = dat.rstrip()
        if len(dat) > 0:
            self.current_dict['data'] = dat

    def result(self):
        return self.parsed


if __name__ == "__main__":  # main
    import json
    xml_test = '''
    <messages>
       <note id="501">
         <to>Tove</to>
         <from>Jani</from>
         <heading>Reminder</heading>
         <body>Don't forget me this weekend!</body>
       </note>
       <note id="502">
         <to>Jani</to>
         <from>Tove</from>
         <heading>Re: Reminder</heading>
         <body>I will not</body>
       </note>
    </messages>
    '''
    print('Example XML:\n%s' % xml_test)
    pd = XMLToDictParser(xml_test)
    print('\nResult with simplify:\n%s\n' % json.dumps(pd.result(),
                                                       sort_keys=True,
                                                       indent=4))
    pd = XMLToDictParser(xml_test, simplify=False)
    print('\nResult without simplify:\n%s\n' % json.dumps(pd.result(),
                                                              sort_keys=True,
                                                              indent=4))
