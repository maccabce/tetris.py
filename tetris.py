#attempting to build tetris in python with a boat load of help from youtube
#lets hope this works

import pygame 
import random
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

#initial spawn block definition for each of the pieces
pieceDefs = {
'I' : ((1,0),(1,1),(1,2),(1,3)),
'O' : ((0,1),(0,2),(1,1),(1,2)),
'T' : ((0,1),(1,0),(1,1),(1,2)),
'S' : ((0,1),(0,2),(1,0),(1,1)),
'Z' : ((0,0),(0,1),(1,1),(1,2)),
'J' : ((0,0),(1,0),(1,1),(1,2)),
'L' : ((0,2),(1,0),(1,1),(1,2)) }

directions = {
'down' : (1,0),
'right' : (0,1),
'left' : (0,-1),
'downRight' : (1,1),
'downLeft' : (1,-1),
'noMove' : (0,0) }

levelSpeeds = (48,43,38,33,28,23,18,13,8,6,5,5,5,4,4,4,3,3,3,2,2,2,2,2,2,2,2,2,2)
#These are the speeds of the moving pieces at each level. The Level speeds are defined as levelSpeeds[level]
#Each 10 cleared lines means a level up, asserting higher speeds at higher levels.
#After level 29, speed is always 1. The highest level is 99.

baseLinePoints = (0,40,100,300,1200)
#Total score is calculated as: Score = level*baseLinePoints[clearedLineNumberAtATime] + totalDropCount
#Drop means the action the player forces the piece down instead of free fall(By key combinations: down, down-left, down-rigth arrows)

#Class for the game input keys and their status
class GameKeyInput:
	
	def __init__(self):
		self.xNav = self.KeyName('idle',False) # 'left' 'right'
		self.down = self.KeyName('idle',False) # 'pressed' 'released'
		self.rotate = self.KeyName('idle',False) # 'pressed' //KEY UP
		self.cRotate = self.KeyName('idle',False) # 'pressed' //KEY Z
		self.enter = self.KeyName('idle',False) # 'pressed' //KEY Enter
		self.pause = self.KeyName('idle',False) # 'pressed' //KEY P
		self.restart = self.KeyName('idle',False) # 'pressed' //KEY R
	
	class KeyName:
	
		def __init__(self,initStatus,initTrig):
			self.status = initStatus
			self.trig = initTrig
				

#Class for the game's timing events
class GameClock:
	
	def __init__(self):
		self.frameTick = 0 #The main clock tick of the game, increments at each frame (1/60 secs, 60 fps)
		self.pausedMoment = 0
		self.move = self.TimingType(MOVE_PERIOD_INIT) #Drop and move(right and left) timing object
		self.fall = self.TimingType(levelSpeeds[STARTING_LEVEL]) #Free fall timing object
		self.clearAniStart = 0
	
	class TimingType:
		
		def __init__(self,framePeriod):
			self.preFrame = 0
			self.framePeriod = framePeriod
			
		def check(self,frameTick):
			if frameTick - self.preFrame > self.framePeriod - 1:
				self.preFrame = frameTick
				return True
			return False
	
	def pause(self):
		self.pausedMoment = self.frameTick
	
	def unpause(self):
		self.frameTick = self.pausedMoment
	
	def restart(self):
		self.frameTick = 0
		self.pausedMoment = 0
		self.move = self.TimingType(MOVE_PERIOD_INIT)
		self.fall = self.TimingType(levelSpeeds[STARTING_LEVEL])
		self.clearAniStart = 0
		
	def update(self):
		self.frameTick = self.frameTick + 1
		

