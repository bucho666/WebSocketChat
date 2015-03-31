# -*- coding: utf-8 -*-

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

  def users(self):
    return list(self._users)
