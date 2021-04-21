import networkx as nx
import plotly.graph_objs as go
from networkx.drawing.nx_agraph import graphviz_layout
import datetime

from globalParameters import colors
from dataBase import blockchain_list, explorer


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
		if block2[2] != "" and (block2[2] in G.nodes):
			G.add_node(block2[1])
			text_node.append(block2[0])
			hovertext_node.append(popup_layout.format(block2[0],block2[1],block2[2],block2[3],block2[7],block2[4],block2[5],block2[6]))
			color_node.append(colors['node-log'])
		else:
			continue

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