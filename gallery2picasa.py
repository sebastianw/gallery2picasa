#!/usr/bin/python

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
FLAGS.AddFlag('y', 'privacy', 'The access level for the album ("private" or "public")', 'public')
FLAGS.AddFlag('o', 'confirm', 'Confirm upload for every album', 'true')
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

  confirm = FLAGS.confirm
  if confirm == 'true':
      confirm = True
  else:
      confirm = False

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

      if confirm:
        upload_album = False
        confirmed = False
        while confirmed == False:
          confirm_input = raw_input('Upload Album "%s"? [y/N]' % album.title().encode(sys.stdout.encoding, 'replace')).lower()
          if confirm_input == 'n' or confirm_input == '':
            confirmed = True
          elif confirm_input == 'y':
            upload_album = True
            confirmed = True

        if upload_album != True:
          continue

      privacy = FLAGS.privacy.lower()
      if privacy != 'public':
        privacy = 'private'
      strout = 'CREATING ALBUM [%s] [%s]' % (album.title(), album.summary())
      print strout.encode(sys.stdout.encoding, 'replace')
      a = pws.InsertAlbum(album.title(), album.summary(), access=privacy)

      for photo in photos_by_album[album.id()]:
        title = photo.title() or photo.path_component()
        strout = '\tCREATING PHOTO [F:%s] [T:%s] [S:%s] [K:%s]' % (
            photo.path_component(), title, photo.summary(), photo.keywords())
        print strout.encode(sys.stdout.encoding, 'replace')

        keywords = ', '.join(photo.keywords().split())
        filename = '%s/albums/%s/%s' % (
            FLAGS.gallery_prefix, album.full_album_path(gdb), photo.path_component())
        pws.InsertPhotoSimple(a.GetFeedLink().href, title,
            photo.summary(), filename, keywords=keywords)
            
  finally:
    gdb.close()

if __name__ == '__main__':
  main(sys.argv)
