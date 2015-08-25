#!/usr/bin/env python
# -*- encoding: utf-8 -*-
__author__ = 'mac'

import SSH_CONNECT
import LOAD_SLAVES
import threading
import time


class MASTER_CENTER(object):
    def __init__(self):
        self.slavelist = None
        self.infolist = {}
        self.sshclients = []
        self.isfinish = True
        self.forcestoplistening = False

    def _getsshclientstate(self, sshclient, ip, usr, pwd):
        # print(threading.currentThread())
        sshclient.connect(ip, usr, pwd)
        self.infolist[threading.currentThread().name] = sshclient.info

    def prepare(self, path):
        self.slavelist = LOAD_SLAVES.LOAD_SLAVES().load(path)

        if len(self.slavelist) == 0:
            print('there is no slaves in the list')
            exit(0)

        for index in xrange(len(self.slavelist)):
            self.sshclients.append(SSH_CONNECT.SSH_CONNECT())
            self.infolist[self.slavelist[index]['machine']] = ''

        for index in xrange(len(self.slavelist)):
            sshthread = threading.Thread(target=self._getsshclientstate,
                                         args=(self.sshclients[index],
                                               self.slavelist[index]['ip'],
                                               self.slavelist[index]['user'],
                                               self.slavelist[index]['password']),
                                         name=self.slavelist[index]['machine'])
            sshthread.start()
            # sshthread.join()

    def _runcommand(self, clientindex, cmd, sleep):
        # print(sshclient.info)
        if cmd == '' or (not self.sshclients[clientindex].info['done']):
            print('empty command or sshclient is working')
            return
        print(cmd)
        self.sshclients[clientindex].command(cmd, sleep)

    def run(self, commandlist):
        for index in xrange(len(self.sshclients)):
            sshthread = threading.Thread(target=self._runcommand,
                                         args=(index,
                                               commandlist[index],
                                               1),
                                         name=self.slavelist[index]['machine'])
            sshthread.start()
            # sshthread.join()

    def listening(self, sleep):
        self.isfinish = False
        while (not self.isfinish) and (not self.forcestoplistening):
            time.sleep(sleep)
            self.isfinish = True
            for index in xrange(len(self.sshclients)):
                self.infolist[self.slavelist[index]['machine']] = self.sshclients[index].info
                self.isfinish = self.isfinish and self.sshclients[index].info['done']

            print(self.infolist)

            # while not self.isfinish:
            #     time.sleep(0.5)
            #     print(self.infolist)

    def reconnect(self, clientindex):
        for index in clientindex:
            sshthread = threading.Thread(target=self._getsshclientstate,
                                         args=(self.sshclients[index],
                                               self.slavelist[index]['ip'],
                                               self.slavelist[index]['user'],
                                               self.slavelist[index]['password']),
                                         name=self.slavelist[index]['machine'])
            sshthread.start()

    def shutdown(self, clientindex):
        for index in clientindex:
            self.sshclients[index].disconnect()


if __name__ == '__main__':
    testclass = MASTER_CENTER()
    testclass.prepare('./slave_list.txt')
    time.sleep(3)
    cmdlist = [
        r'/opt/local/bin/opendcp_j2k -i /Volumes/GoKu/LAOPAO/09_FINAL\ OUT/150822_LAOPAO_EN_TEXT_DCI/R2_0-83996/2048x858 -o /Volumes/GoKu/test_copy/andyJ2C -s 1 -d 1000',
        r'/opt/local/bin/opendcp_j2k -i /Volumes/GoKu/LAOPAO/09_FINAL\ OUT/150822_LAOPAO_EN_TEXT_DCI/R2_0-83996/2048x858 -o /Volumes/GoKu/test_copy/andyJ2C -s 1001 -d 2000'
        ]
    testclass.run(cmdlist)
    listening = threading.Thread(target=testclass.listening,
                                 args=(1,),
                                 name='listening')
    listening.start()
    # testclass.listening(1)
    # time.sleep(5)
    # testclass.forcestoplistening = True
    # time.sleep(5)
    # testclass.forcestoplistening = False
    # listening2 = threading.Thread(target=testclass.listening,
    #                              args=(1,),
    #                              name='listening2')
    # listening2.start()
    time.sleep(5)
    testclass.shutdown(range(2))
    print(testclass.infolist)
