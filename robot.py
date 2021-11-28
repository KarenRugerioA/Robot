#Programa que crea una simulacion donde robots limpian las diferentes casillas que existen en un tablero. En caso de que el robot se encuentre en una casilla
#limpia, tendra que moverse, de lo contrario tendra que limpiarla antes de moverse. El programa recibe NxM filas y columnas del tablero respectivamente, asi como
#el tiempo de ejecucion del programa (numero de movimientos posibles para los robots)y la cantidad de bloques sucios que se encuentran al inicio de la ejecucion.

#Realizado por:
#David Zárate López A01329785
#Karen Rugerio Armenta  A01733228
#José Antonio Bobadilla García A01734433
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
    #numero de casillas limpiadas por el robot
    self.limpiadas = 0
    self.cargando = 0
    self.index = 0
    self.matrix = self.model.matrix
    grid = PathGrid(matrix = self.matrix)
    self.grid = grid

  def step(self):
    #se elige al azar una posicion para que el robot avance
    next_moves = self.model.grid.get_neighborhood(self.pos, moore=False)
    next_move = self.random.choice(next_moves)
    #el robot revisa si el bloque en el que esta se encuentra limpio
    box = self.checkIfClean()
    #si el robot todavia puede hacer movimientos y la casilla no tiene cajas significa que puede moverse
    if self.movements >= self.model.time:
      print("Se ha acabado el tiempo de ejecucion , teniendo un total de",  self.movements * self.model.robots,"movimientos")
    #si el robot todavia puede hacer movimientos y el robot aun no lleva una caja significa que puede moverse
    if(self.movements < self.model.time and self.cargando != 1):
      self.movements += 1
      self.model.grid.move_agent(self, next_move)
    #si el robot ya lleva una caja significa que tiene que moverse y llevarla al stand
    #inicializadores del AStar
    elif (self.movements < self.model.time and self.cargando == 1):
      self.grid.cleanup()
      path = self.getPath()
      print("PATH DENTRO", path)
  
  def getPath(self):
    standList = self.model.stands
    print(standList)

    self.grid.cleanup()
    grid = PathGrid(matrix= self.matrix)
    self.grid = grid
    start = self.grid.node(self.pos[0], self.pos[1])
    # print("START X: ", self.pos[0])
    # print("START Y: ", self.pos[1])
    finder = AStarFinder(diagonal_movement = DiagonalMovement.never)
    end = self.grid.node(((standList[0])[0]), ((standList[0])[0]))
    path, runs = finder.find_path(start, end, self.grid)
    return path

  #funcion auxiliar que revisa si la casilla donde se encuentra el robot esta limpia
  def checkIfClean(self):
    cellmates = self.model.grid.get_cell_list_contents([self.pos])
    for block in cellmates:
      if(block.type == "DirtyBlock"):
        self.cargando += 1
        block.limpio = False
        block.changeColor()
        self.limpiadas += 1
        self.model.dirtyBlocks -= 1
        if self.model.dirtyBlocks == 0:
          print("Se han limpiado todas las casillas sucias en un tiempo de ejecucion de ", self.movements,"movimientos, teniendo un total de", self.movements * self.model.robots)
        return False
      elif(block.type == "CleanBlock"):
        return True

#Agente casilla Sucia
class DirtyBlock(Agent):
  def __init__(self, model, pos):
    super().__init__(model.next_id(), model)
    self.pos = pos
    self.type = "DirtyBlock"
    self.limpio = False

  #funcion  que cambia de color a la casilla al cambiarla de tipo sucia a limpia
  def changeColor(self):
    self.type = "CleanBlock"

class Stand(Agent):
  def __init__(self, model, pos):
    super().__init__(model.next_id(), model)
    self.pos = pos
    self.type = "Stand"
  

#Agente casilla limpia
class CleanBlock(Agent):
  def __init__(self, model, pos):
    super().__init__(model.next_id(), model)
    self.pos = pos
    self.type = "CleanBlock"
    self.limpio = True


