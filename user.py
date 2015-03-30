# -*- coding: utf-8 -*-
from server import WebSocketServer

class UserDB(object):
  _users = dict()

  @classmethod
  def add(cls, socket, user):
    cls._users[socket] = user

  @classmethod
  def find_by_socket(cls, socket):
    return cls._users[socket]

  @classmethod
  def find_by_name(cls, name):
    matchs = [user for user in cls._users.values() if user.name() == name]
    if not matchs: return None
    return matchs[0]

  @classmethod
  def remove_by_socket(cls, socket):
    del cls._users[socket]

  @classmethod
  def flush_send_buffer(cls):
    for user in cls._users.values():
        user.flush()

class User(object):
  def __init__(self, socket, prompt):
    self._name = UserName('', 'silver')
    self._prompt = prompt
    self._socket = socket
    self._buffer = []

  def rename(self, name):
    self._name = UserName(name, self._name.color())

  def change_name_color(self, new_color):
    self._name = UserName(str(self._name), new_color)

  def name(self):
    return str(self._name)

  def name_color(self):
    return self._name.color()

  def send(self, message):
    self._buffer.append(str(message))

  def flush(self):
    if not self._buffer: return
    self.send(self._prompt)
    self._socket.send('<br>' + ''.join(self._buffer))
    self._buffer = []

class UserName(object):
  _INVALID_NAME_CHARACTER = u' 　!"#$%&\'()-=^~\\|@`[{;+:*]},<.>/?_'
  _NAME_MAX_LENGTH = 16

  def __init__(self, name, color='silver'):
    self._name = name
    self._color = color

  def __str__(self):
    return self._name

  def is_too_long(self):
    return len(self._name) > self._NAME_MAX_LENGTH

  def max_length(self):
    return self._NAME_MAX_LENGTH

  def using_invalid_character(self):
    for ch in unicode(self._name, 'UTF-8'):
      if ch in self._INVALID_NAME_CHARACTER: return True
    return False

  def color(self):
    return self._color
