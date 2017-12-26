#!/usr/bin/env python3
import random
import numpy as np
from keras.models import load_model

class A:
    BASIC_SYNTHESIS = 0
    BASIC_TOUCH = 1
    MASTERS_MEND = 2
    STEADY_HAND = 3
    INNER_QUIET = 4
    OBSERVE = 5
    STANDARD_TOUCH = 6
    GREAT_STRIDES = 7
    MASTERS_MEND_II = 8
    STANDARD_SYNTHESIS = 9
    TRICKS_OF_THE_TRADE = 10
    RAPID_SYNTHESIS = 11
    INGENUITY = 12
    RUMINATION = 13
    HASTY_TOUCH = 14
    MANIPULATION = 15
    WASTE_NOT = 16
    CAREFUL_SYNTHESIS = 17
    _TOTAL = 18

class Buffs:
    def __init__(self, s):
        self.steady_hand = s[0]
        self.inner_quiet = s[1]
        self.great_strides = s[2]
        self.manipulation = s[3]
        self.waste_not = s[4]
        self.begin = None

    def to_list(self):
        return [
            self.steady_hand,
            self.inner_quiet,
            self.great_strides,
            self.manipulation,
            self.waste_not,
        ]

    def transition(self):
        self.steady_hand = max(0, self.steady_hand-1)
        self.great_strides = max(0, self.great_strides-1)
        self.manipulation = max(0, self.manipulation-1)
        self.waste_not = max(0, self.waste_not-1)
        if type(self.begin) == int:
            if self.begin == A.STEADY_HAND:
                self.steady_hand = 5
            elif self.begin == A.INNER_QUIET:
                self.inner_quiet = 1
            elif self.begin == A.GREAT_STRIDES:
                self.great_strides = 3
            elif self.begin == A.MANIPULATION:
                self.manipulation = 3
            elif self.begin == A.WASTE_NOT:
                self.waste_not = 4
        self.begin = None

    def __str__(self):
        o = ''
        if self.steady_hand:
            o += 'steady hand: {}'.format(self.steady_hand)
        if self.inner_quiet:
            o += 'inner quiet: {}'.format(self.inner_quiet)
        if self.waste_not:
            o += 'waste not: {}'.format(self.waste_not)
        if self.great_strides:
            o += 'great strides: {}'.format(self.great_strides)
        if self.manipulation:
            o += 'manipulation: {}'.format(self.manipulation)
        return o

