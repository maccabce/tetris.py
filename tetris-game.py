#attempting to build tetris in python with a boat load of help from youtube
#lets hope this works

#must download and import pygame and possibly a linter
import random
import pygame
import math
import sys

pygame.init()
pygame.font.init()
#size of the game- might change if need be
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 600

gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT))
pygame.display.set_caption('Tetris')
clock = pygame.time.Clock()

pieceNames = ('I', 'O', 'T', 'S', 'Z', 'J', 'L')

STARTING_LEVEL = 0 #can change later if to start at a higher level

MOVE_PERIOD_INIT = 4 #Movement speed of pieces when arrows are pressed (up/down/right/left)

CLEAR_ANI_PERIOD = 4 
SINE_ANI_PERIOD = 120 

#Font sizes
SB_FONT_SIZE = 29 
FONT_SIZE_SMALL = 17 
PAUSE_FONT_SIZE = 66
GAMEOVER_FONT_SIZE = 66
TITLE_FONT_SIZE = 70
VERSION_FONT_SIZE = 20

fontSB = pygame.font.SysFont('agencyfb', SB_FONT_SIZE)
fontSmall = pygame.font.SysFont('agencyfb', FONT_SIZE_SMALL)
fontPAUSE = pygame.font.SysFont('agencyfb', PAUSE_FONT_SIZE)
fontGAMEOVER = pygame.font.SysFont('agencyfb', GAMEOVER_FONT_SIZE)
fontTitle = pygame.font.SysFont('agencyfb', TITLE_FONT_SIZE)
fontVersion = pygame.font.SysFont('agencyfb', VERSION_FONT_SIZE)

ROW = (0)
COL = (1)

#defining some of the colors

BLACK = (0,0,0)
WHITE = (255,255,255)
DARK_GRAY = (80,80,80)
GRAY = (110,110,110)
LIGHT_GRAY = (150,150,150)
BORDER_COLOR = GRAY
NUM_COLOR = WHITE
TEXT_COLOR = GRAY
