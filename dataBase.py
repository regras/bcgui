import sqlite3
import datetime
import time
import math

from globalParameters import databaseLocation, timeout, GEN_ARRIVE_TIME, colors

# DATABASE ###################################################################################################################

#Acessa o banco de dados
#retorna listas, onde cada uma possuí cada blocos (dentro de uma lista), onde a primeira a ser retornada deve ser a cadeia principal
#Todos os blocos (de cada lista), devem possuir os seguintes parametros na seguinte ordem:
#id, hash, prev_hash, arrive_time(UTC), round, proof_hash, subuser, arrive_time(local datetime), cor_do_bloco
def blockchain_list(rangeID):	
	db = sqlite3.connect(databaseLocation)
	cursor = db.cursor()

    #cadeia principal
	#Cria uma lista - cada termo é um bloco da localChains- cada bloco possui na ordem: id, hash, prev_hash, arrive_time, round, proof_hash
	cursor.execute('SELECT id, hash, prev_hash, arrive_time, round, proof_hash, stable, subuser FROM localChains WHERE id BETWEEN (SELECT {} FROM localchains) AND (SELECT {} FROM localchains)'.format(rangeID[0],rangeID[1]))
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
		blocks_localChains[i].append(x[7]) #subuser
		blocks_localChains[i].append(datetime.datetime.utcfromtimestamp(float(x[3]))) #arrive_time (local datetime)
		if x[6] == 1:
			blocks_localChains[i].append(colors['node-stable'])
		else:
			blocks_localChains[i].append(colors['node-unstable'])
		i = i + 1

    #Blocos não selecionados
	#Cria uma lista - cada termo é um bloco da log_block - cada bloco possui na ordem: id, hash, prev_hash, arrive_time, round, proof_hash
	cursor.execute('SELECT id, hash, prev_hash, arrive_time, round, proof_hash, subuser FROM log_block t1 WHERE t1.id BETWEEN (SELECT {} FROM log_block) AND (SELECT {} FROM log_block) and EXISTS (SELECT * FROM log_block t2 WHERE t2.round <= t1.round and t1.id == t2.id and t2.arrive_time < t1.arrive_time and t2.proof_hash < t1.proof_hash) and NOT EXISTS (SELECT * FROM localChains t3 WHERE t3.hash == t1.hash)'.format(rangeID[0],rangeID[1]))
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
		blocks_log_blocks[i].append(colors['node-log'])
		i = i + 1
    
	#Cria uma lista - cada termo é um bloco selecionado uma vez, q pode ser obtido na log_block - cada bloco possui na ordem: id, hash, prev_hash, arrive_time, round, proof_hash, subuser
	cursor.execute('SELECT id, hash, prev_hash, arrive_time, round, proof_hash, subuser FROM log_block t1 WHERE t1.id BETWEEN (SELECT {} FROM log_block) AND (SELECT {} FROM log_block) and NOT EXISTS (SELECT * FROM log_block t2 WHERE t2.round <= t1.round and t1.id == t2.id and t2.arrive_time < t1.arrive_time and t2.proof_hash < t1.proof_hash) and NOT EXISTS (SELECT * FROM localChains t3 WHERE t3.hash == t1.hash)'.format(rangeID[0],rangeID[1]))
	c = cursor.fetchall()
	blocks_SelectedOnce = []
	i=0
	for z in c:
		blocks_SelectedOnce.append([])
		blocks_SelectedOnce[i].append(z[0]) #id
		blocks_SelectedOnce[i].append(z[1]) #hash
		blocks_SelectedOnce[i].append(z[2]) #prev_hash
		blocks_SelectedOnce[i].append(z[3]) #arrive_time (UTC)
		blocks_SelectedOnce[i].append(z[4]) #round
		blocks_SelectedOnce[i].append(z[5]) #proof_hash
		blocks_SelectedOnce[i].append(z[6]) #subuser
		blocks_SelectedOnce[i].append(datetime.datetime.utcfromtimestamp(float(z[3]))) #arrive_time (local datetime)
		blocks_SelectedOnce[i].append(colors['node-selected-once'])
		i = i + 1

	"""#Cria uma lista - cada termo é um bloco revertido da blockchain - cada bloco possui na ordem: id, hash, prev_hash, arrive_time, round, proof_hash, subuser
	cursor.execute('SELECT id, hash, prev_hash, arrive_time, round, proof_hash, subuser FROM log_block t1 WHERE t1.id BETWEEN (SELECT {} FROM log_block) AND (SELECT {} FROM log_block) and NOT EXISTS (SELECT * FROM log_block t2 WHERE t2.round <= t1.round and t1.id == t2.id and t2.arrive_time < t1.arrive_time and t2.proof_hash < t1.proof_hash) and NOT EXISTS (SELECT * FROM localChains t3 WHERE t3.hash == t1.hash)'.format(rangeID[0],rangeID[1]))
	d = cursor.fetchall()
	reversed_blocks = []
	i=0
	for w in d:
		reversed_blocks.append([])
		reversed_blocks[i].append(w[0]) #id
		reversed_blocks[i].append(w[1]) #hash
		reversed_blocks[i].append(w[2]) #prev_hash
		reversed_blocks[i].append(w[3]) #arrive_time (UTC)
		reversed_blocks[i].append(w[4]) #round
		reversed_blocks[i].append(w[5]) #proof_hash
		reversed_blocks[i].append(w[6]) #subuser
		reversed_blocks[i].append(datetime.datetime.utcfromtimestamp(float(w[3]))) #arrive_time (local datetime)
		reversed_blocks[i].append(colors['node-rev'])
		i = i + 1"""

	db.close()
	return blocks_localChains, blocks_log_blocks, blocks_SelectedOnce #, reversed_blocks


