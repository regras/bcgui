import networkx as nx
import plotly.graph_objs as go
from networkx.drawing.nx_agraph import graphviz_layout
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import sqlite3
import sys
import datetime


#OBS:
#para evitar o erro 'lazy loading' execute esse arquivo com o seguinte código no terminal: waitress-serve interface:app.server

# GLOBAL PARAMETERS ###########################################################################################################

#cores de cada elemento
colors = {'background_graph':'#f8f8f8',
	'paper-background-graph':'#f8f8f8',
	'title-text':'#000000',
	'pop-up':'#cfcfcf',
	'pop-up-text':'#000000',
	'pop-up-border':'#ffffff',
	'node-stable':'#00c227',
	'node-unstable':'#00bfff',
	'node-log':'#add8e6',
	'node-text':'#000000',
	'edge':'#000000',
	'background_legend':'#e8e8e8'
}

#localização do banco de dados da blockchain
databaseLocation = '../blocks/blockchain.db'

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
    avgrevblock = 0
    avgconf = 0
    numblockstable = 0
    lateblocks = 0
    numblocks = 0
    try:
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
        currentRound = int(math.floor((float(nowTime) - float(parameter.GEN_ARRIVE_TIME))/parameter.timeout))
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

    except Exception as e:
        x = str(e)

    return round(avgconf,2),callsync,callsyncrev,numrevblock,receivedblocks,numround,numblockstable,lateblocks,numblocks

# NETWORKX AND PLOTLY ########################################################################################################

