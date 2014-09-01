
# -*- coding:utf-8 -*-
# Copyright (c) 2011 Renato de Pontes Pereira, renato.ppontes at gmail dot com
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.

import re

'''
A simple PDN parser.

PDN (Portable Draughts Notation) is computer-processible format for recording draughts
games, both the moves and related data. 

This module is based on features of others parser modules (such json and yaml).
The basic usage::

    import pdn

    pdn_text = open('sijbrands.pdn').read()
    pdn_game = pdn.PDNGame()

    print pdn.loads(pdn_text) # Returns a list of PDNGame
    print pdn.dumps(pdn_game) # Returns a string with a pdn game

'''

class PDNGame(object):
    '''
    Describes a single chess game in PDN format.
    '''

    TAG_ORDER = ['Event', 'Site', 'Date', 'Round', 'White', 'Black', 'Result',
                 'GameType', 'Setup', 'FEN', 'PlyCount']

    def __init__(self, event=None, site=None, date=None, round=None, 
                                                         white=None,
                                                         black=None,
                                                         result=None):
        '''
        Initializes the PDNGame, receiving the required tags.
        '''
        self.event = event
        self.site = site
        self.date = date
        self.round = round
        self.white = white
        self.black = black
        self.result = result
        self.annotator = None
        self.plycount = None
        self.timecontrol = None
        self.time = None
        self.termination = None
        self.mode = None
        self.fen = None
        self.fen_string = None

        self.moves = []
    
    def dumps(self):
        return dumps(self)
    
    def fen_to_string(self): 
        if not self.fen:
            return '' 
            
        result = [] 
        for n in xrange(0, 50): 
            result.append('-')
        parts = self.fen[:-1].split(':') 
        for part in parts: 
            for n, s in enumerate(part): 
                if n == 0: 
                    continue
                color = 'o' if part[0] == 'W' else 'x'
                for field in part[1:].split(','):
                    if field[0] == 'K': 
                        result[int(field[1:]) - 1] = color.upper()
                    else: 
                        result[int(field) - 1] = color
        return ''.join(result)

    def __repr__(self):
        return '<PDNGame "%s" vs "%s", %s>' % (self.white, self.black, self.date)

def _pre_process_text(text):
    '''
    This function is responsible for removal of end line commentarys 
    (;commentary), blank lines and aditional spaces. Also, it converts 
    ``\\r\\n`` to ``\\n``.
    '''
    text = re.sub(r'\s*(\\r)?\\n\s*', '\n', text.strip())
    lines = []
    for line in text.split('\n'):
        line = re.sub(r'(\s*;.*|^\s*)', '', line)
        if line:
            lines.append(line)
    
    return lines

def _next_token(lines):
    '''
    Get the next token from lines (list of text pdn file lines).

    There is 2 kind of tokens: tags and moves. Tags tokens starts with ``[``
    char, e.g. ``[TagName "Tag Value"]``. Moves tags follows the example: 
    ``1. 32-28 20-25 2. 31-27``.
    '''
    if not lines:
        return None

    token = lines.pop(0).strip() 
    if token.startswith('['):
        return token

    while lines and not lines[0].startswith('['):
        token += ' '+lines.pop(0).strip()
    
    return token.strip()

def _parse_tag(token):
    '''
    Parse a tag token and returns a tuple with (tagName, tagValue).
    '''
    tag, value = re.match(r'\[(\w*)\s*(.+)', token).groups()
    return tag.lower(), value.strip('"[] ')

def _parse_moves(token):
    '''
    Parse a moves token and returns a list with movements
    '''
    moves = []
    while token:
        token = re.sub(r'^\s*(\d+\.+\s*)?', '', token)

        if token.startswith('{'):
            pos = token.find('}')+1
        else:
            pos1 = token.find(' ')
            pos2 = token.find('{')
            if pos1 <= 0:
                pos = pos2
            elif pos2 <= 0:
                pos = pos1
            else:
                pos = min([pos1, pos2])

        if pos > 0:
            moves.append(token[:pos])
            token = token[pos:]
        else:
            moves.append(token)
            token = ''
    
    return moves

def loads(text):
    '''
    Converts a string ``text`` into a list of PDNGames
    '''
    games = []
    game = None
    lines = _pre_process_text(text)

    while True:
        token = _next_token(lines)

        if not token:
            break

        if token.startswith('['):
            tag, value = _parse_tag(token)
            if not game or (game and game.moves):
                game = PDNGame()
                games.append(game)

            setattr(game, tag, value)
        else:
            game.fen_string = game.fen_to_string()
            game.moves = _parse_moves(token)
    
    return games

def dumps(games):
    '''
    Serialize a list of PDNGames (or a single game) into text format.
    '''
    all_dumps = []

    if not isinstance(games, (list, tuple)):
        games = [games]

    for game in games:
        dump = ''
        for i, tag in enumerate(PDNGame.TAG_ORDER):
            if getattr(game, tag.lower()):
                dump += '[%s "%s"]\n' % (tag, getattr(game, tag.lower()))
            elif i <= 6:
                dump += '[%s "?"]\n' % tag

        
        dump += '\n'
        i = 0
        for move in game.moves:
            if not move.startswith('{'):
                if i%2 == 0:
                    dump += str(i/2+1)+'. '
                
                i += 1

            dump += move + ' '
            
        all_dumps.append(dump.strip())
            
    return '\n\n\n'.join(all_dumps)
