# by LiJing @ SJTU


# For different versions of solvers
variablesDict1 = {'velocity':       'U',
                  'vorticity':      'vorticity',
                  'pressure':       'p',
                  'elevation':      'elevation',
                  'circulation':    'cirulation',
                  'kinetics':       'kinetics',
                  'gauge':          'gauge',
                  }

variablesDict0 = {'velocity':       'U',
                  'vorticity':      'vorticity',
                  'pressure':       'p_rgh',
                  'vof':            'alpha.water',
                  'elevation':      'elevation',
                  'circulation':    'cirulation',
                  'kinetics':       'kinetics',
                  'gauge':          'gauge',
                  }

variablesList = [variablesDict0, variablesDict1]

# Variables to be read from files
varFromFileList = ['velocity',
                   'vorticity',
                   'pressure',
                   'vof',
                   ]

# Two categories for variables to be dumped
varEachStepList = ['velocity',
                   'vorticity',
                   'pressure',
                   'vof',
                   ]
varEndStepList = ['circulation',
                  'kinetics',
                  'gauge',
                  ]

# Mitgo Head Line
headString = '# Mitgo File __ by LiJing @ SJTU copyright 2015\n'
