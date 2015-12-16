# by LiJing @ SJTU
import re
import gzip
import numpy as np


class DataList(object):
    ''' Deal with text and data format processing
    '''
    def __init__(self):
        self.data = np.zeros(1)

    def extract_data_from_foam(self, filename):
        ''' Extract internalField data from OpenFOAM output file
            Return a np.array as the @DataList Class property @data
        '''
        def _inner_process(fileopen):
            tmpList = []
            uniPat = re.compile(r' uniform ')
            startPat = re.compile(r'^\($')
            endPat = re.compile(r'^\)$')
            # Find the line ends with something like '\d\)' or '\d'
            linePat = re.compile(r'(\d\))|\d$')
            # Filter out the numbers in each line
            dataPat = re.compile(r'-?\d+\.?\d*e?-?\d*')
            # For the gz data file of OpenFOAM we have to use gzip.open
            # 'rt' means 'read it as a text rather than the binary file'
            tokenStart = 0
            tokenEnd = 0
            for line in fileopen:
                # Filter out the uniform situation
                if uniPat.search(line):
                    tmpStr = line.split(' uniform ')[1].strip()
                    tmp0 = tmpStr.replace(');', '')
                    tmp1 = tmp0.replace('(', '')
                    tmpList = tmp1.split()
                    break

                elif startPat.match(line):
                    tokenStart = 1
                elif (linePat.search(line) and
                      tokenStart == 1 and tokenEnd == 0):
                    tmpLine = dataPat.findall(line)
                    tmpList.append(
                        [eval(x) for x in tmpLine]
                    )
                elif endPat.match(line):
                    tokenStart = 0
                    tokenEnd = 1
                    break
                else:
                    continue

            return tmpList

        try:
            if filename.endswith('.gz'):
                with gzip.open(filename, 'rt') as fileopen:
                    tmpList = _inner_process(fileopen)
            else:
                with open(filename, 'r') as fileopen:
                    tmpList = _inner_process(fileopen)

        except IOError:
            print(filename + ' is not found.')

        # uniform situation
        if isinstance(tmpList[0], str):
            self.data = [eval(x) for x in tmpList]
        else:
            self.data = np.array(tmpList)
        return self.data

    def cast_to_mesh_data(self, nums):
        ''' Map @data onto the mesh matrix
        '''
        try:
            if len(nums) != 3:
                print('The input argument should be a List with three items')
                return None
            else:
                length = self.data.shape[1]
                if nums[0]*nums[1]*nums[2] == self.data.shape[0]:
                    newdata = self.data.reshape(
                        (nums[2], nums[1], nums[0], length)
                    )
                    return newdata
                else:
                    print('The corresponding dimension does not match the data')
                    return None
        except:
            print('Invalid input argument')
            return None