def Blockchain_Graph(rangeID):

	#gera a lista com os blocos
	blockchain_data, blockchain_log = blockchain_list(rangeID)

	G = nx.DiGraph() #gera um gráfico vazio

	hovertext_node=[] #contem o texto pop-up do bloco
	text_node=[] #contem o texto dentro do bloco
	color_node=[]#contem a cor do node
	dash_type= []#contém o tipo do tracejado dos edges "solid" ou "dot" para tracejado	

	popup_layout = "<b>ID: </b>{}<br><b>Hash: </b>{}<br><b>Prev. Hash: </b>{}<br><b>Arrive Time (UTC): </b>{}<br><b>Arrive Time (local datetime GMT+00:00): </b>{}<br><b>Round: </b>{}<br><b>Proof_Hash: </b>{}<br><b>Successful draws of the creator node: </b>{}"

        #localChains 	############################

	#cria os nodes da localChains com base no hash inserindo seus respectivos textos
	for block in blockchain_data:
		G.add_node(block[1])
		text_node.append(block[0])
		hovertext_node.append(popup_layout.format(block[0],block[1],block[2],block[3],block[8],block[4],block[5],block[7]))

		#o bloco estaveis e instaveis possuirao cores diferentes
		if block[6] == 1:
			color_node.append(colors['node-stable'])
		else:
			color_node.append(colors['node-unstable'])


	#cria os edges (ligando o hash ao prev_hash de cada bloco) dos blocos da localChain
	for block in blockchain_data:
		if block[2] != "" and (block[2] in G.nodes):
			G.add_edge(block[2], block[1])
			dash_type.append("solid")
		else:
			continue

	#log_block	############################
	#cria os nodes da log_blockcom base no hash inserindo seus respectivos textos
	for block2 in blockchain_log:
		G.add_node(block2[1])
		text_node.append(block2[0])
		hovertext_node.append(popup_layout.format(block2[0],block2[1],block2[2],block2[3],block2[7],block2[4],block2[5],block2[6]))
		color_node.append(colors['node-log'])

	#cria os edges (ligando o hash ao prev_hash de cada bloco) dos blocos da log_block
	for block2 in blockchain_log:
		if block2[2] != "" and (block2[2] in G.nodes):
			G.add_edge(block2[2], block2[1])
			dash_type.append("dot")
		else:
			continue


	#Define o layout semelhante ao da blockchain
	pos = graphviz_layout(G, prog='dot', args="-Grankdir=LR")

	#adiciona um vetor da posição do node dentro do próprio node
	for node in G.nodes:
		G.nodes[node]['pos'] = list(pos[node])

	#define o intervalo do zoom que será dado na coordenada x ao iniciar o grafico
	x_zoom_range =[0,0]
	for block in blockchain_data:
		if block[0] == max(text_node):
			x_zoom_range[1] = float(G.nodes[block[1]]['pos'][0])+200
		elif block[0] == (max(text_node)-10): #o numero 10 indica que o zoom sera dado nos ultimos 10 blocos
			x_zoom_range[0] = float(G.nodes[block[1]]['pos'][0])+200

	#separa todas as coordenadas x e y dos edges
	edge_x = []
	edge_y = []
	for edge in G.edges():
		x0, y0 = G.nodes[edge[0]]['pos']
		x1, y1 = G.nodes[edge[1]]['pos']
		edge_x.append(x0)
		edge_x.append(x1)
		edge_x.append(None)
		edge_y.append(y0)
		edge_y.append(y1)
		edge_y.append(None)

	'''#definições dos edges
	edge_trace = go.Scatter(
				x=edge_x, 
				y=edge_y,
				line=dict(	
						width=3, 
						color=colors['edge'],
						dash = "solid", #para edge pontilhado usar "dot"
					), 
				hoverinfo='none', 
				mode='lines', 
				line_shape='spline', 
				opacity=1
				)'''

	#separa todas as coordenadas x e y dos nodes 
	node_x = []
	node_y = []
	for node in G.nodes():
		x, y = G.nodes[node]['pos']
		node_x.append(x)
		node_y.append(y)

	'''#definições dos nodes
	node_trace = go.Scatter(
				x=node_x, 
				y=node_y, 
				hovertext=hovertext_node, 
				text=text_node, 
				textposition="middle center", 
				mode='markers+text', 
				hoverinfo="text", 
				marker=dict(	size=40, 
						color=color_node, 
						symbol='square'
					),
				line=dict(	width=40
					),
				textfont=dict(	color=colors['node-text']
					),
				opacity=1
				)'''


	#renderiza o gráfico
	Graph = go.Figure(
			#data=[edge_trace, node_trace],
			layout=go.Layout(
						title='',#titulo dentro do gráfico 
						titlefont_size=16, 
						plot_bgcolor=colors['background_graph'],
						paper_bgcolor=colors['paper-background-graph'],
						hovermode='closest', 
						dragmode = 'pan',
						margin=dict(	b=20, #tamanho do gráfico
								l=5,
								r=5,
								t=40
							), 
						xaxis=dict(
								showgrid=False, 
								zeroline=False, 
								showticklabels=False,
								range = x_zoom_range
							), 
						yaxis=dict(
								showgrid=False, 
								zeroline=False, 
								showticklabels=False
							), 
						clickmode='event+select'
					)
			)
	
	#cria todos os edges um por um
	#configura cada edge
	
	legend_edges=["Link between two accepted blocks", "Link for an unselected block"]
	i = 0
	t,a,b = 0,0,0
	j = True
	for w in range(0, len(dash_type)):
		#lógica para plotar somente uma legenda de cada trace
		if dash_type[w] == 'solid' and a == 0:
			t = 0
			j = True
		
		elif dash_type[w] == 'solid' and a == 1:
			t = 0
			j = False

		elif dash_type[w] == 'dot' and b == 0:
			t = 1
			j = True
		
		elif dash_type[w] == 'dot' and b == 1:
			t = 1
			j = False


		Graph.add_trace(
			go.Scatter(
				x=[edge_x[i],edge_x[i+1]], 
				y=[edge_y[i],edge_y[i+1]],
				name=legend_edges[t],
				showlegend=j, 
				line=dict(	
						width=3, 
						color=colors['edge'],
						dash = dash_type[w], #para edge pontilhado usar "dot"
					), 
				hoverinfo='none', 
				mode='lines', 
				line_shape='spline', 
				opacity=1
				)
				)
		i = i + 3
		if dash_type[w] == 'solid':
			a = 1
		else:
			b = 1
		

	#cria todos os blocos um por um
	#configura cada node

	legend_node = ["Confirmed block","Not confirmed block","Not selected block"]
	t,a,b,c = 0,0,0,0
	for w in range(0, len(text_node)):
		#lógica para plotar somente uma legenda de cada trace
		if color_node[w] == colors['node-stable'] and a == 0:
			t = 0
			j = True

		elif color_node[w] == colors['node-stable'] and a == 1:
			t = 0
			j = False

		elif color_node[w] == colors['node-unstable'] and b == 0:
			t = 1
			j = True

		elif color_node[w] == colors['node-unstable'] and b == 1:
			t = 1
			j = False

		elif color_node[w] == colors['node-log'] and c == 0:
			t = 2
			j = True

		elif color_node[w] == colors['node-log'] and c == 1:
			t = 2
			j = False

		Graph.add_trace(
			go.Scatter(
				x=[node_x[w]], 
				y=[node_y[w]], 
				hovertext=[hovertext_node[w]], 
				text=[text_node[w]], 
				textposition="middle center", 
				mode='markers+text', 
				hoverinfo="text",
				name=legend_node[t],
				showlegend = j, 
				marker=dict(	size=25, 
						color=color_node[w], 
						symbol='square',
						#cmin=0, # stable variable
					),
				line=dict(	width=40
					),
				textfont=dict(	color=colors['node-text']
					),
				opacity=1
				)
				)
		if color_node[w] == colors['node-stable']:
			a = 1
		elif color_node[w] == colors['node-unstable']:
			b = 1
		elif color_node[w] == colors['node-log']:
			c = 1	


	Graph.update_layout(
				#layout do pop-up
				hoverlabel=dict(
						bgcolor=colors['pop-up'],
						font_size=12,
						font_family="Rockwell",
						font_color=colors['pop-up-text'],
						bordercolor=colors['pop-up-border']
						)
			)
	
	Graph.update_layout(	#layout da legenda
    				legend=dict(
       					x=0,
        				y=1,
        				#traceorder="reversed",
        				bgcolor=colors['background_legend'],
        				#bordercolor="Black",
        				#borderwidth=2,
					itemclick = False,
					itemdoubleclick = False
					
					)
			)

	#atributos do layout: https://plotly.com/javascript/reference/

	return Graph

