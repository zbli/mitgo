# by LiJing @ SJTU
from geometry import *
from category import *
import os


class Output(object):
    ''' Output all types of variables into files
    '''
    def __init__(self, variables, outputPath):
        # Variable list
        self.variables = variables
        if not (os.path.exists(outputPath) and os.path.isdir(outputPath)):
            os.makedirs(outputPath)
        # Path to be output
        self.path = outputPath
        # Variable list for one time step output
        self.varEach = list(set(self.variables).intersection(varEachStepList))
        # Variable list for output in the end
        self.varEnd = list(set(self.variables).intersection(varEndStepList))
        # A number denoting how many variables to be dumped at each time step
        self.isEach = len(self.varEach)
        # A number denoting how many variables to be dumped in the end
        self.isEnd = len(self.varEnd)
        # A token denoting whether to output the elevation in terms of VOF
        if 'elevation' in variables:
            self.isEle = 1
        else:
            self.isEle = 0

    @property
    def mode(self):
        ''' Whether output at each time step or in the end
        '''
        if (self.isEach > 0 and self.isEnd > 0):
            mode = 3
        elif (self.isEach > 0 and self.isEnd == 0):
            mode = 1
        elif (self.isEach == 0 and self.isEnd > 0):
            mode = 2
        else:
            mode = 0
        return mode

    def output_each_step(self, mode, mesh, timeStep):
        ''' Output each variable in @variables into one file according to the
            @timeStep
        '''
        if not (self.mode == 1 or self.mode == 3):
            print('Warning: wrong function is called')
            return False

        # Two containers for objects and dimensions of variables respectively
        varsList = []
        varsDim = []
        for var in self.varEach:
            varName = variablesList[mode].get(var)
            varValue = mesh.variables.get(varName)
            varDim = mesh.vDims.get(varName)
            varsList.append(varValue)
            varsDim.append(varDim)
        # How many variables to be done
        length = self.isEach

        # Complete file path for output
        fileFile = os.path.join(self.path, str(timeStep)+'.dat')

        cellsNum = mesh.cellsNum
        xNum = cellsNum[0]
        yNum = cellsNum[1]
        zNum = cellsNum[2]
        try:
            with open(fileFile, 'w') as fileopen:
                # Output the head lines
                fileopen.write(headString+'# x\ty\tz')
                for item in range(length):
                    # One dimension variable
                    if varsDim[item] == 1:
                        fileopen.write('\t%s' % self.varEach[item])
                    # Three dimensions variable
                    elif varsDim[item] == 3:
                        fileopen.write('\t%s\t%s\t%s' %
                                       (self.varEach[item]+'_x',
                                        self.varEach[item]+'_y',
                                        self.varEach[item]+'_z',)
                                       )
                fileopen.write('\n')
                # Output the data
                for k in range(zNum):
                    for j in range(yNum):
                        for i in range(xNum):
                            cell = mesh.cells[k][j][i]
                            position = cell.pos
                            fileopen.write('%g\t%g\t%g' %
                                           (position[0],
                                            position[1],
                                            position[2])
                                           )
                            for item in range(length):
                                varCell = varsList[item][k][j][i]
                                for var in varCell:
                                    fileopen.write('\t%g' % var)
                            fileopen.write('\n')
            return True

        except IOError:
            print('Error: ' + fileFile + ' can not be found')
            return False
