import sqlite3
import datetime
import time
import math

from globalParameters import databaseLocation, timeout, GEN_ARRIVE_TIME


# DATABASE ###################################################################################################################

#Acessa o banco de dados
def blockchain_list(rangeID):	
	db = sqlite3.connect(databaseLocation)
	cursor = db.cursor()

	#Cria uma lista - cada termo é um bloco da localChains - cada bloco possui na ordem: id, hash, prev_hash, arrive_time, round, stable, proof_hash
	cursor.execute('SELECT id, hash, prev_hash, arrive_time, round, proof_hash, stable, subuser FROM localChains WHERE id > (SELECT MAX(id) - {} FROM localchains)'.format(rangeID))
	a = cursor.fetchall()
	blocks_localChains = []
	i=0
	for x in a:
		blocks_localChains.append([])
		blocks_localChains[i].append(x[0]) #id
		blocks_localChains[i].append(x[1]) #hash
		blocks_localChains[i].append(x[2]) #prev_hash
		blocks_localChains[i].append(x[3]) #arrive_time (UTC)
		blocks_localChains[i].append(x[4]) #round
		blocks_localChains[i].append(x[5]) #proof_hash
		blocks_localChains[i].append(x[6]) #stable
		blocks_localChains[i].append(x[7]) #subuser
		blocks_localChains[i].append(datetime.datetime.utcfromtimestamp(float(x[3]))) #arrive_time (local datetime)

		i = i + 1
	

	#Cria uma lista - cada termo é um bloco da log_block - cada bloco possui na ordem: id, hash, prev_hash, arrive_time, round, proof_hash
	cursor.execute('SELECT id, hash, prev_hash, arrive_time, round, proof_hash, subuser from log_block t1 WHERE t1.id = (SELECT MAX(id) FROM LocalChains) AND NOT EXISTS (SELECT hash from localChains t2 WHERE t1.hash == t2.hash)')
	b = cursor.fetchall()
	blocks_log_blocks = []
	i=0
	for y in b:
		blocks_log_blocks.append([])
		blocks_log_blocks[i].append(y[0]) #id
		blocks_log_blocks[i].append(y[1]) #hash
		blocks_log_blocks[i].append(y[2]) #prev_hash
		blocks_log_blocks[i].append(y[3]) #arrive_time (UTC)
		blocks_log_blocks[i].append(y[4]) #round
		blocks_log_blocks[i].append(y[5]) #proof_hash
		blocks_log_blocks[i].append(y[6]) #subuser
		blocks_log_blocks[i].append(datetime.datetime.utcfromtimestamp(float(y[3]))) #arrive_time (local datetime)
		i = i + 1
	db.close()

	return blocks_localChains, blocks_log_blocks


def explorer(num,node='-1'):
    receivedblocks = 0
    numround = 0
    callsync = 0
    callsyncrev = 0
    numrevblock = 0
    #avgrevblock = 0
    avgconf = 0
    numblockstable = 0
    lateblocks = 0
    numblocks = 0
    #try:
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    #calculating performance
    cursor.execute("SELECT * FROM localChains WHERE id > ((SELECT MAX(id) FROM localChains WHERE stable = 1) - %d) and stable = 1 and round <> 0" %int(num))
    queries = cursor.fetchall()
    sround = queries[0][2]
    if(queries):
        numblockstable = len(queries)
        for query in queries:
            avgconf = avgconf + float(1) / float(query[14] - query[2])
        avgconf = avgconf / len(queries)
    
    #calculating performance
    cursor.execute("SELECT * FROM reversion WHERE sround > %d" %sround)
    queries = cursor.fetchall()
    if(queries):
        callsync = len(queries)
        for query in queries:
            #sync[query[0],query[1],query[2]] = []
            cursor.execute("SELECT * FROM block_reversion WHERE idreversion = %d" %int(query[0]))
            revqueries = cursor.fetchall()
            if(revqueries):
                callsyncrev = callsyncrev + 1
                for revquery in revqueries:
                    numrevblock = numrevblock + 1
                    #sync[query[0],query[1],query[2]] = sync[query[0],query[1],query[2]] + [[revquery[1], revquery[2], revquery[3], revquery[4]]]       
        
    #get arrived blocks
    nowTime = time.mktime(datetime.datetime.now().timetuple())
    currentRound = int(math.floor((float(nowTime) - float(GEN_ARRIVE_TIME))/timeout))
    cursor.execute("SELECT count(*) FROM arrived_block WHERE round >= %d and round < %d and node <> '%s'" %(sround,currentRound,node))
    queries = cursor.fetchone()
    if(queries):
        receivedblocks = queries[0]

    #get produced blocks
    cursor.execute("SELECT count(*) FROM arrived_block WHERE round >= %d and round < %d" %(sround,currentRound))
    queries = cursor.fetchone()
    if(queries):
        numblocks = queries[0]
        
    
    #get rounds to produce all blocks
    cursor.execute("SELECT (max(round) - min(round)) FROM arrived_block WHERE round >= %d" %sround)
    queries = cursor.fetchone()
    if(queries):
        numround = queries[0]
            
    #late block number
    cursor.execute("SELECT COUNT(*) FROM arrived_block WHERE status = 2")
    queries = cursor.fetchone()
    if(queries):
        lateblocks = queries[0]
    db.close()

    #except Exception as e:
        #x = str(e)

    if callsyncrev > 0:
        k = float(numrevblock) / callsyncrev
        y = round(k,2)
    else:
        y = 0

    return round(avgconf,2),y,callsync,callsyncrev,numrevblock,receivedblocks,numround,numblockstable,lateblocks,numblocks
