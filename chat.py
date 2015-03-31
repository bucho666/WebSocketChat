# -*- coding: utf-8 -*-
from user import User
from user import UserDB
from user import UserName
from room import Room
from room import RoomDB
from server import WebSocketServer
from datetime import datetime

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

class ChatService(object):
  DEFAULT_PROMPT = Message('> ', 'white')
  def __init__(self):
    RoomDB.add(Room(0))

  def enter(self, socket):
    new_user = User(socket, self.DEFAULT_PROMPT)
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
    UserHandlers.handle(user, data)
    UserDB.flush_send_buffer()

class LoginHandler(object):
  INVALID_NAME_CHARACTER = u' 　!"#$%&\'()-=^~\\|@`[{;+:*]},<.>/?_'
  NAME_MAX_LENGTH = 16

  def __init__(self, user):
    self._user = user

  def enter(self):
    self._user.send(Message("名前を入力してください\n", 'white'));

  def handle(self, message):
    name = message
    if not self._check_name(name):
      self.enter()
      return
    self._user.rename(name)
    UserHandlers.set_handler(self._user, ChoiceColorHandler(self._user))

  def leave(self):
    pass

  def _check_name(self, name):
    user_name = UserName(name)
    if user_name.using_invalid_character():
      self._user.send(Message('名前に記号や空白は使用できません。\n', 'maroon'))
      return False
    if user_name.is_too_long():
      self._user.send(Message('%d文字(byte)以上の名前は使用できません。\n' % user_name.max_length(), 'maroon'))
      return False
    if UserDB.find_by_name(name):
      self._user.send(Message('既にその名前は使用されています。\n', 'maroon'))
      return False
    return True

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
    self._user.send(Message("名前の色を選択してください\n", 'white'));
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
    self._user.change_name_color(choose_color)
    UserHandlers.set_handler(self._user, ChatHandler(self._user))

class ChatHandler(object):
  def __init__(self, user):
    self._user = user
    self._room = RoomDB.find_by_id(0)

  def enter(self):
    self._user.send(BackLog.read())
    self._room.add_user(self._user)
    self._send_all(Message(self._user.name(), self._user.name_color()).add(' が入室しました。', 'olive'))

  def leave(self):
    self._room.remove_user(self._user)
    self._send_all(Message(self._user.name(), self._user.name_color()).add(' が退室しました。', 'olive'))

  def handle(self, message):
    self._send_all(Message(self._user.name() + " > ", self._user.name_color()).add(message))

  def _send_all(self, message):
      message.add(" <%s>\n" % self._time_stamp(), 'green')
      self._room.send_all(message)
      BackLog.write(message)

  def _time_stamp(self):
    return str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class BackLog(object):
  _length = 64
  _log = []

  @classmethod
  def load(cls, filename):
    cls._log = [line for line in open(filename, 'r')]

  @classmethod
  def save(cls, filename):
    open(filename, 'w').writelines(cls._log)
  
  @classmethod
  def read(cls):
    return ''.join(cls._log)

  @classmethod
  def write(cls, message):
    cls._log.append(str(message))
    cls._log = cls._log[-cls._length:]

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

if __name__ == '__main__':
  logfile = 'log.txt'
  BackLog.load(logfile)
  try:
    WebSocketServer(ChatService()).run(7000)
  finally:
    BackLog.save(logfile)
