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
    matchs = [user for user in cls._users.values() if user.name == name]
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
  def __init__(self, socket):
    self.name = ''
    self._socket = socket
    self._buffer = []

  def send(self, message):
    self._buffer.append(str(message))

  def flush(self):
    if not self._buffer: return
    self._socket.send(''.join(self._buffer))
    self._buffer = []
