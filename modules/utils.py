#!/usr/bin/python2.4

import htmllib

def HtmlUnescape(s):
  p = htmllib.HTMLParser(None)
  p.save_bgn()
  p.feed(s)
  return p.save_end()