#função para buscar algumas estatisticas da cadeia (blocos produzidos, revertidos, etc)
def explorer(range):
    node='-1'
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
    cursor.execute("SELECT * FROM localChains WHERE stable = 1 and round <> 0 and id = 1")
    queries = cursor.fetchall()
    sround = queries[0][2] #round do primeiro bloco estavel produzido


    cursor.execute("SELECT * FROM localChains WHERE id BETWEEN (SELECT {} FROM localChains WHERE stable = 1) AND (SELECT {} FROM localChains WHERE stable = 1) and stable = 1 and round <> 0".format(range[0],range[1]))
    queries = cursor.fetchall()
    if(queries):
        numblockstable = len(queries) #obtendo o número de blocos estáveis
        for query in queries:
            avgconf = avgconf + float(1) / float(query[14] - query[2])
        avgconf = avgconf / len(queries)
        avgconf = 1 / avgconf
    
    #calculating performance
    cursor.execute("SELECT * FROM reversion WHERE id BETWEEN (SELECT {} FROM reversion) AND (SELECT {} FROM reversion) and sround > {}".format(range[0],range[1],sround))
    queries = cursor.fetchall()
    if(queries):
        callsync = len(queries)
        for query in queries:
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
    cursor.execute("SELECT count(*) FROM arrived_block WHERE id BETWEEN (SELECT '%s' FROM arrived_block) AND (SELECT '%s' FROM arrived_block) and round >= %d and round < %d and node <> '%s'" %(range[0],range[1],sround,currentRound,node))

    queries = cursor.fetchone()
    if(queries):
        receivedblocks = queries[0]

    #get produced blocks
    cursor.execute("SELECT count(*) FROM arrived_block WHERE id BETWEEN (SELECT '%s' FROM arrived_block) AND (SELECT '%s' FROM arrived_block) and round >= %d and round < %d" %(range[0],range[1],sround,currentRound))
    queries = cursor.fetchone()
    if(queries):
        numblocks = queries[0]
        
    
    #get rounds to produce all blocks
    cursor.execute("SELECT (max(round) - min(round)) FROM arrived_block WHERE id BETWEEN (SELECT {} FROM arrived_block) AND (SELECT {} FROM arrived_block) and round >= {}" .format(range[0],range[1],sround))
    queries = cursor.fetchone()
    if(queries):
        numround = queries[0]
            
    #late block number
    cursor.execute("SELECT COUNT(*) FROM arrived_block WHERE id BETWEEN (SELECT {} FROM arrived_block) AND (SELECT {} FROM arrived_block) and status = 2".format(range[0],range[1]))
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
