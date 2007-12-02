#!/usr/bin/python2.4

import MySQLdb
import logging
import re

class BadNameError(Exception):
  def __init__(self, msg):
    Exception.__init__(self, msg)
    self.__msg = msg

  def __str__(self):
    return 'BadNameError: %s' % self.__msg

  def msg(self):
    return self.__msg

class Database(object):
  __SAFE_NAME_PATTERN = re.compile(r'^[-_a-zA-Z0-9]+$')
  def validate_name(name):
    return Database.__SAFE_NAME_PATTERN.match(name) is not None
  validate_name = staticmethod(validate_name)

  def __init__(self, username, password, database='gallery2',
      hostname='localhost', table_prefix='g2_', field_prefix='g_'):
    if not Database.validate_name(table_prefix):
        raise BadNameError('Table prefix %s is invalid' % table_prefix)

    if not Database.validate_name(field_prefix):
        raise BadNameError('Field prefix %s is invalid' % field_prefix)
    
    self.__db = MySQLdb.connect(hostname, username, password, database)
    self.__table_prefix = table_prefix
    self.__field_prefix = field_prefix
    self.__id_field = field_prefix + 'id';

  def table_prefix(self):
    return self.__table_prefix

  def field_prefix(self):
    return self.__field_prefix

  def id_field(self):
    return self.__id_field

  def close(self):
    self.__db.close()

  def __table_name(self, table):
    return ''.join([self.table_prefix(), table])

  def __field_name(self, field):
    return ''.join([self.field_prefix(), field])

  def FieldsForItem(self, id, table, *fields):
    if not Database.validate_name(table):
      raise BadNameError('Table name %s is invalid' % table)

    field_list = [self.__field_name(f)
        for f in fields
        if Database.validate_name(f)]
    nfields = len(field_list)

    if field_list <= 0:
      logging.warning('Warning: no fields requested for FieldsForItem')
      return None

    c = self.__db.cursor()

    try:
      query = ['SELECT', ','.join(field_list),
          'FROM %s' % self.__table_name(table),
          'WHERE %s = %%s' % self.id_field()]
      nresults = c.execute(' '.join(query), (id,))

      if nresults <= 0:
        logging.warning('Warning: no results for FieldsForItem')
        return None

      if nresults > 1:
        logging.warning('Warning: more than 1 result for FieldsForItem')

      return c.fetchone()
    finally:
      c.close()

  def ItemIdsForTable(self, table):
    if not Database.validate_name(table):
      raise BadNameError('Table name %s is invalid' % table)

    c = self.__db.cursor()

    try:
      query = ['SELECT %s' % self.id_field(),
          'FROM %s' % self.__table_name(table)]
      nresults = c.execute(' '.join(query))

      if nresults <= 0:
        logging.warning('Warning: no results for ItemIdsForTable(%s)' % table)
        return []

      r = c.fetchone()
      result = []
      while r is not None:
        result.append(r[0])
        r = c.fetchone()

      return result
    finally:
      c.close()
