import sys; sys.path.insert(0, 'wl'); from common import *
from imp import imp
from sm1_redo import clear
k, fi, X0 = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
clear(X0, 42000); imp(k, fi, X0, 455939.0, 'RI%d:' % fi)
