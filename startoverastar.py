import pygame
from pygame.constants import QUIT
import pygame.freetype
from queue import PriorityQueue
from Map import Map_Obj

'''
code-source: https://www.youtube.com/watch?v=JtiK0DOeI4A&t=2s
from: Tech with tim
downloaded: 15.09.2021
modified to fit needs for assignment
'''

# Colors
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
LIGHTGREY = (100,100,100)
GREY = (130,130,130)
DARKGREY = (190,190,190)
PLUM = (221, 160, 221)
ORANGE = (255,165,0)
TURQ = (64,224,208)

#colored spots (pygame tiles)
BARRIER = RED
START = ORANGE
OPEN_SPOT = WHITE
STAIRS = LIGHTGREY
PACKED_STAIRS = GREY
PACKED_ROOM = DARKGREY
CHECKED_PATH = GREEN
CORRECT_PATH = BLUE
CLOSED_PATH = PLUM
GOAL = TURQ

pygame.init()
GAME_FONT = pygame.freetype.SysFont("Arial.tff", 12)

map_obj = Map_Obj(task=1)

START_POS = map_obj.start_pos
END_POS = map_obj.end_goal_pos
START_X, START_Y = START_POS[0], START_POS[1]
GOAL_X, GOAL_Y = END_POS[0], END_POS[1]

ROWS = len(map_obj.str_map)
COLS = len(map_obj.str_map[0])

WIDTH = COLS*13
HEIGHT = ROWS*13
GAP = WIDTH // COLS

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("A* Algorithm for Samfundet")

class Spot:
    def __init__(self, value, row, col, gap, total_rows):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * gap
        self.y = row * gap
        self.neighbors = []
        self.gap = gap
        self.total_rows = total_rows
        self.cost = None

    def get_int_value(self):
        if self.value in [' S ', ' E ', ' P ', ' CP ', ' C ']:
            return 0
        if self.value == ' # ':
            return 0
        if self.value == ' . ':
            return 1
        if self.value == ' , ':
            return 2
        if self.value == ' : ':
            return 3
        if self.value == ' ; ':
            return 4
        else:
            return 0
        
    def get_pos(self):
        return self.row, self.col

    def make_start(self):
        self.value = ' S '

    def make_end(self):
        self.value = ' E '

    def make_closed(self):
        self.value = ' # '

    def make_checked(self):
        self.value = ' C '

    def make_path(self):
        self.value = ' P '

    def make_correct_path(self):
        self.value = ' CP '

    def is_closed(self):
        return self.value == ' # '

    def is_open(self):
        return self.value in [' . ', ' , ', ' : ', ' ; ']

 
    def draw(self, win):
        '''
        Draws spots in the color 
        corresponding to the right value
        '''
        if self.value == ' # ':
            pygame.draw.rect(win, BARRIER, (self.x, self.y, self.gap, self.gap))
        elif self.value == ' C ':
            pygame.draw.rect(win, CLOSED_PATH, (self.x, self.y, self.gap, self.gap))
        elif self.value == ' . ':
            pygame.draw.rect(win, OPEN_SPOT, (self.x, self.y, self.gap, self.gap))
        elif self.value == ' , ':
            pygame.draw.rect(win, STAIRS, (self.x, self.y, self.gap, self.gap))
        elif self.value == ' : ':
            pygame.draw.rect(win, PACKED_STAIRS, (self.x, self.y, self.gap, self.gap))
        elif self.value == ' ; ':
            pygame.draw.rect(win, PACKED_ROOM, (self.x, self.y, self.gap, self.gap))
        elif self.value == ' S ':
            pygame.draw.rect(win, START, (self.x, self.y, self.gap, self.gap))
        elif self.value == ' E ':
            pygame.draw.rect(win, GOAL, (self.x, self.y, self.gap, self.gap))
        elif self.value == ' P ':
            pygame.draw.rect(win, CHECKED_PATH, (self.x, self.y, self.gap, self.gap))
        elif self.value == ' CP ':
            pygame.draw.rect(win, CORRECT_PATH, (self.x, self.y, self.gap, self.gap))
        else:
            pygame.draw.rect(win, (0,0,0), (self.x, self.y, self.gap, self.gap))

    def update_neighbors(self,grid):
        '''
        Updates the neighbor spots to the current spot 
        '''
        if (self.row > 0): #Up
            if not grid[self.row - 1][self.col].is_closed():
                self.neighbors.append(grid[self.row - 1][self.col])

        if (self.col > 0): #Left
            if not grid[self.row][self.col - 1].is_closed():
                self.neighbors.append(grid[self.row][self.col - 1])

        if (self.row < ROWS - 1): #Down
            if not grid[self.row + 1][self.col].is_closed():
                self.neighbors.append(grid[self.row + 1][self.col])

        if (self.col < COLS - 1): #Right
            if not grid[self.row][self.col + 1].is_closed():
                self.neighbors.append(grid[self.row][self.col + 1])

    def __lt__(self, other):
        return False

def h(p1, p2):
    '''
    The heuristic function
    using Manhattan distance
    '''
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    '''
    Draws the shortest path by backtracking
    returns cost for later calulations
    '''
    number = 1
    while current in came_from:
        current  = came_from[current]
        current.make_correct_path()
        number += 1
        draw()
    return number


def a_star_algorithm(draw, grid, start, end):
    '''
    Implementing the algorithm
    '''
    count = 0
    open_set = PriorityQueue() 

    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row} 
    f_score[start] = h(start.get_pos(), end.get_pos())
    closed_set = []

    open_set.put((f_score[start], count, start)) 
    came_from = {}

   
    while not open_set.empty():
        current = open_set.get()[2]
        current.make_path()
        closed_set.append(current)

        if current == end: 
            end.cost = reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + neighbor.get_int_value() 
            if temp_g_score < g_score[neighbor]: 
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), END_POS)
                if neighbor not in closed_set: 
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    neighbor.make_path()
        end.cost = count
        draw()

        if current != start:
            current.make_checked()

    return False


def make_grid():
    '''
    Makes the grid that the spots live in
    Defines start and goal
    '''
    grid = []

    for i in range(ROWS):
        grid.append([])
        for j in range(COLS):
            node = Spot(map_obj.str_map[i][j], i, j, GAP, ROWS)
            grid[i].append(node)
    grid[START_X][START_Y].make_start()
    grid[GOAL_X][GOAL_Y].make_end()
    return grid

def draw(win, grid, rows, cols):
    for row in grid:
        for node in row:
            node.draw(win)
    
    GAME_FONT.render_to(WINDOW, (10,10), "Cost: " + str(grid[GOAL_X][GOAL_Y].cost), (50,50,50))
    pygame.display.update()

def main(win):
    grid = make_grid()
    start = None
    end = None
    run = True
    started = False

    while run: 
        draw(win, grid, ROWS, COLS)
        node1 = grid[START_X][START_Y]
        node1.make_start() 
        node2 = grid[GOAL_X][GOAL_Y]
        node2.make_end() 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if started:
                continue
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    started = True
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                a_star_algorithm(lambda: draw(win, grid, ROWS, COLS), grid, node1, node2)
    pygame.quit()

main(WINDOW)