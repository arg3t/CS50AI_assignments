import os
import sys
import time
import subprocess

combinations = [(0, 0), (0, 1),(1, 1),(2, 2),(1, 2),(0, 2)]

start = time.time()
for count in range(int(sys.argv[1])):
	print("RUN " + str(count + 1))
	for i in combinations:
		os.system("python generate.py data/structure{0}.txt data/words{1}.txt > debug/{0}_{1}.{2}.out".format(i[0], i[1], count))

print("Program took {} seconds to execute on average".format((time.time()-start) / (count + 1)))
proc = subprocess.Popen(["grep 'No solution' debug/*"], stdout=subprocess.PIPE, shell=True)
(out, err) = proc.communicate()
out = out.decode()

print("{} tests did not find any solutions!\n".format(len(out.split("\n")) - 1))
for i in out.split("\n"):
	print(i.split(":")[0])

