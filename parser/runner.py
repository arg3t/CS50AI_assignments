import subprocess
import os

files = os.listdir("sentences")
for i in files:
    with open("sentences/" + i,"r") as f:
        sentence = f.read()
    p = subprocess.Popen(["python", "parser.py"], stdin=subprocess.PIPE)
    print(sentence)
    p.communicate(sentence)