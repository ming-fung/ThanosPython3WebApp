#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 让服务器检测到代码修改后自动重新加载

import os, sys, time, subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def log(s):
    print('[Monitor] %s' % s)

class MyFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, fn):
        super(MyFileSystemEventHandler, self).__init__()
        self.restart = fn

    def on_any_event(self, event):
        # 利用watchdog接收文件变化的通知，如果是.py文件，就自动重启目标进程（这里主要针对wsgiapp.py）
        if event.src_path.endswith('.py'):
            log('Python source file changed: %s' % event.src_path)
            self.restart()

command = ['echo', 'ok']
process = None

def kill_process():
    global process
    if process:
        log('Kill process [%s]...' % process.pid)
        process.kill()
        process.wait()
        log('Process ended with code %s.' % process.returncode)
        process = None

def start_process():
    global process, command
    log('Start process %s...' % ' '.join(command))
    # 利用Python自带的subprocess实现进程的启动和终止，并把输入输出重定向到当前进程的输入输出中
    process = subprocess.Popen(command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

def restart_process():
    kill_process()
    start_process()

def start_watch(path, callback):
    observer = Observer()
    # 安排回调(或代理)对象给watchdog的监听器，当监听到事件时触发回调对象中的回调(代理、协议)方法
    observer.schedule(MyFileSystemEventHandler(restart_process), path, recursive=True)
    observer.start()
    log('Watching directory %s...' % path)
    start_process()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    argv = sys.argv[1:]
    if not argv:
        print('Usage: ./pymonitor your-script.py')
        exit(0)
    if argv[0] != 'python3':
        argv.insert(0, 'python3')
    command = argv
    path = os.path.abspath('.')
    start_watch(path, None)

# 此脚本使用方法如下，即用python3运行两个py脚本，第一个即当前脚本，用于获取进程、监听事件、重启目标进程；第二个是一个可为我们服务重启的一个进程脚本
# Django 中用wsgiapp.py 对应用进行重启，这里使用app.py
# $ python3 pymonitor.py app.py