# Class for all the game mechanics, visuals and events
class MainBoard:

	def __init__(self,blockSize,xPos,yPos,colNum,rowNum,boardLineWidth,blockLineWidth,scoreBoardWidth):
		
		#Size and position initiations
		self.blockSize = blockSize
		self.xPos = xPos
		self.yPos = yPos
		self.colNum = colNum
		self.rowNum = rowNum
		self.boardLineWidth = boardLineWidth
		self.blockLineWidth = blockLineWidth
		self.scoreBoardWidth = scoreBoardWidth
		
		#Matrix that contains all the existing blocks in the game board, except the moving piece
		self.blockMat = [['empty'] * colNum for i in range(rowNum)]
		
		self.piece = MovingPiece(colNum,rowNum,'uncreated')
		
		self.lineClearStatus = 'idle' # 'clearRunning' 'clearFin'
		self.clearedLines = [-1,-1,-1,-1]
		
		self.gameStatus = 'firstStart' # 'running' 'gameOver'
		self.gamePause = False
		self.nextPieces = ['I','I']
		
		self.score = 0
		self.level = STARTING_LEVEL
		self.lines = 0
	
	def restart(self):
		self.blockMat = [['empty'] * self.colNum for i in range(self.rowNum)]
		
		self.piece = MovingPiece(self.colNum,self.rowNum,'uncreated')
		
		self.lineClearStatus = 'idle'
		self.clearedLines = [-1,-1,-1,-1]		
		gameClock.fall.preFrame = gameClock.frameTick
		self.generateNextTwoPieces()
		self.gameStatus = 'running'
		self.gamePause = False
		
		self.score = 0
		self.level = STARTING_LEVEL
		self.lines = 0
		
		gameClock.restart()
		
	def erase_BLOCK(self,xRef,yRef,row,col):
		pygame.draw.rect(gameDisplay, BLACK, [xRef+(col*self.blockSize),yRef+(row*self.blockSize),self.blockSize,self.blockSize],0)
		
	def draw_BLOCK(self,xRef,yRef,row,col,color):
		pygame.draw.rect(gameDisplay, BLACK, [xRef+(col*self.blockSize),yRef+(row*self.blockSize),self.blockSize,self.blockLineWidth],0)
		pygame.draw.rect(gameDisplay, BLACK, [xRef+(col*self.blockSize)+self.blockSize-self.blockLineWidth,yRef+(row*self.blockSize),self.blockLineWidth,self.blockSize],0)
		pygame.draw.rect(gameDisplay, BLACK, [xRef+(col*self.blockSize),yRef+(row*self.blockSize),self.blockLineWidth,self.blockSize],0)
		pygame.draw.rect(gameDisplay, BLACK, [xRef+(col*self.blockSize),yRef+(row*self.blockSize)+self.blockSize-self.blockLineWidth,self.blockSize,self.blockLineWidth],0)

		pygame.draw.rect(gameDisplay, color, [xRef+(col*self.blockSize)+self.blockLineWidth,yRef+(row*self.blockSize)+self.blockLineWidth,self.blockSize-(2*self.blockLineWidth),self.blockSize-(2*self.blockLineWidth)],0)
	
	def draw_GAMEBOARD_BORDER(self):
		pygame.draw.rect(gameDisplay, BORDER_COLOR, [self.xPos-self.boardLineWidth-self.blockLineWidth,self.yPos-self.boardLineWidth-self.blockLineWidth,(self.blockSize*self.colNum)+(2*self.boardLineWidth)+(2*self.blockLineWidth),self.boardLineWidth],0)
		pygame.draw.rect(gameDisplay, BORDER_COLOR, [self.xPos+(self.blockSize*self.colNum)+self.blockLineWidth,self.yPos-self.boardLineWidth-self.blockLineWidth,self.boardLineWidth,(self.blockSize*self.rowNum)+(2*self.boardLineWidth)+(2*self.blockLineWidth)],0)
		pygame.draw.rect(gameDisplay, BORDER_COLOR, [self.xPos-self.boardLineWidth-self.blockLineWidth,self.yPos-self.boardLineWidth-self.blockLineWidth,self.boardLineWidth,(self.blockSize*self.rowNum)+(2*self.boardLineWidth)+(2*self.blockLineWidth)],0)
		pygame.draw.rect(gameDisplay, BORDER_COLOR, [self.xPos-self.boardLineWidth-self.blockLineWidth,self.yPos+(self.blockSize*self.rowNum)+self.blockLineWidth,(self.blockSize*self.colNum)+(2*self.boardLineWidth)+(2*self.blockLineWidth),self.boardLineWidth],0)
	
	def draw_GAMEBOARD_CONTENT(self):
	
		if self.gameStatus == 'firstStart':	
			
			titleText = fontTitle.render('TETRIS', False, WHITE)
			gameDisplay.blit(titleText,(self.xPos++1.55*self.blockSize,self.yPos+8*self.blockSize))
			
			versionText = fontVersion.render('v 1.0', False, WHITE)
			gameDisplay.blit(versionText,(self.xPos++7.2*self.blockSize,self.yPos+11.5*self.blockSize))
			
		else:
		
			for row in range(0,self.rowNum):
				for col in range(0,self.colNum):
					if self.blockMat[row][col] == 'empty':
						self.erase_BLOCK(self.xPos,self.yPos,row,col)
					else:
						self.draw_BLOCK(self.xPos,self.yPos,row,col,blockColors[self.blockMat[row][col]])
						
			if self.piece.status == 'moving':
				for i in range(0,4):
					self.draw_BLOCK(self.xPos,self.yPos,self.piece.blocks[i].currentPos.row, self.piece.blocks[i].currentPos.col, blockColors[self.piece.type])
					
			if self.gamePause == True:
				pygame.draw.rect(gameDisplay, DARK_GRAY, [self.xPos+1*self.blockSize,self.yPos+8*self.blockSize,8*self.blockSize,4*self.blockSize],0)
				pauseText = fontPAUSE.render('PAUSE', False, BLACK)
				gameDisplay.blit(pauseText,(self.xPos++1.65*self.blockSize,self.yPos+8*self.blockSize))
			
			if self.gameStatus == 'gameOver':
				pygame.draw.rect(gameDisplay, LIGHT_GRAY, [self.xPos+1*self.blockSize,self.yPos+8*self.blockSize,8*self.blockSize,8*self.blockSize],0)
				gameOverText0 = fontGAMEOVER.render('GAME', False, BLACK)
				gameDisplay.blit(gameOverText0,(self.xPos++2.2*self.blockSize,self.yPos+8*self.blockSize))
				gameOverText1 = fontGAMEOVER.render('OVER', False, BLACK)
				gameDisplay.blit(gameOverText1,(self.xPos++2.35*self.blockSize,self.yPos+12*self.blockSize))
		
		
	def draw_SCOREBOARD_BORDER(self):
		pygame.draw.rect(gameDisplay, BORDER_COLOR, [self.xPos+(self.blockSize*self.colNum)+self.blockLineWidth,self.yPos-self.boardLineWidth-self.blockLineWidth,self.scoreBoardWidth+self.boardLineWidth,self.boardLineWidth],0)
		pygame.draw.rect(gameDisplay, BORDER_COLOR, [self.xPos+(self.blockSize*self.colNum)+self.boardLineWidth+self.blockLineWidth+self.scoreBoardWidth,self.yPos-self.boardLineWidth-self.blockLineWidth,self.boardLineWidth,(self.blockSize*self.rowNum)+(2*self.boardLineWidth)+(2*self.blockLineWidth)],0)
		pygame.draw.rect(gameDisplay, BORDER_COLOR, [self.xPos+(self.blockSize*self.colNum)+self.blockLineWidth,self.yPos+(self.blockSize*self.rowNum)+self.blockLineWidth,self.scoreBoardWidth+self.boardLineWidth,self.boardLineWidth],0)
	
	def draw_SCOREBOARD_CONTENT(self):
		
		xPosRef = self.xPos+(self.blockSize*self.colNum)+self.boardLineWidth+self.blockLineWidth
		yPosRef = self.yPos
		yLastBlock = self.yPos+(self.blockSize*self.rowNum)
	
		if self.gameStatus == 'running':
			nextPieceText = fontSB.render('next:', False, TEXT_COLOR)
			gameDisplay.blit(nextPieceText,(xPosRef+self.blockSize,self.yPos))
			
			blocks = [[0,0],[0,0],[0,0],[0,0]]
			origin = [0,0]
			for i in range(0,4):
				blocks[i][ROW] = origin[ROW] + pieceDefs[self.nextPieces[1]][i][ROW]
				blocks[i][COL] = origin[COL] + pieceDefs[self.nextPieces[1]][i][COL]
				
				if self.nextPieces[1] == 'O':
					self.draw_BLOCK(xPosRef+0.5*self.blockSize,yPosRef+2.25*self.blockSize,blocks[i][ROW],blocks[i][COL],blockColors[self.nextPieces[1]])
				elif self.nextPieces[1] == 'I':
					self.draw_BLOCK(xPosRef+0.5*self.blockSize,yPosRef+1.65*self.blockSize,blocks[i][ROW],blocks[i][COL],blockColors[self.nextPieces[1]])
				else:
					self.draw_BLOCK(xPosRef+1*self.blockSize,yPosRef+2.25*self.blockSize,blocks[i][ROW],blocks[i][COL],blockColors[self.nextPieces[1]])
			
			if self.gamePause == False:
				pauseText = fontSmall.render('P -> pause', False, WHITE)
				gameDisplay.blit(pauseText,(xPosRef+1*self.blockSize,yLastBlock-15*self.blockSize))
			else:
				unpauseText = fontSmall.render('P -> unpause', False, self.whiteSineAnimation())
				gameDisplay.blit(unpauseText,(xPosRef+1*self.blockSize,yLastBlock-15*self.blockSize))
				
			restartText = fontSmall.render('R -> restart', False, WHITE)
			gameDisplay.blit(restartText,(xPosRef+1*self.blockSize,yLastBlock-14*self.blockSize))
					
		else:
		
			yBlockRef = 0.3
			text0 = fontSB.render('press', False, self.whiteSineAnimation())
			gameDisplay.blit(text0,(xPosRef+self.blockSize,self.yPos+yBlockRef*self.blockSize))
			text1 = fontSB.render('enter', False, self.whiteSineAnimation())
			gameDisplay.blit(text1,(xPosRef+self.blockSize,self.yPos+(yBlockRef+1.5)*self.blockSize))
			text2 = fontSB.render('to', False, self.whiteSineAnimation())
			gameDisplay.blit(text2,(xPosRef+self.blockSize,self.yPos+(yBlockRef+3)*self.blockSize))
			if self.gameStatus == 'firstStart':
				text3 = fontSB.render('start', False, self.whiteSineAnimation())
				gameDisplay.blit(text3,(xPosRef+self.blockSize,self.yPos+(yBlockRef+4.5)*self.blockSize))
			else:
				text3 = fontSB.render('restart', False, self.whiteSineAnimation())
				gameDisplay.blit(text3,(xPosRef+self.blockSize,self.yPos+(yBlockRef+4.5)*self.blockSize))		
		
		pygame.draw.rect(gameDisplay, BORDER_COLOR, [xPosRef,yLastBlock-12.5*self.blockSize,self.scoreBoardWidth,self.boardLineWidth],0)
		
		scoreText = fontSB.render('score:', False, TEXT_COLOR)
		gameDisplay.blit(scoreText,(xPosRef+self.blockSize,yLastBlock-12*self.blockSize))
		scoreNumText = fontSB.render(str(self.score), False, NUM_COLOR)
		gameDisplay.blit(scoreNumText,(xPosRef+self.blockSize,yLastBlock-10*self.blockSize))
		
		levelText = fontSB.render('level:', False, TEXT_COLOR)
		gameDisplay.blit(levelText,(xPosRef+self.blockSize,yLastBlock-8*self.blockSize))
		levelNumText = fontSB.render(str(self.level), False, NUM_COLOR)
		gameDisplay.blit(levelNumText,(xPosRef+self.blockSize,yLastBlock-6*self.blockSize))
		
		linesText = fontSB.render('lines:', False, TEXT_COLOR)
		gameDisplay.blit(linesText,(xPosRef+self.blockSize,yLastBlock-4*self.blockSize))
		linesNumText = fontSB.render(str(self.lines), False, NUM_COLOR)
		gameDisplay.blit(linesNumText,(xPosRef+self.blockSize,yLastBlock-2*self.blockSize))
	