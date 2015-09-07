#!/usr/bin/env python2
import lss
import sys

def test():
    print "CATS MEOW MEOW"

if len(sys.argv) != 3:
    print("Usage: {} [config] [user]".format(sys.argv[0]))
else:
    lss.run_lss(sys.argv[1], sys.argv[2], on_detect=test)

