#Programa que crea una simulacion donde robots limpian las diferentes casillas que existen en un tablero. En caso de que el robot se encuentre en una casilla
#limpia, tendra que moverse, de lo contrario tendra que limpiarla antes de moverse. El programa recibe NxM filas y columnas del tablero respectivamente, asi como
#el tiempo de ejecucion del programa (numero de movimientos posibles para los robots)y la cantidad de bloques sucios que se encuentran al inicio de la ejecucion.

#Realizado por:
#Karen Rugerio Armenta  A01733228
#Ultima modificacion: 11/11/2021


from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.space import MultiGrid
from mesa.visualization.UserParam import UserSettableParameter
from mesa.datacollection import DataCollector
from mesa.visualization.modules import ChartModule
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.grid import Grid as PathGrid
from pathfinding.core.diagonal_movement import DiagonalMovement

#Agente robot
class Robot(Agent):
  def __init__(self, model, pos):
    super().__init__(model.next_id(), model)
    self.pos = pos
    #se asigna el tipo robot a la clase
    self.type = "robot"
    #movimientos realizados por el robot
    self.movements = 0
    #numero de casillas ordered por el robot
    self.ordered = 0
    self.carrying = 0
    self.matrix = self.model.matrix
    grid = PathGrid(matrix = self.matrix)
    self.grid = grid
    

  def step(self):
    #se elige al azar una posicion para que el robot avance
    next_moves = self.model.grid.get_neighborhood(self.pos, moore=False)
    next_move = self.random.choice(next_moves)
    #el robot revisa si el bloque en el que esta se encuentra isBox
    box = self.checkIfOccupated()
    #si el robot todavia puede hacer movimientos y la casilla no tiene cajas significa que puede moverse
    if self.movements >= self.model.time:
      print("Se ha acabado el tiempo de ejecucion , teniendo un total de",  self.movements * self.model.robots,"movimientos")
    #si el robot todavia puede hacer movimientos y el robot aun no lleva una caja significa que puede moverse
    if(self.movements < self.model.time and self.carrying != 1):
      self.movements += 1
      self.model.grid.move_agent(self, next_move)
    #si el robot ya lleva una caja significa que tiene que moverse y llevarla al stand
    #inicializadores del AStar
    elif (self.movements < self.model.time and self.carrying == 1):
      #se obtiene el path a donde se quiere ir
      self.grid.cleanup()
      path = self.getPath()
      #se lleva la caja al stand designado
      if(len(path)>1):
        next_move = path[1]
        self.model.grid.move_agent(self, next_move)
      #se deja la caja
      else:
        self.leaveBox()
        #si ya hay 5 cajas en el stand se avanza al siguiente stand
        if self.model.counter == 5:
          self.model.counter = 0
          self.model.stands.pop(0)
          self.fullStack()

  def leaveBox(self):
    self.carrying = False
    self.model.counter += 1 #api check
    cellmates = self.model.grid.get_cell_list_contents([self.pos])
    for block in cellmates:
      if(block.type == "Stand" and self.carrying == False):
        block.leaved = True
        print("leaved: ", block.leaved)


  #funcion que simula los stacks llenos
  def fullStack(self):
    cellmates = self.model.grid.get_cell_list_contents([self.pos])
    for block in cellmates:
      if(block.type == "Stand"):
        block.type = "StandFull"

  #funcion que calcula el path
  def getPath(self):
    #lista de stands
    standList = self.model.stands
    #valores de inicio y fin del path
    self.grid.cleanup()
    grid = PathGrid(matrix= self.matrix)
    self.grid = grid
    start = self.grid.node(self.pos[0], self.pos[1])
    finder = AStarFinder(diagonal_movement = DiagonalMovement.never)
    #se calcula a qué stand se debe llevar
    end = self.grid.node(((standList[0])[0]), ((standList[0])[1]))
    path, runs = finder.find_path(start, end, self.grid)
    return path

  #funcion auxiliar que revisa si la casilla donde se encuentra el robot esta limpia
  def checkIfOccupated(self):
    #se acceden a las casillas del grid
    cellmates = self.model.grid.get_cell_list_contents([self.pos])
    for block in cellmates:
      #se comprueba si se tiene una caja en el bloque en el que se encuentra el robot
      if(block.type == "BoxBlock"):
        self.carrying += 1
        block.isBox = False
        block.changeColor()
        block.picked = True
        self.ordered += 1
        self.model.disorderedBoxes -= 1
        if self.model.disorderedBoxes == 0:
          print("Se han ordenado todas las cajas en un tiempo de ", self.movements,", teniendo un total de", self.movements * self.model.robots," movimientos")
          #terminar ejecucion break
          return False
      elif(block.type == "NormalBlock"):
        return True

