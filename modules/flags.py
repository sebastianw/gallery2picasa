import getopt

class FlagDefinitionError(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)
    self.__message = message

  def __str__(self):
    return 'FlagDefinitionError: %s' % self.message()

  def message(self):
    return self.__message


class FlagParseError(Exception):
  def __init__(self, message, usage):
    Exception.__init__(self, message)
    self.__message = message
    self.__usage = usage

  def __str__(self):
    return 'FlagParseError: %s' % self.message()

  def message(self):
    return self.__message

  def usage(self):
    return self.__usage


class Flag(object):
  def __init__(self, shortname, longname, description, default=None):
    if len(shortname) != 1:
      raise FlagDefinitionError('Short name can be only 1 character long')

    if len(longname) < 2:
      raise FlagDefinitionError('Long name must be >= 2 characters long')

    self.__shortname = shortname
    self.__longname = longname
    self.__description = description
    self.__default = default
    self.__value = None

  def shortname(self):
    return self.__shortname

  def longname(self):
    return self.__longname

  def description(self):
    return self.__description

  def default(self):
    return self.__default

  def value(self):
    if self.__value is None:
      return self.__default
    else:
      return self.__value

  def set_value(self, value):
    self.__value = value

  def has_value(self):
    return self.__value is not None or self.__default is not None

  def required(self):
    return self.__default is None

  def getopt_short_component(self):
    return '%s:' % self.shortname()

  def getopt_long_component(self):
    return '%s=' % self.longname()

  def shortflag(self):
    return '-%s' % self.shortname()

  def longflag(self):
    return '--%s' % self.longname()

  def UsageString(self):
    parts = []
    parts.append(
        '%s|%s <%s>' % (self.shortflag(), self.longflag(), self.longname()))

    if self.default() is not None:
      parts.append('(default: %s)' % self.default())

    flagline = ' '.join(parts)
    descline = '\t%s' % self.description()
    return '\n'.join([flagline, descline])


class FlagContainer(object):
  def __init__(self):
    self.__flags_by_shortflag = {}
    self.__flags_by_longflag = {}
    self.__required_flags = []
    self.__optional_flags = []
    self.__allflags = []

  def AddFlag(self, shortname, longname, description, default=None):
    flag = Flag(shortname, longname, description, default)
    self.__flags_by_shortflag[flag.shortflag()] = flag
    self.__flags_by_longflag[flag.longflag()] = flag

    if flag.required():
      self.__required_flags.append(flag)
    else:
      self.__optional_flags.append(flag)

    self.__allflags.append(flag)

  def Parse(self, argv):
    getopt_short_components = []
    getopt_long_components = []
    for flag in self.__allflags:
      getopt_short_components.append(flag.getopt_short_component())
      getopt_long_components.append(flag.getopt_long_component())

    try:
      opts, argv = getopt.getopt(
          argv, ''.join(getopt_short_components), getopt_long_components)
    except getopt.GetoptError, e:
      raise FlagParseError(e.msg, self.UsageString())

    for o, a in opts:
      flag = None
      if o in self.__flags_by_shortflag:
        flag = self.__flags_by_shortflag[o]
      if o in self.__flags_by_longflag:
        flag = self.__flags_by_longflag[o]

      if flag is None:
        raise FlagParseError('Unknown flag %s set to %s' % (o, a),
            self.UsageString())

      flag.set_value(a)

    for flag in self.__required_flags:
      if not flag.has_value():
        raise FlagParseError('Required flag %s not set' % flag.longname(),
            self.UsageString())

    return argv

  def UsageString(self):
    lines = []

    if len(self.__required_flags) > 0:
      lines.append('Required flags:')
      for flag in self.__required_flags:
        lines.append('%s' % flag.UsageString())

    if len(lines) > 0:
      lines.append('')

    if len(self.__optional_flags) > 0:
      lines.append('Optional flags:')
      for flag in self.__optional_flags:
        lines.append('%s' % flag.UsageString())

    return '\n'.join(lines)

  def __getattr__(self, name):
    return self.__flags_by_longflag['--%s' % name].value()

FLAGS = FlagContainer()
