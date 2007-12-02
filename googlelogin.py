#!/usr/bin/python2.4

"""A class that can be used with urllib2 to enable ClientLogin for gdata.

Sample usage:
handler = googlelogin.GoogleLoginAuthHandler(username, password, service)
opener = urllib2.build_opener(handler)
urllib2.install_opener(opener)
url = 'http://www.google.com/calendar/feeds/%s/private/full' % username
resp = urllib2.urlopen(url)
"""

__author__ = 'caffeine@google.com (Peter Colijn)'

import logging
import re
import urllib
import urllib2

class GoogleLoginAuthHandler(urllib2.HTTPHandler):
  """Subclass of HTTPHandler that tries to do ClientLogin for google.com URLs

  When requesting a URL in the google.com domain, this class will attempt
  to do ClientLogin before requesting the actual URL. It tries once, and
  will send the Authorization header from then on if successful. If the
  login attempt is unsuccessful, you must call reset() or one of the setter
  methods to try again.
  """

  __AUTH_REGEX = r'^Auth=([-_a-zA-Z0-9]+)$'
  __AUTH_PATTERN = re.compile(__AUTH_REGEX)

  def __init__(self, username, password,
      service, google_frontend='www.google.com'):
    urllib2.HTTPHandler.__init__(self)
    self.__username = username
    self.__password = password
    self.__service = service
    self.__google_frontend = google_frontend

    # use a separate opener so that this handler can be used in the global one
    self.__opener = urllib2.build_opener()

    self.__reset()

  def __reset(self):
    self.__attempted_login = False
    self.__auth = None

  def __authenticate(self):
    self.__attempted_login = True

    if 'www.google.com' == self.__google_frontend:
      proto = 'https'
    else:
      proto = 'http'
    url = '%s://%s/accounts/ClientLogin' % (proto, self.__google_frontend)

    data = (
        ('Email', self.__username),
        ('Passwd', self.__password),
        ('source', 'Google-LoginAuthHandler-1.0'),
        ('service', self.__service),
      )

    try:
      resp = self.__opener.open(url, urllib.urlencode(data))
      for line in resp.readlines():
        m = GoogleLoginAuthHandler.__AUTH_PATTERN.search(line)
        if m is None:
          continue

        self.__auth = m.group(1)
        break
    except urllib2.HTTPError, e:
      logging.warning('Authentication failed: %s', e)
      return

  def reset(self):
    self.__reset()

  def service(self):
    return self.__service

  def set_service(self, service):
    self.__reset()
    self.__service = service

  def google_frontend(self):
    return self.__gaia_service

  def set_google_frontend(self, google_frontend):
    self.__reset()
    self.__google_frontend = google_frontend

  def username(self):
    return self.__username

  def set_username(self, username):
    self.__reset()
    self.__username = username

  def set_password(self, password):
    self.__reset()
    self.__password = password

  def http_open(self, req):
    host, port = urllib.splitport(req.get_host())
    if not host.endswith('google.com'):
      return urllib2.HTTPHandler.http_open(self, req)

    if self.__attempted_login:
      if self.__auth is not None:
        req.add_header(
            'Authorization',
            'GoogleLogin auth=%s' % self.__auth)

      return urllib2.HTTPHandler.http_open(self, req)

    self.__authenticate()
    return self.http_open(req)

  def http_request(self, req):
    return urllib2.HTTPHandler.http_request(self, req)
