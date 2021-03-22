# powerplant-coding-challenge

## Introduction

The objective of this challenge was to compute how much power each of a multitude of different powerplants need to produce 
(a.k.a. the production-plan) when the load is given and taking into account the cost of the underlying energy sources (gas, 
kerosine) and the Pmin and Pmax of each powerplant.

## Setup

Clone the repository from github and enter the project directory:
```
git clone https://github.com/AitAbdel/powerplant-coding-challenge.git
cd powerplant-coding-challenge
```

Then, install the required libraries:

```
pip install -r requirements.txt
```
## How to run

Run the flask app in a terminal:
```
python app.py
```
To submit a POST request to the endpoint /productionplan of the API, open a new terminal and go to the project directory. 

Then run the script client.py which sends a POST request to the endpoint /productionplan of the API:

```
python client.py
```

You can also submit a chosen payload by using the following CURL command: 

```
curl -X POST -d @example_payloads/payload2.json -H "Content-Type: application/json" http://127.0.0.1:8888/productionplan
```