#!/usr/bin/python2.4

import htmllib

def HtmlUnescape(s):
  # TODO(caffeine): this is slow, but at least it's accurate
  p = htmllib.HTMLParser(None)
  p.save_bgn()
  p.feed(s)
  return p.save_end()
