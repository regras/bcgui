import networkx as nx
import plotly.graph_objs as go
from networkx.drawing.nx_agraph import graphviz_layout
import datetime

from globalParameters import colors
from dataBase import blockchain_list, explorer


# NETWORKX AND PLOTLY ########################################################################################################

def Blockchain_Graph(rangeID):

	#gera a lista com os blocos
	aux = blockchain_list(rangeID)
	data = [aux[0],aux[2],aux[1]]

	G = nx.DiGraph() #gera um gráfico vazio

	popup_layout = "<b>ID: </b>{}<br><b>Hash: </b>{}<br><b>Prev. Hash: </b>{}<br><b>Arrive Time (UTC): </b>{}<br><b>Arrive Time (local datetime GMT+00:00): </b>{}<br><b>Round: </b>{}<br><b>Proof_Hash: </b>{}<br><b>Successful draws of the creator node: </b>{}"

	#cria os nodes e os edges da blockchain com base no hash inserindo seus respectivos textos a partir da lista data
	#na primeira iteração do for, "blocks" representa cadeia principal, portanto os edges devem ser solidos
	#nas próximas iterações, "blocks" não será mais a cadeia principal, portanto os edges devem ser pontilhados
	num_ver = 0 #variavel que mostra a a qntdd de iteração do primeiro for
	for blocks in data: 
		for block in blocks:
			if block[2] != "" and ((block[2] in G.nodes) or num_ver == 0):
				G.add_node(block[1])
				G.nodes[block[1]]['cor'] = block[8] #armazena a cor, e os textos dentro do proprio node
				G.nodes[block[1]]['text_node'] = block[0]
				G.nodes[block[1]]['hovertext_node'] = popup_layout.format(block[0],block[1],block[2],block[3],block[7],block[4],block[5],block[6])
		
		#cria os edges (ligando o hash ao prev_hash de cada bloco) dos blocos da lista data
		for block in blocks:
			if block[2] != "" and (block[2] in G.nodes):
				if num_ver == 0:
					G.add_edge(block[2], block[1], dash_type = "solid") #além de criar o edge, armazena o tipo da aresta no edge
				else: 
					G.add_edge(block[2], block[1], dash_type = "dot")
		num_ver = num_ver + 1
	
	#Define o layout semelhante ao da blockchain
	pos = graphviz_layout(G, prog='dot', args="-Grankdir=LR")

	#adiciona um vetor da posição do node dentro do próprio node
	for node in G.nodes:
		G.nodes[node]['pos'] = list(pos[node])
	
	#define o intervalo do zoom que será dado na coordenada x ao iniciar o grafico
	#pega a cordenada do ultimo bloco da cadeia princial (x1) e 10° antes dele (x0)
	x_zoom_range = [0,0]
	y_zoom_range = [0,0]
	for block in data[0]:
		if block[0] == data[0][-1][0]: 
			x_zoom_range[1] = float(G.nodes[block[1]]['pos'][0])+200
			y_zoom_range[1] = float(G.nodes[block[1]]['pos'][1])+30
		elif block[0] == (data[0][-1][0]-5): #o numero 10 indica que o zoom sera dado nos ultimos 10 blocos
			x_zoom_range[0] = float(G.nodes[block[1]]['pos'][0])+200
			y_zoom_range[0] = float(G.nodes[block[1]]['pos'][1])

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
								showticklabels=False,
								range = y_zoom_range
							), 
						clickmode='event+select'
					)
			)
	
	#cria todos os edges
	for edge in G.edges():
		x0, y0 = G.nodes[edge[0]]['pos']
		x1, y1 = G.nodes[edge[1]]['pos']
		Graph.add_trace(
			go.Scatter(
				x=[x0,x1], 
				y=[y0,y1],
				#name="legenda",
				showlegend=False, 
				line=dict(	
						width=3, 
						color=colors['edge'],
						dash = G.edges[edge]['dash_type'], #para edge pontilhado usar "dot" e solido "solid"
					), 
				hoverinfo='none', 
				mode='lines', 
				line_shape='spline', 
				opacity=1
			)
		)

	#cria todos os blocos um por um
	#configura cada node
	for node in G.nodes:
		Graph.add_trace(
			go.Scatter(
				x=[G.nodes[node]['pos'][0]], 
				y=[G.nodes[node]['pos'][1]], 
				hovertext=[G.nodes[node]['hovertext_node']], 
				text=[G.nodes[node]['text_node']], 
				textposition="middle center", 
				mode='markers', #markes é para mostrar o contorno do bloco e text é p/ indice
				hoverinfo="text", # mostrar popup, também da para mostrar as coordenadas 'x', 'y', 'z' 
				#name="legenda",
				showlegend = False, 
				marker=dict(	size=25, 
						color = G.nodes[node]['cor'], 
						symbol='circle', #circle/square
						#cmin=0, # stable variable
					),
				line=dict(	width=40
					),
				textfont=dict(	color=colors['node-text']
					),
				opacity=1
				)
				)

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