'''
Tetris by El Greengo aka anbuf
last update: 24 fevrier 2015
'''

import multiplayer
import pygame
import input_map
import random

'''

Number of players: 2
Type: 1 vs 1
Screen: Split vertically
Rule: Classic Tetris multiplayer (first at the top lose)

TODO:
MANAGE THE SPEED - WAY TO FAST RIGHT NOW - 24 fevrier 2015
1. black background
2. split Screen
3. block (made with green 'X' for more ghettofabulousness)
4. move down blocks
5. rotate blocks
6. remove line
7. lose and win
8. make drink
9. difficulty

optionnal:
1. send line to other player
'''
BLOCK_WIDTH=24
TETRA_CHOICES=(1,4)
START_COORDINATES=(180,50)

GREEN=(0,255,0)
WHITE=(255,255,255)
BLACK=(0,0,0)

GRID_SIZE_X=12
GRID_SIZE_Y=20

MAX_SLOWDOWN = 20

class Tetris(multiplayer.Minigame):
    name = 'Tetris'

    def __init__(self, game):
        multiplayer.Minigame.__init__(self, game)
        self.width, self.height = self.screen.get_size()

        surface0 = pygame.Surface((self.width/2, self.height))
        surface1 = pygame.Surface((self.width/2, self.height))
        self.surfaces = [surface0, surface1]

        self.boards = [Board(self, 0), Board(self, 1)]

        self.middle_separator = pygame.Rect(self.width/2.0, 0, 10, self.height)

        self.events = [[] for i in range(2)]

        self.slowdown = MAX_SLOWDOWN / (self.difficulty + 1)
        self.slowdown_counter = 0
        self.loser = None

    def tick(self):
        results = []
        if(self.slowdown == self.slowdown_counter):
            for board in self.boards:
                board.tick()
            self.slowdown_counter = 0


        self.update()
        self.updateResult()
        self.draw()
        self.slowdown_counter = self.slowdown_counter + 1

    def draw(self):
        self.screen.blit(self.surfaces[0], (0,0))
        self.screen.blit(self.surfaces[1], ((self.width/2)+1,0))
        pygame.draw.rect(self.screen, (255, 255, 255), self.middle_separator)


    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in input_map.PLAYERS_MAPPING[0]:
                    self.events[0].append(event)
                elif event.key in input_map.PLAYERS_MAPPING[1]:
                    self.events[1].append(event)
            elif event.type == pygame.KEYUP:
                if event.key in input_map.PLAYERS_MAPPING[0]:
                    for e in self.events[0]:
                        if e.key == event.key:
                            self.events[0].remove(e)
                elif event.key in input_map.PLAYERS_MAPPING[1]:
                    for e in self.events[1]:
                        if e.key == event.key:
                            self.events[1].remove(e)

    def updateResult(self):
        if self.loser is None:
            for board in self.boards:
                if board.get_result() is False:
                    self.loser = board


    def get_events(self, number):
        return self.events[number]

    def get_results(self):
        results = [True for i in range(len(self.boards))]
        if self.loser is None:
            self.loser = self.boards[0]
            for board in self.boards:
                if board.score < self.loser.score:
                    self.loser = board
                elif board.score == self.loser.score:
                    results[board.number] = False
    
        results[self.loser.number] = False
        return results

