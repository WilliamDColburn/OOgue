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

##
## This "works", but works poorly.  Someone needs to rewrite it!
##

def _buttonClick( event ):
#  print( '_buttonClick()' )
  event.GetEventObject().GetTopLevelParent().Enable( False )
  button = event.GetEventObject()
  interact = button.interact
  player = button.GetTopLevelParent().player
  player.intent = interact
  event.GetEventObject().GetTopLevelParent().EndModal( True )

class scrolledTextPanel( wx.lib.scrolledpanel.ScrolledPanel ):
  def updateText( self, text ):
    self.text.SetLabel( text )
    self.text.Fit()
    self.Fit()
    self.SetupScrolling()
 
  def __init__( self, *args, **kwargs ):
    super( scrolledTextPanel, self ).__init__( *args, **kwargs )
    sizer = wx.BoxSizer( wx.VERTICAL )
    self.text=wx.StaticText( self, -1,  'UNINITIALIZED' )
    sizer.Add( self.text )
    self.SetSizer( sizer )
    self.SetAutoLayout( 1 )
    self.SetupScrolling()

class gameWindow( wx.Dialog ):
  def updateMap( self, map ):
    rows = []
    for row in map:
      if isinstance( row, list ):
        row = ' '.join( row )
      rows.append( row )
    text = '\n'.join( rows )
    self.map.updateText( text )
  def clearButtons( self ):
    self.buttons.clearButtons()
  def updateButtons( self, interactions ):
    dirs = []
    buttons = []
    for i in interactions:
      if i.hint() and ':move:' in i.hint():
        dirs.append( i )
      else:
        buttons.append( i )
    self.directions.updateButtons( dirs )
    self.buttons.updateButtons( buttons )
  def updateMessages( self, messages ):
    self.text.updateText( messages )

  def user_exit( self, callback ):
    print( 'exited', callback )
    sys.exit( 0 )
    
  def __init__( self, parent, *args, **kwargs ):
    super( gameWindow, self ).__init__( parent, *args, **kwargs )
    hsizer = wx.BoxSizer( wx.HORIZONTAL )
    vsizer = wx.BoxSizer( wx.VERTICAL )
    self.map = mapPanel( self )
    self.directions = directionPanel( self )
    self.buttons = buttonPanel( self )
    self.text = scrolledTextPanel( self, size=(500,800) )
    hsizer.Add( vsizer )
    vsizer.Add( self.map )
    vsizer.AddSpacer( 10 )
    vsizer.Add( self.directions )
    vsizer.Add( self.buttons )
    vsizer.AddSpacer( 2 )
    hsizer.AddSpacer( 10 )
    hsizer.Add( self.text )
    hsizer.AddSpacer( 2 )
    self.SetSizer( hsizer )
    self.Bind( wx.EVT_CLOSE, self.user_exit)

class directionPanel( wx.Panel ):
  _dirs = ['Up', 'Down', 'NW', 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'Wait']
  def updateButtons( self, interactions ):
    for b in self._buttons:
      if b in self._dirs:
        self._buttons[b].Enable( False )
        self._buttons[b].interact = None
    for i in interactions:
      for c in self._dirs:
        if i.hint().endswith( ':move:%s' % c ):
          self._buttons[c].Enable( True )
          self._buttons[c].interact = i

  def Zup( self, event ):
    button = event.GetEventObject()
    player = button.GetTopLevelParent().player
    if player.mapZ == player._mapSize:
      self._buttons['Z++'].Enable( False )
    else:
      self._buttons['Z--'].Enable( True )
      player.mapZ = player.mapZ + 1
      button.GetTopLevelParent().updateMap( player.getMap( game.gameClass().map() )[player.mapZ]  )    

  def Zdown( self, event ):
    button = event.GetEventObject()
    player = button.GetTopLevelParent().player
    if -player.mapZ == player._mapSize:
      self._buttons['Z--'].Enable( False )
    else:
      self._buttons['Z++'].Enable( True )
      player.mapZ = player.mapZ - 1
      button.GetTopLevelParent().updateMap( player.getMap( game.gameClass().map() )[player.mapZ]  )    
    
  def __init__( self, *args, **kwargs ):
    wx.Panel.__init__( self, *args, **kwargs )
    sizer = wx.GridSizer( cols = 3, hgap = 10, vgap = 10 )
    self._buttons = {}
    for blabel in ['Z++', 'Up', 'Save',
                  'NW', 'N', 'NE',
                  'W','Wait','E',
                  'SW','S','SE',
                  'Z--', 'Down', 'Load']:
      b = wx.Button( self, label = blabel )
      self._buttons[blabel] = b
      b.Enable( False )
      if blabel in self._dirs:
        b.Bind( wx.EVT_BUTTON, _buttonClick )
      sizer.Add( b )
      if blabel == 'Z++':
        b.Bind( wx.EVT_BUTTON, self.Zup )
        b.Enable( True )
      if blabel == 'Z--':
        b.Bind( wx.EVT_BUTTON, self.Zdown )
        b.Enable( True )
    sizer.AddSpacer( 2 )
    self.SetSizer( sizer )

