# by LiJing @ SJTU


class Argument(object):
    ''' A container as arguments to be passed into functions
    '''
    def __init__(self, argsDict):
        self.argsDict = argsDict
        for key in argsDict.keys():
            exec('self.' + key + ' = argsDict[key]')
