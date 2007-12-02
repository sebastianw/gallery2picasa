#!/usr/bin/python2.4

from modules import items
from modules import db

import getopt
import sys

def usage(appname):
  print '%s -u|--username <username> -p|--password <password>' % appname
  print 'Where:'
  print "\t<username> is the MySQL user to connect as"
  print "\t<password> is the MySQL password to use"

  print '\nOptional arguments:'
  print "\t[-d|--database <database> (default: 'gallery2')]"
  print "\t[-h|--hostname <hostname> (default: 'localhost')]"
  print "\t[-t|--table_prefix <table_prefix> (default: 'g2_')]"
  print "\t[-f|--field_preifx <field_prefix> (default: 'g_')]"

def main(argv):
  appname = argv[0]

  try:
    opts, argv = getopt.getopt(argv[1:], 'u:p:d:h:t:f:', [
        'username=', 'password=', 'database=', 'hostname=',
        'table_prefix=', 'field_prefix=' ])
  except getopt.GetoptError:
    usage(appname)
    sys.exit(1)

  username = None
  password = None
  database = 'gallery2'
  hostname = 'localhost'
  table_prefix = 'g2_'
  field_prefix = 'g_'

  for o, a in opts:
    if o in ('-u', '--username'):
      username = a
    if o in ('-p', '--password'):
      password = a
    if o in ('-d', '--database'):
      database = a
    if o in ('-h', '--hostname'):
      hostname = a
    if o in ('-t', '--table_prefix'):
      table_prefix = a
    if o in ('-f', '--field_prefix'):
      field_prefix = a

  if username is None or password is None:
    usage(appname)
    sys.exit(1)

  gdb = db.Database(username, password, database, hostname,
      table_prefix, field_prefix)

  try:
    albums = []
    album_ids = gdb.ItemIdsForTable(items.AlbumItem.TABLE_NAME)
    for id in album_ids:
      albums.append(items.AlbumItem(gdb, id))

    photos_by_album = {}
    photo_ids = gdb.ItemIdsForTable(items.PhotoItem.TABLE_NAME)
    for id in photo_ids:
      photo = items.PhotoItem(gdb, id)
      if photo.parent_id() not in photos_by_album:
        photos_by_album[photo.parent_id()] = []

      photos_by_album[photo.parent_id()].append(photo)

    for album in albums:
      print album

      if album.id() not in photos_by_album:
        continue

      for photo in photos_by_album[album.id()]:
        print '\t%s' % photo
  finally:
    gdb.close()

if __name__ == '__main__':
  main(sys.argv)
