# -*- coding: utf-8 -*-
from user import User
from user import UserDB
from room import Room
from room import RoomDB
from server import WebSocketServer

# TODO 名前に色を設定
# TODO 発言の最後に時刻を表示
# TODO バックログを保存、ログインした際に送信する。
class ChatService(object):
  def __init__(self):
    RoomDB.add(Room(0))

  def enter(self, socket):
    new_user = User(socket)
    UserDB.add(socket, new_user)
    UserHandlers.set_handler(new_user, LoginHandler(new_user))
    UserDB.flush_send_buffer()

  def leave(self, socket):
    user = UserDB.find_by_socket(socket)
    UserHandlers.leave(user)
    UserHandlers.delete(user)
    UserDB.remove_by_socket(socket)
    UserDB.flush_send_buffer()

  def receve(self, socket, data):
    user = UserDB.find_by_socket(socket)
    user.send(Message(data + '\n', 'yellow'))
    UserHandlers.handle(user, data)
    UserDB.flush_send_buffer()

class LoginHandler(object):
  INVALID_NAME_CHARACTER = u' 　!"#$%&\'()-=^~\\|@`[{;+:*]},<.>/?_'
  NAME_MAX_LENGTH = 16

  def __init__(self, user):
    self._user = user

  def enter(self):
    self._user.send(Message("名前を入力してください: ", 'olive'));

  def handle(self, message):
    name = message
    if not self._check_name(name):
      self.enter()
      return
    self._user.name = name
    UserHandlers.set_handler(self._user, ChoiceColorHandler(self._user))

  def leave(self):
    pass

  def _check_name(self, name):
    if self.use_invalidate_character(name):
      self._user.send(Message('名前に記号や空白は使用できません。\n', 'maroon'))
      return False
    if len(name) > self.NAME_MAX_LENGTH:
      self._user.send(Message('16文字(byte)以上の名前は使用できません。\n', 'maroon'))
      return False
    if UserDB.find_by_name(name):
      self._user.send(Message('既にその名前は使用されています。\n', 'maroon'))
      return False
    return True

  def use_invalidate_character(self, name):
    for ch in unicode(name, 'UTF-8'):
      if ch in self.INVALID_NAME_CHARACTER: return True
    return False

class ChoiceColorHandler(object):
  _colors = (
      'red', 'maroon',
      'yellow', 'olive',
      'lime', 'green',
      'aqua', 'teal',
      'blue', 'navy',
      'fuchsia', 'purple')

  def __init__(self, user):
    self._user = user

  def enter(self):
    self._user.send(Message("名前の色を選択してください:\n", 'olive'));
    for num, color in enumerate(self._colors):
      color_tag = '%s ' % color
      self._user.send(Message(color_tag.ljust(8), color))
      if num % 4 == 3:
          self._user.send(Message('\n'))

  def leave(self):
    pass

  def handle(self, message):
    choose_color = message.lower()
    if not choose_color in self._colors:
      self._user.send(Message('リストの中の色を入力してください。\n', 'maroon'))
      self.enter()
      return
    self._user.send('OK\n')
    UserHandlers.set_handler(self._user, ChatHandler(self._user))

class ChatHandler(object):
  def __init__(self, user):
    self._user = user
    self._room = RoomDB.find_by_id(0)

  def enter(self):
    self._room.send_all(Message(self._user.name, "green").add(' が入室しました。\n', 'olive'))
    self._user.send(Message('ログインしました。\n'))
    self._room.add_user(self._user)

  def leave(self):
    self._room.remove_user(self._user)
    self._room.send_all(Message(self._user.name, "green").add(' が退室しました。\n', 'olive'))

  def handle(self, message):
    self._room.send_all(Message(self._user.name + ": ", 'olive').add(message + '\n'))

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

class Message(object):
  def __init__(self, message, color='Silver'):
    self._messages = [(message, color)]

  def add(self, message, color='Silver'):
    self._messages.append((message, color))
    return self

  def __str__(self):
    string = ''.join(['<font color=%s>%s</font>' % (color, message.replace(' ', '&nbsp;'))\
        for (message, color) in self._messages])
    return string.replace('\n', '<br>')

if __name__ == '__main__':
  WebSocketServer(ChatService()).run(7000)