class buttonPanel( wx.Panel ):
  def clearButtons( self ):
    for x in self._buttons:
      x.SetLabel( 'CLEARED' )
      x.interact = None
      x.Hide()
      
  def updateButtons( self, interactions ):
    self.sizer.Clear()
    for i in range( len( interactions ) - len( self._buttons ) ):
      self._buttons.append( wx.Button( self, label='None Yet' ) )
      self._buttons[-1].Bind( wx.EVT_BUTTON, _buttonClick )
    for i, interact in enumerate( interactions ):
      self.sizer.Add( self._buttons[i] )
      self._buttons[i].SetLabel( interact.title() )
      self._buttons[i].interact = interact
      self._buttons[i].Show()
    self.sizer.AddSpacer( 10 )
  def __init__( self, *args, **kwargs ):
    wx.Panel.__init__( self, *args, **kwargs )
    self.sizer = wx.BoxSizer()
    self._buttons = []
    self.SetSizer( self.sizer )

class mapPanel( wx.Panel ):
  def updateText( self, text ):
    self.text.SetLabel( text )

  def __init__( self, *args, **kwargs ):
    wx.Panel.__init__( self, *args, **kwargs )
    sizer = wx.BoxSizer()
    sizer.AddSpacer( 8 )
    self.text = wx.StaticText( self, label="No Label" )
    self.text.SetFont( wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False) )
    sizer.Add( self.text )
    sizer.AddSpacer( 8 )
    self.SetSizer( sizer )

class gameApp(wx.App):
  pass

import game

def whoami():
  ##
  ## This should really prompt for a name...
  ##
  who = os.environ["USER"].title()
  if not who:
    who = 'Player'
  return who

class playerCharacterClass( game.characterClass ):
  def __init__( self, id ):
    super( playerCharacterClass, self).__init__( id )
    self.activate()
    self.proximate()
    self.frame = gameWindow( None )
    self.frame.player = self
    self.frame.SetTitle( self.id() )
    self.frame.Disable()
        
  def ai( self ):
    self.intent = None
    while not self.intent:
      self.interacted = False
      loc = self.location()
      self.mapZ = 0
      messages = []
      messages.append( 'Au: %d, Ag: %d, Cu: %d' % (self.au(), self.ag(), self.cu()) )
      messages.append( 'Turn: %d' % game.gameClass().turn() )
      if game.gameClass().debug():
        messages.append( 'Location: %s' % str( self.location() ) )
      messages.append( ' ' )
      messages.extend( self.msg().getMessages() )
      map = self.getMap( game.gameClass().map() )[self.mapZ]
      interactions = self.listInteractions( self )
      messages = '\n'.join( messages )
      self.frame.updateMap( map )
      self.frame.updateButtons( interactions )
      self.frame.updateMessages( messages )
      self.frame.Layout()
      self.frame.Fit()
      self.frame.Enable()
      self.frame.ShowModal()
      self.frame.clearButtons()
      return self.intent


app = gameApp( 0 )
g = game.gameClass()
if "--debug" in sys.argv:
  g.setDebug( True )
if os.path.exists( 'debug' ):
  g.setDebug( True )
g.new()
player = playerCharacterClass( whoami() )
g.addDenizen( player, True )
#player2 = playerCharacterClass( whoami() + '2' )
#g.addDenizen( player2, True )
g.play()  



