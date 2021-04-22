# Blockchain Graphical User Interface

Blockchain Graphical User Interface is a Python tool for monitoring the dynamic evolution of a single node blockchain on the network under the control of a consensus mechanism. For practical development, the application has been integrated with the [Probabilistic Proof-of-Stake (PPoS)](https://github.com/regras/ppos_tb/tree/ppos_third_version_2_docker_execution) protocol.

![](header.png)

---
## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.


### Prerequisites

What you need to install to run the software and how to install it on Linux Ubuntu or Windows

#### Requested Python Libraries: Networkx, Graphviz, Plotly, Dash and SQLite3

- **Tutorial for linux Ubuntu**

Open the terminal as an administrator in the project directory and type in order:
1. ```chmod +x requirements-linux.sh```
2. ```./requirements-linux.sh```

- **Tutorial for Windows**

1. open cmd.exe as admin on the directory of the project and type: ```requirements-windows.bat```

2. To install **SQLite3** on Windows, you need to download the file from the SQLite [website](https://www.sqlite.org/download.html)
   - Create a new folder e.g., C:\sqlite
   - Extract the content of the file that you downloaded in the previous section to the C:\sqlite folder
   
3. To install graphviz correctly, follow this steps:
   - Download graphviz-2.38.msi from [Graphviz Website](https://graphviz.gitlab.io/_pages/Download/Download_windows.html) and install and run the file ```setup```.
   - Download the 2.7 wheel file you need from this [website](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pygraphviz)
   - Navigate to the directory that you downloaded the wheel file to
   - Run ```pip install pygraphviz-1.3.1-cp27-none-win_amd64.whl``` on terminal as admin.

### How to Use

Before running the application, you need the consensus mechanism [PPoS](https://github.com/regras/ppos_tb/tree/ppos_third_version_2_docker_execution), into which the application has been integrated. This link represents the testbed to evaluate PPoS consensus blockchain.

After having access to the project, it is necessary to define the location of the blockchain database in the variable ```databaseLocation``` in the ```globalParameters.py``` file. The blockchain data is a file named ```blockchain.db``` which is found in the ```blocks``` folder of the protocol [PPoS](https://github.com/regras/ppos_tb/tree/ppos_third_version_2_docker_execution).

After defining the variable ```databaseLocation```, the application can be started and executed together with the consensus protocol.

To start the application, open the Linux terminal and type:

```
python3 bcgui.py
```

The dash server will be running on ip host ```127.0.0.1``` and port ```8050```. To access the application just access:

```
http://127.0.0.1:8050/
```

Upon opening the link, a preview of the blockchain will be shown allowing interactions with the mouse cursor. 
It is also possible to change the application's website by changing the ip host and the port as shown below:

```
python3 bcgui.py <ip host> <port>
```

In the current state of the tool, the blockchain will be updated every 10 seconds as default, that is, if there is any creation or deletion of blocks from the blockchain the application will update the blockchain visualization every 10 seconds. If you want to change the time that tool updates, it is possible to change directly in the web interface.

## Deployment

This section presents some additional notes on how to deploy this to another active system. 

It is important to emphasize that the tool is still under development and will still undergo several improvements.

To implement the application in a consensus mechanism, it is necessary to understand the structure of the code. The entire interface code is divided into four modules, which are: ```globalParameter.py```, ```dataBase.py```, ```blockchainGraph.py```, ```dashLayout.py``` and ```bcgui.py```.

* **"GLOBAL PARAMETERS" section - ```globalParameter.py```**

This section has parameters corresponding to the colors of each page element and the location of the blockchain database. It is important to define the location of the blockchain database in the variable "databaseLocation" in this section so that the application can extract the necessary data.

* **"DATABASE" section - ```dataBase.py```**

This section is responsible for reading the database, and it extracts all relevant information from the blockchain from the database. This reading is done through the function "blockchain_list()" which returns a list where each term is a block of the blockchain with its respective information. In order to reuse this application in another consensus mechanism, some modifications will be necessary in the way the data is collected in each protocol by the function "blockchain_list()".


* **"NETWORKX AND PLOTLY" section - ```blockchainGraph.py```**

This section is responsible for processing the data acquired from the database. This data is handled by the "Blockchain_Graph()" function, using the "Networkx" and "Plotly" libraries to return an interactive blockchain graph. In order to reuse this application in another consensus mechanism, some modifications will be necessary in the way the data will be handled by the "Blockchain_Graph()" function.


* **"DASH" section - ```dashLayout.py```**

This section is responsible for all information that will be presented on the web interface. This is where the page layout and the elements that the user can interact with are configured.

* **"Start Server" section - ```bcgui.py```**

This is the initiator of the Blockchain Graphical User Interface. 
As stated earlier, the interface can be initialized from the command: ```python3 bcgui.py <ip host>```

---
## Built With

* [Networkx](https://networkx.github.io/documentation/stable/index.html) - Networkx User Guide
* [Plotly](https://plotly.com/python/) - Plotly Python Open Source Graphing Library
* [Dash and Plotly](https://dash.plotly.com/) - Dash User Guide (with Plotly)
* [Plotly and Networkx](https://plotly.com/python/network-graphs/) - Networkx Graphs in Python with Plotly


---
## Authors

* [**Bryan Wolff**](https://github.com/bryan-wolff)
* [**Diego Martins**](https://github.com/diegomat)
* [**ReGrAS**](https://github.com/regras) - Research Group on Applied Security

See also the list of [contributors](https://github.com/regras/bcgui/graphs/contributors)

---
## More information:
* [Wolff B.; Martins D. F. G.; Henriques M. A. A., "Ferramenta de monitoramento gráfico para suporte à criação e testes de novos mecanismos de consenso em blockchains", WTICG- SBSeg 2020, Brazilian Computer Society, Brazil, Oct. 2020.](https://submissao.ciente.live/wp-content/uploads/2020/10/208599.pdf)
