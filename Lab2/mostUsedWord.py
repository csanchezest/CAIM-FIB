import re
import enchant
import os

d = enchant.Dict("en_GB")

directory = os.getcwd()


for f in os.listdir(directory)[1:]:
    if not f.endswith(".py"):
        file = open(f, "r+")
        filtered_content = dict()
        pattern = re.compile("^[a-zA-Z]+$")
        lines = file.readlines()
        for line in lines[:-2]:
            word = line.split(', ')
            if pattern.match(word[1][:-1]) and d.check(word[1][:-1]):
                filtered_content[word[1][:-1]] = int(word[0])
        res = dict(sorted(filtered_content.items(), key=lambda x: x[1], reverse=True))
        print(f, ":", list(res.keys())[0:3])
        file.close()