class Maze(Model):
  #se asignan las variables modificables por el usuario siendo filas, columnas, robots, tiempo de ejecucion y el numero de cajas por acomodar
  def __init__(self, rows = 15, columns = 15, robots = 1, time = 100, dirtyBlocks = 6):
    super().__init__()
    self.schedule = RandomActivation(self)
    self.rows = rows
    self.columns = columns
    self.robots = robots
    self.time = time
    self.dirtyBlocks = dirtyBlocks
    self.grid = MultiGrid(self.columns, self.rows, torus=False)
    self.matrix = [
      # [1,1,1,1,0,0,0,0,0,0,0,1,1,1,1],
      # [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      # [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      # [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      # [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      # [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      # [0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
      # [0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
      # [0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
      # [0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
      # [1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
      # [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      # [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      # [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      # [1,1,1,0,0,0,0,0,0,0,0,0,1,1,1]

    ]
    self.stands = []
    #se crea una matriz de ceros para identificar las casillas sucias y limpias
    self.createCeroMatrix()
    #se crean los robots y bloques tanto limpios como sucios para colocarse en el tablero
    self.placeRobots()
    self.placeDirtyBlocks()
    self.placeCleanBlocks()
    self.placeStands()

  def step(self):
    self.schedule.step()
  
  @staticmethod
  def count_type(model):
      return model.dirtyBlocks

  #se define la cantidad de stands por crear con base a la cantidad de cajas que se encuentran en el almacen
  def placeStands(self):
    standNum = self.dirtyBlocks
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
      # print(self.stands)

    # else:
    #   for i in range (0,standNum):
    #     block = Stand(self, (0,i))
    #     self.grid.place_agent(block, block.pos)




  #se crean los bloques sucios de manera aleatoria
  def placeDirtyBlocks(self):
    blocks = self.dirtyBlocks
    while blocks > 0:
      randomX = self.random.randint(0, self.rows-1)
      randomY = self.random.randint(0, self.columns-1)
      while self.matrix[randomX][randomY] == 0:
        randomX = self.random.randint(0, self.rows-1)
        randomY = self.random.randint(0, self.columns-1)
      block = DirtyBlock(self,(randomY,randomX))
      self.grid.place_agent(block, block.pos)
      self.matrix[randomX][randomY] = 0
      blocks -= 1

  #se crean los bloques limpios
  def placeCleanBlocks(self):
     for _,x,y in self.grid.coord_iter():
      if self.matrix[y][x] == 1: #cambio 0x1
        block = CleanBlock(self,(x,y))
        self.grid.place_agent(block, block.pos)

  #se crea la matriz que contendra las casillas limpias y sucias
  def createCeroMatrix(self):
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

#Agent portrayal permite rea
def agent_portrayal(agent):
  if(agent.type == "robot"):
    return {"Shape": "robot.png", "Layer": 1}
  elif(agent.type == "DirtyBlock"):
    return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "gold", "Layer": 1}
  elif(agent.type == "CleanBlock"):
    return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "#ced4da", "Layer": 1}
  elif(agent.type == "Stand"):
    return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "green", "Layer": 1}
  elif(agent.type == "StandFull"):
    return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "red", "Layer": 1}

grid = CanvasGrid(agent_portrayal, 15, 15, 450, 450)
server = ModularServer(Maze, [grid], "Maze", {
  # "rows": UserSettableParameter("slider","Rows", 17, 1, 100, 1),
  # "columns": UserSettableParameter("slider","Columns", 14, 1, 100, 1),
  # "robots": UserSettableParameter("slider","Robots", 1, 1, 1000, 1),
  # "time": UserSettableParameter("slider","Time", 1, 1, 10000, 1),
  # "dirtyBlocks": UserSettableParameter("slider","Dirty Blocks", 1, 1, 10000, 1)
})

server.port = 8521
server.launch()