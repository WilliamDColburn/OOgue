#!/usr/bin/env python3

__OOGUEVERSION__ = 1593122571

##
## Check for python 3
##
import sys
assert sys.version_info.major == 3

##
## coreClass( object )
##   Parent of anything that isn't a fill
## fillClass( object )
##   Parent of all map locations
## characterClass( coreClass )
##   Parent of entities
## playerClass( characterClass )
##   Child of characterClass
## objectClass( coreClass )
##   Things that chacaters can manipulate
##

##
## callbacks are needed
##   fill callbacks
##   inventory object callbacks
##
## no inventory objects yet, so just fill callbacks for now
##
## a fill callback will give an id and callback name
##
## all fill callbacks calls will look like:
##   callback( self, caller, fill )
##
## the caller will be the object that triggered it
## the fill will be the location of the fill it was triggered from
##
## we need to be able to:
##   add_callback()
##   remove_callback()
##
## the goal is to remove activate() and proximate() from characterClass()
##

##
## Slots
##   head
##   neck
##   hands
##   chest
##   waist
##   pants
##   feet
##   held right hand
##   held left hand
##   worn right ring
##   worn left ring
##   worn trinket
##   worn cloak
##   worn backpack
##
## The "worn backpack" slot is a single item, but the item will hold
## items of its own to increase capacity.
##

##
## Objects
##   size (in cc)
##   weight (in grams)
##   value (gold, silver, copper)

##
## New paradigm for fills
##   No object reuse: each fill needs it's location tuple
##   The map will add the id tuple to the fill as it is added
## 
## Fill Concepts
##   use multiple inheritance to add zones and rooms
##   zone: 
##     zonename: the name of the zone
##   room:
##     roomname: the name of the room
##     roomtext: The description of the room
##
## Fill problems:
##   only one void
##   might need more than one void to do proper callbacks on a wall?
##   not if we use a callbackClass that keeps callbacks by id!
##

##
## fill methods
##   listInteractions() should always call the super class first
##   Subclasses should remove interactions they do not want
##   listInteractions() should make a list of interactions
##   listInteractions() should emit messages relating to possible interactions
##   activate() should be called when a character first enters a location
##   enter( self, caller, from ) called when a fill is entered
##   leave( self, caller, to ) called when a fill is exited
##

##
## Brightness
##   None means no specific illumination
##   <=0 means darkness
##   >=1 means brightness
##

##
## This turns out to be a copy of the interactionClass(), so why...
##
## class intentClass( object ):
##   def __init__( self, duration, interruptable, command ):
##     object.__init__( self )
##     self._duration = duration
##     self._interruptable = interruptable
##     self._command = command
##   def command( self ):
##     return self._command

def debug( msg ):
  fp = open( "game.debug", "w" )
  fp.write( "%s\n" % msg )
  fp.close()

import pickle
import base64
import time
import random
import vector
import pdb

##
## Our own little error codes that belong to us!
##
class ERROR( Exception ): pass
class unreachableERROR( ERROR ): pass
class unimplementedERROR( ERROR): pass
class uninitializedERROR( ERROR ): pass
class existsERROR( ERROR ): pass
class internalERROR( ERROR ): pass
class userERROR( ERROR ): pass

def _N( loc ):
  return (loc[0],loc[1]+1,loc[2])
def _S( loc ):
  return (loc[0],loc[1]-1,loc[2])
def _E( loc ):
  return (loc[0]+1,loc[1],loc[2])
def _W( loc ):
  return (loc[0]-1,loc[1],loc[2])
def _U( loc ):
  return (loc[0], loc[1], loc[2] + 1)
def _D( loc ):
  return (loc[0], loc[1], loc[2] - 1)

class messageClass( object ):
  def __init__( self ):
    super( messageClass, self).__init__()
    self._messages = []
    self._debugs = []
    self._errors = []
    self._warnings = []

  def getErrors( self ):
    return reversed( self._errors )
  def getMessages( self ):
    return reversed( self._messages )
  def getWarnings( self ):
    return reversed( self._warnings )
  def getDebugs( self ):
    return reversed( self._debugs )
  def reset( self ):
    self._errors = []
    self._warnings = []
    self._messages = []
    self._debugs = []
  def _dewakka( self, s ):
    return s.replace( '<', '&lt;' ).replace( '>', '&gt;' )
  def addMessage( self, msg ):
    if msg:
      self._messages.append( '%d: %s' % (gameClass().turn(), self._dewakka( msg )) )
  def addWarning( self, msg ):
    self._warnings.append( '%d: %s' % (gameClass().turn(), self._dewakka( msg )) )
  def addError( self, msg ):
    self._errors.append( '%d: %s' % (gameClass().turn(), self._dewakka( msg )) )
  def addDebug( self, msg ):
    self._debugs.append( '%d: %s' % (gameClass().turn(), self._dewakka( msg )) )

class gameClass( object ):
  _map = None
  _denizens = []
  _turn = 0
  _messages = []
  _debug = False
  _players = []

  def play( self ):
    nextTurn = {}
    while gameClass._players:
      for d in gameClass._denizens:
#        print( '%d' % gameClass._turn )
        if d in nextTurn:
          if nextTurn[d][0] <= gameClass._turn:
#            print( '%d: %s is moving: %s' % (gameClass._turn, d.id(), nextTurn[d][1]) )
            d.interact( d, nextTurn[d][1] )
            nextTurn.pop( d )
        else:
          intent = d.ai()
          if intent:
            nextTurn[d] = (gameClass._turn + intent.duration(), intent.command())
      self.advanceTurn( 1 )

  def setDebug( self, debug=True ):
    gameClass._debug = debug

  def debug( self ):
    return gameClass._debug

  def addDenizen( self, denizen, player=False ):
    if player:
      gameClass._denizens.insert( 0, denizen )
      gameClass._players.append( denizen )
    else:
      gameClass._denizens.append( denizen )

  def updateDenizen( self, denizen ):
    ##
    ## This doesn't do anything yet
    ## Someday denizens might not be stored as a simple list though...
    ##
    pass

  def removeDenizen( self, denizen ):
    ##
    ## Not needed yet
    ##
    pass

  def new( self ):
    start = time.time()
    gameClass._map = mapClass()
    createInn( gameClass._map )
    create_city( gameClass._map )
    random.seed( time.time() ) # AFTER the inn is created
    end = time.time()

  def map( self ):
    return gameClass._map

  def getDenizen( self, loc ):
    ret = []
    for d in gameClass._denizens:
      if loc == d.location():
        ret.append( d )
    return ret

  def listDenizens( self ):
    return gameClass._denizens

  def findDenizen( self, id ):
    for d in gameClass._denizens:
      if d.id() == id:  return d
    return None

  def _wrap( self, data ):
    return base64.urlsafe_b64encode( pickle.dumps( data ) )

  def _unwrap( self, data ):
    return pickle.loads( base64.urlsafe_b64decode( data ) )

  def _checksum( self, data ):
    import md5
    return self._wrap( md5.md5( data ).hexdigest() )

  def newGame( self ):
    return self._wrap( {} )

  def dump( self ):
    d = { 'game:turn':gameClass._turn }
    d.update( gameClass._map.dump() )
    for x in gameClass._denizens:
      d.update( x.dump() )
    d['denizen list'] = [x.id() for x in gameClass._denizens]

    w = { 'data':self._wrap( d ) }
    w['checksum'] = self._checksum( w['data'] )
    return self._wrap( w )

  def load( self, token ):
    w = self._unwrap( token )
    if 'data' in w and 'checksum' in w:
      ##
      ## add the secret here for security
      ##
      if self._checksum( w['data'] ) != w['checksum']:
        raise userERROR
      d = self._unwrap( w['data'] )
      if 'game:turn' in d:
        gameClass._turn = d['game:turn']
##
## All denizens are loaded now, not just the player
##
      gameClass._map.load( d )
      if 'denizen list' in d:
        for dn in d['denizen list']:
          den = gameClass().findDenizen( dn )
          den.load( d )

  def showToken( self, token ):
    w = self._unwrap( token )
    if 'data' in w and 'checksum' in w:
      ##
      ## add the secret here for security
      ##
      if self._checksum( w['data'] ) != w['checksum']:
        raise userERROR
      d = self._unwrap( w['data'] )
      out = []
      for x in d:
        if isinstance( d[x], dict ):
          for y in d[x]:
            out.append( str( x ) +': ' +str( y ) + ' ' + str( d[x][y] ) + '<br>' )
        else:
          out.append( str( x )  + ': ' + str( d[x] )  + '<br>' )
      out.sort() # Python is Stupid
      for x in out:
        print( x )

  def turn( self ):
    return gameClass._turn

  def advanceTurn( self, by ):
    gameClass._turn = gameClass._turn + 1

##
## more than just interuptable=true/false is needed
##
class interactionClass( object) :
  def __init__( self, title, command, hint, duration=10, interruptable=False ):
    super( interactionClass, self ).__init__()
    self._title = title
    self._command = command
    self._hint = hint
    self._duration = duration
    self._interruptable = interruptable
  def title( self ):
    return self._title
  def command( self ):
    return self._command
  def hint( self ):
    return self._hint
  def duration( self ):
    return self._duration
  def interruptable( self ):
    return self.interruptable

class coreClass( object ):
  _ids = {}
  def __init__( self ):
    super( coreClass, self ).__init__()
    self._ascii = 'X'
    self._id = None
    self._title = None
    self._description = None
    self._inventory = {}
  def setTitle( self, title ):
    self._title = title
  def setDescription( self, description ):
    self._description = description
  def description( self, caller ):
    return self._description
  def title( self ):
    if self._title:
      return self._title
    else:
      return self.id()
  def setId ( self, id, force=False ):
    ##
    ## FIXME: raise errors not assertions
    ##
    assert id == self._id or not self.id()
    assert ':' not in id
    if not force:
      if id in coreClass._ids:
        if gameClass().debug():
          print( 'DUPLICATE ID', id )
          pdb.set_trace()
      assert id not in coreClass._ids
    self._id = id
    coreClass._ids[id] = self
  def id( self ):
    return self._id
  def ascii( self, caller, loc ):
    return self._ascii
  def setAscii( self, ascii ):
    self._ascii = ascii
  def listInteractions( self, caller ):
    return []
  def interact( self, caller, cmd ):
    return None
  def activate( self, caller ):
    return None
  def proximate( self, caller ):
    return None

##
## Inventory
##
## hasInventory( self, caller, item )
## removeInventory( self, caller, item )
## addInventory( self, caller, item )
## listInventory( self, caller )
##
## The inventory will be keyed by id()
##
class objectClass( coreClass ):
  def __init__( self, id, title, count ):
    super( objectClass, self ).__init__()
    self.setId( id )
    self.setTitle( title )
    self._count = count
  def canCombine( self, other ):
    return False
  def combine( self, other ):
    pass

