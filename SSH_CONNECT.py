#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'Andy Guo'

import paramiko
import select
import time
import threading


class SSH_CONNECT(object):
    def __init__(self):
        self.info = {'thread': 0,
                     'ready': False,
                     'software': False,
                     'sshinfo': '',
                     'done': True,
                     'displayinfo': '',
                     'taskid': -1,
                     'jobid':-1,
                     'lastinfo': '',
                     'machine':''}
        self.ssh = paramiko.SSHClient()

    def checksoftware(self, softwarepath):
        cmd = 'test -e ' + softwarepath + '&& echo "True" || echo "False"'
        self.command(cmd, -1, -1, 0)
        # print(state)
        if self.info['sshinfo'] == 'True':
            self.info['software'] = True
        else:
            self.info['software'] = False

    def _getCPUcores(self):
        cmd = 'uname'
        self.command(cmd, -1, -1, 0)
        if self.info['sshinfo'].lower() == 'darwin':
            cmd = 'sysctl -n hw.ncpu'
            self.command(cmd, -1, -1, 0)
            self.info['thread'] = int(self.info['sshinfo'])
        elif self.info['sshinfo'].lower() == 'linux':
            cmd = 'nproc'
            self.command(cmd, -1, -1, 0)
            self.info['thread'] = int(self.info['sshinfo'])

    def connect(self, machine, ip, usr, pwd):
        try:
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(ip,
                             username=usr,
                             password=pwd)
            self.info['ready'] = True
            self.info['machine'] = machine
            self.checksoftware('/opt/local/bin/opendcp_j2k')
            self._getCPUcores()
            self.info['displayinfo'] = 'connected'
        except:
            print('%s somthing error in ssh connect' % machine)
            self.info['done'] = True
            self.info['displayinfo'] = 'offline'
            self.info['machine'] = machine
            self.ssh.close()
            return 1
        finally:
            return 0

    def command(self, cmd, jobid, taskid, sleep):
        try:
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            self.info['done'] = False
            self.info['taskid'] = taskid
            self.info['jobid'] = jobid
            while not stdout.channel.exit_status_ready():
                # Only print data if there is data to read in the channel
                time.sleep(sleep)
                if stdout.channel.recv_ready():
                    rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
                    if len(rl) > 0:
                        # Print data from stdout
                        self.info['sshinfo'] = stdout.channel.recv(4096).rstrip()
                        if len(self.info['sshinfo']) > 0:
                            self.info['displayinfo'] = self.info['sshinfo'].rstrip().splitlines()[-1].lstrip()
            self.info['done'] = True
            if len(self.info['sshinfo']) > 0:
                self.info['lastinfo'] = self.info['sshinfo'].rstrip().splitlines()[-1].lstrip()
            # self.info['taskid'] = -1
            if not self.info['displayinfo'] == 'disconnected':
                self.info['displayinfo'] = 'idle'
        except:
            self.info['ready'] = False
            self.info['done'] = True
            self.info['displayinfo'] = 'offline'

    def disconnect(self):
        try:
            self.ssh.close()
            self.info['displayinfo'] = 'disconnected'
        except:
            print('something erro in ssh disconnect')


if __name__ == '__main__':
    testclass = SSH_CONNECT()
    testclass.connect('192.168.9.61', 'mac', 'tgyc')
    # mythreading = threading.Thread(target=testclass.command,
    #                                args=(
    #                                    '/opt/bin/opendcp/opendcp_j2k -i /Volumes/GoKu/LAOPAO/09_FINAL\ OUT/150822_LAOPAO_EN_TEXT_DCI/R2_0-83996/20048x858 -o /Volumes/GoKu/test_copy/andyJ2C -s 1 -d 1000', 1,)
    #                                )

    # testclass.command('/opt/bin/opendcp/opendcp_j2k -i /Volumes/GoKu/LAOPAO/09_FINAL\ OUT/150822_LAOPAO_EN_TEXT_DCI/R2_0-83996/20048x858 -o /Volumes/GoKu/test_copy/andyJ2C -s 1 -d 1000' )
    testclass.command('ping -c 10 192.168.9.1')
    testclass.disconnect()
    print(testclass.info)



    # stdin, stdout, stderr = self.ssh.exec_command(cmd)
    #
    # while not stdout.channel.exit_status_ready():
    #     # Only print data if there is data to read in the channel
    #     time.sleep(1)
    #     if stdout.channel.recv_ready():
    #         rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
    #         if len(rl) > 0:
    #             # Print data from stdout
    #             print stdout.channel.recv(1024)
