#!/usr/bin/python2.4

from modules import flags
from modules import items
from modules import db

import getopt
import sys

FLAGS = flags.FLAGS
FLAGS.AddFlag('u', 'username', 'The username to use for the database')
FLAGS.AddFlag('p', 'password', 'The password to use for the database')
FLAGS.AddFlag('d', 'database', 'The database to use', 'gallery2')
FLAGS.AddFlag('h', 'hostname', 'The hostname to use', 'localhost')
FLAGS.AddFlag('t', 'table_prefix', 'The table prefix to use', 'g2_')
FLAGS.AddFlag('f', 'field_prefix', 'The field prefix to use', 'g_')

def usage(appname, flagusage, flagmessage):
  if flagmessage is not None:
    print '%s\n' % flagmessage

  print 'Usage:\t%s' % appname
  print flagusage

def main(argv):
  appname = argv[0]

  try:
    argv = FLAGS.Parse(argv[1:])
  except flags.FlagParseError, e:
    usage(appname, e.usage(), e.message())
    sys.exit(1)

  gdb = db.Database(FLAGS.username, FLAGS.password, FLAGS.database,
      FLAGS.hostname, FLAGS.table_prefix, FLAGS.field_prefix)

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
