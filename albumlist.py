#!/usr/bin/python

from modules import db
from modules import flags
from modules import items
from modules import utils

import getopt
import sys

FLAGS = flags.FLAGS
FLAGS.AddFlag('u', 'username', 'The username to use for the database')
FLAGS.AddFlag('p', 'password', 'The password to use for the database')
FLAGS.AddFlag('d', 'database', 'The database to use', 'gallery2')
FLAGS.AddFlag('h', 'hostname', 'The hostname to use', 'localhost')
FLAGS.AddFlag('t', 'table_prefix', 'The table prefix to use', 'g2_')
FLAGS.AddFlag('f', 'field_prefix', 'The field prefix to use', 'g_')

def printAlbum(album, subalbums, photos, level=0):

    print level*'\t' + '%s' %  unicode(album).encode(sys.stdout.encoding, 'replace')

    try:
      for sub in subalbums[album.id()]:
        printAlbum(sub, subalbums, photos, level+1)
    except KeyError:
      pass

    try:
      for photo in photos[album.id()]:
        print level*'\t' + '\t%s' % unicode(photo).encode(sys.stdout.encoding, 'replace')
    except KeyError:
      pass


def main(argv):
  appname = argv[0]

  try:
    argv = FLAGS.Parse(argv[1:])
  except flags.FlagParseError, e:
    utils.Usage(appname, e.usage(), e.message())
    sys.exit(1)

  gdb = db.Database(FLAGS.username, FLAGS.password, FLAGS.database,
      FLAGS.hostname, FLAGS.table_prefix, FLAGS.field_prefix)

  try:
    rootalbum = None
    albums = []
    album_ids = gdb.ItemIdsForTable(items.AlbumItem.TABLE_NAME)
    subalbums_by_album = {}
    for id in album_ids:
      album = items.AlbumItem(gdb,id)
      albums.append(items.AlbumItem(gdb, id))
      if album.parent_id():
        if album.parent_id() not in subalbums_by_album:
          subalbums_by_album[album.parent_id()] = []
        subalbums_by_album[album.parent_id()].append(album)
      else:
        rootalbum = album

    photos_by_album = {}
    photo_ids = gdb.ItemIdsForTable(items.PhotoItem.TABLE_NAME)
    for id in photo_ids:
      photo = items.PhotoItem(gdb, id)
      if photo.parent_id() not in photos_by_album:
        photos_by_album[photo.parent_id()] = []

      photos_by_album[photo.parent_id()].append(photo)

    printAlbum(rootalbum, subalbums_by_album, photos_by_album)

  finally:
    gdb.close()

if __name__ == '__main__':
  main(sys.argv)
