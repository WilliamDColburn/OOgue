#!/usr/bin/env python3

__OOGUEVERSION__ = 1593122571

##
## Check for python 3
##
import sys
assert sys.version_info.major == 3

import locale

try:
  import wx
except:
  print( 'ERROR: python wx module is required' )
  sys.exit( 1 )
import wx.lib.scrolledpanel

import os

import game
import time
import readline
import pdb


rows, columns = os.popen('stty size', 'r').read().split()
if int( columns ) < 50:
  print( 'TERMINAL IS TOO NARROW' )
  sys.exit( 1)
if int( rows ) < 40:
  print( 'TERMINAL IS TOO SHORT' )
  sys.exit( 1 )


def whoami():
  who = os.environ["USER"].title()
  if not who:
    who = 'Player'
  return who

class playerCharacterClass( game.characterClass ):
  def __init__( self, id ):
    super( playerCharacterClass, self).__init__( id )
    self.activate()
    self.proximate()
    self._time = time.time()
    self.last_command = 'wait'
    self.uimsg = ''
        
  def ai( self ):
    os.system( 'clear' )
    print()
    self.intent = None

    self.interacted = False
    loc = self.location()
    messages = []
    messages.append( 'Au: %d, Ag: %d, Cu: %d' % (self.au(), self.ag(), self.cu()) )
    messages.append( 'Turn: %d' % game.gameClass().turn() )
    messages.append( 'Location: %s' % str( self.location() ) )
    messages.extend( self.msg().getMessages() )
    messages = '\n'.join( messages[0:8] )
    map = self.getMap( game.gameClass().map() )
    interactions = self.listInteractions( self )
    ##
    ##  Print the map here
    ##
    for row in map[0]:
      print( ' '.join( row ) )
    print()
    print( messages )
    print()
    print( 'Possible Commands: ', end='' )
    for i,I in enumerate( interactions ):
      print( ('%d:"' % i) + I.title() + '" ', end='' )
    print()

    if self.uimsg:
      print( '>>>>>', self.uimsg )
      self.uimsg == ''

    print( 'Your command[%s]? ' % self.last_command, end='' )
    line = ' '.join( sys.stdin.readline().split() ).lower()
    if line.lower() == 'pdb':
      pdb.set_trace()
    if line.lower() == 'q':
      self.uimsg = 'Type "quit" to quit.'
    if line.lower() == 'quit':
      print( 'Quitting' )
      sys.exit( 0 )
    if not line:
      line = self.last_command
    line = ' '.join( line.lower().split() )
    if line.isdigit():
      i = int( line )
      try:
        self.last_command = interactions[i].title()
        return interactions[i]
      except:
        pass
    if line == 'w':
      line = 'west'
    if line == 'e':
      line = 'east'
    if line == 'n':
      line = 'north'
    if line == 's':
      line = 'south'
    if line == 'sw':
      line = 'southwest'
    if line == 'nw':
      line = 'northwest'
    if line == 'se':
      line = 'southeast'
    if line == 'ne':
      line = 'northeast'
    if line == 'u':
      line = 'up'
    if line == 'd':
      line = 'down'
    self.last_command = line
    for i in interactions:
      if i.title().lower() == ' '.join( line.split() ).lower():
        self._time = time.time()
        return i
    return interactions[0]

g = game.gameClass()
g.new()
player = playerCharacterClass( whoami() )
g.addDenizen( player, True )
g.play()  
