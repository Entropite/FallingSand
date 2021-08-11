import pygame
from collections import namedtuple
from enum import Enum
from Colors import Colors
from Particles import Particles
from Particles import PSpace


PARTICLE_SIZE = 12
SPEED = 100

pygame.init()
font = pygame.font.Font('manaspc.ttf', 14)
elementFont = pygame.font.Font('manaspc.ttf', 20)
elementBackgroundFont = pygame.font.Font('manaspc.ttf', 22)

class ViewMode(Enum):
    NORMAL = 0
    PRESSURE = 1

class FallingSandGame:
    def __init__(self, w=516, h=516):
        self.width = w
        self.height = h

        self.pGrid = list([[PSpace("", True)] * (int)(w/PARTICLE_SIZE) for i in range((int)(h/PARTICLE_SIZE)-4)])
        self.infoGrid = list([[[0,0]] * (int)(w/PARTICLE_SIZE) for i in range((int)(h/PARTICLE_SIZE)-4)]) # Holds Pressure and Temperature Data
    
        self.display = pygame.display.set_mode((w, h))
        pygame.display.set_caption('Falling Sand Simulator v.0.1.0')
        #self.toolBar = pygame.display.set_mode((len(Particles.pClasses)*32, 64))
        self.clock = pygame.time.Clock()
        self.frameNum = 0
        self.viewMode = ViewMode.NORMAL
        
        self.particleNum = 0
        self.particlePalette = ["Water", "Sand", ""]
        self.pList = list(Particles.pClasses.keys())
        self._isGamePaused = False

    def play_step(self): 
        #print(self.clock.get_fps())
        # Check for User Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.viewMode = ViewMode.NORMAL
                    print("In Normal View Mode")
                elif event.key == pygame.K_2:
                    self.viewMode = ViewMode.PRESSURE
                    print("In Pressure View Mode")
                if event.key == pygame.K_c:
                    self.pGrid = list([[PSpace("", True)] * len(self.pGrid[0]) for i in range(len(self.pGrid))])
                if event.key == pygame.K_SPACE:
                    self._isGamePaused = not self._isGamePaused
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2:
                    # Middle moues button changes selected particle type
                    self.particlePalette[0] = self.pList[0 if self.pList.index(self.particlePalette[0]) == len(self.pList)-1 else self.pList.index(self.particlePalette[0])+1]
        # Check mouse input
        if(True in pygame.mouse.get_pressed()):
            mouseButtonIndex = pygame.mouse.get_pressed().index(True)
            if(mouseButtonIndex == 1): # Middle button changes the selected particle type
                pass
            else:    
                pos = pygame.mouse.get_pos()
                if(self._isPosInBound(pos[0], pos[1]) and (self._isPSpaceClear(pos[0], pos[1]) or not self.particlePalette[mouseButtonIndex])):
                    self.pGrid[pos[1]//PARTICLE_SIZE][pos[0]//PARTICLE_SIZE] = PSpace(self.particlePalette[mouseButtonIndex], False)
                elif(pos[1] > self.height-PARTICLE_SIZE*4):
                    # Interact with game menu
                    self.particlePalette[0] = self.pList[pos[0]//(self.width//len(self.pList))] 
        # Update Particles, Heat, and Pressure
        newInfoGrid = list([list([[0,0] for j in range(len(self.pGrid[0]))]) for i in range(len(self.pGrid))])
        if(not self._isGamePaused):
            self.frameNum += 1
            for i in range(len(self.pGrid)):
                for j in range(len(self.pGrid[0])):
                    # Make sure a particle exists at the grid space
                    if((self.pGrid[i][j])[0] and not self.pGrid[i][j].updated):
                        Particles.pClasses[self.pGrid[i][j].type].update(i, j, self.pGrid, self.frameNum)
                    if(abs(self.infoGrid[i][j][0]) > 0.05):
                        isOnHorizontalEdge = j in (0, len(self.pGrid[0])-1)
                        isOnVerticalEdge = i in (0, len(self.pGrid)-1)
                        pressureFraction = 9 - (3 if isOnHorizontalEdge != isOnVerticalEdge else 0) - (5 if isOnVerticalEdge and isOnHorizontalEdge else 0)
                        for k in range(max(0, i-1), min(len(self.pGrid)-1, i+1)+1):
                            for l in range(max(0, j-1), min(len(self.pGrid[0])-1, j+1)+1):
                                # if k == 0:
                                #     print("{0}, {1}: {2}".format(k, l, newInfoGrid[k][l][0]))
                                newInfoGrid[k][l][0] += self.infoGrid[i][j][0] / pressureFraction
                                if newInfoGrid[k][l][0] > 1:
                                    newInfoGrid[k][l][0] = 1 # crappy solution
                                # if k == 0:
                                #     print("{0}, {1}: {2}".format(k, l, newInfoGrid[k][l][0]))
                                
            self.infoGrid = newInfoGrid

        # Draw Particles
        self._update_ui()

        self.clock.tick(SPEED)

    def _update_ui(self): # helper method
        self.display.fill(Colors.BLACK.value)

        self.particleNum = 0
        for i in range(len(self.pGrid)):
            for j in range(len(self.pGrid[0])):
                if(self.viewMode == ViewMode.PRESSURE):
                    pygame.draw.rect(self.display, (max(min(self.infoGrid[i][j][0]*255, 255), 0), 0, max(min(-self.infoGrid[i][j][0]*255, 255), 0)), pygame.Rect(j * PARTICLE_SIZE, i * PARTICLE_SIZE, PARTICLE_SIZE, PARTICLE_SIZE))
                if(self.pGrid[i][j].type):
                    self.particleNum += 1 # A particle is counted
                    pygame.draw.rect(self.display, list([i/2 for i in Particles.pClasses[self.pGrid[i][j].type].color]), pygame.Rect(j * PARTICLE_SIZE, i * PARTICLE_SIZE, PARTICLE_SIZE, PARTICLE_SIZE))
                    pygame.draw.rect(self.display, Particles.pClasses[self.pGrid[i][j].type].color, pygame.Rect(j * PARTICLE_SIZE+2, i * PARTICLE_SIZE+2, PARTICLE_SIZE-4, PARTICLE_SIZE-4))
                    self.pGrid[i][j] = PSpace(self.pGrid[i][j].type, False)
                
        if(pygame.mouse.get_pos()[1]<self.height-PARTICLE_SIZE*4):
            gridPos = self._convertPositionToGridPosition(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
            pygame.draw.rect(self.display, Particles.pClasses[self.particlePalette[0]].color, pygame.Rect(gridPos[1]*PARTICLE_SIZE, gridPos[0]*PARTICLE_SIZE, PARTICLE_SIZE, PARTICLE_SIZE))

        # Update Text
        self._update_text()

        elementButtonWidth = self.width // len(Particles.pClasses)
        for i in range(len(Particles.pClasses)):
            elementColor = Particles.pClasses[self.pList[i]].color
            pygame.draw.rect(self.display, elementColor, pygame.Rect(i*elementButtonWidth, self.height-PARTICLE_SIZE*4+8, elementButtonWidth-8, PARTICLE_SIZE*4-16))
            
            elementTitle = elementFont.render(self.pList[i], True, (255, 255, 255) if sum(elementColor) < 192 else (0, 0, 0))
            self.display.blit(elementTitle, [i*elementButtonWidth+8, self.height - PARTICLE_SIZE * 2])

        pygame.display.flip()

    def _update_text(self):
        if(self._isGamePaused):
            pausedText = font.render("Paused", True, (255, 0, 0))
            self.display.blit(pausedText, [4, 4])
        
        gridSpaceInfo = (0, 0)
        if(pygame.mouse.get_pos()[1] < self.height-PARTICLE_SIZE*4):
            gridPos = self._convertPositionToGridPosition(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
            gridSpaceInfo = self.infoGrid[gridPos[0]][gridPos[1]]

            positionText = font.render("x: {1}, y: {0}".format(gridPos[0], gridPos[1]), True, (255, 255, 255))
            self.display.blit(positionText, [self.width-320, 32]) 

        particleNumText = font.render("FPS: {0}, #Parts: {1} {2} Pa {3} K".format(self.clock.get_fps()//1, self.particleNum, (gridSpaceInfo[0]*255)//1, (gridSpaceInfo[1]*255)//1), True, (255, 255, 255))
        
        self.display.blit(particleNumText, [self.width-320, 4])

    def _isPSpaceClear(self, x, y):
        if not self._isPosInBound(x, y):
            #raise Exception("Position out of range")
            return False
        else:
            return not self.pGrid[(int)(y/PARTICLE_SIZE)][(int)(x/PARTICLE_SIZE)].type

    @staticmethod
    def isPSpaceClear(i, j, pGrid=[[PSpace("", True)]]):
        if i > len(pGrid) or j > len(pGrid[0]) or i < 0 or j < 0:
            return False
        else:
            return not pGrid[i][j].type
        
    def _isPosInBound(self, x, y):
        return (x > 0 and x < len(self.pGrid[0])*PARTICLE_SIZE and y > 0 and y < len(self.pGrid)*PARTICLE_SIZE)

    def _convertPositionToGridPosition(self, x, y):
        return ((int)(y/PARTICLE_SIZE), (int)(x/PARTICLE_SIZE))

if __name__ == '__main__':
    game = FallingSandGame()

    # Game loop
    while True:
        game.play_step()

    pygame.quit()