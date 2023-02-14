import re
import enchant
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.linear_model import LinearRegression


def heaps(n, k, beta):
    return k * np.power(n, beta)


d = enchant.Dict("en_GB")
filtered_content = dict()

freqs = []
vtotal = []
vdistinct = []
vparams = []
files = ["1", "5", "10", "12", "15"]

for f in files:
    file = open("data" + f + "novel/data.txt","r+")

    pattern = re.compile("^[a-zA-Z]+$")
    lines = file.readlines()

    for line in lines[:-2]:
        word = line.split(', ')
        if pattern.match(word[1][:-1]) and d.check(word[1][:-1]):
            filtered_content[word[1][:-1]] = word[0]
            freqs.append(int(word[0]))

    file.close()

    freqs.sort(reverse=True)
    ranks = [j+1 for j in range(len(freqs))]

    n = len(filtered_content)
    total = sum(freqs)
    vtotal.append(total)
    vdistinct.append(n)
    
    popt, pcov = curve_fit(heaps, n, total, bounds=(0.,[500., 1.]), method='trf')
    print("file data" + f + "novel: ", popt)
    vparams.append(heaps(n, *popt))


fig, ax = plt.subplots()
ax.set_xscale('log')
ax.set_yscale('log')
plt.plot(vtotal, vdistinct, 'r-', label='data')
plt.plot(vtotal, vparams, 'b-', label='fit')

plt.xlabel('total nº of words')
plt.ylabel('nº of distinct words')
plt.title('total-distinct words in log-log scale')
plt.legend()

model2 = LinearRegression()
model2.fit(np.log(vtotal).reshape(-1, 1), np.log(vdistinct))
print(f"slope_data: {model2.coef_}")

model1 = LinearRegression()
model1.fit(np.log(vtotal).reshape(-1, 1), np.log(vparams))
print(f"slope_fit: {model1.coef_}")

plt.show()
