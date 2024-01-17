import sys
import os

class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)
    
    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)
    
    def empty(self):
        return len(self.frontier) == 0
    
    def remove(self):
        if self.empty():
            raise Exception("La Frontera esta vacía")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node
        
class QueueFrintier(StackFrontier):
    def remove(self):
        if self.empty():
            raise Exception("La Frontera esta vacía")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node
        
class Laberinto():

    typeSearch = None

    def __init__(self, filename):
        #Leemos el archivo y configuramos las dimensiones del laberinto
        with open(filename) as f:
            contents = f.read()
        
        #Validamos el punto de partida y la meta
        if contents.count("A") != 1:
            raise Exception("El labeinto debe de tener un punto de partida")
        if contents.count("B") != 1:
            raise Exception("El laberinto de tener un objetivo")
        
        #Determinamos las dimensiones del laberinto
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        #Mantenemos la trazabilidad de las paredes del Lab
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)
        
        self.solution = None
    
    #Imprimimos en la pantalla el laberinto
    def print(self):
        solution = self.solution[1] if self.solution is not None else None 
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i,j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()

    #Obtenemos los movimientos en el Laberinto
    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        
        return result
    
    #Resolvemos el Laberinto
    def solve(self):
        """Hallamos una solucion al Laberinto, si existe una solucion"""

        #Guardamos la trazabilidad del numero de estados explorados
        self.num_explored = 0

        #Inicializamos la Frontera a la posicion de inicio
        start = Node(state=self.start, parent=None, action=None)
        frontier = QueueFrintier()
        frontier.add(start)

        self.typeSearch = "Queue - Cola" if isinstance(frontier, QueueFrintier) else "Stack - Pila"

        #Inicializamos el conjunto de nodos explorados a vacio
        self.explored = set()

        #Mantenemos el bucle hasta hallar la solucion
        while True:
            #Si no queda nada en la frontera, no hay camino
            if frontier.empty():
                raise Exception("No hay solución")
            
            #Elige un nodo de la frontera
            node = frontier.remove()
            self.num_explored += 1

            #Si el nodo es el objetivo, resolvemos el laberinto
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return
        
            #Marcamos el nodo como explorado
            self.explored.add(node.state)

            #Agregamos vecinos del nodo a la frontera
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)
    
    #Dibujamos la imagen de salida
    def output_image(self, filename, show_solution=True, show_explored=False):
        
        from PIL import Image, ImageDraw

        cell_size_width = 50
        cell_size_height = 50
        cell_border = 2

        #Creamos un lienzo en blanco
        img = Image.new(
            "RGBA", 
            (self.width * cell_size_width, self.height * cell_size_height),
            (25, 26, 46)
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                #Paredes
                if col:
                    fill = (25, 26, 46)
                
                #Inicio
                elif (i, j) == self.start:
                    fill = (222, 97, 176)
                
                #Meta
                elif (i, j) == self.goal:
                    fill = (255, 190, 48)

                #Solucion
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (25, 206, 165)

                #Conjunto explorado
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (83, 43, 113)

                #Celda vacia 
                else:
                    fill = (228, 199, 249)
                
                #Dibujamos una celda
                draw.rectangle(
                    ([(j * cell_size_height + cell_border, i * cell_size_width + cell_border), ((j +1) * cell_size_height - cell_border, (i +1) * cell_size_width - cell_border)]),
                    fill=fill
                )
        img.save(filename)

if len(sys.argv) != 2:
    sys.exit("Usa: python laberinto.py lab1.txt")

name = sys.argv[1]
m = Laberinto(name)
print("Laberinto: ")
m.print()
print("Resolviendo...")
m.solve()
print("Estados explorados: ", m.num_explored)
print("Tipo de Lista: ", m.typeSearch)
print("Solucion:")
m.print()
m.output_image(os.path.splitext(name)[0] + ".png", show_explored=True)

