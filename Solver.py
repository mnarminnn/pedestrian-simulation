import numpy as np
from Pedestrian import Pedestrian
import math

def calculateDistance(y1,x1,y2,x2):
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
     return dist

#Function to get x and y corodinates of point
def yx(ny,nx,Ny,cellSize):

    y = Ny*cellSize - ny*cellSize - 0.5*cellSize
    x = nx*cellSize + 0.5*cellSize
    return [y, x]
#Get indicies of neighbouring cells
neighbours = lambda y, x,Ny,Nx : [(y2, x2) for y2 in range(y-1, y+2)
                               for x2 in range(x-1, x+2)
                               if (-1 < y < Ny and
                                   -1 < x < Nx and
                                   (0 <= y2 < Ny) and
                                   (0 <= x2 <Nx))]

class Solver:

    def __init__(self, yLen, xLen,cellSize,rMax):

        #Number of y cells
        self.Ny = int(yLen/cellSize)
        #Number of x cells
        self.Nx = int(xLen/cellSize)

        #square cell size
        self.cellSize = cellSize

        #domain length in x direction
        self.xLen = xLen

        #domain length in y-direction
        self.yLen = yLen


        #Matrix to store state of cells
        # 0 => Freespace 1 => Pedestrian 2 => Obstacle 3 => Target
        self.data = np.zeros((self.Ny,self.Nx))

        #List to hold Pedestrians
        self.Ped = []

        #List to hold the locations of the findTargets
        self.targetIndicies = []

        #Keep track of time steps
        self.nTimeStep = 0

        #Shortest path table
        self.paths = None

        #distances from Dijkstra
        self.distanceField = None

        #pedestrian cost function values
        self.pedCost = np.zeros((self.Ny,self.Nx))

        #Radius of influence by pedestrian for the cost Function
        self.rMax = rMax



    def getData(self):
        return self.data

    def getTimeStep(self):
        return self.nTimeStep

    def addPCost(self,jj,ii,pp):
        for i in range(self.Nx):
            for j in range(self.Ny):
                yy, xx = yx(j,i,self.Ny,self.cellSize)
                ppy,ppx = yx(pp.ny,pp.nx,self.Ny,self.cellSize)
                r = calculateDistance(ppy,ppx,yy,xx)
                if(r < self.rMax):
                    self.pedCost[j][i] += math.exp(1/(r**2-self.rMax**2))


    def removePCost(self,jj,ii,pp):
        for i in range(self.Nx):
            for j in range(self.Ny):
                yy, xx = yx(j,i,self.Ny,self.cellSize)
                ppy,ppx = yx(pp.ny,pp.nx,self.Ny,self.cellSize)
                r = calculateDistance(ppy,ppx,yy,xx)
                if(r < self.rMax):
                    self.pedCost[j][i] -= math.exp(1/(r**2-self.rMax**2))


    def addPedestrian(self, jj, ii,speed):

        pp =Pedestrian(ny = jj,nx = ii,speed = speed)
        self.Ped.append(pp)
        self.data[jj][ii] = 1
        self.addPCost(jj,ii,pp)
        print("+++ PEDESTRIAN",Pedestrian.totalP -1,"WITH SPEED",speed,"m/s ADDED +++")




    def removePedestrian(self, jj, ii):
        rpd = None
        for pp in self.Ped:
            if((pp.ny ==jj) and (pp.nx == ii)):
                rpd = pp.pedN
                self.Ped.remove(pp)
                self.removePCost(jj,ii,pp)
                break

        #in case multiple pedestrians in cell
        flag = False
        for pp in self.Ped:
            if((pp.ny ==jj) and (pp.nx == ii)):
                flag = True
                break
        if(not flag):
            self.data[jj][ii] = 0
        print("--- PEDESTRIAN",rpd, "REMOVED ---")

    def pedNum(self):
        return len(self.Ped)

    def addTarget(self,jj,ii):
        self.data[jj][ii] = 3
        self.targetIndicies.append((jj,ii))
        self.dijkstra()
        print("+++ TARGET ADDED +++")

        #dijkstra algorith needs to be called again

    def removeTarget(self,jj,ii):
            self.data[jj][ii] = 0
            self.targetIndicies.remove((jj,ii))
            self.dijkstra()
            print("--- TARGET REMOVED ---")


            #dijkstra algorith needs to be called again

    def addObstacle(self,jj,ii):
        self.data[jj][ii] = 2
        self.dijkstra()
        print("+++ OBSTACLE ADDED +++")


    def removeObstacle(self,jj,ii):
        self.data[jj][ii] = 0
        self.dijkstra()
        print("-- OBSTACLE REMOVED ---")

        #dijkstra algorith needs to be called again


    def dijkstra(self):

        print("### UPDATING DISTANCE FIELD USING DIJKSTRA'S ALGORITHM ###")

        distM = [0]*len(self.targetIndicies)
        ctr = 0
        for targets in self.targetIndicies:
            distM[ctr] = np.zeros((self.Ny,self.Nx))
            #indicies of the target
            tj, ti = targets
             #coordinates of target
            ty, tx = yx(tj,ti,self.Ny,self.cellSize)

            for i in range(self.Nx):
                for j in range(self.Ny):
                    yy, xx = yx(j,i,self.Ny,self.cellSize)
                    distM[ctr][j][i] = calculateDistance(ty,tx,yy,xx)
                    if (self.data[j][i] == 2):
                        distM[ctr][j][i] = 99999

            ctr = ctr + 1

        #Dijkstra's Algorithm
        #initialize previous cell Matrix
        prevCell = [[[0 for i in range(self.Nx)] for j in range(self.Ny)] for k in range(len(self.targetIndicies))]
        td = np.zeros((len(self.targetIndicies),self.Ny,self.Nx))
        for tt in range(len(self.targetIndicies)):

            #Get target incidies
            tar = self.targetIndicies[tt]
            tj  = tar[0]
            ti  = tar[1]
            #Keep track of visisted and unvisited cells
            visited = np.full((self.Ny, self.Nx), False)

            #initialize with large values for all cells
            td[tt].fill(10e10)

            #initial cell distance is zero
            td[tt][tj][ti] = 0


            while (0 in visited):
                cj = 10e10
                ci = 10e10
                #find unvisited cell with smallest distance from target
                minUnvisted = 10e10
                for ii in range(self.Nx):
                    for jj in range(self.Ny):
                        if((td[tt][jj][ii] < minUnvisted) and (not visited[jj][ii])):
                            minUnvisted = td[tt][jj][ii]
                            #current cell indecies
                            cj = jj
                            ci = ii


                for nn in neighbours(cj,ci,self.Ny,self.Nx):
                    #make sure neighbour is not visited
                    if(not visited[nn[0]][nn[1]]):

                        #Calculate the distance of each neighbour from start cell
                        cd = td[tt][cj][ci] + distM[tt][nn[0]][nn[1]]
                        if(td[tt][nn[0]][nn[1]] > cd):
                            #update shortest distance for neighbour
                            td[tt][nn[0]][nn[1]] = cd

                            #update previous cell
                            prevCell[tt][nn[0]][nn[1]] = [cj,ci]

                visited[cj][ci] = True


        self.paths = prevCell
        self.distanceField = td

    def showPaths(self):
        print("*** FINDING PATH TO CLOSEST TARGET TO PEDESTRIAN ***")
        for pp in self.Ped:
            closestDistance = 10e10
            closestTarget = 10e10
            #find closes targets
            for tt in range(len(self.targetIndicies)):
                if(self.distanceField[tt][pp.ny][pp.nx] < closestDistance):
                    closestDistance = self.distanceField[tt][pp.ny][pp.nx]

                    closestTarget = self.targetIndicies[tt]
                    closestIndex = tt

            cvy = pp.ny
            cvx = pp.nx

            while(not(cvy == closestTarget[0] and cvx == closestTarget[1])):

                pv = self.paths[closestIndex][cvy][cvx]

                cvy = pv[0]
                cvx = pv[1]
                #ct = self.targetIndicies[closestTarget]
                if(not(cvy == closestTarget[0] and cvx == closestTarget[1])):
                    self.data[cvy][cvx] = 4



    def timeMarch(self):
        print("*********************************************")
        print("### Time Step: " + str(self.nTimeStep) +" ###")
        #In case path shown
        self.data[self.data == 4] = 0



        kk = 0
        while(kk < len(self.Ped) and len(self.targetIndicies) != 0):

            pp = self.Ped[kk]
            minDist = 10e10
            cCell = 1000
            atTarget = False
            j = pp.ny
            i = pp.nx
            for nn in neighbours(j,i,self.Ny,self.Nx):
                if(self.data[nn[0]][nn[1]] == 3):
                    atTarget = True


            if(not atTarget):
                for nn in neighbours(j,i,self.Ny,self.Nx):
                    for tt in range(len(self.targetIndicies)):

                        #Subtract the influence of the current pedestrian from the pedestrian cost function
                        pc = 0
                        yy, xx = yx(nn[0],nn[1],self.Ny,self.cellSize)
                        ppy,ppx = yx(pp.ny,pp.nx,self.Ny,self.cellSize)
                        r = calculateDistance(ppy,ppx,yy,xx)
                        if(r < self.rMax):
                            pc = math.exp(1/(r**2-self.rMax**2))

                        cost = self.distanceField[tt][nn[0]][nn[1]] + self.pedCost[nn[0]][nn[1]] - pc

                        if(cost  < minDist and ((self.data[nn[0]][nn[1]] == 0) or ((nn[0] == j) and (nn[1] == i)))):
                            minDist = cost
                            cCell = nn


                ppy,ppx = yx(pp.ny,pp.nx,self.Ny,self.cellSize)
                yy, xx = yx(cCell[0],cCell[1],self.Ny,self.cellSize)

                addDistance = calculateDistance(ppy,ppx,yy,xx)
                #Case where pedestrian moved faster than assigned speed
                if(pp.offset >= self.cellSize):
                    pp.waitInMotion()
                    pp.offset -= self.cellSize
                    kk += 1
                #Case where pedestrian moved slower than assigned speed
                elif(pp.offset <= -self.cellSize):
                    pp.offset += self.cellSize
                    self.data[j][i] = 0
                    self.data[cCell[0]][cCell[1]] = 1
                    self.removePCost(j,i,pp)
                    pp.initialMove(cCell[0],cCell[1],addDistance)
                    self.addPCost(cCell[0],cCell[1],pp)

                else:
                    self.data[j][i] = 0
                    self.data[cCell[0]][cCell[1]] = 1
                    #updateMatrix[cCell[0]][cCell[1]] = 1
                    self.removePCost(j,i,pp)
                    pp.move(cCell[0],cCell[1],addDistance)
                    self.addPCost(cCell[0],cCell[1],pp)
                    kk += 1
            else:
                kk += 1


        self.nTimeStep += 1
        for pp in self.Ped:
            print("####################################################\n")
            print("Pedestrian number = ",pp.pedN)
            print("Time steps where the pedestrian moved = ",pp.inMotion)
            print("Assigned speed =", pp.speed)
            print("calculated speed = ",pp.calculateSpeed())
            print("traveled distance = ", pp.distance)
            print(pp.ny,pp.nx)
            print("####################################################\n")
