#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import curses
import sys
from subprocess import Popen, PIPE


class TaskWarrior(object):
    def __init__(self):
        self.cmd = 'task'

    def get_ids(self):
        cmd = [self.cmd, 'next', 'rc.report.next.columns=id', 'rc.report.next.labels=id', 'limit:999999']
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        out = out.decode('utf8')
        ids = [int(id) for id in out.rstrip().split('\n')[2:-2] if id.isdigit()]
        ids.sort()
        return ids

    def info(self, task_id):
        return self._cmd(task_id, 'info')

    def done(self, task_id):
        return self._cmd(task_id, 'done')

    def delete(self, task_id):
        return self._cmd(task_id, 'delete', ['rc.confirmation=no'])

    def wait(self, task_id, till_when):
        return self._cmd(task_id, 'modify', ['wait:%s' % till_when])

    def add_tag(self, task_id, tag):
        return self._cmd(task_id, 'modify', ['+%s' % tag])

    def _cmd(self, task_id, cmd, extra=None):
        cmd = [self.cmd, str(task_id), cmd]
        if extra: cmd += extra
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return out.decode('utf8')


tw = TaskWarrior()

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)

start_id = int(sys.argv[1]) if len(sys.argv) > 1 else None


def main(screen):
    current_pos = 0
    if start_id:
        ids = tw.get_ids()
        if start_id in ids:
            current_pos = ids.index(start_id)

    while True:
        height, width = screen.getmaxyx()

        screen.clear()
        ids = tw.get_ids()
        if not ids:
            print('No Tasks in Warrior')
            exit()
        screen.addstr(1, int(width / 2), '[%i] %i / %i' % (ids[current_pos], current_pos + 1, len(ids)))

        screen.addstr(3, 1, '|' * round(current_pos / len(ids) * width))
        screen.addstr(5, 1, tw.info(ids[current_pos]))
        screen.addstr(height - 4, 0, '-' * width)
        screen.addstr(height - 2, 0, '-' * width)

        footer = [('q', 'quit'), ('d', 'done'), ('x', 'delete'), ('s', 'someday'), ('n', 'next'), ('m', 'mark')]
        for i in range(len(footer)):
            left = int(i * width / len(footer))
            screen.addstr(height - 3, left, '|')
            content = ': '.join(footer[i])
            screen.addstr(height - 3, left + int(width / len(footer) / 2) - int(len(content) / 2), content)
        screen.addstr(height - 3, width - 1, '|')
        screen.addstr(0, width - 1, '')
        screen.refresh()

        key = screen.getkey()

        if key in ['KEY_HOME', 'k']:
            current_pos = 0
        elif key in ['KEY_END', 'j']:
            current_pos = len(ids) - 1
        elif key in ['KEY_LEFT', 'h']:
            if current_pos > 0:
                current_pos -= 1
        elif key in ['KEY_RIGHT', 'l']:
            if current_pos < len(ids) - 1:
                current_pos += 1
        elif key in ['d']:
            tw.done(ids[current_pos])
        elif key in ['x']:
            tw.delete(ids[current_pos])
        elif key in ['s']:
            tw.wait(ids[current_pos], 'someday')
        elif key in ['n']:
            tw.add_tag(ids[current_pos], 'next')
        elif key in ['m']:
            tw.add_tag(ids[current_pos], 'marked')
        elif key in ['q']:
            break


curses.wrapper(main)
