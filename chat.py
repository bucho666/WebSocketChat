# -*- coding: utf-8 -*-
from server import WebSocketServer

# TODO 色選択
# TODO 発言の最後に時刻を表示
# TODO バックログを保存、ログインした際に送信する。
class ChatService(object):
  def __init__(self):
    RoomDB.add(Room(0))

  def enter(self, socket):
    new_user = User(socket)
    UserDB.add(socket, new_user)
    UserHandlers.set_handler(new_user, LoginHandler(new_user))

  def leave(self, socket):
    user = UserDB.find_by_socket(socket)
    UserHandlers.leave(user)
    UserHandlers.delete(user)
    UserDB.remove_by_socket(socket)

  def receve(self, socket, data):
    user = UserDB.find_by_socket(socket)
    UserHandlers.handle(user, data)

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
    UserHandlers.set_handler(self._user, ChatHandler(self._user))

  def leave(self):
    pass

  def _check_name(self, name):
    if self.use_invalidate_character(name):
      self._user.send(Message('名前に記号や空白は使用できません。', 'maroon'))
      return False
    if len(name) > self.NAME_MAX_LENGTH:
      self._user.send(Message('16文字(byte)以上の名前は使用できません。', 'maroon'))
      return False
    if UserDB.find_by_name(name):
      self._user.send(Message('既にその名前は使用されています。', 'maroon'))
      return False
    return True

  def use_invalidate_character(self, name):
    for ch in unicode(name, 'UTF-8'):
      if ch in self.INVALID_NAME_CHARACTER: return True
    return False

class ChatHandler(object):
  def __init__(self, user):
    self._user = user
    self._room = RoomDB.find_by_id(0)

  def enter(self):
    self._room.send_all(Message(self._user.name, "green").add(' が入室しました。', 'yellow'))
    self._user.send(Message('ログインしました。'))
    self._room.add_user(self._user)

  def leave(self):
    self._room.remove_user(self._user)
    self._room.send_all(Message(self._user.name, "green").add(' が退室しました。', 'olive'))

  def handle(self, message):
    self._room.send_all(Message(self._user.name + ": ", 'olive').add(message))

class RoomDB(object):
  _rooms = dict()

  @classmethod
  def add(cls, room):
    cls._rooms[room.object_id()] = room

  @classmethod
  def find_by_id(cls, room_id):
    return cls._rooms[room_id]

class Room(object):
  def __init__(self, object_id=0):
    self._object_id = object_id
    self._users = []

  def object_id(self):
    return self._object_id


  def add_user(self, user):
    self._users.append(user)

  def remove_user(self, user):
    self._users.remove(user)

  def send_all(self, message):
    for user in self._users:
      user.send(message)

class UserHandlers(object):
  _handler = dict()

  @classmethod
  def set_handler(cls, user, handler):
    cls._handler[user] = handler
    cls._handler[user].enter()

  @classmethod
  def delete(cls, user):
    del cls._handler[user]

  @classmethod
  def leave(cls, user):
    cls._handler[user].leave()

  @classmethod
  def handle(cls, user, data):
    cls._handler[user].handle(data)

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
