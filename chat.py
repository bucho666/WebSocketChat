# -*- coding: utf-8 -*-
from server import WebSocketServer

# TODO チャットハンドラ作成
# TODO 発言の最後に時刻を表示
# TODO バックログを保存、ログインした際に送信する。
class ChatService(object):
  def login(self, socket):
    new_user = User(socket)
    Users.add(socket, new_user)
    UserHandler.set_handler(new_user, LoginHandler(new_user))
    UserHandler.enter(new_user)

  def logout(self, socket):
    user = Users(socket)
    UserHandler.logout(user)
    UserHandler.delete(user)
    Users.remove(socket)

  def receve(self, socket, data):
    user = Users.find_by_socket(socket)
    UserHandler.handle(user, data)

class LoginHandler(object):
  INVALID_NAME_CHARACTER = u' 　!"#$%&\'()-=^~\\|@`[{;+:*]},<.>/?_'
  NAME_MAX_LENGTH = 16

  def __init__(self, user):
    self._user = user

  def enter(self):
    self._user.send(Message("名前を入力してください:", 'yellow'));

  def handle(self, message):
    name = message
    if not self._check_name(name):
      self.enter()
      return
    self._user.name = name
    self._user.send(Message(name, 'Yellow').add(' は有効な名前です'))

  def _check_name(self, name):
    if self.use_invalidate_character(name):
      self._user.send(Message('名前に記号や空白は使用できません。', 'maroon'))
      return False
    if len(name) > self.NAME_MAX_LENGTH:
      self._user.send(Message('16文字(byte)以上の名前は使用できません。', 'maroon'))
      return False
    if Users.find_by_name(name):
      self._user.send(Message('既にその名前は使用されています。', 'maroon'))
      return False
    return True

  def use_invalidate_character(self, name):
    for ch in unicode(name, "UTF-8"):
      if ch in self.INVALID_NAME_CHARACTER: return True
    return False

class UserHandler(object):
  _handler = dict()

  @classmethod
  def set_handler(cls, user, handler):
    cls._handler[user] = handler

  @classmethod
  def delete(cls, user):
    del cls._handler[user]

  @classmethod
  def enter(cls, user):
    cls._handler[user].enter()

  @classmethod
  def logout(cls, user):
    cls._handler[user].logout()

  @classmethod
  def handle(cls, user, data):
    cls._handler[user].handle(data)

class Users(object):
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
  def remove(cls, socket):
    del cls._users[socket]

  @classmethod
  def send_all(cls, message):
    for user in cls._users.values():
      user.send(message)

class User(object):
  def __init__(self, socket):
    self.name = ""
    self._socket = socket

  def send(self, message):
    self._socket.send(str(message))

class Message(object):
  def __init__(self, message, color='Silver'):
    self._messages = [(message, color)]

  def add(self, message, color='Silver'):
    self._messages.append((message, color))
    return self

  def __str__(self):
    return ''.join(['<font color=%s>%s</font>' % (color, message)\
        for (message, color) in self._messages])

if __name__ == '__main__':
  WebSocketServer(ChatService()).run(7000)