class State:
    C_FAILURE = -999999

    C_POOR = 0
    C_NORMAL = 1
    C_GOOD = 2
    C_EXCELLENT = 3

    def __init__(self, s):
        s = s[0,:]
        self.base_progress = s[0]*100
        self.control = s[1]*100
        self.max_durability = s[2]*100
        self._durability = s[3]*100
        self.difficulty = s[4]*100
        self._progress = s[5]*100
        self.quality = s[6]*100
        self.max_cp = s[7]*100
        self._cp = s[8]*100
        self.condition = s[9]
        self.buffs = Buffs(s[10:-1])

    def to_list(self):
        return np.array([[
            self.base_progress/100,
            self.control/100,
            self.max_durability/100,
            self._durability/100,
            self.difficulty/100,
            self._progress/100,
            self.quality/100,
            self.max_cp/100,
            self._cp/100,
            self.condition,
        ] + self.buffs.to_list() + [0]])

    @property
    def durability(self):
        return self._durability
    @durability.setter
    def durability(self, value):
        self._durability = min(max(0,value),self.max_durability)

    @property
    def progress(self):
        return self._progress
    @progress.setter
    def progress(self, value):
        self._progress = min(max(0,value),self.difficulty)

    @property
    def cp(self):
        return self._cp
    @cp.setter
    def cp(self, value):
        self._cp = min(max(0,value),self.max_cp)

    def good_plus(self):
        return self.condition >= self.C_GOOD

    def pay(self, cp=0, durability=10, touch=False):
        if self.cp < cp:
            return self.C_FAILURE
        if self.progress >= self.difficulty:
            return int(self.quality)
        if self.durability <= durability:
            return self.C_FAILURE
        self.cp -= cp
        self.durability -= durability


        if self.buffs.inner_quiet and touch:
            self.buffs.inner_quiet += 1
        if self.buffs.waste_not:
            self.durability += durability/2
        if self.buffs.manipulation:
            self.durability += 10

        self.buffs.transition()

        if self.condition == self.C_EXCELLENT:
            self.condition = self.C_POOR
        elif self.condition == self.C_GOOD or self.condition == self.C_POOR:
            self.condition = self.C_NORMAL
        else:
            if random.random() < .01:
                self.condition = self.C_EXCELLENT
            elif random.random() < .23:
                self.condition = self.C_GOOD
        return self

    @property
    def base_quality(self):
        # http://forum.square-enix.com/ffxiv/threads/93108-Theory-Crafting-The-formula-for-Quality-increase-%28control%29-and-a-TOOL-%21
        # https://www.reddit.com/r/ffxiv/comments/1n7tlf/indepth_crafting_mechanics_part_deux/
        q = 34.2792 + 0.351 * self.control + 0.0000336 * self.control**2
        if self.buffs.inner_quiet:
            q += .2 * q * (self.buffs.inner_quiet - 1)
        return round(q)

    @property
    def p_mod(self):
        if self.buffs.steady_hand:
            return .2
        return 0

    @property
    def q_mod(self):
        v = 1
        if self.condition == self.C_POOR:
            v -= .5
        elif self.condition == self.C_GOOD:
            v += .5
        elif self.condition == self.C_EXCELLENT:
            v += 3
        if self.buffs.great_strides:
            self.buffs.great_strides = 0
            v += 2
        return v

    def inner_quiet(self):
        if self.buffs.inner_quiet and self.buffs.inner_quiet < 11:
            self.buffs.inner_quiet += 1

    def action(self, a):
        s = State(self.to_list())
        a = int(a)

        if a == A.BASIC_SYNTHESIS:
            if random.random() < .9+s.p_mod:
                s.progress += s.base_progress
            return s.pay()
        elif a == A.BASIC_TOUCH:
            if random.random() < .7+s.p_mod:
                s.quality += s.base_quality*s.q_mod
                s.inner_quiet()
            return s.pay(18)
        elif a == A.MASTERS_MEND:
            s.durability += 30
            return s.pay(92, durability=0)
        elif a == A.STEADY_HAND:
            s.buffs.begin = a
            return s.pay(22, 0)
        elif a == A.INNER_QUIET:
            s.buffs.begin = a
            return s.pay(18, 0)
        elif a == A.OBSERVE:
            return s.pay(7, 0)
        elif a == A.STANDARD_TOUCH:
            if random.random() < .8+s.p_mod:
                s.quality += 1.25*s.base_quality*s.q_mod
                s.inner_quiet()
            return s.pay(32)
        elif a == A.GREAT_STRIDES:
            s.buffs.begin = a
            return s.pay(32, 0)
        elif a == A.MASTERS_MEND_II:
            s.durability += 60
            return s.pay(160, durability=0)
        elif a == A.STANDARD_SYNTHESIS:
            if random.random() < .9+s.p_mod:
                s.progress += 1.5*s.base_progress
            return s.pay(15)
        elif a == A.TRICKS_OF_THE_TRADE:
            if not self.good_plus():
                return self.C_FAILURE
            s.cp += 20
            return s.pay(0, 0)
        elif a == A.RAPID_SYNTHESIS:
            if random.random() < .5+s.p_mod:
                s.progress += 2.5*s.base_progress
            return s.pay()
        elif a == A.INGENUITY:
            return self.C_FAILURE
        elif a == A.RUMINATION:
            if not s.buffs.inner_quiet:
                return self.C_FAILURE
            v = 0
            iq = s.buffs.inner_quiet
            if iq == 2: v = 15
            elif iq == 3: v = 24
            elif iq == 4: v = 32
            elif iq == 5: v = 39
            elif iq == 6: v = 45
            elif iq == 7: v = 50
            elif iq == 8: v = 54
            elif iq == 9: v = 57
            elif iq == 10: v = 59
            elif iq == 11: v = 60
            s.buffs.inner_quiet = 0
            s.cp += v
            return s.pay(0, 0)
        elif a == A.HASTY_TOUCH:
            if random.random() < .5+s.p_mod:
                s.quality += s.base_quality*s.q_mod
                s.inner_quiet()
            return s.pay()
        elif a == A.MANIPULATION:
            s.buffs.begin = a
            return s.pay(88, 0)
        elif a == A.WASTE_NOT:
            s.buffs.begin = a
            return s.pay(56, 0)
        elif a == A.CAREFUL_SYNTHESIS:
            s.progress += .9*s.base_progress
            return s.pay()

    def __repr__(self):
        return 'Progress: {}/{}, Quality: {}, Durability: {}/{}, CP: {}/{}, Condition: {}, Buffs: {}'.format(self.progress, self.difficulty, self.quality, self.durability, self.max_durability, self.cp, self.max_cp, self.condition, str(self.buffs))

def initial_state(base_progress=20, control=105, max_durability=70, difficulty=100, max_cp=215):
    s = np.array([[
        base_progress/100,
        control/100,
        max_durability/100,
        max_durability/100,
        difficulty/100,
        0,
        0,
        max_cp/100,
        max_cp/100,
        State.C_NORMAL,
        0, 0, 0, 0, 0,
        0,
    ]])
    return State(s)

if __name__ == '__main__':
    nn = load_model('nn.h5')
    while True:
        s = initial_state()
        while True:
            print(s)
            o = list(nn.predict(s.to_list())[0,:])
            print(o)
            print('prediction: {}'.format(o.index(max(o))))
            while True:
                action = input('Action? ')
                try:
                    int(action)
                    break
                except:
                    print('Invalid action.')
            s = s.action(action)
            if type(s) == int:
                print('GAME ENDED, REWARD {}'.format(s))
                break

