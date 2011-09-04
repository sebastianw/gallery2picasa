#!/usr/bin/python

from modules import db
from modules import flags
from modules import items
from modules import utils

import gdata.photos
import gdata.photos.service
import getopt
import sys
import time

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

  # Error avoidance
  retry = 10   # Number of retries
  delay = 0.2 # Delay in (sub-)seconds
  backoff = 2  # Double delay on every retry

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
      summary = album.summary() or album.description()

      mtries, mdelay = retry, delay
      success = False
      while mtries > 0:
        if mtries != retry:
          strout = 'Retrying album creation.'
          print strout.encode(sys.stdout.encoding, 'replace')
        try:
          strout = 'CREATING ALBUM [%s] [%s]' % (album.title(), summary)
          print strout.encode(sys.stdout.encoding, 'replace')
          pws.InsertAlbum(album.title(), summary, access=privacy)
          success = True
          break
        except gdata.photos.service.GooglePhotosException, e:
          strout = 'Google error: gdata.photos.service.GooglePhotosException %s' % e
          print strout.encode(sys.stdout.encoding, 'replace')
        mtries -=1
        strout = 'Sleeping %.2f seconds.' % mdelay
        print strout.encode(sys.stdout.encoding, 'replace')
        time.sleep(mdelay)
        mdelay *= backoff
      if not success:
        raise Exception('Could not create album')

      for photo in photos_by_album[album.id()]:
        # Title is displayed nowhere in picasa?
        title = photo.title() or photo.path_component()
        summary = photo.summary() or photo.description() or photo.title()

        keywords = ', '.join(photo.keywords().split())
        filename = '%s/albums/%s/%s' % (
            FLAGS.gallery_prefix, album.full_album_path(gdb), photo.path_component())

        mtries, mdelay = retry, delay
        success = False
        while mtries > 0:
          if mtries != retry:
            strout = 'Retrying photo upload.'
            print strout.encode(sys.stdout.encoding, 'replace')
          try:
            strout = '\tCREATING PHOTO [F:%s] [T:%s] [S:%s] [K:%s]' % (
                photo.path_component(), title, summary, photo.keywords())
            print strout.encode(sys.stdout.encoding, 'replace')
            pws.InsertPhotoSimple(a.GetFeedLink().href, title,
                summary, filename, keywords=keywords)
            success = True
            break
          except gdata.photos.service.GooglePhotosException, e:
            strout = 'Google error: gdata.photos.service.GooglePhotosException %s' % e
            print strout.encode(sys.stdout.encoding, 'replace')
          mtries -=1
          strout = 'Sleeping %.2f seconds.' % mdelay
          print strout.encode(sys.stdout.encoding, 'replace')
          time.sleep(mdelay)
          mdelay *= backoff
        if not success:
          raise Exception('Could not upload photo')

  finally:
    gdb.close()

if __name__ == '__main__':
  main(sys.argv)