class characterClass( coreClass ):
  def __init__( self, id ):
    super( characterClass, self).__init__()
    self._location = (0,0,10000)
    self._states = {'waypoints:list':[], 'falling catches':0}
    self._au = 0
    self._ag = 0
    self._cu = 0
    self._msg = messageClass()
    self.setId( id )
    self._mapSize = 12
    self._moved = False
  def broadcast( self, dist, message ):
    for d in gameClass().listDenizens():
      if vector.length( vector.subtract( self.location(), d.location() ) ) <= dist:
        d.msg().addMessage( message )
  def moved( self ):
    ##
    ## Used by other objects to know if the character moved 
    ##
    return self._moved
  def ai( self ):
    ##
    ## This method must be overridden.
    ## Each override must:
    ##  self.listInteractions( self )
    raise internalERROR
  def ascii( self, caller ):
    return '@'
  def id( self ):
    return self._id
  def msg( self ):
   return self._msg
  def getState( self, id, key ):
    k = '%s:%s' % (id, key)
    if k in self._states:
      return self._states[k]
    else:
      return None
  def au( self ):
    return self._au
  def ag( self ):
    return self._ag
  def cu( self ):
    return self._cu
  def addAu( self, au ):
    self._au = self._au + au
  def removeAu( self, au ):
    self._au = self._au - au
    assert self._au >= 0
  def addAg( self, ag ):
    self._ag = self._ag + ag
  def removeAg( self, ag ):
    self._ag = self._ag - ag
    assert self._ag >= 0
  def addCu( self, cu ):
    self._cu = self._cu + cu
  def removeCu( self, cu ):
    self._cu = self._cu - cu
    assert self._cu >= 0
  def setState( self, id, key, data ):
    self._states['%s:%s' % (id, key)] = data
  def location( self ):
    return self._location
  def setLocation( self, location ):
    if mapClass().getFill( location[0], location[1], location[2] ).isPassable( self ):
      ##
      ## FIXME I'm not sure this is a good idea...
      ##
      if location != self._location:
        self._moved = True
      self._location = location
      self.activate()
      self.proximate()
      gameClass().updateDenizen( self )  
    else:
      raise internalERROR
  def dumpV1( self ):
    d = {}
    d['character:%s:location'%self.id()] = self._location
    d['character:%s:states'%self.id()] = self._states
    d['character:%s:au'%self.id()] = self._au
    d['character:%s:ag'%self.id()] = self._ag
    d['character:%s:cu'%self.id()] = self._cu
    d['character:%s:moved'%self.id()] = self._moved
    return d
  def loadV1( self, d ):
    if 'character:%s:location'%self.id() in d:
      self._location = d['character:%s:location'%self.id()]     
      if 'character:%s:states'%self.id() in d:
        self._states.update( d['character:%s:states'%self.id()] )
      if 'character:%s:au'%self.id() in d:
        self._au = d['character:%s:au'%self.id()]
      if 'character:%s:ag'%self.id() in d:
        self._ag = d['character:%s:ag'%self.id()]
      if 'character:%s:cu'%self.id() in d:
        self._cu = d['character:%s:cu'%self.id()]
      if 'character:%s:moved'%self.id() in d:
        self._moved = d['character:%s:moved'%self.id()]
  def dump( self ):
    return self.dumpV1()
  def load( self, data ):
    return self.loadV1( data )
  def activate( self ):
    m = mapClass()
    x = self.location()[0]
    y = self.location()[1]
    z = self.location()[2]
    m.getFill( x, y, z ).activate( self )
    for feature in m.listFeatures( self, x, y, z ):
      feature.activate( self )
  def proximate( self ):
    start = time.time()
    m = mapClass()
    l = self.location()
    for x in [-1,0,1]:
      for y in [-1,0,1]:
        for z in [-1,0,1]:
          if x == 0 and y == 0 and z == 0:
            continue
          m.getFill( l[0]+x, l[1]+y, l[2]+z ).proximate( self )
          for f in m.listFeatures( x, y, z, self ):
            f.proximate( x, y, z )
    end = time.time()
    self.msg().addDebug( "characterClass().proximate() ran in %f seconds" % (end-start) )

  def interact( self, caller, command ):
#    self._msg.addMessage( 'interact( %s, %s, %s )' % (str( self ), str( caller ), str( command )) )
#    print( 'characterClass().interact()', self.id(), caller.id(), command )
    self._moved = False
    descend = (self == caller)
    start = time.time()
    t = 1
    found = False
    m = mapClass()      
    
    if gameClass().debug() and command =='pdb':
      import pdb
      pdb.set_trace()
      return 0
    if command.split( ':' )[0:2 + 1] == ["character",self.id(),"hello"]:
      target = gameClass().findDenizen( command.split( ':' )[3] )
      caller.msg().addMessage( 'You say "hello" to %s.' % target.id() )
      target.msg().addMessage( '%s says hello to you.' % caller.id() )
      found = True
    elif command.startswith( "character:%s:move:wait"%self.id() ):
        found = True
    elif command.startswith( "character:%s:move:"%self.id() ):
      self._moved = True
      dir = eval( command.split( ':' )[-1] )
      x = self.location()[0] + dir[0]
      y = self.location()[1] + dir[1]
      z = self.location()[2] + dir[2]
      if m.getFill( x, y, z ).isPassable( None ):
        self.setLocation( (x,y,z) )
#        if (abs( dir[0] ) + abs( dir[1] ) + abs( dir[2] )) > 1:
#          t = 1
        found = True
      else:
        ##
        ## This could happen if an NPC closes a door.  NPCs can't close
        ## doors yet.
        ##
        print( '#############################' )
        print( 'self', self.id() )
        print( 'caller', caller.id() )
        print( 'command', command )
        import pdb
        pdb.set_trace()
        raise internalERROR
        
    ##
    ## Look around here
    ##
    if not found or not descend:
      x = self.location()[0]
      y = self.location()[1]
      z = self.location()[2]
      for xoff in [-1, 0, 1]:
        for yoff in [-1, 0, 1]:
          for zoff in [-1, 0, 1]:
            cmd = m.getFill( x+xoff, y+yoff, z+zoff ).interact( self, command  )
            if cmd:
              found = True
#              if isinstance( cmd, int ):
#                t = cmd

    if not found or not descend:
      for f in m.listFeatures( self, x, y, z ):
        cmd = f.interact( self, command )
        if cmd:
          found = True
#          if isinstance( cmd, int ):
#            t = cmd

    if not found and descend:
      for xoff in [-1, 0, 1]:
        for yoff in [-1, 0, 1]:
          for d in gameClass().getDenizen( (x+xoff, y+yoff, z) ):
            if d == self:
              continue
            cmd = d.interact( self, command )
            if cmd:
              found = True
#              if isinstance( cmd, int ):
#                t = cmd
                
    if not found:
      ##
      ## With the advent of time based intentions, this case
      ## is suddenly possible and no longer an error.  So make
      ## it into a warning and move on.
      ##
      caller.msg().addMessage( 'Unable to complete command "%s".' % command )
    ##
    ## FALLING!
    ##
    def isFallingAt( c, l ):
      x = l[0]
      y = l[1]
      z = l[2]
      f = mapClass().getFill( x, y, z - 1 )
      if f.isPassable( c ) and not f.allowsUpwardMovement( c ):
        return True
      else:
        return False
    falldist = 0
    falltime = 16
    while isFallingAt( self, self.location() ):
      self._moved = True
      l = self.location()
      x = l[0]
      y = l[1]
      z = l[2]
      falltime = max( 1, int( falltime / 2 ) )
      self.setLocation( ( x, y, z - 1 ) )
      t = t + falltime
      ##
      ## ERROR: A new fill has been entered, the activate() should be called
      ##
      falldist = falldist + 1
      ##
      ## grab a ledge here!
      ##
      if isFallingAt( self, self.location() ):
        grabbed = False
        for xoff in [-1,0,1]:
          if grabbed:
            break
          for yoff in [-1,0,1]:
            if grabbed:
              break
            l = self.location()
            if xoff == 0 and yoff == 0:
              continue
            if not m.getFill( l[0]+xoff, l[1]+yoff, l[2] ).isPassable( self ):
              continue
            if not isFallingAt( self, (l[0]+xoff, l[1]+yoff, l[2]) ):
              if random.randint( 0, 16 ) <= self._states['falling catches']:
                self._msg.addMessage( 'You grab a ledge!' )
                self._states['falling catches'] = self._states['falling catches'] + 1
                self.setLocation( (l[0]+xoff, l[1]+yoff,l[2]) )
                grabbed = True
              else:
                self._msg.addMessage( 'You fly past an opening.' )

    if falldist:
      self._msg.addMessage( 'You fell %d fills at a terminal velocity of %d time units per fill.' % (falldist,falltime) )
    
    x = self.location()[0]
    y = self.location()[1]
    z = self.location()[2]
    features = m.listFeatures( self, x, y, z )
    for f in features:
      d = f.description( self )
      if d:
        self._msg.addMessage( d )

    end = time.time()
    self._msg.addDebug( 'characterClass().interact() ran in %f seconds' % (end - start) )
    d = mapClass().getFill( x,y,z ).description( self )
    if d:
      self._msg.addMessage( d )

  def listInteractions( self, caller ):
    descend = (self == caller)
    start = time.time()
    ret = []

    m = mapClass()
    ##
    ## movement first!
    ## 
    x = self.location()[0]
    y = self.location()[1]
    z = self.location()[2]

    if self == caller:
      ret.append( interactionClass( "Wait", "character:%s:move:wait"%self.id(), "character:move:Wait" ) )
  
      hint = { (-1,1,0):'character:move:NW', (0,1,0):'character:move:N', (1,1,0):'character:move:NE',
               (-1,0,0):'character:move:W', (1,0,0):'character:move:E',
               (-1,-1,0):'character:move:SW', (0,-1,0):'character:move:S', (1,-1,0):'character:move:SE',
               (0,0,1):'character:move:Up', (0,0,-1):'character:move:Down' }
  
      title = { (-1,1,0):'Northwest', (0,1,0):'North', (1,1,0):'Northeast',
               (-1,0,0):'West', (1,0,0):'East',
               (-1,-1,0):'Southwest', (0,-1,0):'South', (1,-1,0):'Southeast',
               (0,0,1):'Up', (0,0,-1):'Down' }
  
      zoff = 0
      for xoff in [-1, 0, 1]:
        for yoff in [-1, 0, 1]:
          if m.getFill( x+xoff, y+yoff, z+zoff ).isPassable( None ):
            if xoff == 0 and yoff == 0 and zoff == 0:
              pass
            else:
              dir = (xoff,yoff,zoff)
              if (xoff + yoff + zoff) == 1:
                duration = 10
              else:
                duration = 14
              ret.append( interactionClass( title[dir], "character:%s:move:%s" % (self.id(),str( dir )), hint[dir], duration ) )
      if m.getFill( x, y, z ).allowsDownwardMovement( None ):
        if m.getFill( x, y, z-1).isPassable( None ):
          dir = (0,0,-1)
          ret.append( interactionClass( title[dir], "character:%s:move:%s" % (self.id(),str( dir )), hint[dir] ) )
      if m.getFill( x, y, z ).allowsUpwardMovement( None ):
        if m.getFill( x, y, z+1).isPassable( None ):
          dir = (0,0,1)
          ret.append( interactionClass( title[dir], "character:%s:move:%s" % (self.id(),str( dir )), hint[dir] ) )

    ##
    ## Now we should scan for other interactions.  Such as a door!
    ##
    if descend:
      for xoff in [-1, 0, 1]:
        for yoff in [-1, 0, 1]:
          for zoff in [-1, 0, 1]:
            ret.extend( m.getFill( x+xoff, y+yoff, z+zoff ).listInteractions( self ) )
      for feature in  m.listFeatures( self, x, y, z ):
        ret.extend( feature.listInteractions( self ) )

    ##
    ## Find nearby denizens
    ## 
    for xoff in [-1,0,1]:
      for yoff in [-1,0,1]:
        for d in gameClass().getDenizen( (x+xoff, y+yoff, z) ):
          if self == d: continue
          if descend:
            ret.extend( d.listInteractions( self ) )
          if caller == self: 
            ret.append( interactionClass( "Hello %s" % d.id(), "character:%s:hello:%s"%(self.id(),d.id()), None ) )

    end = time.time()
    self._msg.addDebug( 'characterClass().listInteractions() ran in %f seconds' % (end - start) )

    if caller == self and gameClass().debug():
      ret.append( interactionClass( 'pdb', 'pdb', None ) )
        
    return ret

  def getMap( self, map, version=0 ):
    if version == 0:
      return self._getMap0( map )
    else:
      return self._getMap1( map )

  def _getMap1( self, map ):
    size = self._mapSize
    
  def _getMap0( self, map ):  
    size = self._mapSize
    d = { 'size': size}
    upper = size + 1
    lower = -size
##
## If the getMap() is slow, uncomment the following two lines to override upper and lower to 1 and 0
##
#    upper = 1
#    lower = 0
    for z in range( lower, upper ):
      m = []
      y = self.location()[1] + size
      while y >= self.location()[1] - size:
        m.append( [] )
        for x in range( self.location()[0]-size, self.location()[0] + size + 1 ):
          if not map.getFill( x, y, self.location()[2] + z):
            print( 'What?' )
          sl = self.location()
          if z == 0 and x == sl[0] and y == sl[1]:
            m[-1].append( '@' )
          else:
            m[-1].append( map.getFill( x, y, self.location()[2] + z).ascii( self, (x, y, self.location()[2] + z) ) )
        y = y -1 
      d[z] = m
    return d
