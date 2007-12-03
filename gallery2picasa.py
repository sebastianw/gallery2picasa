#!/usr/bin/python2.4

from modules import db
from modules import flags
from modules import items
from modules import utils

import gdata.photos
import gdata.photos.service
import getopt
import sys

FLAGS = flags.FLAGS
FLAGS.AddFlag('b', 'dbuser', 'The username to use for the database')
FLAGS.AddFlag('a', 'dbpass', 'The password to use for the database')
FLAGS.AddFlag('d', 'database', 'The database to use', 'gallery2')
FLAGS.AddFlag('h', 'hostname', 'The database hostname', 'localhost')
FLAGS.AddFlag('t', 'table_prefix', 'The table prefix to use', 'g2_')
FLAGS.AddFlag('f', 'field_prefix', 'The field prefix to use', 'g_')
FLAGS.AddFlag('u', 'username', 'The Google username to use')
FLAGS.AddFlag('p', 'password', 'The Google password to use')
FLAGS.AddFlag('g', 'gallery_prefix', 'Prefix for gallery photos',
    '/var/local/g2data')

def main(argv):
  appname = argv[0]

  try:
    argv = FLAGS.Parse(argv[1:])
  except flags.FlagParseError, e:
    utils.Usage(appname, e.usage(), e.message())
    sys.exit(1)

  gdb = db.Database(FLAGS.dbuser, FLAGS.dbpass, FLAGS.database,
      FLAGS.hostname, FLAGS.table_prefix, FLAGS.field_prefix)

  pws = gdata.photos.service.PhotosService()
  pws.ClientLogin(FLAGS.username, FLAGS.password)

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
      if album.id() not in photos_by_album:
        continue

      print 'CREATING ALBUM [%s] [%s]' % (album.title(), album.summary())
      a = pws.InsertAlbum(album.title(), album.summary())

      for photo in photos_by_album[album.id()]:
        print '\tCREATING PHOTO [%s] [%s] [%s]' % (
            photo.path_component(), photo.summary(), photo.keywords())

        keywords = ', '.join(photo.keywords().split())
        filename = '%s/albums/%s/%s' % (
            FLAGS.gallery_prefix, album.title(), photo.path_component())
        pws.InsertPhotoSimple(a.GetFeedLink().href, photo.path_component(),
            photo.summary(), filename, 'image/jpeg', keywords)
            
  finally:
    gdb.close()

if __name__ == '__main__':
  main(sys.argv)
