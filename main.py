import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib import colors
from Solver import Solver
from matplotlib.widgets import RadioButtons, Slider, Button, TextBox


def readpgm(name):
    with open(name) as f:
        lines = f.readlines()
    # This ignores commented lines
    for l in list(lines):
        if l[0] == '#':
            lines.remove(l)
    # here,it makes sure it is ASCII format (P2)
    assert lines[0].strip() == 'P2'
    # Converts data to a list of integers
    dat = []
    for line in lines[1:]:
        dat.extend([int(c) for c in line.split()])
    return (np.array(dat[3:]),(dat[1],dat[0]),dat[2])


def pathButton(ev):
    solver.showPaths()
    updateVis()

#Update visualization
def updateVis():

    im.set_data(solver.data)
    fig.text(y= 0.75,x=0.1,text = "Time: " + str(solver.getTimeStep()) + " s\nPedestrians: " + str(solver.pedNum()),
    ha= 'center',bbox=dict(facecolor='mediumturquoise',
    alpha=1),s =1)
    plt.draw()


#Radio button function
def colorfunc(label):
    dict = { 'Pedestrian': 1, 'Obstacle': 2, 'Target': 3,'Empty': 0}
    global choice
    choice = dict[label]

#keyboard press
def on_key(event):
    if(str(event.key) == " "):
        solver.timeMarch()
    if(str(event.key) == "g" and task == 7):


        spd1 = [0]*len(solver.Ped)
        for s in range(len(solver.Ped)):
            spd1[s] = solver.Ped[s].calculateSpeed()

        fig1.suptitle('Real vs. Simulated')
        axs[0].plot(age, spd , label = "real")
        axs[0].plot(age, spd1, label = "simulated")
        axs[0].set_ylabel('Speed (m/s)')
        axs[0].set_xlabel('Age (years)')

        axs[1].scatter(age,np.subtract(spd1,spd))
        axs[1].hlines(y = 0,xmin = 0,xmax = 90, colors='k', linestyles='solid',lw=0.5)


        handles, labels = axs[0].get_legend_handles_labels()
        axs[0].legend(handles, labels)
        axs[1].set_xlim([0,90])
        plt.show()

    updateVis()



#clicking on cells to change
def onclick(event):
    ii = math.floor(event.xdata/solver.cellSize)
    jj = math.floor(event.ydata/solver.cellSize)

    print(jj,ii)

    if(event.dblclick and (event.xdata != None or event.ydata != None)):
        #In case path shown
        solver.data[solver.data == 4] = 0
        if(choice != 0):
            if(solver.data[jj][ii] == 0):
                if(choice == 1):
                    solver.addPedestrian(jj,ii,round(slider.val,3))
                elif(choice == 2):
                    solver.addObstacle(jj,ii)
                elif(choice == 3):
                    solver.addTarget(jj,ii)

            else:
                print("!!! CELL ALREADY OCUPIED !!!")

        else:
            if(solver.data[jj][ii] == 1):
                solver.removePedestrian(jj,ii)
            elif(solver.data[jj][ii] == 2):
                solver.removeObstacle(jj,ii)
            elif(solver.data[jj][ii] == 3):
                solver.removeTarget(jj,ii)

    updateVis()

def main(name):
    global fig
    global im
    global choice
    global slider
    global ax
    nTimeStep = 0

    #Number of x-cells
    Nx = solver.Nx
    #Number of y-cells
    Ny = solver.Ny


    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)


