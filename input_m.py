# by LiJing @ SJTU
import re
import os
import gzip


class Input(object):
    ''' Read all the parameter files from the given project path @path
    '''
    def __init__(self, path='../'):
        self.path = path
        self.parameters = {}

    def read_dict_value(self, filepath, keyPat):
        ''' Read any dict entry given by key in a parameter file
            and ends with a semicolon
        '''
        path = self.path
        filename = os.path.join(path, filepath)

        def _inner_process(fileopen, keyPat):
            semiColon = ';'
            token = 0
            value = ''
            for line in fileopen:
                cleanLine = line.strip()
                # One line case, like 'key  value;'
                if (cleanLine.startswith(keyPat) and
                    cleanLine.endswith(semiColon)):
                    tmp0 = cleanLine.replace(keyPat, '', 1)
                    tmp1 = tmp0.replace(semiColon, '', 1)
                    value = tmp1
                    break

                # Multi-lines case, like 'key\n value;'
                elif (cleanLine.startswith(keyPat) and not
                      cleanLine.endswith(semiColon)):
                    token = 1
                    tmp = line.replace(keyPat, '', 1)
                    value += tmp
                elif token == 1 and not cleanLine.endswith(semiColon):
                    value += line
                elif (token == 1 and cleanLine.endswith(semiColon)
                      and not cleanLine.startswith(keyPat)):
                    token = 0
                    tmp = line.replace(semiColon, '', 1)
                    value += tmp
                    break

                else:
                    continue
            return value.strip()

        try:
            # Compressed case
            if filename.endswith('.gz'):
                # For the gz data file of OpenFOAM we have to use gzip.open
                # 'rt' means 'read it as a text rather than the binary file'
                with gzip.open(filename, 'rt') as fileopen:
                    value = _inner_process(fileopen, keyPat)
            # ASCII case
            else:
                with open(filename, 'r') as fileopen:
                    value = _inner_process(fileopen, keyPat)

            return value

        except IOError:
            print(filepath + 'is not found.')
            return None

    @property
    def solver(self):
        ''' Read solver
        '''
        keyPat = 'application'
        filepath = 'system/controlDict'
        value = self.read_dict_value(filepath, keyPat)
        self.parameters['solver'] = value
        return value

    @property
    def cellsNum(self):
        ''' Read the amount of cells along different dimensions
        '''
        keyPat = 'blocks'
        filepath = 'constant/polyMesh/blockMeshDict'
        valueBlock = self.read_dict_value(filepath, keyPat)
        value = valueBlock.replace('\n', '')
        cellsNumPat = re.compile(r'.*?hex.*?\(.*?\).*?\((.*?)\)', re.S)
        ### to be modified into multi-blocks case
        tmp0 = cellsNumPat.findall(value)
        tmp1 = tmp0[0].split()
        cellsNumList = [eval(x) for x in tmp1]
        self.parameters['cellsNum'] = cellsNumList
        return cellsNumList

    @property
    def timeRange(self):
        ''' Read time range
        '''
        startPat = 'startTime'
        endPat = 'endTime'
        filepath = 'system/controlDict'
        startTime = eval(self.read_dict_value(filepath, startPat))
        endTime = eval(self.read_dict_value(filepath, endPat))
        value = [startTime, endTime]
        self.parameters['timeRange'] = value
        return value
