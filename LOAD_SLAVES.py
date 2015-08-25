#!/usr/bin/env python
# -*- encoding: utf-8 -*-
__author__ = ''

import os
import sys
import copy

APP_PATH = os.path.realpath(sys.path[0])


class LOAD_SLAVES(object):
    def __init__(self):
        self.slaves = []

    def load(self, path):
        with open(path, 'r') as slavefile:
            slavefile_readlines = slavefile.readlines()
            for index, line in enumerate(slavefile_readlines):
                if len(line) == 0:
                    continue
                if line[0] == '#':
                    continue

                if 'machine' in line:
                    tempmachine = {}
                    tempmachine['machine'] = line.split('=')[-1].lstrip().rstrip()
                    tempmachine['ip'] = slavefile_readlines[index + 1].split('=')[-1].lstrip().rstrip()
                    tempmachine['user'] = slavefile_readlines[index + 2].split('=')[-1].lstrip().rstrip()
                    tempmachine['password'] = slavefile_readlines[index + 3].split('=')[-1].lstrip().rstrip()
                    self.slaves.append(copy.deepcopy(tempmachine))

        return self.slaves


if __name__ == '__main__':
    testclass = LOAD_SLAVES()
    testclass.load('./slave_list.txt')
    print(testclass.slaves)
