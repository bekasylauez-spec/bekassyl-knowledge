import ab,sys
o=ab.run([{'t':'tform','h':h} for h in sys.argv[1:]],'tf')
print(o)