#configuração das ferramentas de analise do gráfico
tools =  {'displayModeBar':True,'scrollZoom':True, 'displaylogo':False}
#todas as configs: https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js#L6

"""
EXEMPLO P/ REMOVER OU ADD FERRAMENTAS DE ANALISE DO GRÁFICOS (BOTOES)
'modeBarButtonsToAdd':['drawline','drawopenpath','drawclosedpath', 'drawcircle' , 'drawrect' , 'eraseshape']
#'modeBarButtonsToRemove':['drawline']
#botoes existentes: https://github.com/plotly/plotly.js/blob/master/src/components/modebar/buttons.js
"""


# DASH #######################################################################################################################



#importa o template css e passa para o Dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#título da página web
app.title = "Blockchain Graph" 

#definindo uma função para o layout para instanciar no app.layout (layout do app web)
#isso faz com que ao recarregar a pagina será feita uma nova consulta no banco para renderizar o gráfico
def serve_layout():
	return html.Div(
			#style = dict(backgroundColor= colors['web_backgroung']),
			children = [
    			

				html.Div(
					style=dict(
						textAlign= 'center', 
						color=colors['title-text']
						),
					
					children = [
							html.H1('Blockchain Graph')
						]
									
					),



				html.Div(
					style=dict(
							width = '80%',
							float = 'left',
							textAlign = "center",
							#height='300px'#,
						), #style={'width': '60%', 'float': 'left', 'display': 'inline-block','textAlign': "center"}
						
					children = [	
							dcc.Graph(	
								id='my-graph',
								figure=Blockchain_Graph(10),
								config=tools
							),
							dcc.Interval( #atualizar o gráfico a cada 10 segundos
            							id='interval_component',
            							interval=10000, #em ms
            							n_intervals=0
        						)
						]		
					),


				html.Div(
					#style=dict(),
						
					children = [
							'ID range:',

							dcc.RadioItems(
                						id='id_range',
               							options=[{'label': i, 'value': i} for i in [10, 20, 50, 100]],
                						value=10,
               							labelStyle={'display': 'inline-block'}
            							)
						]#,style=dict()
					),

				html.Br(style = {'height': '1px'}),

				html.Div(
					#style=dict(),
						
					children = [	
							'Update Period:',
							dcc.RadioItems(
                						id='update_period',
               							options=[
        								{'label':'2,5s', 'value': 2500},
        								{'label':'5s', 'value': 5000},
        								{'label':'10s', 'value': 10000},
        								{'label':'30s', 'value': 30000},
        								{'label':'1min', 'value': 60000},
        								{'label':'10min', 'value': 600000}
    									],
                						value=10000,
               							labelStyle={'display': 'inline-block'}
            						)
						]			
					),

				html.Br(style = {'height': '1px'}),

				html.Div(
					#style=dict(),
						
					children = [	
							html.Button(	children="Pause Updates", 
									id='btn_1', 
									n_clicks=0
								)
						]			
					),
				
				html.Br(),
				
				html.Div(
						
					children = [
							html.B("Range blocks info: ", style={'font-size':15}),

							    dcc.Input( 
								#placeholder = "type an integer",
        							id='num_explorer',
        							type='number',
        							value=10,
								style={'font-size':12, 'width': '80px', 'float': 'right', 'height': '30px'}
    								)
						]		
					),

				html.Div(						
					children = [	html.Br(),
							html.Div([html.B(" Block confirmation average (block/round): "), html.B(id="num_avgconf")], style = {'border': '1px solid black'}),
							html.Div([html.B(" Sync function calls number: "), html.B(id="num_callsync")], style = {'border': '1px solid black'}),
							html.Div([html.B(" Reversions number: "), html.B(id="num_callsyncrev")], style = {'border': '1px solid black'}),
							html.Div([html.B(" Reversed blocks number: "), html.B(id="num_numrevblock")], style = {'border': '1px solid black'}),
							html.Div([html.B(" Received blocks number: "), html.B(id="num_receivedblocks")], style = {'border': '1px solid black'}),
							html.Div([html.B(" Round number: "), html.B(id="num_numround")], style = {'border': '1px solid black'}),
							html.Div([html.B(" Confirmation Blocks number: "), html.B(id="num_numblockstable")], style = {'border': '1px solid black'}),
							html.Div([html.B(" Late blocks number: "), html.B(id="num_lateblocks")], style = {'border': '1px solid black'}),
							html.Div([html.B(" Produced blocks: "), html.B(id="num_numblocks")], style = {'border': '1px solid black'})
						],
					style={'font-size':9, 'width': '20%', 'float': 'right'}
	
					)

				]

			)

