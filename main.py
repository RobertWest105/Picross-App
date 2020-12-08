import pygame
import os
import random
import math
import tkinter as tk
from tkinter.filedialog import askopenfilename
from photoToPicross import imageToPicross

# Pygame setup
pygame.init()
pygame.font.init()

# Window setup
WIDTH, HEIGHT = 850, 650
bottomBarHeight = HEIGHT//10

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

FONT_SIZE = 20

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Picross App")

BG = pygame.transform.scale(pygame.image.load(os.path.join("PicrossAppAssets", "PicrossBackground.png")), (WIDTH, HEIGHT))


class Board:
    def __init__(self, boardOrigin, gridWidth, gridHeight, sqSize=30):
        self.origin = boardOrigin
        self.cols = gridWidth
        self.rows = gridHeight
        self.sqSize = sqSize

        self.squares = [[Square(self.origin[0] + j * sqSize, self.origin[1] + i * sqSize, sqSize) for j in range(gridWidth)] for i in range(gridHeight)]

    def draw(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.squares[i][j].draw()

    def makeSquaresChangeable(self):
        for row in self.squares:
            for sq in row:
                sq.stateChangeable = True

    def resetBoard(self):
        for row in self.squares:
            for sq in row:
                sq.reset()


class Square:
    def __init__(self, posX, posY, size=40):
        self.x = posX
        self.y = posY
        self.size = size
        self.state = 0
        self.xSprite = pygame.transform.scale(pygame.image.load(os.path.join("PicrossAppAssets", "XSquare.png")), (self.size - 2, self.size - 2))
        self.stateChangeable = True

    def draw(self):
        if self.state == 0 or self.state == 1:
            pygame.draw.rect(WINDOW, WHITE if self.state == 0 else BLUE, (self.x, self.y, self.size - 2, self.size - 2))
        else:
            WINDOW.blit(self.xSprite, (self.x, self.y))

    def setState(self, newState):
        if self.stateChangeable:
            if self.state != newState and self.state < 2:
                self.state = newState
            else:
                self.state = 0
            self.stateChangeable = False

    def reset(self):
        self.state = 0
        self.stateChangeable = True


def getClues(line):
    clues = []
    contiguousCount = 0
    for p in line:
        if p == 1:
            contiguousCount += 1
        elif contiguousCount != 0:
            clues.append(contiguousCount)
            contiguousCount = 0
    if contiguousCount != 0:
        clues.append(contiguousCount)
    if len(clues) == 0:
        clues.append(0)
    return clues


def makeRandPuzzle(width, height):
    rows = [[random.randint(0, 1) for j in range(width)] for i in range(height)]
    cols = [[row[j] for row in rows] for j in range(width)]

    return (rows, cols)


def checkLine(line, clues):
    return getClues(line) == clues


def createButton(picture, centre):
    image = pygame.image.load(picture)
    imagerect = image.get_rect()
    imagerect.center = centre
    WINDOW.blit(image, imagerect)
    return imagerect


def mouseInRect(rect, mousePos):
    return rect.topleft[0] <= mousePos[0] <= rect.bottomright[0] and rect.topleft[1] <= mousePos[1] <= rect.bottomright[1]


def main(mode, randomSize=None, imageFile=None):
    run = True
    fps = 60
    clock = pygame.time.Clock()

    mainFont = pygame.font.SysFont("calibri", FONT_SIZE)
    solvedFont = pygame.font.SysFont("calibri", FONT_SIZE*2)

    rows, cols = (0, 0)

    # Create puzzle based on mode selected from main menu
    if mode == "image" and imageFile is not None:
        try:
            targetHeight = 20
            rows, cols = imageToPicross(imageFile, targetHeight)
        except Exception as e:
            # Unable to create puzzle from image
            return
    elif mode == "random" and randomSize is not None:
        rows, cols = makeRandPuzzle(randomSize[0], randomSize[1])
    else:
        # Invalid mode selected
        return

    # Get clues and prepare to initialize board
    gridWidth = len(cols)
    gridHeight = len(rows)

    rowClues = [getClues(row) for row in rows]
    colClues = [getClues(col) for col in cols]

    rowClueTextLines = []
    for i in range(len(rowClues)):
        index = 0
        cluesString = ""
        for clue in rowClues[i]:
            cluesString += (str(clue) + ", " if index < len(rowClues[i]) - 1 else str(clue))
            index += 1
        cluesText = mainFont.render(cluesString, 1, WHITE)
        rowClueTextLines.append(cluesText)

    cluesWidth = max([cluesLine.get_width() for cluesLine in rowClueTextLines]) + FONT_SIZE*0.25
    cluesHeight = max([len(colClues[j]) for j in range(gridWidth)])*FONT_SIZE

    maxSqSize = 40
    sqSize = int(min((WIDTH - cluesWidth)//gridWidth, (HEIGHT - cluesHeight - bottomBarHeight)//gridHeight, maxSqSize))

    # Initialize board
    board = Board((cluesWidth, cluesHeight), gridWidth, gridHeight, sqSize)

    # Initialize solved variables
    solvedRows = [False for i in range(gridHeight)]
    solvedCols = [False for i in range(gridWidth)]
    solved = False
    solvedTimer = 0

    # Display background
    WINDOW.blit(BG, (0, 0))

    # Display row clues
    index = 0
    for cluesLine in rowClueTextLines:
        WINDOW.blit(cluesLine, (cluesWidth - cluesLine.get_width() - FONT_SIZE*0.25, cluesHeight + int(0.1*sqSize) + index*sqSize))
        index += 1

    # Display col clues
    for i in range(len(colClues)):
        index = 0
        for clue in reversed(colClues[i]):
            clueText = mainFont.render(f"{clue}", 1, (255, 255, 255))
            digits = 1 + (int(math.log10(clue)) if clue > 0 else 0)
            WINDOW.blit(clueText, (cluesWidth + int(i*sqSize + (0.3*sqSize if digits == 1 else 0)), cluesHeight - FONT_SIZE - index*FONT_SIZE))
            index += 1

    # Display 'main menu' and 'restart' buttons
    menuButton = createButton(os.path.join("PicrossAppAssets", "MainMenuButton.png"), (WIDTH//5, HEIGHT - bottomBarHeight//2))
    restartButton = createButton(os.path.join("PicrossAppAssets", "RestartButton.png"), (3*WIDTH//5, HEIGHT - bottomBarHeight//2))

    def redrawWindow():
        board.draw()

        if solved:
            solvedText = solvedFont.render("Complete!", 1, RED)
            WINDOW.blit(solvedText, (WIDTH//2 - solvedText.get_width()//2, HEIGHT//2))

        pygame.display.update()

    mouseDown = False

    # Main loop
    while run:
        clock.tick(fps)
        redrawWindow()

        if solved:
            solvedTimer += 1
            if solvedTimer > fps*2:
                run = False
            else:
                continue

        # Check if puzzle is solved
        for rowIndex in range(len(board.squares)):
            solvedRows[rowIndex] = checkLine([sq.state for sq in board.squares[rowIndex]], rowClues[rowIndex])
        i = 0
        for col in [[row[j] for row in board.squares] for j in range(gridWidth)]:
            solvedCols[i] = checkLine([sq.state for sq in col], colClues[i])
            i += 1
        solved = all(solvedRows) and all(solvedCols)

        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN or mouseDown:
                mouseDown = True
                pos = pygame.mouse.get_pos()
                if pos[0] > cluesWidth and pos[0] < cluesWidth + gridWidth*sqSize and pos[1] > cluesHeight and pos[1] < cluesHeight + gridHeight*sqSize:
                    colClicked = int((pos[0] - cluesWidth)//sqSize)
                    rowClicked = int((pos[1] - cluesHeight)//sqSize)

                    if pygame.mouse.get_pressed()[0]:  # left click = 1st element in returned tuple
                        board.squares[rowClicked][colClicked].setState(1)  # state 1 means filled
                    elif pygame.mouse.get_pressed()[2]:  # right click = 3rd element
                        board.squares[rowClicked][colClicked].setState(2)  # any other state number means 'x' / grey
                elif mouseInRect(restartButton, pos) and event.type == pygame.MOUSEBUTTONDOWN:
                    board.resetBoard()
                elif mouseInRect(menuButton, pos) and event.type == pygame.MOUSEBUTTONDOWN:
                    run = False
            if event.type == pygame.MOUSEBUTTONUP:
                mouseDown = False
                board.makeSquaresChangeable()


def mainMenu():
    titleFont = pygame.font.SysFont("calibri", FONT_SIZE*3)
    menuTextFont = pygame.font.SysFont("calibri", FONT_SIZE)

    # Main menu text
    title = titleFont.render("PICROSS", 1, WHITE)

    widthText = menuTextFont.render("Choose width: ", 1, WHITE)
    heightText = menuTextFont.render("Choose height: ", 1, WHITE)

    instructionText = menuTextFont.render("How to play:", 1, WHITE)
    textLine1 = menuTextFont.render("Satisfy all row and column clues by filling squares, leaving gaps between contiguous blocks", 1, WHITE)
    textLine2 = menuTextFont.render("Left click to fill squares", 1, WHITE)
    textLine3 = menuTextFont.render("Right click to mark squares as empty", 1, WHITE)

    # Width and height of size buttons in pixels
    numberButtonWidth, numberButtonHeight = (42, 42)

    run = True

    modeChoice = None

    selectedWidth, selectedHeight = (0, 0)

    # mainMenu loop
    while run:
        WINDOW.blit(BG, (0, 0))

        # Draw title, dividing line and text for the width and height buttons
        WINDOW.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//8))

        pygame.draw.line(WINDOW, WHITE, (WIDTH//2, HEIGHT//3 - numberButtonHeight), (WIDTH//2, HEIGHT//2 + numberButtonHeight))

        WINDOW.blit(widthText, (WIDTH//4 - widthText.get_width() - numberButtonWidth//2, HEIGHT/3 - numberButtonHeight//4))
        WINDOW.blit(heightText, (WIDTH//4 - widthText.get_width() - numberButtonWidth//2, HEIGHT//3 + 3*numberButtonHeight//4))

        # Flag for whether or not the random button should be enabled
        randomButtonEnabled = selectedWidth != 0 and selectedHeight != 0

        # Draw correct versions of the width and height buttons depending on which ones have been selected
        widthButtons = [
            createButton(os.path.join("PicrossAppAssets", "5ButtonPressed.png" if selectedWidth == 5 else "5Button.png"), (WIDTH // 4, HEIGHT // 3)),
            createButton(os.path.join("PicrossAppAssets", "10ButtonPressed.png" if selectedWidth == 10 else "10Button.png"), (WIDTH // 4 + numberButtonWidth, HEIGHT // 3)),
            createButton(os.path.join("PicrossAppAssets", "15ButtonPressed.png" if selectedWidth == 15 else "15Button.png"), (WIDTH // 4 + 2 * numberButtonWidth, HEIGHT // 3)),
            createButton(os.path.join("PicrossAppAssets", "20ButtonPressed.png" if selectedWidth == 20 else "20Button.png"), (WIDTH // 4 + 3 * numberButtonWidth, HEIGHT // 3))
        ]
        heightButtons = [
            createButton(os.path.join("PicrossAppAssets", "5ButtonPressed.png" if selectedHeight == 5 else "5Button.png"), (WIDTH // 4, HEIGHT // 3 + numberButtonHeight)),
            createButton(os.path.join("PicrossAppAssets", "10ButtonPressed.png" if selectedHeight == 10 else "10Button.png"), (WIDTH // 4 + numberButtonWidth, HEIGHT // 3 + numberButtonHeight)),
            createButton(os.path.join("PicrossAppAssets", "15ButtonPressed.png" if selectedHeight == 15 else "15Button.png"), (WIDTH // 4 + 2 * numberButtonWidth, HEIGHT // 3 + numberButtonHeight)),
            createButton(os.path.join("PicrossAppAssets", "20ButtonPressed.png" if selectedHeight == 20 else "20Button.png"), (WIDTH // 4 + 3 * numberButtonWidth, HEIGHT // 3 + numberButtonHeight))
        ]

        # Draw correct version of random button depending on if the width and height have been selected
        randomButton = createButton(os.path.join("PicrossAppAssets", "RandomPuzzleButton.png" if randomButtonEnabled else "RandomPuzzleButtonDisabled.png"), (WIDTH // 3, HEIGHT // 2))

        # Draw 'from image' button
        imagePuzzleButton = createButton(os.path.join("PicrossAppAssets", "FromImageButton.png"), (2*WIDTH//3, 5*HEIGHT//12))

        # Draw instruction text
        WINDOW.blit(instructionText, (WIDTH//2 - instructionText.get_width()//2, 2*HEIGHT//3))
        WINDOW.blit(textLine1, (WIDTH//2 - textLine1.get_width()//2, 2*HEIGHT//3 + instructionText.get_height()))
        WINDOW.blit(textLine2, (WIDTH//2 - textLine2.get_width()//2, 2*HEIGHT//3 + instructionText.get_height() + textLine1.get_height()))
        WINDOW.blit(textLine3, (WIDTH//2 - textLine3.get_width()//2, 2*HEIGHT//3 + instructionText.get_height() + textLine1.get_height() + textLine2.get_height()))

        pygame.display.update()

        # start main in appropriate mode depending on user choice
        if modeChoice == "random":
            main("random", randomSize=(selectedWidth, selectedHeight))

            # main just returned so reset mainMenu variables
            modeChoice = None
            selectedWidth, selectedHeight = (0,0)
        elif modeChoice == "image":
            viableImageTypes = [("Image Files", ("*.png", "*.jpg"))]
            imageFileName = askopenfilename(initialdir=os.getcwd(), title="Select Image To Create Puzzle From",
                                            filetypes=viableImageTypes)
            tk.Tk().destroy()
            main("image", imageFile=imageFileName)
            
            # main just returned so reset mainMenu variables
            modeChoice = None
            selectedWidth, selectedHeight = (0, 0)

        # mainMenu event loop
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mousePos = pygame.mouse.get_pos()
                if mouseInRect(randomButton, mousePos) and randomButtonEnabled:
                    modeChoice = "random"
                elif mouseInRect(imagePuzzleButton, mousePos):
                    modeChoice = "image"
                elif mouseInRect(widthButtons[0], mousePos):
                    selectedWidth = 5
                elif mouseInRect(widthButtons[1], mousePos):
                    selectedWidth = 10
                elif mouseInRect(widthButtons[2], mousePos):
                    selectedWidth = 15
                elif mouseInRect(widthButtons[3], mousePos):
                    selectedWidth = 20
                elif mouseInRect(heightButtons[0], mousePos):
                    selectedHeight = 5
                elif mouseInRect(heightButtons[1], mousePos):
                    selectedHeight = 10
                elif mouseInRect(heightButtons[2], mousePos):
                    selectedHeight = 15
                elif mouseInRect(heightButtons[3], mousePos):
                    selectedHeight = 20

    pygame.quit()

# Start program
tk.Tk().withdraw()
mainMenu()
