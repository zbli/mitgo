#!/usr/bin/env python3.3
# by LiJing @ SJTU
from extract import *
from geometry import *
from input_m import *
from parameters import *
from category import *
from output_m import *
import os


def process_mesh(filePath, arg):
    ''' Generate mesh and cell instances
    '''
    path = arg.path
    cellsNum = arg.cellsNum
    # Get the points file path
    fileName = eval(os.path.basename(filePath))
    if fileName == 0:
        meshFile = os.path.join(path, 'constant/polyMesh/points.gz')
    else:
        meshFile = os.path.join(filePath, 'polyMesh/points.gz')

    rawPoints = DataList()
    # Read all coordinates from the points file
    print('Extracting data from mesh file...')
    rawPoints.extract_data_from_foam(meshFile)
    pointsNum = [cellsNum[i] + 1 for i in range(len(cellsNum))]
    # Map points data onto mesh
    points = rawPoints.cast_to_mesh_data(pointsNum)

    # Generate the mesh instance of @Mesh
    print('Generating the mesh instance...')
    mesh = Mesh(cellsNum)
    print('Generating each cell instance...')
    mesh.generate_cells(points)

    return mesh


def process(filePath, mesh, arg):
    ''' Generate variables in one time directory
    '''
    cellsNum = mesh.cellsNum
    cellsAmount = mesh.cellsAmount
    variables = arg.variables
    mode = arg.mode

    # Read all variables into @mesh instance
    for var in variables:
        # Variables to be read must be available as files
        if var in varFromFileList:
            variableName = variablesList[mode].get(var)

            variableFile = os.path.join(filePath, variableName)
            variableFileGzip = variableFile + '.gz'
            if os.path.exists(variableFileGzip):
                variableFile = variableFileGzip
            elif not os.path.exists(variableFile):
                print('Error: file ' + variableFile + 'does not exist')
                continue

            rawVariable = DataList()
            print('Extracting data from ' + var + ' file...')
            rawVariable.extract_data_from_foam(variableFile)

            # For uniform situation
            rawData = rawVariable.data
            if isinstance(rawData, list):
                rawVariable.data = np.tile(rawData, (cellsAmount, 1))

            vDim = len(rawVariable.data[0])

            # Map variable data onto mesh
            variable = rawVariable.cast_to_mesh_data(cellsNum)
            # Add variable into @Mesh instance
            mesh.add_variable(variableName, vDim, variable)
        else:
            continue

    return mesh


def main_loop(dirList, mesh, arg, op):
    ''' The main loop function
    '''
    path = arg.path
    timeRange = arg.timeRange
    start = timeRange[0]
    end = timeRange[1]
    step = timeRange[2]
    token = 0
    for item in dirList:
        if item < start:
            print('%f skip' % item)
            continue
        elif start+token*step <= item <= min(start+(token+1)*step, end):
            print('Directory %g' % item)
            dirFile = os.path.join(path, str(item))
            # Read mesh every time step if mesh is Lagranian
            if arg.mode == 1:
                mesh = process_mesh(dirFile, arg)
            # Read variables from files
            meshIns = process(dirFile, mesh, arg)
            # Output variables at each step
            if op.mode == 1 or op.mode == 3:
                print('Dumping data for time=' + str(item) + ' ...')
                op.output_each_step(arg.mode, meshIns, item)
            token += 1
            print('%f run' % item)
        elif item > end:
            break
        else:
            print('%f skip' % item)
            continue


def main(arg):
    ''' The main function to run over all processes
    '''
    # ...File = ...Path + ...Name
    #
    # Assign values to inputDict keys
    # keys = inpDict.keys()
    # for key in keys:
    #     exec(key + "= inpDict[key]")
    ### to be modified as @exec func has scope problems for locals and globals

    path = arg.path
    op = Output(arg.variables, arg.outputPath)

    # A regular expression to find time directories
    dirPattern = re.compile(r'^\d*\.?\d*$')

    dirList = []
    # List all files and directories in current path
    for dirName in os.listdir(path):
        dirFile = os.path.join(path, dirName)
        # Discriminate between directories and files
        if os.path.isdir(dirFile):
            # Discriminate between time directories and others
            if re.match(dirPattern, dirName):
                dirList.append(eval(dirName))

    # Reorder all directories according to numbers
    dirList.sort()
    # Only read mesh once if mesh is Eulerian
    if arg.mode == 0:
        mesh = process_mesh(os.path.join(path, str(dirList[0])), arg)

    # Execute main loop function
    main_loop(dirList, mesh, arg, op)


if __name__ == '__main__':
    # A dict for different solvers to tell whether
    solverDict = {'interTrackFoam': 1,
                  'waveFoam':       0,
                  'interFoam':      0,
                  }

    ### to be modified into argument input
    path = '../'
    outputPath = '../output'

    paraFile = Input(path)
    solver = paraFile.solver
    cellsNum = paraFile.cellsNum

    ### to be modified into argument input
    variables = ['vof']
    # timeRange = paraFile.timeRange
    timeRange = [1.5, 2.5, 0.1]

    inputDict = {'mode': solverDict[solver],
                 'path': path,
                 'cellsNum': cellsNum,
                 'variables': variables,
                 'timeRange': timeRange,
                 'outputPath': outputPath,
                 }

    arg = Argument(inputDict)

    main(arg)
