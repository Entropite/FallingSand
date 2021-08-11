from collections import namedtuple
import random

PSpace = namedtuple("PSpace", "type, updated") # "x, y"

class Particles:

    rightCounter = 0
    leftCounter = 0

    @staticmethod
    def switchParticles(i, j, k, l, pGrid):
        if all(y in range(len(pGrid)) for y in (i, k)) and all(x in range(len(pGrid[0])) for x in (j, l)):
            temp = pGrid[i+1][j]
            pGrid[i+1][j] = pGrid[i][j]
            pGrid[i][j] = temp

    @staticmethod
    def getDensity(i, j, pGrid):
        if (i < 0 or i > len(pGrid) or j < 0 or j > len(pGrid[0])):
            return 2 # normal range is 0 to 1
        else:
            return Particles.pClasses[pGrid[i][j].type].density

    class Sand:

        # Particle Type Data
        color = (221, 190, 145)
        gravity = 0.3
        density = 0.5

        def update(i, j, pGrid, frameNum):
            maxWidth = len(pGrid[0])
            maxHeight = len(pGrid)
            density = Particles.Sand.density
            if(i < maxHeight-1 and frameNum % int(1/Particles.Sand.gravity) == 0): # Check if particle can move down (driven by gravity)
                if (Particles.getDensity(i+1, j, pGrid) < density):
                    temp = pGrid[i+1][j]
                    pGrid[i+1][j] = PSpace("Sand", True)
                    pGrid[i][j] = temp
                elif (j < maxWidth-1 and not pGrid[i+1][j+1].type and not pGrid[i][j+1].type and random.random() > 0.5):
                    pGrid[i][j+1] = PSpace("Sand", True)
                    pGrid[i][j] = PSpace("", True) # What about DRY?!
                elif (j > 0 and not pGrid[i+1][j-1].type and not pGrid[i][j-1].type):
                    pGrid[i][j-1] = PSpace("Sand", True)
                    pGrid[i][j] = PSpace("", True) # What about DRY?!

    class Metal:
        
        # Particle Type Data
        color = (202, 204, 206)
        gravity = 0
        density = 1

        def update(j, i, pGrid, frameNum):
            pass

    class Water:

        # Particle Type Data
        color = (0, 32, 240)
        gravity = 0.5
        density = 0.1

        def update(i, j, pGrid, frameNum):
            maxWidth = len(pGrid[0])
            maxHeight = len(pGrid)
            if(i < maxHeight): # Check if particle can move down (driven by gravity)
                if (i < maxHeight-1 and Particles.getDensity(i+1, j, pGrid) < Particles.Water.density):
                    temp = pGrid[i+1][j]
                    pGrid[i+1][j] = PSpace("Water", True)
                    pGrid[i][j] = temp
                else:
                    canMoveRight = j < maxWidth-1 and Particles.getDensity(i, j+1, pGrid) < Particles.Water.density
                    canMoveLeft = j > 0 and Particles.getDensity(i, j-1, pGrid) < Particles.Water.density
                    if (canMoveRight and not canMoveLeft or (canMoveRight and canMoveLeft and random.random() > 0.5)):
                        temp = pGrid[i][j+1]
                        pGrid[i][j+1] = PSpace("Water", True)
                        pGrid[i][j] = temp
                    elif (canMoveLeft):
                        temp = pGrid[i][j-1]
                        pGrid[i][j-1] = PSpace("Water", True)
                        pGrid[i][j] = temp

    class EmptySpace:
        
        # Particle Type Data
        color = (255, 0, 0)
        density = 0

    class Gas:

        # Particle Type Data
        color = (194, 64, 255)
        density = 0.01

        def update(i, j, pGrid, frameNum):
            for k in range(max(0, i-1), min(len(pGrid)-1, i+1)+1):
                for l in range(max(0, j-1), min(len(pGrid[0])-1, j+1)+1):
                    if(Particles.getDensity(k, l, pGrid) < Particles.Gas.density and random.random() < 0.01+0.01*(1+k-max(0, i-1))):
                        temp = pGrid[k][l]
                        pGrid[k][l] = PSpace("Gas", True)
                        pGrid[i][j] = temp
                        return

    class Hole:

        # Particle Type Data
        color = (177, 67, 49)
        density = 1

        def update(i, j, pGrid, frameNum):
            for k in range(max(0, i-1), min(len(pGrid)-1, i+1)+1):
                for l in range(max(0, j-1), min(len(pGrid[0])-1, j+1)+1):
                    if(not pGrid[k][l].type in ("", "Hole")):
                        pGrid[k][l] = PSpace("", True)


    pClasses = {
        "Sand":Sand,
        "Metal":Metal,
        "Water":Water,
        "Gas":Gas,
        "Hole":Hole,
        "":EmptySpace
    }


    
