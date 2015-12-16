# by LiJing @ SJTU
import numpy as np


indexA = [0, 3, 1, 7, 5, 6, 4, 2, 3, 6, 0, 5]
indexB = [1, 2, 5, 3, 4, 7, 0, 6, 7, 2, 4, 1]
indexC = [2, 1, 3, 5, 7, 4, 6, 0, 2, 7, 1, 4]


def walk_all(num, func, **kwargs):
    ii = num[0]
    jj = num[1]
    kk = num[2]
    container = kwargs
    for k in range(kk):
        for j in range(jj):
            for i in range(ii):
                container = func(i, j, k, **container)
    return container


class Mesh(object):
    ''' A container of mesh info
        @cells is a three dimensional np.array.
        Each entry of @cells is a @Cell instance.
        @cellsNum is a simple List.
    '''
    def __init__(self, cellsNum):
        self.cellsNum = cellsNum
        self.cellsAmount = cellsNum[0]*cellsNum[1]*cellsNum[2]
        self.variables = {}
        self.vDims = {}
        self.cells = None

    def generate_cells(self, points):
        ''' Dump all corresponding vertices into one @Cell Class to generate
            all cells
        '''
        numX = self.cellsNum[0]
        numY = self.cellsNum[1]
        numZ = self.cellsNum[2]
        rawCells = np.array([object]*numX*numY*numZ)
        cells = rawCells.reshape((numZ, numY, numX))

        def _populate_cell(i, j, k, **kwargs):
            vertices = np.array([
                points[k][j][i],
                points[k][j][i+1],
                points[k][j+1][i],
                points[k][j+1][i+1],
                points[k+1][j][i],
                points[k+1][j][i+1],
                points[k+1][j+1][i],
                points[k+1][j+1][i+1]
            ])
            cells[k][j][i] = Cell(vertices)
            cells[k][j][i].index = [i, j, k]
            return {}

        walk_all(self.cellsNum, _populate_cell)
        self.cells = cells.copy()

    def integrate(self, variableName, mode=1, **kwargs):
        ''' Calculate the integration for the given variable
        '''
        vDim = self.vDims[variableName]
        result = 0
        cellsFlat = self.cells.flat
        if vDim == 3:
            tmpVariable = self.variables[variableName]
            oneDimVariable = tmpVariable[:, :, :, 2]
            variableFlat = oneDimVariable.flat
        elif vDim == 1:
            variableFlat = self.variables[variableName].flat

        cellsNum = self.cellsNum
        num = cellsNum[0]*cellsNum[1]*cellsNum[2]

        if mode == 1:
            for i in range(num):
                result += variableFlat[i]*cellsFlat[i].vol/0.1
            return result

        elif mode == 2:
            for i in range(num):
                result += variableFlat[i]*cellsFlat[i].vol
            return result

        elif mode == 3:
            tmpList = []
            for cell in cellsFlat:
                tmpList.append(cell.pos)
            flatCells = np.array(tmpList)
            crestIndex = flatCells.argmax(axis=0)[1]
            xmin = flatCells[crestIndex][0] - 0.5
            xmax = flatCells[crestIndex][0] + 0.5
            ymin = 0.8

            for i in range(num):
                cell = cellsFlat[i]
                if xmin <= cell.pos[0] <= xmax and cell.pos[1] >= ymin:
                    result += variableFlat[i]*cell.vol/0.1
            return result

    def add_variable(self, variableName, vDim, variable):
        ''' Add new variable to @self.variables
        '''
        self.variables[variableName] = variable
        self.vDims[variableName] = vDim


class Cell(object):
    ''' A container of cell info
        @vertices is a np.array with 8 vertices and self-explanatory.
        Each vertex of @vertices is the coordinate.
    '''
    def __init__(self, vertices):
        self.vertices = vertices
        self.index = []

    @property
    def pos(self):
        ''' The @Cell Class property @pos for the center point of the cell
        '''
        position = self.vertices.sum(axis=0)/8.
        return position

    @property
    def vol(self):
        ''' The @Cell Class property @vol for the volume of the cell
            The 12 tetrahedrons comprise an arbitrary hexahedron is in use
            The volume of a tetrahedron is calculated by
            $$V=\frac{|(a-b)\cdot*((b-d)\times(c-d))|}{6}$$
        '''
        vertices = self.vertices
        pos = self.pos

        def _get_volume(a, b, c):
            return abs(
                np.dot(
                    (vertices[a] - pos),
                    np.cross(
                        (vertices[b] - pos),
                        (vertices[c] - pos)
                    )
                )
            )/6.

        volume = 0.
        for i in range(12):
            volume += _get_volume(indexA[i], indexB[i], indexC[i])

        return volume

    def dx(self, variableName, mesh):
        ''' Calculate the derivative of the given Scalar variable
            in terms of 'x'
        '''
        pass
