import es, playerlib, gamethread, psyco
psyco.full()

cvars = {
    'noblock_allow_block': 'If this is non-zero, blocking will be allowed by typing !block or !unghost\nTo stop blocking, type !noblock, !unblock or !ghost',
    'noblock_block_time': 'The time in seconds the blocking will last',
    'noblock_block_amount': 'The amount of times a player will be allowed to block in a single round',
    'noblock_round_advert': 'If this is non-zero, there will be shown an advert at the start of the round',
    'noblock_load_advert': 'If this is non-zero, there will be shown an advert when the plugin is loaded',
    'noblock_unload_advert': 'If this is non-zero, there will be shown an advert when the plugin is unloaded'
}

players = dict()

def load():
    for k, v in cvars.items():
        es.ServerVar(k, 0, v)
    es.server.cmd('exec noblock')
    es.ServerVar('noblock_version', '1.0.0', 'The version of the ES Python noblock script')
    for k in playerlib.getPlayerList():
        players[k.userid] = dict(queued=False)
    if(es.getInt('noblock_load_advert')): es.msg('#multi', '#green[NoBlock]#default NoBlock has been loaded')

def unload():
    if(es.getInt('noblock_load_advert')): es.msg('#multi', '#green[NoBlock]#default NoBlock has been unloaded')

def round_start(ev):
    if int(es.ServerVar('noblock_round_advert')):
        es.msg('#multi', '#green[NoBlock]#default NoBlock is currently enabled. Type !block to disable noblock for a short period of time.')

def player_spawn(ev):
    playerlib.getPlayer(ev['userid']).noblock(1)

#def player_death(ev):

def noblock(userid):
    playerlib.getPlayer(userid).noblock(1)
    players[userid]['queued'] = False
    es.tell(userid, '#multi', '#green[NoBlock]#default You are no longer solid')

def player_say(ev):
    userid = ev['userid']
    text = ev['text']
    plyinst = playerlib.getPlayer(userid)
    if text == '!block' or text == '!unghost':
        if int(es.ServerVar('noblock_allow_block')) >= 1:
            if not plyinst.isdead and plyinst.teamid != 1 and plyinst.teamid != 0:
                try:
                    if not players[userid]['queued']:
                        plyinst.noblock(0)
                        gamethread.delayedname(float(es.ServerVar('noblock_block_time')), userid, noblock, userid)
                        players[userid]['queued'] = True
                        es.tell(userid, '#multi', '#green[NoBlock]#default You are now solid for ' + float(es.ServerVar('noblock_block_time')) + ' seconds')
                    else:
                        es.tell(userid, '#multi', '#green[NoBlock]#default You are already blocking')
                except KeyError:
                    es.msg('#green', 'Error in keys')
                    for k, v in players.items():
                        es.msg('#green', str(k) + '=' + str(v))
            else:
                es.tell(userid, '#multi', '#green[NoBlock]#default You cannot block when you are dead or not on a team')
        else:
            es.tell(userid, '#multi', '#green[NoBlock]#default Blocking is not allowed on this server')
    if text == '!noblock' or text == '!unblock' or text == '!ghost':
        if int(es.ServerVar('noblock_allow_block')) >= 1:
            if not plyinst.isdead and plyinst.teamid != 1 and plyinst.teamid != 0:
                if players[userid]['queued']:
                    gamethread.cancelDelayed(userid)
                    plyinst.noblock(1)
                    es.tell(userid, '#multi', '#green[NoBlock]#default You are no longer solid')
                else:
                    es.tell(userid, '#multi', '#green[NoBlock]#default You are not blocking')
            else: es.tell(userid, '#multi', '#green[NoBlock]#default You cannot unblock when dead or not on a team')
        else:
            es.tell(userid, '#multi', '#green[NoBlock]#default Cannot unblock because blocking is not allowed')