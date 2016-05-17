#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on 2016-5-8
@author: isunchy
'''

import numpy as np

class chessboradstate:
    '''
    state: the state of the chessboard
    turn: which player to play
    roundcnt: count of round from begining
    '''
    def __init__(self):
        self.state = np.zeros([10,9], dtype=np.string_)
        self.turn = 'w'
        self.roundcnt = 1

def state2fen(cstate):
    '''
    transfer the chessboard to fen string
    state: state of the current chessboard
    turn: which player to play
    round: count of round
    return: fen string
    '''
    fen = ''
    [m,n] = cstate.state.shape
    for i in range(m):
        zcnt = 0
        for j in range(n):
            if cstate.state[i][j] != ' ':
                if zcnt != 0:
                    fen += str(zcnt)
                    zcnt = 0
                fen += cstate.state[i][j]
            else:
                zcnt += 1
        if zcnt != 0:
            fen += str(zcnt)
            zcnt = 0
        fen += '/'
    fen = fen[:-1]
    fen += ' ' + cstate.turn
    fen += ' - - 0 '
    fen += str(cstate.roundcnt)
    return fen

def fen2state(fen):
    '''
    transfer the fen string to chessboard
    fen: fen string
    return: state of the chessboard
    '''
    fenstrlist = fen.split()
    cstate = chessboradstate()
    cstate.state = np.zeros([10, 9], np.string_)
    fenstr1st = fenstrlist[0].split('/')
    for i in range(len(fenstr1st)):
        current = 0
        for j in range(len(fenstr1st[i])):
            if fenstr1st[i][j].isdigit():
                num = int(fenstr1st[i][j])
                for k in range(num):
                    cstate.state[i][current+k] = ' '
                current += num
            else:
                cstate.state[i][current] = fenstr1st[i][j]
                current += 1
    cstate.turn = fenstrlist[1]
    cstate.roundcnt = int(fenstrlist[5])
    return cstate

def move(cstate, move):
    '''
    move the chess according to the move action
    state: the current chessborad, numpy.array[10][9], dtype=string_
    move: the action to move, string format as:'D5-E5'
    '''
    src = []
    des = []
    src.append(9 - int(move[1]))
    src.append(ord(move[0]) - ord('A'))
    des.append(9 - int(move[4]))
    des.append(ord(move[3]) - ord('A'))
    # print src, des
    chess = cstate.state[src[0]][src[1]]
    cstate.state[src[0]][src[1]] = ' '
    cstate.state[des[0]][des[1]] = chess
    cstate.roundcnt += 1
    if cstate.turn == 'b':
        cstate.turn = 'w'
    else:
        cstate.turn = 'b'

def initfen():
    '''
    initialize the fen string of the beginning of the chessboard
    return: the init fen string
    '''
    fen = 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1'
    return fen
   
def visualstate(cstate):
    '''
    visual the chessborad
    '''
    print "   -------------------------------%s-%d-" % (cstate.turn, cstate.roundcnt)
    r = 9
    for row in cstate.state:
        print '%d |' % r,
        for i in range(len(row)):
            print "%s  " % (row[i]),
        print '\b\b|\n',
        r -= 1
    print "   -----------------------------------"
    print "   -A---B---C---D---E---F---G---H---I-"

def transfer(srcfile, desfile=None):

    # read file
    file_input = open(srcfile)
    Head = file_input.read(9)
    MoveList = file_input.read().split('+')
    file_input.close()

    # init fen string 
    fen_start = initfen()
    state_start = fen2state(fen_start)

    # init chessborad state
    cstate = chessboradstate()
    cstate = fen2state(fen_start)

    # get fen string according to source data
    fenList = []
    fenList.append(fen_start)
    for item in MoveList:
        if len(item)==5:
            fenList[-1] += '\t' + item
            move(cstate, item)
            fen = state2fen(cstate)
            fenList.append(fen)
    fenList[-1] += '\tWIN!'

    # write fen string to file
    if desfile==None:
        file_write = srcfile + '.fen'
    else:
        file_write = desfile + '.fen'
    file_output = file(file_write, 'w')
    for item in fenList:
        file_output.write(item + '\n')
    file_output.close()


if __name__ == '__main__':

    '''
    # init state
    state = np.zeros([10, 9], np.string_)
    state[0] = ['r','n','b','a','k','a','b','n','r']
    state[1] = [' ',' ',' ',' ',' ',' ',' ',' ',' ']
    state[2] = [' ','c',' ',' ',' ',' ',' ','c',' ']
    state[3] = ['p',' ','p',' ','p',' ','p',' ','p']
    state[4] = [' ',' ',' ',' ',' ',' ',' ',' ',' ']
    state[5] = [' ',' ',' ',' ',' ',' ',' ',' ',' ']
    state[6] = ['P',' ','P',' ','P',' ','P',' ','P']
    state[7] = [' ','C',' ',' ',' ',' ',' ','C',' ']
    state[8] = [' ',' ',' ',' ',' ',' ',' ',' ',' ']
    state[9] = ['R','N','B','A','K','A','B','N','R']
    '''

    transfer('187') 
