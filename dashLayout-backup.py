import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input

from globalParameters import colors
from dataBase import explorer
from blockchainGraph import Blockchain_Graph, tools

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
							html.Div([html.B("⠀Block confirmation average (block/round): "), html.B(id="num_avgconf")], style = {'border': '1px solid black'}),
							html.Div([html.B("⠀Reversed blocks number average: "), html.B(id="num_y")], style = {'border': '1px solid black'}),
							html.Div([html.B("⠀Sync function calls number: "), html.B(id="num_callsync")], style = {'border': '1px solid black'}),
							html.Div([html.B("⠀Reversions number: "), html.B(id="num_callsyncrev")], style = {'border': '1px solid black'}),
							html.Div([html.B("⠀Reversed blocks number: "), html.B(id="num_numrevblock")], style = {'border': '1px solid black'}),
							html.Div([html.B("⠀Received blocks number: "), html.B(id="num_receivedblocks")], style = {'border': '1px solid black'}),
							html.Div([html.B("⠀Round number: "), html.B(id="num_numround")], style = {'border': '1px solid black'}),
							html.Div([html.B("⠀Confirmation Blocks number: "), html.B(id="num_numblockstable")], style = {'border': '1px solid black'}),
							html.Div([html.B("⠀Late blocks number: "), html.B(id="num_lateblocks")], style = {'border': '1px solid black'}),
							html.Div([html.B("⠀Produced blocks: "), html.B(id="num_numblocks")], style = {'border': '1px solid black'})
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
	Output('num_y', 'children'),
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