#Set up visualization
    for yy in range(Ny):
        ax.hlines(y = yy*solver.cellSize,xmin = 0,xmax = solver.xLen, colors='k', linestyles='solid',lw=0.5)
    for xx in range(Nx):
        ax.vlines(x = xx*solver.cellSize,ymin = 0,ymax = solver.yLen, colors='k', linestyles='solid',lw=0.5)


    cmap = colors.ListedColormap(['white','red','midnightblue','gold','salmon'])

    im = plt.imshow(solver.data, interpolation='none', origin='lower', vmin=0, vmax=4, aspect = 'auto', cmap = cmap, extent= [0,solver.xLen,0,solver.yLen])
    ax.set_ylabel('metres')
    ax.set_xlabel('metres')

    plt.gca().set_aspect('equal', adjustable='box')

    if(task == 2):
        circ=plt.Circle((25.5,25.5), radius=23, color='g', fill=False)
        ax.add_patch(circ)

    choice = 1
    plt.subplots_adjust(left=0.3)

    radioAx  = plt.axes([0.004, 0.4, 0.20, 0.26],aspect='equal',facecolor = 'deepskyblue')
    radio = RadioButtons(radioAx, ('Pedestrian', 'Obstacle', 'Target','Empty'),activecolor='k')
    radio.on_clicked(colorfunc)

    pathAx = plt.axes([0.004, 0.15, 0.20, 0.21])
    bpath = Button(pathAx, 'Show projected\npaths\nto targets',color = 'lightsalmon',hovercolor = 'salmon')
    bpath.on_clicked(pathButton)

    sliderAx = plt.axes([0.3, 0.025, 0.5, 0.02])

    slider = Slider(sliderAx,      # the axes object containing the slider
                    label = 'Pedestrian\nSpeed',            # the name of the slider parameter
                    valmin = 0.2,          # minimal value of the parameter
                    valmax = 3,          # maximal value of the parameter
                    valinit= 1,# initial value of the parameter
                    color = 'grey',
                    valfmt ='%1.2f'
                    )


    fig.text(y= 0.75,x=0.1,text = "Time: " + str(solver.getTimeStep()) + " s\nPedestrians: " + str(solver.pedNum()),
    ha= 'center',bbox=dict(facecolor='mediumturquoise',
    alpha=1),s =1)
    fig.suptitle(name, fontsize=16)


    cid1 = fig.canvas.mpl_connect('key_press_event', on_key)
    cid  = fig.canvas.mpl_connect('button_press_event', onclick)


    plt.show()

