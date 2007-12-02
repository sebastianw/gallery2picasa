#!/usr/bin/python2.4

class Item(object):
  TABLE_NAME = 'Item'

  def __init__(self, db, id):
    self.__id = id
    (description, keywords, summary, title) = db.FieldsForItem(
        id, Item.TABLE_NAME, 'description', 'keywords', 'summary', 'title')

    # TODO(caffeine): these need HTML-unescaping
    self.__description = description
    self.__keywords = keywords
    self.__summary = summary
    self.__title = title

  def __str__(self):
    return "%s: title='%s' summary='%s' description='%s' keywords='%s'" % (
      self.type(), self.__title, self.__summary,
      self.__description, self.__keywords)

  def type(self):
    return 'Item'

  def id(self):
    return self.__id

  def description(self):
    return self.__description

  def keywords(self):
    return self.__keywords

  def summary(self):
    return self.__summary

  def title(self):
    return self.__title


class ChildItem(Item):
  TABLE_NAME = 'ChildEntity'

  def __init__(self, db, id):
    Item.__init__(self, db, id)
    (parent_id,) = db.FieldsForItem(id, ChildItem.TABLE_NAME, 'parentId')
    self.__parent_id = parent_id

  def type(self):
    return 'ChildItem'

  def parent_id(self):
    return self.__parent_id


class PhotoItem(ChildItem):
  TABLE_NAME = 'PhotoItem'

  def __init__(self, db, id):
    ChildItem.__init__(self, db, id)
    self.__id = id
    (width, height) = db.FieldsForItem(
        id, PhotoItem.TABLE_NAME, 'width', 'height')
    self.__width = width
    self.__height = height

  def type(self):
    return 'Photo'

  def width(self):
    return self.__width

  def height(self):
    return self.__height


class AlbumItem(Item):
  TABLE_NAME = 'AlbumItem'

  def __init__(self, db, id):
    Item.__init__(self, db, id)
    (theme,) = db.FieldsForItem(
        id, AlbumItem.TABLE_NAME, 'theme')
    self.__theme = theme

  def type(self):
    return 'Album'

  def theme(self):
    return self.__theme
