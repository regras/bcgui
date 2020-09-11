# bcgui

Is a Python tool for monitoring the dynamic evolution of a blockchain under the control of a consensus mechanism. 
For practical development, the application has been integrated with the [PPoS](https://github.com/regras/bc_pos) protocol.



## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.


### Prerequisites

What you need to install to run the software and how to install it on Linux Ubuntu

#### Requested Python Libraries:

- Networkx
```
sudo pip install networkx
```
- Graphviz
```
sudo pip install graphviz
```
- Plotly
```
sudo pip install plotly
```
- Dash
```
sudo pip install dash==1.16.0
```
- SQLite 3
```
sudo apt-get install sqlite3
```


### Running

To start the application, open the Linux terminal and type:

```
python3 interface.py
```

The dash server will be running and to access the application just access:

```
http://127.0.0.1:8050/
```
Upon opening the url, a preview of the blockchain will be shown allowing interactions with the mouse cursor. In the current state of the tool, the blockchain will be updated every 10 seconds, that is, if there is any creation or deletion of blocks from the blockchain the application will update the blockchain visualization every 10 seconds.



## Deployment

This section presents some additional notes on how to deploy this to another active system. To implement the application in the consensus engine, it is necessary to define the location of the blockchain database in the variable "databaseLocation" in the blockchain_list () function. This function is responsible for reading the information from the database returning a list where each element is a block of the blockchain. To reuse this application in another consensus mechanism, some modifications are needed in the way data is collected in each protocol by the blockchain_list () function. Extracting the relevant information from the cited function of the protocol, it may be necessary to adjust how the Blockchain_Graph () function will work with this data. It is important to emphasize that the tool is still under development and will still undergo several improvements.

## Built With

* [Networkx](https://networkx.github.io/documentation/stable/index.html) - Networkx User Guide
* [Plotly](https://plotly.com/python/) - Plotly Python Open Source Graphing Library
* [Dash and Plotly](https://dash.plotly.com/) - Dash User Guide (with Plotly)
* [Plotly and Networkx](https://plotly.com/python/network-graphs/) - Networkx Graphs in Python with Plotly




## Authors

* **Bryan Wolff**
* **Diego Fernandes Gonçalves Martins**
* **Marco Aurelio Amaral Henriques**

See also the list of [contributors](https://github.com/regras/bcgui/graphs/contributors) who participated in this project.