app.layout = serve_layout

#As "entradas" e "saídas" da nossa interface de aplicação são descritas declarativamente através do @app.callback, de forma a criar Dash interativos

#atualização do gráfico
@app.callback(
	Output('my-graph','figure'),
	[Input('interval_component','n_intervals'), Input('id_range','value')]
)
def update_my_graph(interval_component, id_range):
	return Blockchain_Graph(id_range)

#radioitem id range
@app.callback(
	Output('interval_component','interval'),
	[Input('update_period','value')]
)
def update_period_refresh(update_period):
	return update_period


#botão desativar/ativar updates
@app.callback(
	Output('interval_component','max_intervals'),
	[Input('btn_1', 'n_clicks')]
)
def disabled_update_refresh(btn_1):

	if (btn_1%2) == 0:
		return -1
	else:
		return 0


#mudar o texto do botão
@app.callback(
	Output('btn_1', 'children'),
	[Input('interval_component','max_intervals')]
)
def update_period_refresh(interval_component):
	if interval_component == -1:
		return "Pause Updates"
	else:
		return "Start Updates"

#atualizar as informações do explorer
@app.callback(
	[Output('num_avgconf', 'children'),
	Output('num_callsync', 'children'),
	Output('num_callsyncrev', 'children'),
	Output('num_numrevblock', 'children'),
	Output('num_receivedblocks', 'children'),
	Output('num_numround', 'children'),
	Output('num_numblockstable', 'children'),
	Output('num_lateblocks', 'children'),
	Output('num_numblocks', 'children')],
	[Input('interval_component','n_intervals'),Input('num_explorer','value')]
)
def update_explorer_infos(interval_component,num_explorer):
	return explorer(num_explorer)

if __name__ == '__main__':
	if(len(sys.argv) >= 2):
		app.run_server(debug=True, use_reloader=True, host=sys.argv[1],port=8050)
	else:
		app.run_server(debug=True, use_reloader=True, host='127.0.0.1',port=8050)
	#debug=True significa que o Dash atualizará automaticamente o navegador quando você fizer uma alteração no código.
