#!/usr/bin/python3
#-*-coding:utf-8-*-
#$File: value_dataset.py
#$Date: Fri May 27 12:03:31 2016
#$Author: Like Ma <milkpku[at]gmail[dot]com>

import tensorflow as tf

from util.tools import batch_flatten

from config import config

class Reactor(object):
    def __init__(self, policy_model, load_path):
        self.player = policy_model
        self.sess = tf.Session()
        saver = tf.train.Saver()
        saver.restore(self.sess, load_path)

    def react(self, states, move):
        '''
        return the final states and reward
        '''
        # flip the state
        enemy_pos, self_pos = change_state(states, move)
        self_pos = self_pos[:,:,::-1,:]
        enemy_pos = enemy_pos[:,:,::-1,:]
        self_move = valid_move([self_pos, enemy_pos])

        # eval reward
        enemy_win = batch_flatten(self_move).sum(axis=1)==0
        if_terminated = np.copy(enemy_win)
        reward = np.copy(enemy_win)

        # choose react
        mask = np.logical_not(if_terminated)
        input_data = [self_pos[mask], self_move[mask], enemy_pos[mask]]
        input_dict = {}
        for var, data in zip(self.player.inputs, input_data):
            input_dict[var] = data
        pred = self.sess.run(self.player.pred, feed_dict=input_dict)

        # change state
        current_move = pred
        next_self_pos, next_enemy_pos = change_state([input_data[0], input_data[2]], current_move)
        # switch palyer
        next_mask_self_pos = next_enemy_pos[:, :, ::-1, :]
        next_mask_enemy_pos = next_self_pos[:, :, ::-1, :]

        # eval reward
        next_mask_move = valid_move([next_mask_self_pos, next_mask_enemy_pos])
        self_win = batch_flatten(next_mask_move).sum(axis=1)==0
        if_terminated[mask] = self_win
        reward[mask] = -self_win

        #return reward, next_state, if_terminated, next_move
        next_self_pos = np.zeros(self_pos.shape)
        next_self_pos[mask] = next_mask_self_pos
        next_enemy_pos = np.zeros(enemy_pos.shape)
        next_enemy_pos[mask] = next_mask_enemy_pos
        next_self_move = np.zeros(self_move.shape)
        next_self_move[mask] = next_mask_move

        return reward, [next_self_pos, next_enemy_pos], if_terminated, next_self_move

def valid_move(states):
    '''
    states = [self_pos, enemy_pos]
    self_pos.shape = [None, 9, 10, 32]
    enemy_pos.shape = [None, 9, 10, 32]

    return valid_moves.shape = [None, 9, 10, 32]
    '''
    return states[1]

def change_state(states, move):
    return states