#Agente casilla con caja
class BoxBlock(Agent):
  def __init__(self, model, pos):
    super().__init__(model.next_id(), model)
    self.pos = pos
    self.type = "BoxBlock"
    self.isBox = False
    self.picked = False #api
    self.leaved = False #api

  #funcion  que cambia de color a la casilla al cambiarla de tipo ocupada a desocupada (nor,al)
  def changeColor(self):
    self.type = "NormalBlock"

#Agente casilla stand
class Stand(Agent):
  def __init__(self, model, pos):
    super().__init__(model.next_id(), model)
    self.pos = pos
    self.type = "Stand"
  

#Agente casilla sin caja (normal)
class NormalBlock(Agent):
  def __init__(self, model, pos):
    super().__init__(model.next_id(), model)
    self.pos = pos
    self.type = "NormalBlock"
    self.isBox = True

#Agente tablero
class Maze(Model):
  #se asignan las variables modificables por el usuario siendo filas, columnas, robots, tiempo de ejecucion y el numero de cajas por acomodar
  def __init__(self, rows = 10, columns = 10, robots = 5, time = 10000, disorderedBoxes = 11):
    super().__init__()
    self.schedule = RandomActivation(self)
    self.rows = rows
    self.columns = columns
    self.robots = robots
    self.time = time
    self.disorderedBoxes = disorderedBoxes
    self.grid = MultiGrid(self.columns, self.rows, torus=False)
    self.matrix = [ ]
    self.counter = 0
    self.stands = []
    #se crea una matriz de ceros para identificar las casillas con cajas y sin cajas
    self.createMatrix()
    #se crean los robots y bloques con cajas, sin cajas y de stands
    self.placeRobots()
    self.placeBoxBlocks()
    self.placeNormalBlocks()
    self.placeStands()

  def step(self):
    self.schedule.step()
  
  @staticmethod
  def count_type(model):
      return model.disorderedBoxes

  #se define la cantidad de stands por crear con base a la cantidad de cajas que se encuentran en el almacen
  def placeStands(self):
    standNum = self.disorderedBoxes
    #Se crea la cantidad necesaria de stands para la cantidad de cajas a ordenar
    if standNum % 5 == 0:
      standNum = int(standNum / 5)
    else:
      standNum = int(standNum / 5) + 1
    while standNum > 0:
      for i in range (0,self.rows):
        if standNum > 0:
          for j in range(0, self.columns):
            if standNum > 0:
              block = Stand(self, (i,j))
              self.grid.place_agent(block, block.pos)
              standNum -= 1
              self.stands.append((i,j))
              # print(": Stands",standNum)
            else:
              break
        else:
          break


  #se crean los bloques sucios de manera aleatoria
  def placeBoxBlocks(self):
    blocks = self.disorderedBoxes
    while blocks > 0:
      randomX = self.random.randint(0, self.rows-1)
      randomY = self.random.randint(0, self.columns-1)
      while self.matrix[randomX][randomY] == 0:
        randomX = self.random.randint(0, self.rows-1)
        randomY = self.random.randint(0, self.columns-1)
      block = BoxBlock(self,(randomY,randomX))
      self.grid.place_agent(block, block.pos)
      self.matrix[randomX][randomY] = 0
      blocks -= 1
      self.schedule.add(block)

  #se crean los bloques limpios
  def placeNormalBlocks(self):
     for _,x,y in self.grid.coord_iter():
      if self.matrix[y][x] == 1: #cambio 0x1
        block = NormalBlock(self,(x,y))
        self.grid.place_agent(block, block.pos)

  #se crea la matriz que contendra las casillas limpias y sucias
  def createMatrix(self):
    for i in range(0,self.rows):
      zeros = []
      for j in range(0,self.columns):
        zeros.append(1) #cambio 0x1
      self.matrix.append(zeros) 
  
  #se colocan los robots
  def placeRobots(self):
    for x in range(0,self.robots):
      robot = Robot(self, (0, x))
      self.grid.place_agent(robot, robot.pos)
      self.schedule.add(robot)

#Agent portrayal permite realizar la simulacion grafica 
def agent_portrayal(agent):
  if(agent.type == "robot"):
    return {"Shape": "robot.png", "Layer": 1}
  elif(agent.type == "BoxBlock"):
    return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "gold", "Layer": 1}
  elif(agent.type == "NormalBlock"):
    return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "#ced4da", "Layer": 1}
  elif(agent.type == "Stand"):
    return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "green", "Layer": 1}
  elif(agent.type == "StandFull"):
    return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "red", "Layer": 1}

grid = CanvasGrid(agent_portrayal, 10, 10, 450, 450)
# server = ModularServer(Maze, [grid], "Maze", {
# })

# server.port = 8521
# server.launch()

