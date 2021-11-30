from typing import Counter
import flask
from flask.json import jsonify
import uuid
import robotCode
from robotCode import Maze, Robot, BoxBlock

games = {}

app = flask.Flask(__name__)

@app.route("/games", methods=["POST"])

def create():
    global games
    id = str(uuid.uuid4())
    games[id] = Maze()
    return "ok", 201, {'Location': f"/games/{id}"}


@app.route("/games/<id>", methods=["GET"])
def queryState(id):
    global model
    model = games[id]
    model.step()
    agentList = []
    #buscar todos los agentes del modelo y si son cajas o robots incluirlos en el arreglo de diccionarios a mandar al json
    for i in range(len(model.schedule.agents)):
        agent = model.schedule.agents[i]
        # print("tipo: ", type(agent))
        # print("modelo: ", model.schedule.agents)
        if type(agent) is robotCode.Robot:
            temp = {"x": agent.pos[0], "y": agent.pos[1], "tipo" : "Robot", "carrying" : agent.carrying, "counterRobot": agent.counterRobot, "pickedBox" : agent.pickedBox if agent.pickedBox is not None else -1}
            agentList.append(temp)
            print(agent.counterRobot)
        elif type(agent) is robotCode.BoxBlock:
            agentList.append({"x": agent.pos[0], "y": agent.pos[1], "tipo" : "BoxBlock", "picked" : agent.picked, "id" : agent.id})
        else:
            i = i - 1
    return jsonify({"Items":agentList})

app.run()