class zoneClass( object ):
  def zoneName( self ): return 'NO ZONE'

##
## A fill is the contents of a cube in the map.  The fill title is like
## a room name.  A 3x3 room will have 9 fills of the same title.  The
## zone is the collection of rooms.  Eventually zone traits will come
## from the zone.
##
class fillClass( coreClass, zoneClass ):
  def __init__( self ):
    super( fillClass, self ).__init__( )
    self._id = None
    self._ascii = '*'
    self._inventory = {}
  def id( self ):
    return self._id
  def isPassable( self, caller ):
    raise unimplementedERROR
  def allowsUpwardMovement( self, caller ):
    return False
  def allowsDownwardMovement( self, caller ):
    return False
  def ascii( self, caller, loc ):
    denizens = gameClass().getDenizen( loc )
    if denizens:
      return denizens[0].ascii( caller )
    if not self.isPassable( caller ):
      return self._ascii
    below = mapClass().getFill( loc[0],loc[1],loc[2] - 1 )
    if below.isPassable( None ) and not below.allowsUpwardMovement( None ):
      return ' '
    else:
      ##
      ## look for features and mark them on the map
      ##
      if mapClass().listFeatures( caller, loc[0], loc[1], loc[2] ):        
        return ':' # FIXME!  This will require a lot of work to fix...
      else:
        return self._ascii

##
## The void is any location without an explicit fill
##
#class voidFillClass( fillClass ):
#  def __init__( self, title=None ):
#    super( voidFillClass, self ).__init__( )
#    self.setTitle( 'The Void' )
#    self.setAscii( '*' )
#  def isPassable( self, caller ):
#    return False

##
## Solids are walls, floors, and ceilings
##
class solidFillClass( fillClass ):
  def __init__( self ):
    super( solidFillClass, self ).__init__()
    self.setTitle( 'Solid Stone' )
    self.setAscii( '#' )
  def isLit( self, caller ):
    raise internalERROR
  def blocksLOS( self, caller ):
    return True
  def isPassable( self, caller ):
    return False

##
## Open fills are where the player moves
##
class openFillClass( fillClass ):
  def __init__( self ):
    super( openFillClass, self ).__init__()
    self._ascii = '.'
  def isPassable( self, caller ):
    return True
  def allowsUpwardMovement( self, caller ): return False
  def allowsDownwardMovement( self, caller ): return False
  def activate( self, caller ):
    super( openFillClass, self ).activate( caller )
    if caller.moved():
      pCu = caller.cu()
      pAg = caller.ag()
      pAu = caller.au()
      if pCu < 16 and random.randint( 0, 2 ** (pCu + 5) ) == 0:
        caller.msg().addMessage( 'You found a copper piece!' )
        caller.addCu( 1 )
      elif pAg < 8 and random.randint( 0, 2 ** (pAg + 10) ) == 0:
        caller.msg().addMessage( 'You found a silver piece!' )
        caller.addAg( 1 )
      elif pAu < 4 and random.randint( 0, 2 ** (pAu + 20) ) == 0:
        caller.msg().addMessage( 'You found a gold piece!' )
        caller.addAu( 1 )

##
## A stair will be a fill that you can enter without falling if there is
## no floor.  You can move vertically on a stair.  A stair with an empty
## fill under it is a trap (a one way stair if there is only one blank
## fill beneath it, or a damage causing fall if there is more than one
## blank fill)!  A stair with a solid fill under it is the bottom of the
## stairs.  A stair with a solid fill above it is the top of the stairs.
## A stair with an empty fill above it is a trap as well (you could go
## up the stair, but not come back down).
##
class stairFillClass( openFillClass ):
  def __init__( self ):
    super( stairFillClass, self ).__init__()
    self._ascii = '/'
  def allowsUpwardMovement( self, caller ):
    return True
  def allowsDownwardMovement( self, caller ):
    return True
##
## Doors are harder.  They have a two basic states (open or closed).  An
## open door can either be open or broken.  A closed door can either be
## locked, unlocked, or stuck.  Actually, it could be locked and stuck!
## There should be different kinds of locked and stuck.
##
class doorFillClass( fillClass ):
  def __init__( self, doorName ):
    super( doorFillClass, self ).__init__()
    self._doorName = doorName
    m = mapClass()
    m.setState( doorName, 'open', False )
    m.setState( doorName, 'broken', False )
    m.setState( doorName, 'locked', 0 )
    m.setState( doorName, 'stuck', 0 )
    m.setState( doorName, 'keys', [] )
    self._ascii = '+'
    self.setTitle( 'Door' )
  def isOpen( self, caller ):
    return mapClass().getState( self._doorName, 'open' )
  def isBroken( self, caller ):
    return mapClass().getState( self._doorName, 'broken' )
  def isLocked( self, caller ):
    raise unimplementedError
  def isStuck( self, caller ):
    raise unimplementedError
  def blocksLOS( self, caller ):
    if self.isBroken( caller ):
      return False
    return not self.isOpen( caller )
  def isPassable( self, caller ):
    if self.isOpen( caller ) or self.isBroken( caller ):
      return True
    else:
      return False
  def interact( self, caller, command ):
    found = False
    if command.startswith( "door:close:%s" % str( self._doorName ) ):
      found = 3
      mapClass().setState( self._doorName, 'open', False )
      caller.msg().addMessage( "You close the door." )
    if command.startswith( "door:open:%s" % str( self._doorName ) ):
      found = 3
      mapClass().setState( self._doorName, 'open', True )
      caller.msg().addMessage( "You open the door." )
    if command.startswith( "door:lock:%s" % str( self._doorName ) ):
      if mapClass().getState( self.id(), 'keys' ):
        raise unimplementedERROR
      else:
        found = 5
        mapClass().setState( self._doorName, 'locked', 1 )
        caller.msg().addMessage( "You lock the door." )
    if command.startswith( "door:unlock:%s" % str( self._doorName ) ):
      if mapClass().getState( self._doorName, 'keys' ):
        raise unimplementedERROR
      else:
        found = 5
        mapClass().setState( self._doorName, 'locked', 0 )
        caller.msg().addMessage( "You unlock the door." )
    return found

  def listInteractions( self, caller):
    m = mapClass()
    ret = []
    if caller.location() != self.id():
      if m.getState( self._doorName, 'open' ):
        ret.append( interactionClass( "Close Door", "door:close:%s" % str( self._doorName ), None ) )
      else:
        if not mapClass().getState( self._doorName, 'locked' ):
          ret.append( interactionClass( "Open Door", "door:open:%s" % str( self._doorName ), None ) )
        if m.getState( self._doorName, 'keys' ):
          if self._locked:
            ret.append( interactionClass( "Unlock Door", "door:unlock:%s" % str( self._doorName ), None ) )
          else:
            ret.append( interactionClass( "Lock Door", "door:lock:%s" % str( self._doorName ), None ) )
    return ret

##
## an opaque fill blocks LOS but not movement.  If you are in an opaque
## fill, then you can see in all directions out of it.  Examples of
## opaque squares would be curtains and smoke.
##
class opaqueFillClass( fillClass ):
  def blocksLOS( self, caller ):
    return True

class featureClass( coreClass ):
  def __init__( self ):
    super( featureClass,  self ).__init__()
    self.setDescription( 'This feature is undescribed.' )
    self._messages = []
  def addMessage( self, message ):
    self._messages.append( message )
  def messages( self ):
    return( self._messages )
  def location( self ):
    return self._location
  def setLocation( self, location ):
    self._location = location

class noWhereLeverClass( featureClass ):
  def __init__( self ):
    super( noWhereLeverClass, self ).__init__()
    self.setDescription( 'This lever has no obvious purpose.' )
    mapClass().setState( 'no where lever', 'pulled', False )
  def listInteractions( self, caller ):
    return [interactionClass( 'pull lever', 'no where lever:pull', 'pull lever' )]
  def interact( self, caller, command ):
    if command == 'no where lever:pull':
      state = mapClass().getState( 'commons lever', 'pulled' )
      caller.msg().addMessage( 'You pull the lever!' )
      mapClass().setState( 'commons lever', 'pulled', not state )
      return 3
    return False

class oneWayUpStairsWarningClass( featureClass ):
  def __init__( self ):
    super().__init__()
    self.setDescription( "These stairs go up, but they don't come down!" )
  
class waypointFeatureClass( featureClass ):
  _waypoints = {}
  def __init__( self, title, x, y, z ):
    super( waypointFeatureClass, self ).__init__()
    self._title = title
    self._location = (x, y, z)
    self._waypoints[(x,y,z)] = self
  def title( self, caller ):
    return self._title
  def location( self ):
    return self._location
  def description( self, caller ):
    return 'Offical Waypoint: This is location ' + str( self._location ) + '.'
  def activate( self, caller ):
    super( waypointFeatureClass, self ).activate( caller )
    waypoints = caller.getState( 'waypoints', 'list' )
    if self.location() not in waypoints:
      caller.msg().addMessage( 'Waypoint %s activated.' % self.title( None ) )
      waypoints.append( self.location() )
      caller.setState( 'waypoints', 'list', waypoints )
  def listInteractions( self, caller ):
    ret = []
    waypoints = caller.getState( 'waypoints', 'list' )
    for waypoint in waypoints:
      if self.location() != waypoint:
        wp = self._waypoints[waypoint]
        ret.append( interactionClass( 'Waypoint to %s' % wp.title( caller ), 'waypoint:%s' % str( wp.location() ), 'waypoint:%s' % str( wp.location() ) ) )
    return ret

  def interact( self, caller, command ):
    if command.startswith( 'waypoint:' ):
      dest = tuple( int( x ) for x in command[9:][1:-1].split( ',' ) )
      caller.setLocation( dest )
      caller.msg().addMessage( 'This is just like that movie Stargate.' )
      return 1
    return None

