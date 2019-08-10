"""Creates user named directory within current working directory and executes
2D Diffusion limited aggregation (DLA) simulation.
"""
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.cm as cm
import time
import shutil
from datetime import datetime

def setup():
    r"""Description.

    Parameters
    ----------
    None

    Returns
    -------
    runName : string
        The user inputted name for the working directory of the simulation.
    length : integer
        The x and y dimension of the lattice.
    """

    # Get current working directory
    cur = os.getcwd()

    # Ask for runName and check for invalid input
    while (True):
        runName = str(input('Run Name: '))
        if " " in runName:
            print('Error: spaces within run name. Please retry.')
        else:
            break

    # Create directory named 'runName' if it does not exist
    try:
        os.mkdir(runName)
    # If directory 'runName' already exists then either rename 'runName' or replace it
    except:
        delete = str(input('Error: directory with that name already exists. Would you like to replace it (yes/no)? '))
        if (delete == "yes"):
            shutil.rmtree(runName)
            os.mkdir(runName)
        else:
            while (True):
                runName = str(input('Run Name: '))
                if " " in runName:
                    print('Error: spaces within run name. Please retry.')
                else:
                    os.mkdir(runName)
                    break

    # Change directory to runName
    os.chdir(os.path.join(cur, runName))

    # Input lattice length
    while (True):
        length = int(input('Length of lattice: '))
        if (length <= 10):
            print('Error: lattice length too small. Please enter L > 10.')
        else:
            break

    return runName, length

def save(runName, length, size, rCluster, elapsed, lattice):
    r"""Description.

    Parameters
    ----------
    runName : string
        The user inputted name for the working directory of the simulation.
    length : integer
        The x and y dimension of the lattice.
    size : integer
        Number of particels within cluster.
    rCluster : float
        Maximum radius of cluster (center to furthest particle.)
    elapsed : float
        Runtime of simulation [seconds].
    lattice : integer array
        2D array of cluster. Non-zero integers represent part of the cluster.

    Returns
    -------
    None
    """

    # Get date and time
    now = datetime.now()

    # Write data to file
    filename = runName + "-data.txt"
    cmapName = runName + "-cmap.png"
    file = open(filename, "w")
    file.write('Run Name: {}        Date: {}        Time: {}\n'.format(runName, now.strftime("%d-%m-%y"), now.strftime("%H:%M")))
    file.write('--------------------------------------------------------------------------------\n')
    file.write('PARAMETERS \n')
    file.write('    Lattice length: {}\n'.format(length))
    file.write('    Lattice points: {}\n'.format(length**2))
    file.write('OUTPUT \n')
    file.write('      Cluster size: {}\n'.format(size))
    file.write('    Cluster radius: {}\n'.format(rCluster))
    file.write('    Execution time: {} sec\n'.format(elapsed))
    file.write('FIGURES\n')
    file.write('          Colormap: {} \n'.format(cmapName))
    file.close()

    # Generate and save colourmap
    fig, ax = plt.subplots()
    cmap = cm.get_cmap('gnuplot2', 10)
    im = ax.imshow(lattice, cmap=cmap)
    plt.imsave(cmapName, lattice, format='png', cmap=cmap)

    return

def main():

    # Call setup function - sets environment and prompts user for runName and length
    runName, length = setup()

    # Construct array and define center
    lattice = np.zeros((length, length))
    r0 = [length//2, length//2]
    lattice[r0[1], r0[0]] = 1

    # Define maximum radisu of cluster
    rMax = length//2

    # Define cluster radius, rCluster, and cluster size, size
    rCluster = 0
    size = 0

    # Define initial inner and outer radii
    rStart = 0.2*rMax
    rOuter = 1.2*rStart

    # Variables for monitoring deposition with time
    unit = 1
    unit_div = 2*length

    # Store initial time for calculation of elapsed time
    start = time.process_time()


    while (rOuter < (length//2)-2):

        # Change integer for colormap time deposition monitoring
        if (size % unit_div == 0):
            unit += 1

        # Generate random number to define spawn point
        thetaRandom = np.random.uniform(low=0.0, high=1.0, size=None) * 2.0 * np.pi
        newSpawn = [int(rStart*np.sin(thetaRandom) + r0[1]), int(rStart*np.cos(thetaRandom) + r0[0])]

        while (True):

            # Check adjacent positions for cluster
            if (lattice[newSpawn[0]+1, newSpawn[1]] != 0 or lattice[newSpawn[0]-1, newSpawn[1]] != 0 \
                or lattice[newSpawn[0], newSpawn[1]+1] != 0 or lattice[newSpawn[0], newSpawn[1]-1] != 0):

                # Cluster adjacent, thus change zero -> unit
                lattice[newSpawn[0], newSpawn[1]] = unit

                # Calculate new point deposition radius
                rParticle = np.sqrt((newSpawn[1] - r0[1])**2 + (newSpawn[0] - r0[0])**2)

                # Compare against current max cluster radius
                rCluster = max(rCluster, rParticle)

                # Incriment cluster size
                size += 1

                break

            else:

                # Generate random number to define movement direction
                dirRandom = int(np.random.uniform(low=0.0, high=1.0, size=None) * 4.0)

                if (dirRandom == 0):
                    # Move left
                    newSpawn[1] -= 1
                elif (dirRandom == 1):
                    # Move up
                    newSpawn[0] -= 1
                elif (dirRandom == 2):
                    # Move right
                    newSpawn[1] += 1
                else:
                    # Move down
                    newSpawn[0] += 1

            # Calulate spawned particle radius and remove if outside rOuter
            rParticle = np.sqrt((newSpawn[1] - r0[1])**2 + (newSpawn[0] - r0[0])**2)
            if (rParticle > rOuter):
                break

        # Increase inner and outer radii as cluster radius increases
        if (rCluster > 0.75*rStart):
            rStart += 2
            rOuter += 2

    # Calculate elapsed time
    elapsed = time.process_time() - start

    # Save data and figures
    save(runName, length, size, rCluster, elapsed, lattice)

    return


if __name__ == '__main__':
    main()
