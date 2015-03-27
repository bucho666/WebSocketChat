# -*- coding: utf-8 -*-
from server import WebSocketServer

class User(object):
  def __init__(self, socket):
    self._socket = socket

class Users(object):
  def __init__(self):
    self._users = dict()

  def add(self, socket, user):
    self._users[socket] = user

  def remove(self, socket):
    del self._users[socket]

  def send_all(self, message):
    for socket in self._users.keys():
      socket.send(message)

class ChatService(object):
  def __init__(self):
    self._users = Users()

  def login(self, socket):
    self._users.add(socket, User(socket))

  def logout(self, socket):
    self._users.remove(socket)

  def receve(self, socket, data):
    self._users.send_all(data)

if __name__ == '__main__':
  WebSocketServer(ChatService()).run(7000)