##
## Most things will move through open fills.  If something moves into a
## square without a solid fill beneath it, then it falls.  Stairs are
## special.  They are most often treated as open fills.  If you are in a
## stair fill then you can move up or down if there is a stair fill or
## an open fill above or below you.  I assume stairs are spiral, so they
## block line of sight.
##
## The mapClass keeps track of where everything is.  Everything, so far,
## is fills, objects, and features.  Characters (player and non-player)
## need to go in there too.
##
## Eventually the map should be backed by an SQL database instead of
## being crafted on the fly.
##
## There needs to be a way to dump the state so that it can be passed
## back and forth between web page views.
##
## The map holds state for the fills.  All fills query the map to find
## out anything they need to find out.  They should use the format
## 'fillname:location:trait' for the key.
##
class mapClass( object ):
  _fills = {}
  _features = {}
  _states = {}
  _msg = messageClass()
  _lx = 0
  _ly = 0
  _lz = 0
  _ux = 0
  _uy = 0
  _uz = 0
  _void = None
  def __init__( self ):
    super( mapClass, self ).__init__()
  def msg( self ):
    return self._msg
  def setMakeVoid( self, func ):
    mapClass._void = func
  def load( self, d ):
    if 'map:states' in d:
      self._states.update( d['map:states'] )
  def dump( self ):
    d = { 'map:states':mapClass()._states }
    return( d )
  def getState( self, id, key ):
    k = '%s:%s' % (id, key)
    if k in self._states:
      return self._states[k]
    else:
      return None
  def setState( self, id, key, data ):
    if None == data:
      if '%s:%s' % ( id, key) in self._states:
        self._states.pop( '%s:%s' % (id, key) )
    else:
      self._states['%s:%s' % (id, key)] = data
  def dumpStates( self ):
    for x in self._states:
      print( x, self._states[x] )
  def _bounds( self, x, y, z ):
    if x < self._lx:
      self._lx = x
    if x > self._ux:
      self._ux = x
    if y < self._ly:
      self._ly = y
    if y > self._uy:
      self._uy = y
    if z < self._lz:
      self._lz = z
    if z > self._uz:
      self._uz = z
  def lowerBounds( self ):
    return (self._lx, self._ly, self._lz)
  def upperBounds( self ):
    return (self._ux, self._uy, self._uz)
  def countFills( self ):
    return len( self._fills.keys() )
  def _setFill( self, x, y, z, f, force ):
    assert f
    if not force and (x,y,z) in self._fills:
      debug( 'Exists: %s %s %s' % ((x,y,z),f,f.title()) )
      raise existsERROR
    f.setId( (x,y,z), force )
    self._bounds( x, y, z )
    self._fills[(x,y,z)] = f
  def setFill( self, x, y, z, f, force=False ):
    if not f.title():
      self._msg.addDebug( 'Fill %s %s has no title.' % (str( (x,y,z) ),f) )
    return( self._setFill( x, y, z, f, force ) )
  def forceSetFill( self, x, y, z, f ):
    return self._setFill( x, y, z, f, True )
  def hasFill( self, x, y, z ):
    return (x,y,z) in self._fills
  def getFill( self, x, y, z ):
    if (x,y,z) in self._fills:
      return( self._fills[(x,y,z)] )
    else:
      void = self._void( (x,y,z) )
      return( void )
  def addFeature( self, x, y, z, feature ):
    feature.setLocation( (x,y,z) )
    if (x,y,z) in self._features:
      self._features[(x,y,z)].append( feature )
    else:
      self._features[(x,y,z)] = [feature]
  def listFeatures( self, caller, x, y, z ):
    if (x,y,z) in self._features:
      return self._features[(x,y,z)]
    else:
      return []
  def encaseOpen( self, fill ):
    self._msg.addDebug( 'Map has %d defined fills' % self.countFills() )
    for loc in self._fills.keys():
      if isinstance( self._fills[loc], openFillClass) or issubclass( self._fills[loc].__class__, doorFillClass ):
        for x in range( -1, 1 + 1 ):
          for y in range( -1, 1 + 1 ):
            for z in range( -1, 1 + 1 ):
              if (x+loc[0],y+loc[1],z+loc[2]) not in self._fills:
                self.setFill( x+loc[0], y+loc[1], z+loc[2], fill() )
              
    self._msg.addDebug( 'Map has %d total fills' % self.countFills() )
  def validate( self ):
    ret = True
    for loc in self._fills.keys():
      if isinstance( self._fills[loc], openFillClass):
        for x in range( -1, 1 + 1 ):
          for y in range( -1, 1 + 1 ):
            for z in range( -1, 1 + 1 ):
              if (x+loc[0],y+loc[1],z+loc[2]) not in self._fills:
                print( loc, self._fills[loc], 'not bounded at', (x+loc[0],y+loc[1],z+loc[2]) )
                ret = False
    return ret

  ##
  ## This is just for testing.  It won't work for real since the map
  ## icon for an open fill depends on the fill beneath the current z
  ## location, and individual fills don't know their own coordinates.
  ##
  def ascii( self, minx, miny, maxx, maxy, z ):
    import sys
    y = maxy
    while y >= miny:
      for x in range( minx, maxx + 1):
        sys.stdout.write( self.getFill( x, y, z ).ascii() )
      y = y - 1
      print()


##
## Here starts the inn, I think
##
def innMakeVoid( self, loc ):
  if loc[2] >= 10000:
    return surfaceOpenFillClass()
  else:
    return solidFillClass()
mapClass().setMakeVoid( innMakeVoid )

originFeature = waypointFeatureClass( 'The Origin', 0, 0, 0 )
leverFeature = noWhereLeverClass()

class lonelyInnZoneClass( zoneClass ):
  def zoneName( self ): return 'The Lonely Inn'

class sewerZoneClass( zoneClass ):
  def zoneName( self ): return 'The Sewers'

class nowhereZoneClass( zoneClass ):
  def zoneName( self ): return 'The Tunnel To Nowhere'

class surfaceOpenFillClass( openFillClass ):
  def __init__( self ):
    super( surfaceOpenFillClass, self ).__init__()
    self._ascii = '%'
  def zoneName( self ): return 'The Surface'
  
class innCommonRoomClass( openFillClass, lonelyInnZoneClass ):
  def __init__( self ):
    super( innCommonRoomClass, self ).__init__()
    self.setTitle( "Common Room" )
  
class innGuestRoomClass( openFillClass, lonelyInnZoneClass ):
  def __init__( self ):
    super( innGuestRoomClass, self ).__init__()
    self.setTitle( "Guest Room" )
  
class innDoorClass( doorFillClass, lonelyInnZoneClass ):
  def __init__( self, doorName, inside ):
    super( innDoorClass, self ).__init__( doorName )
    self._inside = inside
  def inside( self ):
    return self._inside
  def listInteractions( self, caller):
    m = mapClass()
    ret = super( innDoorClass, self ).listInteractions( caller )
    if not self._doorName: raise internalERROR
    if caller.location() != self.id():
      if not m.getState( self._doorName, 'open' ):
        if m.getState( self._doorName, 'locked' ):
          if caller.location()[0] == self.inside():
            ret.append( interactionClass( "Unlock Door", "door:unlock:%s" % str( self._doorName ), None ) )
        else:
          if caller.location()[0] == self.inside():
            ret.append( interactionClass( "Lock Door", "door:lock:%s" % str( self._doorName), None ) )
  
    return ret
  
class innStairClass( stairFillClass, lonelyInnZoneClass ):
  def __init__( self ):
    super( innStairClass, self ).__init__()
    self.setTitle( "The Lonely Inn" )
 
class tunnelStairClass( stairFillClass ):
  def __init__( self ):
    super( tunnelStairClass, self ).__init__()
    self.setTitle( "Stairs To No Where" )
  
class tunnelToNowhereClass( openFillClass, nowhereZoneClass ):
  def __init__( self ):
    super( tunnelToNowhereClass, self ).__init__()
    self.setTitle( 'The Tunnel To No Where' )

class nowhereRoomClass( openFillClass, nowhereZoneClass ):
  def __init__( self ):
    super( nowhereRoomClass, self ).__init__()
    self.setTitle( "No Where" )
  
class commonsRoomClass( openFillClass ):
  def __init__( self ):
    super( commonsRoomClass, self ).__init__()
    self.setTitle( 'The Commons' )
  
class commonsSecretDoorClass( openFillClass ):
  def __init__( self ):
    super( commonsSecretDoorClass, self ).__init__()
    self.setTitle( "Secret Door" )
    self.setAscii( '#' )
  def listInteractions( self, caller ):
    caller.msg().addMessage( 'Hey, an illusionary wall!' )
    return []
class commonsStairClass( stairFillClass ):
  def __init__( self ):
    super( commonsStairClass, self ).__init__()
    self.setTitle( "The Commons" )
class commonsDoorClass( doorFillClass ):
  def __init__( self, doorName ):
    super( commonsDoorClass, self ).__init__( doorName )
  def interact( self, caller, command ):
    caller.msg().addDebug( 'commonsDoorClass' )
    found = False
    if command.startswith( "door:close:%s" % str( self._doorName ) ):
      found = 3
      mapClass().setState( self._doorName, 'open', False )
      caller.msg().addMessage( 'You hear an ominous click.' )
      mapClass().setState( 'commons lever', 'pulled', False )
    if command.startswith( "door:open:%s" % str( self._doorName) ):
      found = 3
      if mapClass().getState( 'commons lever', 'pulled' ) == True:
        mapClass().setState( self._doorName, 'open', True )
        caller.msg().addMessage( 'I bet you are glad you pulled that lever!' )
      else:
        caller.msg().addMessage( 'This door will not open until you pull the Lever of No Where' )
        found = 1
    return found

class commonsUpperDoorClass( doorFillClass ):
  def __init__( self, doorName ):
    super( commonsUpperDoorClass, self ).__init__( doorName )
  def interact( self, caller, command ):
    caller.msg().addDebug( 'commonsDoorClass' )
    found = False
    if command.startswith( "door:open:%s" % str( self._doorName) ):
      found = 3
      if mapClass().getState( 'commons lever', 'pulled' ) == False:
        mapClass().setState( self._doorName, 'open', True )
        caller.msg().addMessage( 'This door opens easily.' )
      else:
        caller.msg().addMessage( 'You are mysteriously unable to open this door.' )
        found = 1
    if found:
      return found
    else:
      return super( commonsUpperDoorClass, self ).interact( caller, command )

class dungeonRoomClass( openFillClass ):
  def __init__( self ):
    super( dungeonRoomClass, self ).__init__()
    self.setTitle( 'Dungeon' )
class dungeonStairClass( stairFillClass ):
  def __init__( self ):
    super( dungeonStairClass, self ).__init__()
    self.setTitle( 'Dungeon Stairs' )


class sewerShaftClass( openFillClass, sewerZoneClass ):
  def __init__( self ):
    super( sewerShaftClass, self ).__init__()
    self.setTitle( 'Sewer Shaft' )
  def proximate( self, caller ):
    if self.id()[2] == caller.location()[2]:
      caller.msg().addMessage( 'The open shaft emits a foul smell.' )

class sewerRoomClass( openFillClass, sewerZoneClass ):
  def __init__( self ):
    super( sewerRoomClass, self ).__init__()
    self.setTitle( 'The Sewer' )
  def activate( self, caller ):
    caller.msg().addMessage( 'It smells bad here.  And whatever you stepped in is ankle deep.' )
    l = self.id()
    if isinstance( mapClass().getFill( l[0], l[1], l[2]+1 ), sewerShaftClass ):
      caller.msg().addMessage( "You are standing below a sewer shaft.  Don't look up." )
class sewerStairClass( stairFillClass, sewerZoneClass ):
  def __init__( self ):
    super( sewerStairClass, self ).__init__()
    self.setTitle( 'The Sewer Stairs' )
  def activate( self, caller ):
    caller.msg().addMessage( 'The bottom of these stairs is not anywhere you want to be.' )

class jobsOfficeSewerDoorClass( doorFillClass ):
  def __init__( self, doorName ):
    super( jobsOfficeSewerDoorClass, self ).__init__( doorName )
    self.setTitle( 'Bathroom Door' )
class jobsOfficeBathRoomClass( openFillClass ):
  def __init__( self ):
    super( jobsOfficeBathRoomClass, self ).__init__()
    self.setTitle( 'Jobs Office Shaft Closet' )

class underbankVaultClass( openFillClass ):
  def __init__( self ):
    super( underbankVaultClass, self ).__init__()
    self.setTitle( 'The Underbank Vault' )
  def activate( self, caller ):
    looted = mapClass().getState( 'vault:%s' % str( self.id() ), 'looted' )
    if not looted:
      loot = [ 1 for x in range( 100 ) ]
      loot.extend( [ 2 for x in range( 10 ) ] )
      loot.extend( [ 3 for x in range( 5 ) ] )
      loot.extend( [ 4 for x in range( 3 ) ] )
      loot.extend( [ 5 for x in range( 2 ) ] )
      loot.extend( [ 6 ] )
      au = random.choice( loot )
      caller.addAu( au )
      caller.msg().addMessage( 'You "find" %d gold!' % au )
      mapClass().setState( 'vault:%s' % str( self.id() ), 'looted', True )

class underbankVaultDoorClass( solidFillClass ):
  def __init__( self ):
    super( underbankVaultDoorClass, self ).__init__()
    self.setTitle( 'The Underbank Vault Door' )
    self.setAscii( '+' )
  def proximate( self, caller ):
    caller.msg().addMessage( 'The vault door is locked and cannot be opened.' )

class underbankSewerDoorClass( doorFillClass ):
  def __init__( self, doorName ):
    super( underbankSewerDoorClass, self ).__init__( doorName )
    self.setTitle( 'The Underbank Sewer Access Door' )
class underbankSewerRoomClass( openFillClass ):
  def __init__( self ):
    super( underbankSewerRoomClass, self ).__init__()
    self.setTitle( 'The Underbank Sewer Access' )

class bankRoomClass( openFillClass ):
  def __init__( self ):
    super( bankRoomClass, self ).__init__()
    self.setTitle( 'The Underbank' )

class bankStairClass( stairFillClass ):
  def __init__( self ):
    super( bankStairClass, self ).__init__()
    self.setTitle( "The Underbank" )