class Board():

    def __init__(self, tetris, number):
        self.number = number
        self.tetris = tetris
        self.screen = tetris.surfaces[number]
        self.width, self.height = self.screen.get_size()

        self.sprites = pygame.sprite.RenderUpdates()
        self.sprites_to_update=pygame.sprite.RenderUpdates()

        self.block_grid=[[Block(5,(0,0)) for y in range (0,GRID_SIZE_Y,1)] for x in range (0,GRID_SIZE_X,1)]#y is the y axis
        x_coordinate=60
        for i in range (0,GRID_SIZE_X,1):
            x_coordinate+=BLOCK_WIDTH
            y_coordinate=50
            for j in range(0,GRID_SIZE_Y,1):
                self.block_grid[i][j].rect.topleft=x_coordinate,y_coordinate
                self.block_grid[i][j].indexes=i,j
                self.sprites.add(self.block_grid[i][j])
                y_coordinate+=BLOCK_WIDTH

        self.current_tetra=[]
        self.result = True
        self.score = 0

    def tick(self):
        self.update()
        self.draw()

    def draw(self):
        self.screen.fill((0, 0, 0))

        for sprite in self.sprites_to_update:
            sprite.update()

        self.sprites.draw(self.screen)

    def update(self):
        if not self.current_tetra:
            if not self.createNewCurrentTetra():
                self.result = False
        else:
            self.handleEvents()
            self.moveTetra("down")
            self.score += 1

        if not self.current_tetra:
                self.clearLines()
                self.score += 10

    def get_result(self):
        return self.result

    def handleEvents(self):        
        for event in self.tetris.get_events(self.number):
            if event.type == pygame.QUIT:
                return False
            elif event.type==pygame.KEYDOWN and self.current_tetra:
                if event.key==pygame.K_RIGHT or event.key==pygame.K_d:
                    self.moveTetra("right")
                        
                elif event.key==pygame.K_LEFT or event.key==pygame.K_a:
                     self.moveTetra("left")

                elif event.key==pygame.K_DOWN or event.key==pygame.K_s:
                    self.moveTetra("straight down")
                elif event.key==pygame.K_SPACE  or event.key==pygame.K_0:
                    self.rotateTetra()
        return True

    def removeBlocksForRotation(self):
        self.block_grid[self.current_tetra[0][0]][self.current_tetra[0][1]].transform(5)
        self.block_grid[self.current_tetra[2][0]][self.current_tetra[2][1]].transform(5)
        self.block_grid[self.current_tetra[3][0]][self.current_tetra[3][1]].transform(5)

    def transformBlocksForRotation(self,b_type):
        self.block_grid[self.current_tetra[0][0]][self.current_tetra[0][1]].transform(b_type)
        self.block_grid[self.current_tetra[2][0]][self.current_tetra[2][1]].transform(b_type)
        self.block_grid[self.current_tetra[3][0]][self.current_tetra[3][1]].transform(b_type)
  

    def areBoxesFilled(self,index1,index2,index3):
        "checks if boxes are filled AND if indexes are not negative!"
        for i in (index1,index2,index3):
            if self.block_grid[i[0]][i[1]].block_type!=5 and i not in self.current_tetra:
                print self.current_tetra
                print i
                print "ITS FILLED!"
                return True
        for i in (index1,index2,index3):
            if i[0]<0 or i[1]<0:
                return True
        return False

    def createNewCurrentTetra(self):
        "returns True if possible, False if cannot, meaning a loss"
        current_type=random.randint(TETRA_CHOICES[0],TETRA_CHOICES[1])#1 is 2x2, 2 is 1x4, 3 is upside down T, 4 is an S
        if current_type==1:#square
            if (self.block_grid[4][0].block_type==5 and self.block_grid[5][0].block_type==5
                and self.block_grid[4][1].block_type==5 and self.block_grid[5][1].block_type==5):
                self.current_tetra.append([4,0])
                self.current_tetra.append([4,1])
                self.current_tetra.append([5,0])
                self.current_tetra.append([5,1])
            else:
                return False
                
        elif current_type==2:#line
            if (self.block_grid[4][0].block_type==5 and self.block_grid[4][2].block_type==5
                and self.block_grid[4][1].block_type==5 and self.block_grid[4][3].block_type==5):
                self.current_tetra.append([4,0])
                self.current_tetra.append([4,1])
                self.current_tetra.append([4,2])
                self.current_tetra.append([4,3])
            else:
                return False
            
        elif current_type==3:#T
            if (self.block_grid[4][0].block_type==5 and self.block_grid[5][0].block_type==5
                and self.block_grid[5][1].block_type==5 and self.block_grid[6][0].block_type==5):
                self.current_tetra.append([4,0])
                self.current_tetra.append([5,0])
                self.current_tetra.append([6,0])
                self.current_tetra.append([5,1])
            else:
                return False

        elif current_type==4:#S
            if (self.block_grid[5][0].block_type==5 and self.block_grid[6][0].block_type==5
                and self.block_grid[4][1].block_type==5 and self.block_grid[5][1].block_type==5):
                self.current_tetra.append([4,1])
                self.current_tetra.append([5,0])
                self.current_tetra.append([5,1])
                self.current_tetra.append([6,0])
            else:
                return False
        for index in self.current_tetra:
            self.block_grid[index[0]][index[1]].transform(current_type)
        return True

    def moveTetra(self,movement):
        temp_tetra=[]
        try:
            current_type=self.block_grid[self.current_tetra[0][0]][self.current_tetra[0][1]].block_type
        except IndexError:
            pass
        if movement=="down":        
            for index in self.current_tetra:
                if index[1]+1<=GRID_SIZE_Y-1:
                    if self.block_grid[index[0]][index[1]+1].block_type==5 or [index[0],index[1]+1] in self.current_tetra:
                        
                        temp_tetra.append([index[0],index[1]+1])                        
                    else:
                        self.current_tetra=[]
                        return False
                else:
                    self.current_tetra=[]
                    return False

        elif movement=="straight down":
            while True:
                if not self.moveTetra("down"):
                    print "YES"
                    #return False
                    break
        elif movement=="left":
            for index in self.current_tetra:
                if index[0]-1>=0:
                    if self.block_grid[index[0]-1][index[1]].block_type==5 or [index[0]-1,index[1]] in self.current_tetra:
                        
                        temp_tetra.append([index[0]-1,index[1]])
                    else:
                        return False
                else:
                    print "WHOOPS!"
                    return False
        elif movement=="right":
            for index in self.current_tetra:
                if index[0]+1<=GRID_SIZE_X-1:
                    if self.block_grid[index[0]+1][index[1]].block_type==5 or [index[0]+1,index[1]] in self.current_tetra:
                        
                        temp_tetra.append([index[0]+1,index[1]])
                            
                    else:
                        return False
                else:
                    print "WHOOPS!"
                    return False

        for index in self.current_tetra:
            self.block_grid[index[0]][index[1]].transform(5)
        for index in temp_tetra:
            self.block_grid[index[0]][index[1]].transform(current_type)
        self.current_tetra=temp_tetra+[]
        return True

    def clearLines(self):
        is_line_full=False
        for y in range (GRID_SIZE_Y-1,-1,-1):
            if is_line_full:
                y+=1
            else:
                is_line_full=True
            for x in range(0,GRID_SIZE_X,1):
                if self.block_grid[x][y].block_type==5:
                    is_line_full=False
                    break
            if is_line_full:
                for z in range (y-1,-1,-1):
                    for x in range(0,GRID_SIZE_X,1):
                        self.block_grid[x][z+1].transform(self.block_grid[x][z].block_type)
                for x in range(0,GRID_SIZE_X,1):
                        self.block_grid[x][0].transform(5)

    def rotateTetra(self):
        b_type=self.block_grid[self.current_tetra[0][0]][self.current_tetra[0][1]].block_type
        if b_type!=1:
            if b_type==2:
                if self.current_tetra[0][1]+1==self.current_tetra[1][1]:#takes form of |
                    if not self.areBoxesFilled([self.current_tetra[1][0]-1,self.current_tetra[1][1]],
                                          [self.current_tetra[1][0]+1,self.current_tetra[1][1]],
                                          [self.current_tetra[1][0]+2,self.current_tetra[1][1]]):
                        self.removeBlocksForRotation()

                        self.current_tetra[0]=[self.current_tetra[1][0]-1,self.current_tetra[1][1]]
                        self.current_tetra[2]=[self.current_tetra[1][0]+1,self.current_tetra[1][1]]
                        self.current_tetra[3]=[self.current_tetra[1][0]+2,self.current_tetra[1][1]]

                        self.transformBlocksForRotation(b_type)

                else :
                    if not self.areBoxesFilled([self.current_tetra[1][0],self.current_tetra[1][1]-1],
                                          [self.current_tetra[1][0],self.current_tetra[1][1]+1],
                                          [self.current_tetra[1][0],self.current_tetra[1][1]+2]):
                        self.removeBlocksForRotation()

                        self.current_tetra[0]=[self.current_tetra[1][0],self.current_tetra[1][1]-1]
                        self.current_tetra[2]=[self.current_tetra[1][0],self.current_tetra[1][1]+1]
                        self.current_tetra[3]=[self.current_tetra[1][0],self.current_tetra[1][1]+2]

                        self.transformBlocksForRotation(b_type)
            elif b_type==3:
                if self.current_tetra[0][0]+1==self.current_tetra[1][0]:#T
                    if not self.areBoxesFilled([self.current_tetra[1][0],self.current_tetra[1][1]+1],
                                          [self.current_tetra[1][0],self.current_tetra[1][1]-1],
                                          [self.current_tetra[1][0]+1,self.current_tetra[1][1]]):
                        self.removeBlocksForRotation()

                        self.current_tetra[0]=[self.current_tetra[1][0],self.current_tetra[1][1]+1]
                        self.current_tetra[2]=[self.current_tetra[1][0],self.current_tetra[1][1]-1]
                        self.current_tetra[3]=[self.current_tetra[1][0]+1,self.current_tetra[1][1]]

                        self.transformBlocksForRotation(b_type)
                    
                elif self.current_tetra[0][1]-1==self.current_tetra[1][1]:#|-
                    if not self.areBoxesFilled([self.current_tetra[1][0]+1,self.current_tetra[1][1]],
                                          [self.current_tetra[1][0]-1,self.current_tetra[1][1]],
                                          [self.current_tetra[1][0],self.current_tetra[1][1]-1]):
                        self.removeBlocksForRotation()

                        self.current_tetra[0]=[self.current_tetra[1][0]+1,self.current_tetra[1][1]]
                        self.current_tetra[2]=[self.current_tetra[1][0]-1,self.current_tetra[1][1]]
                        self.current_tetra[3]=[self.current_tetra[1][0],self.current_tetra[1][1]-1]

                        self.transformBlocksForRotation(b_type)

                elif self.current_tetra[0][0]-1==self.current_tetra[1][0]:#upside down T
                    if not self.areBoxesFilled([self.current_tetra[1][0],self.current_tetra[1][1]-1],
                                          [self.current_tetra[1][0],self.current_tetra[1][1]+1],
                                          [self.current_tetra[1][0]-1,self.current_tetra[1][1]]):
                        self.removeBlocksForRotation()

                        self.current_tetra[0]=[self.current_tetra[1][0],self.current_tetra[1][1]-1]
                        self.current_tetra[2]=[self.current_tetra[1][0],self.current_tetra[1][1]+1]
                        self.current_tetra[3]=[self.current_tetra[1][0]-1,self.current_tetra[1][1]]

                        self.transformBlocksForRotation(b_type)

                elif self.current_tetra[0][1]+1==self.current_tetra[1][1]:#-|
                    if not self.areBoxesFilled([self.current_tetra[1][0]-1,self.current_tetra[1][1]],
                                          [self.current_tetra[1][0]+1,self.current_tetra[1][1]],
                                          [self.current_tetra[1][0],self.current_tetra[1][1]+1]):
                        self.removeBlocksForRotation()

                        self.current_tetra[0]=[self.current_tetra[1][0]-1,self.current_tetra[1][1]]
                        self.current_tetra[2]=[self.current_tetra[1][0]+1,self.current_tetra[1][1]]
                        self.current_tetra[3]=[self.current_tetra[1][0],self.current_tetra[1][1]+1]

                        self.transformBlocksForRotation(b_type)
                    
            elif b_type==4:
                if self.current_tetra[2][1]-1==self.current_tetra[1][1]:#>^>
                    if not self.areBoxesFilled([self.current_tetra[1][0]+1,self.current_tetra[1][1]+1],
                                          [self.current_tetra[1][0]+1,self.current_tetra[1][1]],
                                          [self.current_tetra[1][0],self.current_tetra[1][1]-1]):
                        self.removeBlocksForRotation()

                        self.current_tetra[0]=[self.current_tetra[1][0]+1,self.current_tetra[1][1]+1]
                        self.current_tetra[2]=[self.current_tetra[1][0]+1,self.current_tetra[1][1]]
                        self.current_tetra[3]=[self.current_tetra[1][0],self.current_tetra[1][1]-1]

                        self.transformBlocksForRotation(b_type)
                    print "rotate"
                    
                elif self.current_tetra[2][0]-1==self.current_tetra[1][0]:#V>V
                    if not self.areBoxesFilled([self.current_tetra[1][0]-1,self.current_tetra[1][1]+1],
                                          [self.current_tetra[1][0],self.current_tetra[1][1]+1],
                                          [self.current_tetra[1][0]+1,self.current_tetra[1][1]]):
                        self.removeBlocksForRotation()

                        self.current_tetra[0]=[self.current_tetra[1][0]-1,self.current_tetra[1][1]+1]
                        self.current_tetra[2]=[self.current_tetra[1][0],self.current_tetra[1][1]+1]
                        self.current_tetra[3]=[self.current_tetra[1][0]+1,self.current_tetra[1][1]]
                    
                        self.transformBlocksForRotation(b_type)

        
