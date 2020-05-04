class Pedestrian:

    totalP = 0

    def __init__(self,ny,nx,speed):
        self.ny = ny
        self.nx = nx
        #distance per time step
        self.speed = speed
        #number of timesteps the pedestrian is in motion (not at target/obstacle) (used to calculaete the speed)
        self.inMotion = 0
        #total distance traveled by pedestrian
        self.distance = 0

        #used to compare if pedestrian moved faster or slower than required
        self.offset = 0

        self.pedN = Pedestrian.totalP

        Pedestrian.totalP += 1


    #when pedestrian moves and time moves forward
    def move(self,newJ,newI,addedDistance):
        self.ny = newJ
        self.nx = newI

        self.inMotion += 1

        self.distance += addedDistance
        self.offset += addedDistance - self.speed

    #Incase a pedestrian moves multiple times within a time step
    def initialMove(self, newJ, newI, addedDistance):
        self.ny = newJ
        self.nx = newI
        #incremented because
        self.distance += addedDistance

    def calculateSpeed(self):
        if(self.inMotion != 0):
            return self.distance/self.inMotion

    #called when idle waiting to adjust speed (moved to fast)
    def waitInMotion(self):
        self.inMotion += 1