class sleeplessNightsInnHallwayClass( openFillClass ):
  def __init__( self ):
    super( sleeplessNightsInnHallwayClass, self ).__init__()
    self.setTitle( "The Sleepless Nights Inn Entrance Hallway" )

class sleeplessNightsInnDoorClass( doorFillClass ):
  def __init__( self, doorName ):
    super( sleeplessNightsInnDoorClass, self ).__init__( doorName )
    self.setTitle( 'The Sleepless Nights Inn Door' )

class sleeplessNightsInnLobbyClass( openFillClass ):
  def __init__( self ):
    super( sleeplessNightsInnLobbyClass, self ).__init__()
    self.setTitle( "The Sleepless Nights Inn Lobby" )

class commonsWellClass( openFillClass ):
  def __init__( self ):
    super( commonsWellClass, self ).__init__()
    self.setTitle( "The Commons Well" )

class commonsWellStairClass( stairFillClass ):
  def __init__( self ):
    super( commonsWellStairClass, self ).__init__()
    self.setTitle( "The UndercommonsWell" )
commonsWellStair = commonsWellStairClass()

class wellWarningClass( featureClass ):
  def __init__( self ):
    super( wellWarningClass, self ).__init__()
    self.setDescription( 'Caution: deep well' )

class oneWayUpWarningClass( featureClass ):
  def __init__( self ):
    super( wellWarningClass, self ).__init__()
    self.setDescription( 'Caution: The stairs go, but they do not come down.' )
    
class libraryAisleClass( openFillClass ):
  def __init__( self ):
    super( libraryAisleClass, self ).__init__()
    self.setTitle( "The Klein Library: Aisle" )

class libraryPlaqueFeatureClass( featureClass ):
  def __init__( self ):
    super( libraryPlaqueFeatureClass, self ).__init__()
    self.setDescription( 'Dedicated to Josh Klein who donated most of the books housed here.' )

class libraryStacksClass( openFillClass ):
  def __init__( self ):
    super( libraryStacksClass, self ).__init__()
    self.setTitle( "The Klein Library: Stacks" )
  def listInteractions( self, caller ):
    ret = super( libraryStacksClass, self ).listInteractions( caller )
    loc = caller.location()
    if mapClass().getFill( loc[0], loc[1], loc[2] ) == self:
      ret.append( interactionClass( "Browse books", "library:browse", None, 120, True ) )
    return( ret )
  def interact( self, caller, command ):
    books = [ "A History of the Dimwit Flatheads",
              "The Happy Adventurer",
              "Ideas for Book Names",
              "A Brief History of Ozerath",
              "Wimblewort's Four-hundred and Fifty-Six Applications for Old Boots",
              "The Grand Compendium of the History of The Imperial Majesty of Gaxbeginstan",
              "The Travels of Jerry Longshanks",
              "The Furndar Affair",
              "An old leather-bound chronicle that has for better or worse been left almost entirely blank. ",
              "The Order-Keeper's Cookbook",
              "Eight-hundred Years of Waiting: A Treatise on being in a Time out of Place",
              "The Ninth War, The Eigth War, The Seventh War, The Sixth War, The Final War, The Second Great War, The Third War, The First Great War, and The Founding War",
              "The Tax Codes of Meldibourne",
              "The Art of the Sword (with full color illustration) ",
              "The Warm Dead, a thrilling novela of the unquiet dead",
              "A Tattered Manuscript by Robert Jitterjavelin",
              "A Book of Poetry, that Existential Trash",
              "A Book of Poetry, saying with flowery words how bad things are",
              "A Book of Poetry, with social commentary",
              "The Story of Mary and the Three Foolish Kings",
              "Waterstained Blueprints of a Palace in Gurxburginstan that may never have been built",
              "The Book of Names, yes, yours is in it too",
              "A loose-bound book that falls apart as you take it off the shelf. Its unordered pages describe a wonderous scene, only made more wonderous by the utter lack of coherency!",
              "The Karabon Cycle",
              "The Journeys of Sammy B. Flaxson",
              "Sammy B. Flaxson and Jerry Longshanks versus the Mantankerous Menace",
              "Jerry Longshanks and Sammy B. Flaxson versus the Thing that Should Be Named Differently",
              "Viscera and Vittles - A Vintner's Guide to Good Growing. Wine does WHAT to your insides? ",
              "Three Funerals and a Wedlock Birth",
              "The History of Skottham",
              "The History of Shidu-Haral",
              "The Fiction of The Allied Counties of Mercada",
              "Dragons: Where Not To Stand. The book can be summed up by saying \"Within 100 miles\"",
              "Beginner's Alchemy. A recipe for Ashes: 1 piece of Wood, 1 Large Firepit. These Alchemists are brilliant! "
 ]
    if command == 'library:browse':
      if self.id() == (-15,-18,0) and random.choice( [0,1,2,3,4] ) == 0:
        caller.msg().addMessage( 'You accidentally read a teleport spell.' )
        l = mapClass().getState( 'library', 'teleport' )
        caller.setLocation( l )
      else:
        caller.msg().addMessage( 'You browse through %s.' % random.choice( books ) )
      return 50    
  
class jobsOfficeClass( openFillClass ):
  def __init__( self ):
    super( jobsOfficeClass, self ).__init__()
    self.setTitle( "The Jobs Office" )
  def interact( self, caller, command ):
    ret = super( jobsOfficeClass, self ).interact( caller, command )
    if command == 'jobs office:browse' and self.id() == caller.location():
      jobs = [ 'Dungeon Developer: A developer is needed to create more rooms and tunnels for the game.',
               'Librarian: A writer is needed to create more book titles and possible summaries for the library.',
               'Play tester: You already are one.',
               'No Where Expander: A developer is needed to double the length of the Tunnel To No Where and then add a room titled Half Way To No Where in the middle.',
               "Moneychanger Developer: A developer is needed to create a new dungeon section titled Merchant's Way.  The first merchant will be a money changer.  The money changer should charge a modest fee to change money.",
               "Falling Developer: A developer is needed to give falling characters a chance to grab a passing ledge.  This should probably be done via an activate() callback on the fill being passed through.  State is needed on the characterClass of the caller to indicate a fall is in progress.  The fall should stop progress and give the character an interact to actually grab the ledge, allowing them to skip ledges.  The further the fall the harder it should be to grab on (based on terminal velocity).",
               'Treasure Vault Developer: A developer is needed to create a treasure vault at the end of the mysterious tunnel that can be viewed from the suicide stairs in the Underbank.  The vault should have free coins laying on the floor.  Access to the tunnel leading to the vault needs to be added as well.  There should be a tunnel and stairs leading to above the West end of the tunnel and a fall passed the tunnel.  This depends on the falling code modification.',
               'Prostitute Implementer: Once there is a source of money, and a money changer, the obvious next step is a prostitute who only accepts exact change.  This will be a big deal.  Private rooms with locable doors will need to be added to the brothel.  The prostitute will not work if the door is open, and will charge extra if the door is not locked.',
               'Message Repair: Currently all methods assume that all instances of a characterClass() are the player and they pass messages to the UI via the bare messageClass() as class data.  The messageClass() class needs to be reverted back to instance data and stored inside the characterClass() so that NPCs can be added without the player seeing any interact() actions the NPC might make.' ]
      caller.msg().addMessage( 'You read a job posting.  %s' % random.choice( jobs ) )
      ret = 15
    return ret
  def listInteractions( self, caller ):
    ret = super( jobsOfficeClass, self ).listInteractions( caller )
    if self.id() == caller.location():
      ret.append( interactionClass( "Browse job listings", "jobs office:browse", None ) )
    return ret
      
class jobsOfficeDoorClass( doorFillClass ):
  def __init__( self, doorName ):
    super( jobsOfficeDoorClass, self ).__init__( doorName )
    self.setTitle( "The Jobs Office Door" )
  
class marketRowTunnelClass( openFillClass ):
  def __init__( self ):
    super( marketRowTunnelClass, self ).__init__()
    self.setTitle( "Market Row" )

class moneychangersDoorClass( doorFillClass ):
  def __init__( self, doorName ):
    super( moneychangersDoorClass, self ).__init__( doorName )
    self.setTitle( "The Money Changers Door" )
class moneychangersRoomClass( openFillClass ):
  def __init__( self ):
    super( moneychangersRoomClass, self ).__init__()
    self.setTitle( "The Money Changer" )

class hookerRoomClass( openFillClass ):
  def __init__( self, hookerName ):
    super( hookerRoomClass, self ).__init__()
    self.setTitle( "%s's Private Room" % hookerName )
class hookerDoorClass( doorFillClass ):
  def __init__( self, hookerName ):
    self._hookerName = hookerName
    super( hookerDoorClass, self ).__init__( "%s's Door" % hookerName )
    self.setTitle( "%s's Door" % hookerName )
  def proximate( self, caller ):
    caller.msg().addMessage( 'The name on the door is %s.' % self._hookerName )

class moneyChangerClass( characterClass ):
  def ai( self ):
    interacts = self.listInteractions( self )
    for i in interacts:
      if ':hello:' in i.command():
        return i
    return None
  def interact( self, caller, command ):
    if command.startswith( 'exchange:' ):
      if command[-4:] == "auag":
        caller.removeAu( 1 )
        caller.addAg( 10 )
        caller.msg().addMessage( 'You exchange 1 gold for 10 silver.' )
        return 10
      if command[-4:] == "agau":
        caller.removeAg( 10 )
        caller.addAu( 1 )
        caller.msg().addMessage( 'You exchange 10 silver for 1 gold.' )
        return 10
      if command[-4:] == "agcu":
        caller.removeAg( 1 )
        caller.addCu( 10 )
        caller.msg().addMessage( 'You exchange 1 silver for 10 copper.' )
        return 10
      if command[-4:] == "cuag":
        caller.removeCu( 10 )
        caller.addAg( 1 )
        caller.msg().addMessage( 'You exchange 10 copper for 1 silver.' )
        return 10
    else:
      return super( moneyChangerClass, self ).interact( caller, command )
  def listInteractions( self, caller ):
    ret = super( moneyChangerClass, self ).listInteractions( caller )
    if caller.location() == self.location():
      caller.msg().addMessage( 'I think you are looking for the Restless Nights Inn.' )
    if caller.au() > 0:
      ret.append( interactionClass( "Exchange gold for silver", "exchange:auag", None ) )

    if caller.ag() > 0:
      ret.append( interactionClass( "Exchange silver for copper", "exchange:agcu", None ) )
    if caller.ag() >= 10:
      ret.append( interactionClass( "Exchange silver for gold", "exchange:agau", None ) )      

    if caller.cu() > 10:
      ret.append( interactionClass( "Exchange copper for silver", "exchange:cuag", None ) )
    
    return ret

class hookerClass( characterClass ):
  def __init__( self, name, au, ag, cu, shy ):
    super( hookerClass, self ).__init__( name )
    self._auCost = au
    self._agCost = ag
    self._cuCost = cu
    self._shy = shy

  def ai( self ):
    interacts = self.listInteractions( self )
    return None

  def listInteractions( self, caller ):
    open = mapClass().getState( "%s's Door" % self.id(), 'open' )
    locked = mapClass().getState( "%s's Door" % self.id(), 'locked' )
    if locked:
      if self._shy:
        mult = 1
      else:
        mult = 3
    elif not open:
      mult = 2
    else:
      if self._shy:
        mult = 3
      else:
        mult = 1
    au = self._auCost * mult
    ag = self._agCost * mult
    cu = self._cuCost * mult
#      caller.msg().addMessage( "base: %d %d %d open: %s locked: %s shy: %s mult: %d  total: %d %d %d" % (self._auCost, self._agCost, self._cuCost, str( open ), str( locked) , str( self._shy ), mult, au, ag, cu) )
    ret = []    
    ret.extend( super( hookerClass, self ).listInteractions( caller ) )
    if (self != caller) and (self.location() == caller.location()):
      ret.append( interactionClass( "Give %s %d gold, %d silver, %d copper" % (self.id(), au, ag, cu), "pay hooker:%s:%d %d %d" % (self.id(), au, ag, cu), None ) )
    return ret

  def interact( self, caller, command ):