class Block(pygame.sprite.Sprite):
    def __init__ (self,block_type, xy):
        "just the basic building block of tetras, makes up the grid"
        pygame.sprite.Sprite.__init__(self)
        self.block_type=block_type
        if block_type==1:            
            self.image =pygame.image.load('./res/img/tetris/block1.gif')
        elif block_type==2:
            self.image =pygame.image.load('./res/img/tetris/block2.gif')
        elif block_type==3:    
            self.image =pygame.image.load('./res/img/tetris/block3.gif')
        elif block_type==4:
            self.image =pygame.image.load('./res/img/tetris/block4.gif')
        elif block_type==5:
            self.image =pygame.image.load('./res/img/tetris/block5.gif')
        self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = xy
        
    def transform(self,block_type):
        self.block_type=block_type
        if block_type==1:            
            self.image =pygame.image.load('./res/img/tetris/block1.gif')
        elif block_type==2:
            self.image =pygame.image.load('./res/img/tetris/block2.gif')
        elif block_type==3:    
            self.image =pygame.image.load('./res/img/tetris/block3.gif')
        elif block_type==4:
            self.image =pygame.image.load('./res/img/tetris/block4.gif')
        elif block_type==5:
            self.image =pygame.image.load('./res/img/tetris/block5.gif')
        self.image.convert()
