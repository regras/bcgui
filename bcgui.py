import sys
from dashLayout import app

#execute: python3 bcgui.py <ip host>
#OBS: para evitar o erro 'lazy loading' execute esse arquivo com o seguinte código no terminal: waitress-serve interface:app.server

if __name__ == '__main__':
	if(len(sys.argv) == 2):
		app.run_server(debug=True, use_reloader=True, host=sys.argv[1],port=8050)
	elif (len(sys.argv) == 3):
		app.run_server(debug=True, use_reloader=True, host=sys.argv[1],port=sys.argv[2])
	else:
		app.run_server(debug=True, use_reloader=True, host='127.0.0.1',port=8050)
	#debug=True significa que o Dash atualizará automaticamente o navegador quando você fizer uma alteração no código.