#      print( 'hookerClass().interact()', self.id(), caller.id(), command )

    if command.startswith( "pay hooker:%s:" % self.id() ):
      price = command.split( ':' )[2].split( ' ' )
      au = int( price[0] )
      ag = int( price[1] )
      cu = int( price[2] )
      if au <= caller.au() and ag <= caller.ag() and cu <= caller.cu():
        caller.msg().addMessage( "Money well spent..." )
        caller.removeAu( au )
        caller.removeAg( ag )
        caller.removeCu( cu )
        random.seed( time.time() )
        if random.choice( range( 25 ) ) == 0:
          caller.msg().addMessage( "But what happened?" )
          caller.setLocation( (13, -8, -4) )
        return random.choice( range( 1000, 2000 ) )
      else:
        caller.msg().addMessage( "%s only takes exact change, and you can't afford her!" % self.id() )
        return 5
    else:
      return super( hookerClass, self ).interact( caller, command )

class touristRoomClass( openFillClass ):
  def __init__( self ):
    super( touristRoomClass, self ).__init__()
    self.setTitle( 'Tourist Information' )
  def interact( self, caller, command ):
    ret = super( touristRoomClass, self ).interact( caller, command )
    if command == 'tourist:browse' and self.id() == caller.location():
      brochures = [ 'Visit the inside of the Vault!  Yes, you can get in there without working for the bank.',
                    "No Where is a long way away, but the journey isn't something so bad if you research it first.",
                    "The Money Changer wants to say 'Hello', so stop on by.",
                    "Time to kill?  There are three working waypoints for you to use!",
                    "Bored?  Why not go through the ``secret door''?"
      ]
      caller.msg().addMessage( 'You read a brochure.  %s' % random.choice( brochures ) )
      ret = 15
    return ret
  def listInteractions( self, caller ):
    ret = super( touristRoomClass, self ).listInteractions( caller )
    if self.id() == caller.location():
      ret.append( interactionClass( "Browse brochures", "tourist:browse", None ) )
    return ret

class elevporterFeatureClass( featureClass ):
  def __init__( self, dest ):
    super( elevporterFeatureClass, self ).__init__()
    self.setDescription( 'Like an elevator, except without the shaft.' )
    self._dest = dest
  def interact( self, caller, command ):
    ret = super( elevporterFeatureClass, self ).interact( caller, command )
#    caller.msg().addMessage( 'self._dest: %s' % str( self._dest ) )
#    caller.msg().addMessage( 'self.location(): %s' % str( self.location() ) )
#    caller.msg().addMessage( 'caller.location(): %s' % str( caller.location() ) )
#    caller.msg().addMessage( 'command: %s' % str( command ) )
    if command == 'elevporter:port:%s' % str(self._dest) and self.location() == caller.location():
      caller.msg().addMessage( 'You Elevport!' )
      caller.setLocation( self._dest )
      ret = 5 # elevporters are fast
    return ret


  def listInteractions( self, caller ):
    ret = super( elevporterFeatureClass, self ).listInteractions( caller )
    if self.location() == caller.location():
      ret.append( interactionClass( "Take the elevporter", "elevporter:port:%s" % str( self._dest ), None ) )
    return ret

class touristElevporterRoomClass( openFillClass ):
  def __init__( self ):
    super( touristElevporterRoomClass, self ).__init__()
    self.setTitle( 'Elevporter To The Surface' )

class farmElevporterRoomClass( openFillClass ):
  def __init__( self ):
    super( farmElevporterRoomClass, self ).__init__()
    self.setTitle( 'Elevporter To The G.U.E.' )


class farmRoomClass( openFillClass ):
  def __init__( self ):
    super( farmRoomClass, self ).__init__()
    self.setTitle( "Alli's Surface Farm" )

class farmSoilClass( solidFillClass ):
  def __init__( self ):
    super( farmSoilClass, self ).__init__()
    self.setTitle( 'Rich Fertile Soil' )
    self.setAscii( '%' )
  def proximate( self, caller ):
    if caller.location() != _U( self.id() ): return None
    turnips = mapClass().getState( self.id(), 'turnips' )
    if not turnips:
      turnips = 0
    if random.choice( range( 10 + turnips ) ) == 0:
      turnips = turnips + 1
      mapClass().setState( self.id(), 'turnips', turnips )
    if turnips == 1:
      caller.msg().addMessage( 'There is a turnip growing here.' )
    elif turnips > 1:
      caller.msg().addMessage( 'There are %d turnips growing here.' % turnips )
    return None

class turnipSeekingClass( characterClass ):
  def ai( self ):
    loc = self.location()
    l = _D( loc )
    f = mapClass().getFill( l[0], l[1], l[2] )
    turnips = mapClass().getState( f.id(), 'turnips' )
    if turnips:
      self.broadcast( 1, '%s picks %d turnips from the ground.' % (self.id(), turnips) )
      mapClass().setState( f.id(), 'turnips', None )
      return None
    else:
      turnips = 0
    count = 0
    at = (0,0,0)
    for x in [-1, 0, 1]:
      for y in [-1, 0, 1]:
        if x == 0 and y == 0: continue
        l = (loc[0] + x, loc[1] + y, loc[2])
        f = mapClass().getFill( l[0], l[1], l[2] - 1 )
        turnips = mapClass().getState( f.id(), 'turnips' )
        if turnips and turnips > count:
          count = turnips
          at = (x, y, 0)

    interactions = self.listInteractions( self )
    moves = [x for x in interactions if ':move:' in x.command()]
    if count:
      self.broadcast( 3, '%s spots something in the ground nearby!' % self.id() )
      return [x for x in moves if str( at ) in x.command()][0]
    else:
      return random.choice( moves )
    return None

class wanderClass( characterClass ):
  def ai( self ):
    interactions = self.listInteractions( self )
    moves = [x for x in interactions if ':move:' in x.command()]
    return random.choice( moves )

class firstAidRoomClass( openFillClass ):
  def __init__( self ):
    super( firstAidRoomClass, self ).__init__()
    self.setTitle( "First Aid Station" )

class fountainRoomClass( openFillClass ):
  def __init__( self ):
    super( fountainRoomClass, self ).__init__()
    self.setTitle( "The Fountain Room" )

class apshaiRoomClass( openFillClass ):
  def __init__( self ):
    super( apshaiRoomClass, self ).__init__()
    self.setTitle( "The Temple Of Apshai" )

class apshaiPillarClass( solidFillClass ):
  def __init__( self ):
    super( apshaiPillarClass, self ).__init__()
    self.setTitle( "A Pillar Of Apshai" )

class apshaiRoomClass( openFillClass ):
  def __init__( self ):
    super( apshaiRoomClass, self ).__init__()
    self.setTitle( "The Temple Of Apshai" )

class uselessLeverClass( featureClass ):
  def __init__( self ):
    super( uselessLeverClass, self ).__init__()
    self.setDescription( 'This lever has no obvious purpose.' )
  def listInteractions( self, caller ):
    return [interactionClass( 'pull lever', 'useless lever:pull', 'pull lever' )]
  def interact( self, caller, command ):
    if command == 'useless lever:pull':
      caller.msg().addMessage( 'You pull the lever!' )
      return 3
    return False

class stayAwayClass( characterClass ):
  def ai( self ):
    self.broadcast( 2, '%s warns you not to come any closer or she will show you on herself where she wants the bad person to touch her.' % self.id() )

def createInn( inn ):
  ##
  ## Inn: my prototype inn
  ##
  inn.addFeature( 0, 0, 0, originFeature )
