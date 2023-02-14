#!/usr/bin/python

from collections import namedtuple
from tabulate import tabulate
import numpy as np
import toolz
import time
import sys


class Edge:
    def __init__(self, origin=None):
        self.origin = origin  # write appropriate value
        self.weight = 0  # write appropriate value

    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)

    # write rest of code that you need for this class


class Airport:
    def __init__(self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = []  # keys in routeHash
        self.routeHash = {}  # key: aeropuerto origen (el aeropuerto destino conserva los aeropuertos que van hacia él); value: k
        self.outweight = 0  # write appropriate value

    def __repr__(self):
        return f"{self.code}\t{self.name}"


edgeList = []  # list of Edge
edgeHash = {}  # hash of edge to ease the match ==> lista de adyacencias
airportList = []  # list of Airport
airportHash = {}  # hash key IATA code -> Airport


def readAirports(fd):
    print("Reading Airport file from {0}".format(fd))
    airportsTxt = open(fd, "r")
    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp[4]) != 5:
                raise Exception('not an IATA code')
            a.name = temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code = temp[4][1:-1]
        except Exception as inst:
            pass
        else:
            cont += 1
            airportList.append(a)
            airportHash[a.code] = a
    airportsTxt.close()
    print(f"There were {cont} Airports with IATA code")


def readRoutes(fd):
    print("Reading Routes file from {fd}")
    routesTxt = open(fd, "r")
    cont = 0
    for line in routesTxt.readlines():
        e = Edge()
        temp = line.split(',')
        xOg, xDest = temp[2], temp[4]
        if len(xOg) != 3 or len(xDest) != 3:
            raise Exception('not an IATA code')
        if xDest not in airportHash or xOg not in airportHash:
            continue
        aDest = airportHash[xDest]
        if xOg in edgeHash:
            e = edgeHash[xOg]
        else:
            e.origin = xOg
            edgeHash[xOg] = e
            cont += 1
        e.weight += 1
        if xOg in aDest.routeHash:
            aDest.routeHash[xOg] += 1
        else:
            aDest.routeHash[xOg] = 1
    routesTxt.close()
    for key, a in airportHash.items():
        a.routes += list(a.routeHash.keys())
        try:
            a.outweight = edgeHash[a.code].weight
        except:
            continue
    edgeList = list(edgeHash.keys())
    print(f"There were {cont} routes with IATA code")


def getVals(dest, P):
    vals = []
    for og, val in dest.routeHash.items():
        try:
            x = P[og] * val / airportHash[og].outweight
            vals.append(x)
        except:
            continue
    return vals


def computePageRanks(df,lim):
    n = len(airportHash)
    P = dict.fromkeys(list(airportHash.keys()), 1/n)
    L = df     # between 0.8-0.9
    limit = lim
    diff = 10
    prev = 10
    nit = 0
    j = (1-L)/n
    while diff > limit:
        Q = dict.fromkeys(list(airportHash.keys()), 0)
        for key, dest in airportHash.items():
            Q[key] = L * sum(getVals(dest, P)) + j
        P = Q
        val = sum(P.values())
        P = toolz.valmap(lambda x: x/val, P)
        val = sum(P.values())
        diff = abs(prev - val)
        prev = val
        nit += 1
    return nit, P


def outputPageRanks(P):
    P = dict(sorted(P.items(), key=lambda item: item[1], reverse=True))
    data = [['IATA CODE','OUTWEIGHT','PAGERANK']]
    for key, val in P.items():
        data.append([key, airportHash[key].outweight, val])
    print(tabulate(data,headers='firstrow',tablefmt='fancy_grid'))

def main(argv=None):
    readAirports("airports.txt")
    readRoutes("routes.txt")

    possible_dampfactors = [0.1,0.2,0.4,0.6,0.8,0.85,0.88,0.9,0.99]
    limit = 1e-64
    print(tabulate([['Limit', str(limit)]],tablefmt='fancy_grid'))
    data = [[]]
    data.append(['DampFact','Iterations','CompTime'])
    for df in possible_dampfactors:
        time1 = time.time()
        iterations, P = computePageRanks(df,limit)
        time2 = time.time()
        data.append([df,iterations,time2-time1])
    print(tabulate(data,headers='firstrow',tablefmt='fancy_grid'))


if __name__ == "__main__":
    sys.exit(main())
