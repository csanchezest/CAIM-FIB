import re
import enchant
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.linear_model import LinearRegression


def zipf(i, a, b, c):
    return [c / pow(j + b, a) for j in i]

def expfunc(x, a, b, c):
    return a * np.exp(-b * x) + c


d = enchant.Dict("en_GB")
filtered_content = dict()

freqs = []

file = open("datanovels/data.txt","r+")
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

z = np.array(ranks)
t = np.array(freqs)

fig, ax = plt.subplots()
ax.set_xscale('log')
ax.set_yscale('log')
plt.plot(z, t, 'ro', label='data')

popt, pcov = curve_fit(zipf, z, t, bounds=(1., [2.5, 2.5, 5.]))
print(popt)
plt.plot(ranks, zipf(ranks, *popt), 'bo', label='fit')

model2 = LinearRegression()
model2.fit(np.log(ranks).reshape(-1, 1), np.log(t))
print(f"slope_data: {model2.coef_}")

model1 = LinearRegression()
model1.fit(np.log(ranks).reshape(-1, 1), np.log(zipf(ranks, *popt)))
print(f"slope_fit: {model1.coef_}")

plt.xlabel('rank')
plt.ylabel('frequency')
plt.title('Word frequencies in log-log scale')
plt.legend()
plt.show()