if __name__ == "__main__":
    # execute only if run as a script
    #
    #
    global solver
    global task
    print("\n\n\n************************* Group H Worksheet 1 *************************\n")

    print("1.First step of a single pedestrian.")
    print("2.Interaction of pedestrians.")
    print("3.Obstacle avoidance.")
    print("4.RiMEA scenario 1 (straight line)")
    print("6.RiMEA scenario 6 (movement around a corner).")
    print("7.RiMEA scenario 7 (demographic parameters).")
    print("8.Maze.")
    print("9.Custom simulation.")
    task = int(input("Please choose what to run: "))
    print(task)
    if(task == 1):
        print("1.First step of a single pedestrian.")
        solver = Solver(yLen = 50, xLen = 50,cellSize =1, rMax = 0)

        solver.addPedestrian(24,4, 1)
        print("!!!Preparing scenario !!!")
        solver.addTarget(24,24)
        main("First step of a single pedestrian")
    elif(task == 2):
        print("2.Interaction of pedestrians.")
        rMax = float(input("Please enter an r max value: "))

        solver = Solver(yLen = 51, xLen = 51,cellSize =1, rMax = rMax)

        solver.addPedestrian(24,48,1)
        solver.addPedestrian(36, 5,1)
        solver.addPedestrian(6, 12,1)
        solver.addPedestrian(48,25,1)
        solver.addPedestrian(14,45,1)
        print("!!!Preparing scenario !!!")
        solver.addTarget(25,25)
        main("Interaction of pedestrians")

    elif(task == 3):
        print("3.Obstacle avoidance.")
        solver = Solver(yLen = 20, xLen = 20,cellSize =1, rMax = 0)

        solver.addPedestrian(10, 2,1)
        solver.addObstacle(8, 6)
        solver.addObstacle(8, 7)
        solver.addObstacle(8, 8)
        solver.addObstacle(8, 9)
        solver.addObstacle(8, 10)
        solver.addObstacle(8, 11)
        solver.addObstacle(9, 11)
        solver.addObstacle(10, 11)
        solver.addObstacle(11, 11)
        solver.addObstacle(12, 11)
        solver.addObstacle(12, 10)
        solver.addObstacle(12, 9)
        solver.addObstacle(12, 8)
        solver.addObstacle(12, 7)
        solver.addObstacle(12, 6)
        print("!!!Preparing scenario !!!")
        solver.addTarget(10, 15)
        main("Obstacle avoidance")

    elif(task == 4):
        print("4.RiMEA scenario 1 (straight line)")
        solver = Solver(yLen = 2, xLen = 40,cellSize =0.4, rMax = 0)

        solver.addPedestrian(2,0,1.33)
        print("!!!Preparing scenario !!!")
        solver.addTarget(2,99)
        main("RiMEA scenario 1 (straight line)")

    elif(task == 6):
        print("6.RiMEA scenario 6 (movement around a corner).")
        rMax = float(input("Please enter an r max value: "))
        solver = Solver(yLen = 16, xLen = 16,cellSize =0.4, rMax = rMax)

        for n in range(25):
            solver.data[6][n] = 2
        for n in range(31):
            solver.data[0][n] = 2
        for n in range(25):
            solver.data[n][30] = 2
        for n in range(7,25):
            solver.data[n][24] = 2

        solver.addPedestrian(5, 0,1)
        solver.addPedestrian(5, 4,1)
        solver.addPedestrian(5, 8,1)
        solver.addPedestrian(5, 12,1)
        solver.addPedestrian(4, 14,1)
        solver.addPedestrian(4, 10,1)
        solver.addPedestrian(4, 6,1)
        solver.addPedestrian(4, 2,1)
        solver.addPedestrian(3, 0,1)
        solver.addPedestrian(3, 4,1)
        solver.addPedestrian(3, 8,1)
        solver.addPedestrian(3, 12,1)
        solver.addPedestrian(2, 14,1)
        solver.addPedestrian(2, 10,1)
        solver.addPedestrian(2, 6,1)
        solver.addPedestrian(2, 2,1)
        solver.addPedestrian(1, 0,1)
        solver.addPedestrian(1, 4,1)
        solver.addPedestrian(1, 8,1)
        solver.addPedestrian(1, 12,1)
        print("!!!Preparing scenario !!!")
        solver.addTarget(36, 27)

        main("RiMEA scenario 6 (movement around a corner)")

    elif(task == 7):
        print("7.RiMEA scenario 7 (demographic parameters).")
        values = np.loadtxt(open("test7.csv", "rb"), delimiter=",", skiprows=1)

        global spd, age

        age = [0]*len(values)

        spd = [0]*len(values)
        for index in range(len(values)):
            age[index],spd[index] = values[index]

        xLen = 100
        yLen = 70
        solver = Solver(yLen = yLen, xLen = xLen,cellSize =1, rMax = 0)


        for i in range(0,xLen,2):

            solver.addPedestrian(0,i,spd[i//2])
            for j in range(yLen):
                solver.data[j][i-1] = 2

        print("!!!Preparing scenario !!!")
        solver.addTarget(yLen-1,xLen//2)

        main("RiMEA scenario 7 (demographic parameters)")

    elif(task == 8):
        print("8.Maze.")
        maze = readpgm("maze.pgm")

        yLen = maze[1][1]
        xLen = maze[1][0]
        mat = maze[0].reshape(xLen,yLen)
        solver = Solver(yLen = yLen, xLen = xLen,cellSize =1, rMax = 0)

        for i in range(xLen):
            for j in range(yLen):
                if(mat[i][j] == 0):
                    solver.data[yLen- j-1][xLen - i-1] = 2
        main("Maze (place targets and pedestrians whereever you want!)")

    else:
        print("9.Custom simulation.")
        yLen = float(input("Please enter length in y direction: "))
        xLen = float(input("Please enter length in x direction: "))
        cellSize = float(input("Please enter size of cell (dimension of pedestrian): "))
        rMax = float(input("Please enter an r max value: "))
        solver = Solver(yLen = yLen, xLen = xLen,cellSize =cellSize, rMax = rMax)
        main("Cellular Automaton Simulator")
