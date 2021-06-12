import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import dash_daq as daq

from globalParameters import colors
from dataBase import explorer
from blockchainGraph import Blockchain_Graph, tools

# DASH #######################################################################################################################



#importa o template css e passa para o Dash
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)#, external_stylesheets=external_stylesheets)

#título da página web
app.title = "Blockchain Graph" 

#definindo uma função para o layout para instanciar no app.layout (layout do app web)
#isso faz com que ao recarregar a pagina será feita uma nova consulta no banco para renderizar o gráfico
def serve_layout():
	return html.Div(	#div com todos os elementos
			children = [

				#header
				html.Div(		
					children = [	html.Img(src="assets/logo.png"),
									dbc.Navbar(
										children=[
											html.A(
												# Use row and col to control vertical alignment of logo / brand
												dbc.Row(
													[
														dbc.Col(
															dbc.NavbarBrand("Blockchain Graphical User Interface", className="header_bar")
														),
													],
													align="center",
													no_gutters=True,
												),
												href="https://github.com/regras/bcgui",
											)
										]
									),
						],
					className = "app_header"				
					),
				
				html.Br(),
				html.Br(),
				html.Br(),
				#gráfico
				html.Div(
					children = [	
							dcc.Graph(	
								id='my-graph',
								figure=Blockchain_Graph(["MAX(id) - {}".format(10), "MAX(id)"]),
								config=tools
							),
							dcc.Interval( #atualizar o gráfico a cada 10 segundos
            							id='interval_component',
            							interval=10000, #em ms
            							n_intervals=0
        						)
						],
					className = "app_Graph"		
					),

				html.Div(
					children = [
							html.B("Debug Mode: ", className = "toggle_switch_title"),
						    daq.BooleanSwitch(
        					id='toggle_switch',
							color="#343a40",
							#label = "Debug Mode",
							#labelPosition = "top",
        					on=False
    						)
					],
					className = "checkbox_div",
				),

				html.Br(),
				html.Br(),

				#Radio Item (ID)
				html.Div(
					#style=dict(),
						
					children = [
							html.B('ID range:'),

							dcc.RadioItems(
                						id='id_range',
               							options=[{'label': 10, 'value': 10},
										   		{'label': 20, 'value': 20},
												{'label': 50, 'value': 50},
												{'label': 100, 'value': 100},
												{'label': "Custom", 'value': -1}
										    	],
                						value=10,
               							labelStyle={'display': 'inline-block'}
            							)
						],
					className = "radio_ID"
					),

				html.Div([
					html.Div([html.B("Min: ", className = 'inputs_number_range_ID_min_title'),
							dcc.Input(
							id='rangeIDmin',
							type='number',
							value="MAX(id) - 10",
							disabled = True,
							#required = True,
							)
						],	
						className = "inputs_number_range_ID_min"
						),

					html.Div([html.B("Max: ", className = 'inputs_number_range_ID_max_title'),
							dcc.Input(
							id='rangeIDmax',
							type='number',
							value="MAX(id)",
							#required = True,
							disabled = True
							)
						],
						className = "inputs_number_range_ID_max"
						)
				],
				style = {'display': 'none'},
				id = "rangesDIV"),

				html.Br(),
				html.Br(),
			
				#Rádio Item (Update)
				html.Div(
					children = [	
							html.B('Update Period:'),
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
               							labelStyle={'display': 'inline-block'},
            						)
						],
					className = "radio_update_period"			
					),

				html.Br(),

				#button pause updates
				html.Div(
					#style=dict(),
						
					children = [	
							html.Button(	children="Pause Updates", 
									id='btn_1', 
									n_clicks=0,
									className="button_pause_updates"
								)
						]		
					),
					
				html.Br(),
				html.Br(),
					
				#html.B(children= [html.Br(),"Statistics:"], className = "statistics_title"),

				#tabela explorer
				html.Div(						
					children = [	html.Br(),
							html.Div([html.B("⠀Block confirmation average latency [rounds]: "), html.B(id="num_avgconf")],className = "label_table"),
							html.Div([html.B("⠀Reversed blocks number average: "), html.B(id="num_y")], className = "label_table"),
							html.Div([html.B("⠀Sync function calls number: "), html.B(id="num_callsync")], className = "label_table"),
							html.Div([html.B("⠀Reversions number: "), html.B(id="num_callsyncrev")], className = "label_table"),
							html.Div([html.B("⠀Reversed blocks number: "), html.B(id="num_numrevblock")], className = "label_table"),
							html.Div([html.B("⠀Received blocks number: "), html.B(id="num_receivedblocks")], className = "label_table"),
							html.Div([html.B("⠀Round number: "), html.B(id="num_numround")], className = "label_table"),
							html.Div([html.B("⠀Confirmation Blocks number: "), html.B(id="num_numblockstable")], className = "label_table"),
							html.Div([html.B("⠀Late blocks number: "), html.B(id="num_lateblocks")], className = "label_table"),
							html.Div([html.B("⠀Produced blocks: "), html.B(id="num_numblocks")], className = "label_table")
						],
					#style={'font-size':9, 'width': '20%', 'float': 'right'},

					className = "table_explorer"
	
					),
				html.H5(children="Research Group on Applied Security (ReGrAS) - FEEC - DCA - UNICAMP", className="rodape")


				],

			className = "app_elements"

			)

app.layout = serve_layout

#As "entradas" e "saídas" da nossa interface de aplicação são descritas declarativamente através do @app.callback, de forma a criar Dash interativos

#atualização do gráfico
@app.callback(
	Output('my-graph','figure'),
	[Input('interval_component','n_intervals'),
	Input('id_range','value'),
	Input('toggle_switch', 'on'),
	Input('rangeIDmin','value'),
	Input('rangeIDmax','value')
	]
)
def update_my_graph(interval_component, id_range, toggle_switch, rangeIDmin,rangeIDmax):
	range = id_range
	if id_range == -1 and (rangeIDmin != None and rangeIDmax != None):
		if rangeIDmin < rangeIDmax: 
			range = [rangeIDmin, rangeIDmax]
		else:
			range = [-1, -1]

	elif id_range == -1 and (rangeIDmin == None or rangeIDmax == None):
		#range = ["MAX(id) - {}".format(10), "MAX(id)"]
		range = [-1, -1]
	else:
		range = ["MAX(id) - {}".format(id_range), "MAX(id)"]
	return Blockchain_Graph(range, toggle_switch)


#radioitem id_range
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

#desabilitar/habilitar custom
@app.callback(
	[Output('rangeIDmin','disabled'),
	Output('rangeIDmax','disabled'),
	Output('rangesDIV','style')],
	[Input('id_range','value')]
)
def disable_custom_rangeID(id_range):
	if id_range == -1: 
		return False, False, None
	else:
		return True, True, {'display': 'none'}


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
	[Input('interval_component','n_intervals'),
	Input('id_range','value'),
	Input('rangeIDmin','value'),
	Input('rangeIDmax','value')]
)
def update_explorer_infos(interval_component,id_range,rangeIDmin,rangeIDmax):
	range = id_range
	if id_range == -1 and (rangeIDmin != None and rangeIDmax != None):
		if rangeIDmin < rangeIDmax: 
			range = [rangeIDmin, rangeIDmax]
		else:
			range = [-1, -1]

	elif id_range == -1 and (rangeIDmin == None or rangeIDmax == None):
		#range = ["MAX(id) - {}".format(10), "MAX(id)"]
		range = [-1, -1]
	else:
		range = ["MAX(id) - {}".format(id_range), "MAX(id)"]
	return explorer(range)
