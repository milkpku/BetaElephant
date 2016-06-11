#!/usr/bin/python3
#-*-coding:utf-8-*-

import numpy as np
import pickle

def tensor2fen(tensor_frd, tensor_emy):
    '''
    tensor_frd, tensor_emy: ndarray [9,10,16]
    return fen string
    '''
    return state2fen(tensor2state(tensor_frd, tensor_emy))

def tensor2state(tensor_frd, tensor_emy):
    '''
    transform tensor 2 state
    tensor_frd, tensor_emy ndarray [9,10,16]
    return state ndarray [10,9]
    '''
    assert tensor_frd.shape == tensor_emy.shape
    state = np.zeros((10,9), dtype=np.str)
    chessfrdplayer = 'KAABBNNRRCCPPPPP'
    chessemyplayer = 'kaabbnnrrccppppp'
    for i in range(tensor_frd.shape[0]):
        for j in range(tensor_frd.shape[1]):
            if ~(tensor_frd[i][j] == 0).all():
                layer = np.argmax(tensor_frd[i][j])
                state[9-j][i] = chessfrdplayer[layer]
            elif ~(tensor_emy[i][j] == 0).all():
                layer = np.argmax(tensor_emy[i][j])
                state[9-j][i] = chessemyplayer[layer]
            else:
                state[9-j][i] = ' '
    return state

def state2fen(state):
    '''
    transfer the chessboard to fen string
    state: state of the current chessboard
    turn: which player to play
    round: count of round
    return: fen string
    '''
    fen = ''
    [m,n] = state.shape
    for i in range(m):
        zcnt = 0
        for j in range(n):
            if state[i][j] != ' ':
                if zcnt != 0:
                    fen += str(zcnt)
                    zcnt = 0
                fen += state[i][j]
            else:
                zcnt += 1
        if zcnt != 0:
            fen += str(zcnt)
            zcnt = 0
        fen += '/'
    fen = fen[:-1]
    fen += ' b'
    fen += ' - - 0 1'
    return fen


def visualstate(state):
    '''
    visual the chessborad
    '''
    print("   -----------------------------------")
    r = 9
    for row in state:
        print('%d | ' % r, end='')
        for i in range(len(row)):
            print("%s   " % (row[i]), end='')
        print('\b\b|\n', end='')
        r -= 1
    print("   -----------------------------------")
    print("   -A---B---C---D---E---F---G---H---I-")

if __name__ == '__main__':
    file = '../pred.tensor'
    fh = open(file, 'rb')
    data, label, pred = pickle.load(fh)
     
    state = tensor2state(data[0][1],data[1][1])
    fen = state2fen(state)
    from IPython import embed;embed()
    print(state)
    visualstate(state)
    print(fen)
    
    frdpos = data[0]
    emypos = data[1]
    fenlist = []
    for k in range(frdpos.shape[0]):
        fenlist.append(tensor2fen(frdpos[k],emypos[k]))
    #print(fenlist)
    label = tensor2fen(label[1],label[1])
    #print(label)
