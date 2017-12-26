#!/usr/bin/env python3

import random
import numpy as np
from simulator import A, State, initial_state
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import Adam

def argmax(l, f):
    vals = [f(x) for x in l]
    return vals.index(max(vals))

class MDP:
    def __init__(self):
        self.discount_factor = 9/10

    def terminal(self, s):
        return s.to_list()[0,-1]

    def approx_q_value(self, s, a):
        return self.nn.predict(s.to_list()) [0,a]

    def approx_value(self, s):
        return np.max([self.approx_q_value(s, a) for a in range(A._TOTAL)])

    def approx_greedy(self, s):
        return argmax(range(A._TOTAL), lambda a: self.approx_q_value(s, a))

    def approx_epsilon_greedy(self, s, eps=0.5):
        if random.random() < eps:
            return round(A._TOTAL*random.random()-.5)
        return self.approx_greedy(s)

    def transition(self, s, a):
        s = s.action(a)
        if type(s) == int:
            return State(np.array([[0]*15+[1]])), s
        else:
            return s, 1

    def nn_Q_learn(self, num_layers, num_units, iters, lr=.001, eps=.5):
        self.nn = Sequential()
        self.nn.add(Dense(num_units, activation='relu', input_dim=16))
        for i in range(num_layers-1):
            self.nn.add(Dense(num_units, activation='relu'))
        self.nn.add(Dense(units=A._TOTAL, activation='linear'))
        self.nn.compile(loss='mse', optimizer=Adam())

        #print(self.nn)

        s = initial_state()
        for i in range(iters):
            a = self.approx_epsilon_greedy(s, eps)

            if self.terminal(s):
                self.nn.fit(s.to_list(), np.array([[0]*A._TOTAL]), epochs=1, verbose=1)
                s = initial_state()
            else:
                l = []
                for a in range(A._TOTAL):
                    s_prime, r = self.transition(s, a)
                    l += [r+self.discount_factor+self.approx_value(s_prime)]
                self.nn.fit(s.to_list(), np.array([l]), epochs=1, verbose=0)

                a = self.approx_epsilon_greedy(s, eps)
                s = self.transition(s, a) [0]
            #if i % iters/100 == 0:
            if i % int(iters/10) == 0:
                print("{}%".format(int(i/10)))

        self.nn.save('nn.h5')

def test_nnq_play(num_layers=2, num_units=100, eps=.5, iters=1000, num_play_episodes=10):
    game = MDP()
    game.nn_Q_learn(num_layers, num_units, iters=iters, eps=eps)

test_nnq_play()
