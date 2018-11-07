import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.common.exceptions import ElementNotVisibleException

width = 18
height = 18

browser = webdriver.Chrome(executable_path=r"./chromedriver")
matrix = [[-1 for x in range(width)] for y in range(height)] 

def sfind(row, column):
    return browser.find_element_by_id(str(row) + '_' + str(column))

# Reveals a certain square by clicking
def sopen(row, column):
    #print("Opening cell", row, column)
    try:
        sfind(row, column).click()
    except ElementNotVisibleException:
        print('', end='')
        #print("Failed opening cell", row, column)

# Marks a certain square by right-clicking
def smark(row, column):
    if matrix[row][column] != 9:
        ac = ActionChains(browser)
        ac.context_click(sfind(row, column)).perform()
        matrix[row][column] = 9
        return True
    return False

# Parses the board to update the bot's perception of the board
# since the board can reveal many new squares upon revealing one
# and the bot may not be aware of that
def parse_board():
    game = browser.find_element_by_id('game')
    for square in game.find_elements_by_class_name('square'):
        row, column = square.get_attribute('id').split('_')
        state = square.get_attribute('class').split(' ')[1]
        if state == 'blank':
            matrix[int(row)][int(column)] = -1
        if state.startswith('open'):
            matrix[int(row)][int(column)] = int(state[4])

# Prints the bot's perception of the board for debug purposes
def print_board():
    for y in range(height):
        for x in range(width):   
            print(matrix[y][x], end=' ')
        print()

# Find squares around a certain square
def squares_around(row, column):
    squares = list()
    for y in range(max(0, row - 1), min(height, row + 2)):
        for x in range(max(0, column - 1), min(width, column + 2)):
            squares.append((y, x))
    return squares

def closed_squares_around(row, column):
    squares = list()
    for square in squares_around(row, column):
        if matrix[square[0]][square[1]] == -1 or matrix[square[0]][square[1]] == 9:
            squares.append(square)
    return squares

# Find marked(flagged) squares around a certain square
def marked_squares_around(row, column):
    squares = list()
    for square in squares_around(row, column):
        if matrix[square[0]][square[1]] == 9:
            squares.append(square)
    return squares

# 
def open_all_available(row, column):
    if(matrix[row][column] == -1 or matrix[row][column] == 9):
        return
    if(matrix[row][column] == len(marked_squares_around(row, column))):
        for square in squares_around(row, column):
            if matrix[square[0]][square[1]] == -1:
                sopen(square[0], square[1])

def solve():
    browser.find_element_by_id('face').click()
    sopen(5, 15)
    for i in range(50):
        changed = False
        print("Solving a new iteration.")
        parse_board()
        print("Done parsing!")
        for y in range(height):
            for x in range(width):
                if matrix[y][x] != -1 and matrix[y][x] != 9:
                    #print("Cell", y, x, "has", len(closed_squares_around(y, x)), "closed neighbours.")
                    neighbours = closed_squares_around(y, x)
                    if len(neighbours) <= matrix[y][x]:
                        for neighbour in neighbours:
                            #print("Marking cell", neighbour[0], neighbour[1])
                            if smark(neighbour[0], neighbour[1]):
                                changed = True
                            
        for y in range(height):
            for x in range(width):
                open_all_available(y, x)

        if changed is False:
            print("I am stuck! There are no other fool proof moves. Restarting in 5 seconds.")
            time.sleep(5)
            break




print("Loading..")
browser.get('http://minesweeperonline.com/#intermediate')
print("Loaded.")
while True:
    print("Starting a new game.")
    solve()



