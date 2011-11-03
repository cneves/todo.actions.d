#!/usr/bin/env python
# encoding: utf-8

import os
import subprocess

class TodoLine (object):
  def __init__ (self, line):
    self.line = line
    self.todonr = -1
    self.pri = ''
    line = line.strip().split(' ')
    if len(line) < 2:
      self.done=False
      return
    self.linenr = int(line[0])
    self.done = line[1] == 'x'
    if self.done:
      self.donedate = line[2]
      self.args = line[3:]
    else:
      self.args = line[1:]
    msg = []
    context = []
    for e in self.args:
      if e.startswith('[') and e.endswith(']') and e[1:-1].isdigit():
        self.todonr = int(e[1:-1])
      elif e.startswith('(') and e.endswith(')') and len(msg) == 0:
        self.pri = e[1:-1]
      elif e.startswith('@'):
        context.append(e[1:])
      else:
        msg.append(e)
    self.msg = ' '.join(msg)
    self.context = '.'.join(context)

  def __cmp__ (self, other):
    if isinstance(other, TodoLine):
      a = cmp(self.context, other.context)
      if a == 0:
        a = cmp(self.todonr, other.todonr)
      return a
    else:
      return cmp(self.todonr, other)

  def __unicode__ (self):
    return '%s.%d %s' % (self.context, self.todonr, self.msg)

  def __str__ (self):
    return str(self.__unicode__())

def listidx (line, lsall=False):
  line.append('\[[[:digit:]]*\]')
  V = os.environ['TODOTXT_VERBOSE']
  os.environ['TODOTXT_VERBOSE'] = '0'
  stdout = call(lsall and 'listall' or 'list', line, ['-p'])
  os.environ['TODOTXT_VERBOSE'] = V
  lines = filter(lambda x: x.todonr>=0, [TodoLine(x) for x in stdout.split('\n')])
  return lines

def findnextidx(line):
  idx = [x.todonr for x in listidx([y for y in line if y.startswith('@')], lsall=True)]
  if len(idx) == 0:
    return 1
  return max(idx) + 1

def call(cmdname, args, opts=[]):
  cmd = [os.environ['TODO_FULL_SH']]
  cmd += opts
  cmd += ['command', cmdname]
  cmd += args
  shcall = subprocess.Popen(cmd, stdout=subprocess.PIPE)
  stdout, x = shcall.communicate()
  return stdout

def gettodoline(linenr):
  f = open(os.environ['TODO_FILE'], 'r')
  [f.readline() for i in range(linenr-1)]
  return TodoLine("%d %s" % (linenr, f.readline().strip()))
