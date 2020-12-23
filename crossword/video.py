import os
import time

combinations = [(0,0),(0,1),(1,1),(2,2),(0,2)]

for i in combinations:
	print("Running structure {} with words {}".format(i[0], i[1]))
	os.system("python generate.py data/structure{0}.txt data/words{1}.txt images/{0}_{1}.png".format(i[0], i[1]))
	time.sleep(0.5)	