#  inn.setVoid( solidFillClass )
  z = 0
  for x in range( -3, 3 + 1 ):
    for y in range( -8, 8 + 1):
      inn.setFill( x, y, z, innCommonRoomClass() )
      inn.setFill( x, y, z + 1, innCommonRoomClass() )
      inn.setFill( x, y, z + 3, innCommonRoomClass() )

  for x in range( -4, 4 + 1 ):
    for y in range( -9, 9 + 1):
      inn.setFill( x, y, z + 2, innCommonRoomClass() )

  for x in range( -2, 2 + 1 ):
    for y in range( -7, 7 + 1):
      inn.setFill( x, y, z + 4, innCommonRoomClass() )


  inn.setFill( -4, 0, z, innDoorClass( 'Inn Door 1',-5 ) ) # should be a door
  basex = -6
  basey = 0
  for x in range( -1, 1 + 1 ):
    for y in range( -1, 1 + 1 ):
      inn.setFill( basex + x, basey + y, z, innGuestRoomClass() )
  
  inn.setFill( 4, 0, z, innDoorClass( 'Inn Door 2', 5 ) ) # should be a door
  basex = 6
  basey = 0
  for x in range( -1, 1 + 1 ):
    for y in range( -1, 1 + 1 ):
      inn.setFill( basex + x, basey + y, z, innGuestRoomClass() )

  inn.setFill( 4, 8, z, innDoorClass( 'Inn Door 3', 5 ) ) # should be a door
  basex = 6
  basey = 8
  for x in range( -1, 1 + 1 ):
    for y in range( -1, 1 + 1 ):
      inn.setFill( basex + x, basey + y, z, innGuestRoomClass() )

  inn.setFill( 4, -8, z, innDoorClass( 'Inn Door 4', 5 ) ) # should be a door
  basex = 6
  basey = -8
  for x in range( -1, 1 + 1 ):
    for y in range( -1, 1 + 1 ):
      inn.setFill( basex + x, basey + y, z, innGuestRoomClass() )

  inn.setFill( -4, 8, z, innDoorClass( 'Inn Door 5', -5 ) ) # should be a door
  basex = -6
  basey = 8
  for x in range( -1, 1 + 1 ):
    for y in range( -1, 1 + 1 ):
      inn.setFill( basex + x, basey + y, z, innGuestRoomClass() )

  inn.setFill( -4, -8, z, innDoorClass( 'Inn Door 6', -5 ) ) # should be a door
  basex = -6
  basey = -8
  for x in range( -1, 1 + 1 ):
    for y in range( -1, 1 + 1 ):
      inn.setFill( basex + x, basey + y, z, innGuestRoomClass() )

  inn.setFill( -3, 9, 0, innCommonRoomClass() )
  inn.setFill( -3, 10, 0, innCommonRoomClass() )
  inn.setFill( -3, 11, 0, innCommonRoomClass() )
  inn.setFill( -3, 12, 0, innStairClass() )
  inn.setFill( -3, 12, 1, innStairClass() )
  inn.setFill( -3, 12, 2, innStairClass() )
  
  ##
  ## The tunnel to nowhere
  ##
  import random
  random.seed( 79 ) # always make the same tunnel
  
  def tunnellen():
    return random.randint( 4, 11 )
  
  def stairlen():
    if random.randint( 0, 5 ) == 0:
      return 2
    else:
      return random.randint( 3, 6 )
  
  def direction( last ):
    dirs = [(1,0,0), (-1,0,0), (0,0,1), (0,0,-1)]
    try:
      dirs.remove( (last[0]*-1, last[1]*-1, last[2]*-1) )
      dirs.remove( last )
    except:
      pass
    return random.choice( dirs )

  ##
  ## It goes North
  ##
  dir = (0,1,0)
  count = 16
  x = -3
  y = 12
  z = 2
  flip = 0
  tunnelLength = 100 # normally 100
  for i in range( 0, tunnelLength ):
    while count:
      if dir[0] or dir[1]:
        inn.setFill( x+dir[0], y+dir[1], z+dir[2], tunnelToNowhereClass() )
      else:
        inn.forceSetFill( x, y, z, tunnelStairClass() )
        inn.setFill( x+dir[0], y+dir[1], z+dir[2], tunnelStairClass() )
      count = count - 1
      x = x+dir[0]
      y = y+dir[1]
      z = z+dir[2]
    last = dir
    flip = flip + 1
    flip = flip % 2
    if flip:
      dir = direction( dir )
    else:
      dir = (0,1,0)
    if dir[0] or dir[1]:
      count = tunnellen()
    else:
      count=stairlen()

  mapClass().setState( 'library', 'teleport', (x,y,z) )
  for dir in [ (0,1,0),(0,1,0),(0,1,0),(0,1,0),(0,1,0) ]:
    x = x+dir[0]
    y = y+dir[1]
    z = z+dir[2]
    inn.setFill( x, y, z, tunnelToNowhereClass() )

  for xoff in range( -5, 5 + 1 ):
    for yoff in range( 1, 25 + 1 ):
      inn.setFill( x+xoff, y+yoff, z, nowhereRoomClass() )
  inn.addFeature( x, y+yoff, z, leverFeature )  
  noWhereWaypoint = waypointFeatureClass( 'No Where', x, y + yoff - 1, z )
  inn.addFeature( x, y + yoff - 1, z, noWhereWaypoint )

  for xoff in range( -3, 3 + 1 ):
    for yoff in range( 3, 23 + 1 ):
      inn.forceSetFill( x+xoff, y+yoff, z, solidFillClass() )

  commonsRoom = commonsRoomClass()

  commonsSecretDoor = commonsSecretDoorClass()

  commonsStair = commonsStairClass()

  inn.setFill( 4, -10, 2, commonsUpperDoorClass( 'commons upper door' ) )
  for z in [2,3,4,5,6,7,8,9]:
    inn.setFill( 4, -11, z, dungeonStairClass() )
  inn.setFill( 4, -10, 9, dungeonRoomClass() )
  inn.setFill( 4, -9, 9, dungeonRoomClass() )
  inn.setFill( 4, -8, 9, dungeonRoomClass() )
  inn.setFill( 4, -7, 9, dungeonRoomClass() )
  inn.setFill( 4, -7, 8, dungeonRoomClass() )
  inn.setFill( 0, -9, 0, commonsRoomClass() )
  inn.setFill( 0, -10, 0, commonsRoomClass() )
  inn.setFill( 0, -11, 0, commonsRoomClass() )
  for x in range( -5, 5 + 1):
    for y in range( -22, -11):
      z = 0
      inn.setFill( x, y, z, commonsRoomClass() )

  for z in [7,6,5,4,3,2,1]:
    inn.setFill( 13, -8, z, dungeonRoomClass() )

  for z in [0,-1,-2,-3]:
    inn.setFill( 13, -8, z, sewerShaftClass() )

  inn.setFill( 13,-8,-4,sewerRoomClass() )

  for xy in [(-6,-10), (-6,-2), (-6,6), (6,6), (6,-2), (6,-10)]:
    for z in [0,-1,-2,-3]:
      inn.setFill( xy[0], xy[1], z, sewerShaftClass() )

  inn.setFill( 6, -10, -4, sewerRoomClass() )

  for y in [6,5,4,3,2,1,0,-1,-2]:
    inn.setFill( 6, y, -4, sewerRoomClass() )
    inn.setFill( -6, y, -4, sewerRoomClass() )
  for x in [-5,-4,-3,-2,-1,0,1,2,3,4,5]:
    inn.setFill( x, 2, -4, sewerRoomClass() )
  for y in [1,0,-1,-2,-3,-4,-5,-6,-7,-8,-9,-10,-11,-12,-13,-14,-15,-16,-17,-18]:
    inn.setFill( 0, y, -4, sewerRoomClass() )
  inn.setFill( 1,-18,-4,sewerRoomClass() )
  for x in [-6,-5,-4,-3,-2,-1]:
    inn.setFill( x, -10, -4, sewerRoomClass() )

  for z in [2,1,0,-1,-2,-3]:
    inn.setFill( -7, -5, z, sewerShaftClass() )

  inn.setFill( -7,-7,2, jobsOfficeSewerDoorClass( 'jobs office sewer door' ) )
  inn.setFill( -7, -6, 2, jobsOfficeBathRoomClass() )
  for x in [-7,-6,-5,-4,-3,-2,-1]:
    inn.setFill( x, -5, -4, sewerRoomClass() )
  for x in [12,11,10,9,8,7]:
    inn.setFill( x, -8, -4, sewerRoomClass() )
  for y in [-9,-10,-11,-12,-13,-14,-15,-16]:
    inn.setFill( 7, y, -4, sewerRoomClass() )
  for x in [6,5,4,3,2]:
    inn.setFill( x, -16, -4, sewerRoomClass() )
  for y in [-17,-18,-19,-20,-21,-22,-23,-24]:
    inn.setFill( 2, y, -4, sewerRoomClass() )
  inn.setFill( 2, -25, -4, sewerStairClass() )
  inn.setFill( 2, -25, -3, sewerStairClass() )

  for x in [12,13,14,15,16]:
    for y in [-13,-14,-15]:
      inn.setFill( x,y,0,underbankVaultClass() )

  inn.setFill( 11,-14,0, underbankVaultDoorClass() )
  inn.setFill( 13,-12,0, underbankSewerDoorClass( 'underbank sewer door' ) )
  inn.setFill( 13, -11, 0, underbankSewerRoomClass() )
  inn.setFill( 13, -10, 0, underbankSewerRoomClass() )
  inn.setFill( 13, -9, 0, underbankSewerRoomClass() )

  inn.setFill( 6, -14, 0, bankRoomClass() )
  bankHeight = 15
  for x in range( 7, 11 ):
    for y in range( -15, -12 ):
      for z in range( bankHeight ):
        inn.setFill( x, y, z, bankRoomClass() )

  for z in range( bankHeight ):
    inn.setFill( 8, -11, z, bankStairClass() )
    if 0 == z % 2:
      inn.setFill( 8, -12, z, bankRoomClass() )

  for z in range( 1, bankHeight, 2 ):
    inn.setFill( 9, -11, z, bankRoomClass() )
    inn.setFill( 9, -12, z, bankRoomClass() )

  for x in [4,5,6,7,8,9,10,11,12,13]:
    inn.setFill( x, -7, 7, dungeonRoomClass() )

  for x in range( 7,16):
    inn.setFill( x,-22,0, sleeplessNightsInnHallwayClass() )
  inn.setFill( 6,-22,0, sleeplessNightsInnDoorClass( 'sleepless nights inn door') )


  for x in range( 16, 21):
    for y in range( -27, -18):
      inn.setFill( x, y, 0, sleeplessNightsInnLobbyClass() )

  inn.setFill( -3, -11, 0, commonsDoorClass( 'Commons Door 1') )
  inn.setFill( -3, -10, 0, commonsRoomClass() )
  inn.setFill( -2, -10, 0, commonsStairClass() ) ## one way stairs up
  inn.setFill( 3, -11, 0, commonsRoomClass() )
  inn.setFill( 3, -10, 0, commonsRoomClass() )
  inn.setFill( 2, -10, 0, commonsRoomClass() )
  inn.setFill( 2, -10, 1, commonsRoomClass() )
  inn.setFill( 2, -10, 2, commonsRoomClass() )
#  inn.setFill( 1, -10, 2, commonsRoomClass() )
#  inn.setFill( 0, -10, 2, commonsRoomClass() )
#  inn.setFill( -1, -10, 2, commonsRoomClass() )
  inn.setFill( -2, -10, 2, commonsRoomClass() )
  inn.setFill( -2, -10, 1, commonsStairClass() ) # one way up stairs
  inn.setFill( 2, -28, -4, commonsWellClass() )
  inn.setFill( 2, -26, -3, commonsWellClass() )

##
## warn about the one way up stairs
##
  oneWayUpStairsWarning = oneWayUpStairsWarningClass()
  inn.addFeature( -2, -10, 0, oneWayUpStairsWarning )
  inn.addFeature( -2, -10, 1, oneWayUpStairsWarning )
  
  inn.setFill( 2, -27, -4, commonsWellStairClass() )
  inn.setFill( 2, -27, -3, commonsWellStairClass() )


  for y in range( -28, -22 ):
    inn.setFill( -2, y, 0, commonsWellClass() )

  for x in range( -3, -1 + 1 ):
    for y in range( -31, -29 + 1 ):
      inn.setFill( x, y, 0, commonsWellClass() )
      inn.setFill( x, y, -50, commonsWellClass() )

  for z in range( -49, -1 + 1 ):
    inn.setFill( -2, -30, z, commonsWellClass() )
    inn.setFill( 2, -29, z, commonsWellStairClass() )
  inn.setFill( 2, -29, -50, commonsWellStairClass() )
  inn.setFill( 2, -29, 0, commonsWellStairClass() )
  inn.setFill( 0, -29, 0, commonsWellClass() )
  inn.setFill( 1, -29, 0, commonsWellClass() )
  inn.setFill( 0, -31, -50, commonsWellClass() )
  inn.setFill( 1, -31, -50, commonsWellClass() )
  inn.setFill( 2, -31, -50, commonsWellClass() )
  inn.setFill( 2, -30, -50, commonsWellClass() )
  
  inn.setFill( 3, -29, -47, commonsWellClass() )
  commonsWellWaypoint = waypointFeatureClass( 'Commons Well', 3, -29,  -47 )
  inn.addFeature( 3, -29, -47, commonsWellWaypoint )

  wellWarning = wellWarningClass()
  inn.addFeature( -3, -29, 0, wellWarning )
  inn.addFeature( -2, -29, 0, wellWarning )
  inn.addFeature( -1, -29, 0, wellWarning )
  inn.addFeature( -3, -30, 0, wellWarning )
  inn.addFeature( -1, -30, 0, wellWarning )
  inn.addFeature( -3, -31, 0, wellWarning )
  inn.addFeature( -2, -31, 0, wellWarning )
  inn.addFeature( -1, -31, 0, wellWarning )

  inn.setFill( -6, -13, 0, commonsSecretDoorClass() )
  for x in range (-9, -6 ):
    inn.setFill( x, -13, 0, dungeonRoomClass() )
  for y in range( -12, 20 + 1 ):
    inn.setFill( -9, y, 0, dungeonRoomClass() )

  inn.setFill( -6, -17, 0, libraryAisleClass() )
  inn.addFeature( -6, -17, 0, libraryPlaqueFeatureClass() )
  for x in range( -17, -6 ):
    inn.setFill( x, -17, 0, libraryAisleClass() )
  for x in range( -17, -6, 2 ):
    inn.setFill( x, -16, 0, libraryStacksClass() )
    inn.setFill( x, -18, 0, libraryStacksClass() )
  
  for x in [-9,-8,-7,-6]:
    for y in [-11,-10,-9,-8]:
      inn.setFill( x, y, 2, jobsOfficeClass() )
  inn.setFill( -5, -9, 2, jobsOfficeDoorClass( 'jobs office door 1') )

  for y in range( -40, -23 + 1 ):
    inn.setFill( 4, y, 0, marketRowTunnelClass() )


  inn.setFill( 3, -25, 0, moneychangersDoorClass( 'money changers door' ) )
  for x in [0,1,2]:
    for y in [-24,-25,-26]:
      inn.setFill( x,y,0,moneychangersRoomClass() )

  inn.setFill( 18, -18, 0, hookerDoorClass( 'Amanda' ) )
  for x in [18,19,20]:
    for y in [-17,-16,-15]:
      inn.setFill( x, y, 0, hookerRoomClass( 'Amanda' ) )
  for z in [0,-1,-2,-3]:
    inn.setFill( 21, -16, z, sewerShaftClass() )
  inn.setFill( 21, -20, 0, hookerDoorClass( 'Montana' ) )
  for x in [22,23,24]:
    for y in [-18,-19,-20]:
      inn.setFill( x, y, 0, hookerRoomClass( 'Montana' ) )
  for z in [0,-1,-2,-3]:
    inn.setFill( 25, -19, z, sewerShaftClass() )
  inn.setFill( 21, -23, 0, hookerDoorClass( 'Pink Rose' ) )
  for x in [22,23,24]:
    for y in [-22, -23, -24]:
      inn.setFill( x, y, 0, hookerRoomClass( 'Pink Rose' ) )
  for z in [0,-1,-2,-3]:
    inn.setFill( 25, -23, z, sewerShaftClass() )
  inn.setFill( 21, -26, 0, hookerDoorClass( 'Sloppy Samantha' ) )
  for x in [22,23,24]:
    for y in [-26,-27,-28]:
      inn.setFill( x, y, 0, hookerRoomClass( 'Sloppy Samantha' ) )
  for z in [0,-1,-2,-3]:
    inn.setFill( 25, -27, z, sewerShaftClass() )
  inn.setFill( 18, -28, 0, hookerDoorClass( 'Jezebel' ) )
  for x in [16,17,18,19,20]:
    for y in [-29,-30,-31,-32,-33,-34,-35,-36,-37,-38]:
      inn.setFill( x, y, 0, hookerRoomClass( 'Jezebel' ) )
  for z in [0,-1,-2,-3]:
    inn.setFill( 18, -39, z, sewerShaftClass() )

  for x in [18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]:
    inn.setFill( x, -39, -4, sewerRoomClass() )
  for y in [-25,-26,-27,-28,-29,-30,-31,-32,-33,-34,-35,-36,-37,-38]:
    inn.setFill( 0, y, -4, sewerRoomClass() )
  inn.setFill( 1, -25, -4, sewerRoomClass() )

  inn.setFill( 21, -16, -4, sewerRoomClass() )
  inn.setFill( 21, -17, -4, sewerRoomClass() )
  inn.setFill( 22, -17, -4, sewerRoomClass() )
  inn.setFill( 22, -18, -4, sewerRoomClass() )
  inn.setFill( 23, -18, -4, sewerRoomClass() )
  inn.setFill( 23, -19, -4, sewerRoomClass() )
  inn.setFill( 24, -19, -4, sewerRoomClass() )
  inn.setFill( 25, -19, -4, sewerRoomClass() )
  inn.setFill( 25, -23, -4, sewerRoomClass() )
  inn.setFill( 25, -27, -4, sewerRoomClass() )
  for y in [-20,-21,-22,-23,-24,-25,-26,-27]:
    inn.setFill( 24, y, -4, sewerRoomClass() )
  
  inn.setFill( 20, -16, -4, sewerRoomClass() )
  inn.setFill( 20, -15, -4, sewerRoomClass() )
  inn.setFill( 19, -15, -4, sewerRoomClass() )
  inn.setFill( 19, -14, -4, sewerRoomClass() )
  inn.setFill( 18, -14, -4, sewerRoomClass() )
  inn.setFill( 18, -13, -4, sewerRoomClass() )
  inn.setFill( 17, -13, -4, sewerRoomClass() )
  inn.setFill( 17, -12, -4, sewerRoomClass() )
  inn.setFill( 16, -12, -4, sewerRoomClass() )
  inn.setFill( 16, -11, -4, sewerRoomClass() )
  inn.setFill( 15, -11, -4, sewerRoomClass() )
  inn.setFill( 15, -10, -4, sewerRoomClass() )
  inn.setFill( 14, -10, -4, sewerRoomClass() )
  inn.setFill( 14, -9, -4, sewerRoomClass() )
  inn.setFill( 13, -9, -4, sewerRoomClass() )



  ##
  ## NPCS!
  ##
  
  moneyChanger = moneyChangerClass( 'The Money Changer' )
  moneyChanger.setLocation( (1, -25, 0) )
  gameClass().addDenizen( moneyChanger )  


  hookerAmanda = hookerClass( 'Amanda', 1, 3, 2, True )
  hookerAmanda.setLocation( (19, -16, 0) )
  gameClass().addDenizen( hookerAmanda )

  hookerMontana = hookerClass( 'Montana', 2, 4, 1, False )
  hookerMontana.setLocation( (23, -19, 0) )
  gameClass().addDenizen( hookerMontana )

  hookerPinkRose = hookerClass( 'Pink Rose', 0, 1, 3, True )
  hookerPinkRose.setLocation( (23, -23, 0) )
  gameClass().addDenizen( hookerPinkRose )

  hookerSloppySamantha = hookerClass( 'Sloppy Samantha', 0, 0, 1, False )
  hookerSloppySamantha.setLocation( (23, -27, 0) )
  gameClass().addDenizen( hookerSloppySamantha )

  inn.setFill( 0,9,0, touristRoomClass() )
  for x in [-1,0,1]:
    for y in [10,11,12]:
      inn.setFill( x, y, 0, touristRoomClass() )

