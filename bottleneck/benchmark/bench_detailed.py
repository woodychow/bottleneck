
import numpy as np
import bottleneck as bn
from .autotimeit import autotimeit

__all__ = ['bench_detailed']


def bench_detailed(function='nansum'):
    "Bottleneck benchmark of C rewrite."

    tab = '    '

    # Header
    print('%s benchmark' % function)
    print("%sBottleneck %s; Numpy %s" % (tab, bn.__version__, np.__version__))
    print("%sSpeed is Bottleneck Cython time divided by Bottleneck C time"
          % tab)
    print("")

    print("   Speed  Call                     Array")
    suite = benchsuite(function)
    for test in suite:
        name = test["name"]
        speed = timer(test['statements'], test['setup'], test['repeat'])
        print("%8.1f  %s   %s" % (speed, name[0].ljust(22), name[1]))


def timer(statements, setup, repeat):
    if len(statements) != 2:
        raise ValueError("Two statements needed.")
    with np.errstate(invalid='ignore'):
        t0 = autotimeit(statements[0], setup, repeat=repeat)
        t1 = autotimeit(statements[1], setup, repeat=repeat)
    speed = t1 / t0
    return speed


def benchsuite(function):

    repeat_array_sig = [

     (10, "rand(1)",             "(a)",    "(a, 1)",         "(a, np.nan, 0)"),
     (10, "rand(10)",            "(a)",    "(a, 2)",         "(a, np.nan, 0)"),
     (6,  "rand(100)",           "(a)",    "(a, 20)",        "(a, np.nan, 0)"),
     (3,  "rand(1000)",          "(a)",    "(a, 200)",       "(a, np.nan, 0)"),
     (2,  "rand(1000000)",       "(a)",    "(a, 200)",       "(a, np.nan, 0)"),

     (6,  "rand(10, 10)",        "(a)",    "(a, 2)",         "(a, np.nan, 0)"),
     (3,  "rand(100, 100)",      "(a)",    "(a, 20)",        "(a, np.nan, 0)"),
     (2,  "rand(1000, 1000)",    "(a)",    "(a, 200)",       "(a, np.nan, 0)"),

     (6,  "rand(10, 10)",        "(a, 1)", None,             None),
     (3,  "rand(100, 100)",      "(a, 1)", None,             None),
     (3,  "rand(1000, 1000)",    "(a, 1)", None,             None),
     (2,  "rand(100000, 2)",     "(a, 1)", "(a, 2)",         None),

     (6,  "rand(10, 10)",        "(a, 0)", None,             None),
     (3,  "rand(100, 100)",      "(a, 0)", None,             None),
     (2,  "rand(1000, 1000)",    "(a, 0)", None,             None),

     (2,  "rand(100, 100, 100)", "(a, 0)", None,             None),
     (2,  "rand(100, 100, 100)", "(a, 1)", None,             None),
     (2,  "rand(100, 100, 100)", "(a, 2)", "(a, 20)",        "(a, np.nan, 0)"),

     # TODO replace last None with (a, 0, 2) after removing cython
     (10, "array(1)",            "(a)",    None,             None),

     ]

    setup = """
        import numpy as np
        from bottleneck import %s
        from bottleneck import %s2 as %s_c
        from numpy.random import rand
        from numpy import array
        a=%s
    """
    setup = '\n'.join([s.strip() for s in setup.split('\n')])

    # what kind of function signature do we need to use?
    if function in bn.get_functions('reduce', as_string=True):
        index = 0
    elif function in bn.get_functions('move', as_string=True):
        index = 1
    elif function in ['rankdata', 'nanrankdata']:
        index = 0
    elif function in ['partsort', 'argpartsort', 'push']:
        index = 1
    elif function == 'replace':
        index = 2
    else:
        raise ValueError("`function` (%s) not recognized" % function)

    # create benchmark suite
    f = function
    suite = []
    for instructions in repeat_array_sig:
        signature = instructions[index + 2]
        if signature is None:
            continue
        repeat = instructions[0]
        array = instructions[1]
        run = {}
        run['name'] = [f + signature, array]
        run['statements'] = [f + "_c" + signature, f + signature]
        run['setup'] = setup % (f, f, f, array)
        run['repeat'] = repeat
        suite.append(run)

    return suite
