import networkx as nx
import plotly.graph_objs as go
from networkx.drawing.nx_agraph import graphviz_layout
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import sqlite3
import threading
import sys
#OBS:
#para evitar o erro 'lazy loading' execute esse arquivo com o seguinte código no terminal: waitress-serve interface:app.server

# GLOBAL PARAMETERS ###########################################################################################################

#intervalo de atualização da ferramenta em milissegundos (ms)
intervalfreq = 10000

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
	cursor.execute('SELECT id, hash, prev_hash, arrive_time, round, proof_hash, stable FROM localChains WHERE id > (SELECT MAX(id) - {} FROM localchains)'.format(rangeID))
	a = cursor.fetchall()
	blocks_localChains = []
	i=0
	for x in a:
		blocks_localChains.append([])
		blocks_localChains[i].append(x[0]) #id
		blocks_localChains[i].append(x[1]) #hash
		blocks_localChains[i].append(x[2]) #prev_hash
		blocks_localChains[i].append(x[3]) #arrive_time
		blocks_localChains[i].append(x[4]) #round
		blocks_localChains[i].append(x[5]) #proof_hash
		blocks_localChains[i].append(x[6]) #stable
		i = i + 1
	

	#Cria uma lista - cada termo é um bloco da log_block - cada bloco possui na ordem: id, hash, prev_hash, arrive_time, round, proof_hash
	cursor.execute('SELECT id, hash, prev_hash, arrive_time, round, proof_hash from log_block t1 WHERE t1.id = (SELECT MAX(id) FROM LocalChains) AND NOT EXISTS (SELECT hash from localChains t2 WHERE t1.hash == t2.hash)')
	b = cursor.fetchall()
	blocks_log_blocks = []
	i=0
	for y in b:
		blocks_log_blocks.append([])
		blocks_log_blocks[i].append(y[0]) #id
		blocks_log_blocks[i].append(y[1]) #hash
		blocks_log_blocks[i].append(y[2]) #prev_hash
		blocks_log_blocks[i].append(y[3]) #arrive_time
		blocks_log_blocks[i].append(y[4]) #round
		blocks_log_blocks[i].append(y[5]) #proof_hash
		i = i + 1
	db.close()

	return blocks_localChains, blocks_log_blocks

# NETWORKX AND PLOTLY ########################################################################################################

def Blockchain_Graph(rangeID):

	#gera a lista com os blocos
	blockchain_data, blockchain_log = blockchain_list(rangeID)

	G = nx.DiGraph() #gera um gráfico vazio

	hovertext_node=[] #contem o texto pop-up do bloco
	text_node=[] #contem o texto dentro do bloco
	color_node=[]#contem a cor do node
	dash_type= []#contém o tipo do tracejado dos edges "solid" ou "dot" para tracejado	

	popup_layout = "<b>ID: </b>{}<br><b>Hash: </b>{}<br><b>Prev. Hash: </b>{}<br><b>Arrive Time: </b>{}<br><b>Round: </b>{}<br><b>Proof_Hash: </b>{}"

        #localChains 	############################

	#cria os nodes da localChains com base no hash inserindo seus respectivos textos
	for block in blockchain_data:
		G.add_node(block[1])
		text_node.append(block[0])
		hovertext_node.append(popup_layout.format(block[0],block[1],block[2],block[3],block[4],block[5]))

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
		hovertext_node.append(popup_layout.format(block2[0],block2[1],block2[2],block2[3],block2[4],block2[5]))
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
				marker=dict(	size=40, 
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
tools =  {'displayModeBar':True,'scrollZoom':False, 'displaylogo':False}
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
					
					children = [html.H1('Blockchain Graph')]
									
					),

				html.Div(
					className="row", 
					children = [
							'ID range:',

							dcc.RadioItems(
                						id='id_range',
               							options=[{'label': i, 'value': i} for i in [10, 20, 50, 100]],
                						value=10,
               							labelStyle={'display': 'inline-block'}
            						),

							dcc.Graph(	
								id='my-graph',
								figure=Blockchain_Graph(10),
								config=tools,
							),

							dcc.Interval( #atualizar o gráfico a cada 10 segundos
            							id='interval_component',
            							interval=intervalfreq, #em ms
            							n_intervals=0
        						)
							
						]#, style={'width': '48%', 'float': 'right', 'display': 'inline-block'}
           				)
		     		]
			)

app.layout = serve_layout

#As "entradas" e "saídas" da nossa interface de aplicação são descritas declarativamente através do @app.callback, de forma a criar Dash interativos

@app.callback(
	Output('my-graph','figure'),
	[Input('interval_component','n_intervals'), Input('id_range','value')]
)
def update_my_graph(interval_component, id_range):

#	if(node.Status( )):
#      		node.sema.acquire( )
#		graph = Blockchan_Graph( )
#		node.clear( )
#		node.sema.release( )
#		return graph

	return Blockchain_Graph(id_range)


if __name__ == '__main__':
	if(len(sys.argv) >= 2):
		app.run_server(debug=True, use_reloader=True, host=sys.argv[1],port=8050)
	else:
		app.run_server(debug=True, use_reloader=True, host='127.0.0.1',port=8050)
	#debug=True significa que o Dash atualizará automaticamente o navegador quando você fizer uma alteração no código.