#  inn.encaseOpen( solidFillClass )
#  inn.validate()



##
## Elevporter at 2,11,0 through 2,11,10000
##
  farmsize = 5           
  for x in range( -farmsize, farmsize + 1):
    for y in range( -farmsize, farmsize + 1):
      inn.setFill( x + 2, y + 11, 10000 - 1, farmSoilClass() )
      z = 10000
      inn.setFill( x + 2,y + 11, z, farmRoomClass() )
  inn.setFill( 2, 11, 10000, farmElevporterRoomClass(), True )
  inn.addFeature( 2, 11, 0, elevporterFeatureClass( (2,11,10000) ) )
  inn.addFeature( 2, 11, 10000, elevporterFeatureClass( (2,11,0) ) )

  inn.setFill( 2, 11, 0, touristElevporterRoomClass() )

  alli = turnipSeekingClass( 'Alli The Turnip Girl' )
  alli.setLocation( (2,11,10000) )
  gameClass().addDenizen( alli )

#  hookerExtra = hookerClass( 'Temporary Convienence Hooker (DELETE BEFORE RELEASE)', 0, 0, 1, False )
#  hookerExtra.setLocation( (1, 1, 0) )
#  gameClass().addDenizen( hookerExtra )

  sally = stayAwayClass( 'Sally Stay Away')
  sally.setLocation( (6,8,0) )
  gameClass().addDenizen( sally )
  
  innkeeper = wanderClass( 'Brownian Innkeeper' )
  random.seed( time.time() )
  innkeeper.setLocation( (random.choice( range( -3, 3 + 1 ) ), random.choice( range( -3, 3 + 1 ) ), 0) )
  gameClass().addDenizen( innkeeper )

  inn.setFill( 5, -27, 0, firstAidRoomClass() )
  inn.setFill( 6, -26, 0, firstAidRoomClass() )
  inn.setFill( 6, -27, 0, firstAidRoomClass() )
  inn.setFill( 6, -28, 0, firstAidRoomClass() )
  inn.setFill( 7, -26, 0, firstAidRoomClass() )
  inn.setFill( 7, -27, 0, firstAidRoomClass() )
  inn.setFill( 7, -28, 0, firstAidRoomClass() )
  inn.setFill( 8, -26, 0, firstAidRoomClass() )
  inn.setFill( 8, -27, 0, firstAidRoomClass() )
  inn.setFill( 8, -28, 0, firstAidRoomClass() )

  inn.setFill( -6, -21, 0, fountainRoomClass() )  
  inn.setFill( -7, -21, 0, fountainRoomClass() )  
  for x in [-8, -9, -10, -11]:
    for y in [-20, -21, -22]:
      inn.setFill( x, y, 0, fountainRoomClass() )
      inn.setFill( x, y, 1, fountainRoomClass() )
      
  inn.setFill( -4, -23, 0, apshaiRoomClass() )
  inn.setFill( -4, -24, 0, apshaiRoomClass() )
  inn.setFill( -5, -24, 0, apshaiRoomClass() )
  inn.setFill( -6, -24, 0, apshaiRoomClass() )
  for y in [-25, -26, -27, -28, -29, -30]:
    inn.setFill( -6, y, 0, apshaiRoomClass() )

  for x in [-7, -8, -9]:
    inn.setFill( x, -30, 0, apshaiRoomClass() )

  for x in [ -11, -10,]:
    inn.setFill( x, -30, 0, apshaiRoomClass() )

  for x in range( -26, -12 + 1):
    for y in [-26, -27, -28, -29, -30, -31, -32, -33, -34]:
      for z in [0,1,2,3]:
        if x in [-25,-19,-13] and y in [-27, -33]:
          inn.setFill( x, y, z, apshaiPillarClass() )
        else:
          inn.setFill( x, y, z, apshaiRoomClass() )
  for x in range( -28, -10 +1 ):
    for y in [-24, -25, -35, -36]:
      for z in [-3, -2, -1, 0, 1, 2, 3]:
        if z == -3 and x == -25 and y in [-35,-36]: continue
        inn.setFill( x, y, z, sewerShaftClass() )
      inn.setFill( x, y, -4, sewerRoomClass() )

  for x in [-28, -27, -11, -10]:
    for y in range( -34, -26 + 1 ):
      for z in [-3, -2, -1, 0, 1, 2, 3]:
        if y == -30 and x in [-11, -10] and z<=0: continue
        inn.setFill( x, y, z, sewerShaftClass() )
      if y == -30 and x in [-11, -10]: continue
      inn.setFill( x, y, -4, sewerRoomClass() )

  # start at -10, -33 and go East!
  for x in range( -9, -1 + 1 ):
    inn.setFill( x, -33, -4, sewerRoomClass() )

  inn.setFill( -19, -34, -4, sewerRoomClass() )
  inn.setFill( -19, -33, -4, sewerStairClass() )
  inn.setFill( -19, -33, -3, sewerStairClass() )

  inn.setFill( -18, -33, -3, dungeonRoomClass() )
  inn.setFill( -20, -33, -3, dungeonRoomClass() )
  inn.setFill( -18, -32, -3, dungeonRoomClass() )
  inn.setFill( -19, -32, -3, dungeonRoomClass() )
  inn.setFill( -20, -32, -3, dungeonRoomClass() )

  for x in range( -40, -37 + 1 ):
    inn.setFill( -25, x, -2, dungeonRoomClass() )
  inn.addFeature( -25, -40, -2, uselessLeverClass() )
##
## End of the inn, unfinished as it is...
##


##
## The surface city!  Ang?
##
class cityStreetFill( openFillClass ):
  def zoneName( self ): return 'The City Of Ang'
class cityAlleyFill( openFillClass ):
  def zoneName( self ): return 'The City Of Ang'
class cityBuildingFill( openFillClass ):
  def zoneName( self ): return 'The City Of Ang'
class cityPlazaFill( openFillClass ):
  def zoneName( self ): return 'The City Of Ang'
class cityBrickFill( solidFillClass ):
  def zoneName( self ): return 'The City Of Ang'
  

##
## Helper functions?
##
def set_bounded_fill( m, l, u, fill ):
  for x in range( min( l[0], u[0]), max(l[0], u[0]) +1 ):
    for y in range( min( l[1], u[1]), max(l[1], u[1]) +1 ):
      for z in range( min( l[2], u[2]), max(l[2], u[2]) +1 ):
        m.setFill( x,y,z, fill() )

##
## The encased bounded fill will skip any outer fill that already
## exists
##
def set_encased_bounded_fill( m, l, u, ofill, ifill ):
  lx = min( l[0], u[0] )
  ux = max( l[0], u[0] )
  assert (ux - lx) > 1
  ly = min( l[1], u[1] )
  uy = max( l[1], u[1] )
  assert (uy - ly) > 1
  lz = min( l[2], u[2] )
  uz = max( l[2], u[2] )
  assert (uz - lz) > 1
  for x in range( lx, ux + 1 ):
    for y in range( ly, uy + 1 ):
      for z in range( lz, uz + 1 ):
        ##
        ## assume the inner fill is uncontested
        ##
        if x in [lx,ux] or y in [ly,uy] or z in [lz,uz]:
          if not m.hasFill( x,y,z ):
            m.setFill( x,y,z, ofill() )
        else:
          m.setFill( x,y,z, ifill() )

def create_city( city ):        
  zCity = 10000
  city.setFill( 0,-3,zCity,cityBuildingFill() )
  city.setFill( 0,-4,zCity,cityBuildingFill() )
  set_encased_bounded_fill( city, (-3, 3, zCity-1), (3,-3,zCity+1), cityBrickFill, cityBuildingFill )

  ##
  ## put a wall around the farm
  ## farm is centered on x+2 y+11, size 5
  ##
  for y in range( -6, 6 + 1 ):
    city.setFill( -4, 11-y, zCity, cityBrickFill() )
    city.setFill( 8, 11-y, zCity, cityBrickFill() )

  for x in range( -5, 5 + 1 ):
    city.setFill( 2 - x , 5, zCity, cityBrickFill() )
    city.setFill( 2 - x , 17, zCity, cityBrickFill() )

  city.setFill( 0, 4, zCity, stairFillClass() )
  city.setFill( 0, 4, zCity + 1, stairFillClass() )
