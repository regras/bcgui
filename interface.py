import networkx as nx
import plotly.graph_objs as go
from networkx.drawing.nx_agraph import graphviz_layout
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import sqlite3
import threading

#OBS:
#para evitar o erro 'lazy loading' execute esse arquivo com o seguinte código no terminal: waitress-serve interface:app.server

############################################################################################################## BANCO DE DADOS

#Acessa o banco de dados - Retorna uma lista - cada termo é um bloco - cada bloco possui na ordem: id, hash, prev_hash, arrive_time, round
def blockchain_list():
	databaseLocation = 'bc_pos-pos_graphic_interface/blocks/blockchain.db'	
	db = sqlite3.connect(databaseLocation)
	cursor = db.cursor()
	cursor.execute('SELECT id, hash, prev_hash, arrive_time, round FROM localChains')
	a = cursor.fetchall()
	blocks = []
	i=0
	for b in a:
		blocks.append([])
		blocks[i].append(b[0]) #id
		blocks[i].append(b[1]) #hash
		blocks[i].append(b[2]) #prev_hash
		blocks[i].append(b[3]) #arrive_time
		blocks[i].append(b[4]) #round
		i = i + 1
	db.close()
	return blocks

############################################################################################################## NETWORKX E PLOTLY

#cores de cada elemento
colors = {'background_graph':'#f8f8f8',
	'paper-background-graph':'#f8f8f8',
	'title-text':'#000000',
	'pop-up':'#00bfff',
	'pop-up-text':'#000000',
	'pop-up-border':'#ffffff',
	'node':'#00bfff',
	'node-text':'#000000',
	'edge':'#000000',
	'web_backgroung':'#000000' #pesquisar como mudar o background da pag inteira
}


def Blockchain_Graph():

	#gera a lista com os blocos
	blockchain_data = blockchain_list()

	G = nx.DiGraph() #gera um gráfico vazio

	hovertext_node=[] #contem o texto pop-up do bloco
	text_node=[] #contem o texto dentro do bloco

	popup_layout = "<b>ID: </b>{}<br><b>Hash: </b>{}<br><b>Prev. Hash: </b>{}<br><b>Arrive Time: </b>{}<br><b>Round: </b>{}"

	#cria os nodes com base no hash inserindo seus respectivos textos
	for block in blockchain_data:
		G.add_node(block[1])
		text_node.append(block[0])
		hovertext_node.append(popup_layout.format(block[0],block[1],block[2],block[3],block[4]))

	#cria os edges (ligando o hash ao prev_hash de cada bloco)
	for block in blockchain_data:
		if block[2] != "":
			G.add_edge(block[2], block[1])
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

	#definições dos edges
	edge_trace = go.Scatter(
				x=edge_x, 
				y=edge_y,
				line=dict(	
						width=3, 
						color=colors['edge']
						#,dash = "dot" #para edge pontilhado
					), 
				hoverinfo='none', 
				mode='lines', 
				line_shape='spline', 
				opacity=1
				)

	#separa todas as coordenadas x e y dos nodes 
	node_x = []
	node_y = []
	for node in G.nodes():
		x, y = G.nodes[node]['pos']
		node_x.append(x)
		node_y.append(y)

	#definições dos nodes
	node_trace = go.Scatter(
				x=node_x, 
				y=node_y, 
				hovertext=hovertext_node, 
				text=text_node, 
				textposition="middle center", 
				mode='markers+text', 
				hoverinfo="text", 
				marker=dict(	size=40, 
						color=colors['node'], 
						symbol='square'
					),
				line=dict(	width=40
					),
				textfont=dict(	color=colors['node-text']
					),
				opacity=1
				)

	#renderiza o gráfico
	Graph = go.Figure(
			data=[edge_trace, node_trace], 
			layout=go.Layout(
						title='',#titulo dentro do gráfico 
						titlefont_size=16, 
						showlegend=False, 
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


############################################################################################################## DASH



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
							dcc.Graph(	
								id='my-graph',
								figure=Blockchain_Graph(),
								config=tools,
							),

							dcc.Interval( #atualizar o gráfico a cada 10 segundos
            							id='interval_component',
            							interval=10000, #em ms
            							n_intervals=0
        						),
							html.H6('ID range:'),
							dcc.RadioItems(
                						id='id_range',
               							options=[{'label': i, 'value': i} for i in [10, 15, 20, 'all']],
                						value='Linear',
               							labelStyle={'display': 'inline-block'}
            						)
						]
           				)
		     		]
			)

app.layout = serve_layout

#As "entradas" e "saídas" da nossa interface de aplicação são descritas declarativamente através do @app.callback, de forma a criar Dash interativos

@app.callback(
	Output('my-graph','figure'),
	[Input('interval_component','n_intervals')]
)
def update_my_graph(interval_component):

#	if(node.Status( )):
#      		node.sema.acquire( )
#		graph = Blockchan_Graph( )
#		node.clear( )
#		node.sema.release( )
#		return graph

	return Blockchain_Graph()


if __name__ == '__main__':
	app.run_server(debug=True, use_reloader=True, host='127.0.0.1',port=8050)
	#debug=True significa que o Dash atualizará automaticamente o navegador quando você fizer uma alteração no código.
		
