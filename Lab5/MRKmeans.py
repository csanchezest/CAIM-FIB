"""
.. module:: MRKmeans

MRKmeans
*************

:Description: MRKmeans

    Iterates the MRKmeansStep script

:Authors: bejar
    

:Version: 

:Created on: 17/07/2017 10:16 

"""

from MRKmeansStep import MRKmeansStep
import shutil
import argparse
import collections
import os
import sys
import time
from mrjob.util import to_lines

__author__ = 'bejar'

fichero = open("OUTPUT.txt",'w')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prot', default='prototypes.txt', help='Initial prototpes file')
    parser.add_argument('--docs', default='documents.txt', help='Documents data')
    parser.add_argument('--iter', default=5, type=int, help='Number of iterations')
    parser.add_argument('--ncores', default=2, type=int, help='Number of parallel processes to use')

    args = parser.parse_args()
    assign = {}

    # Copies the initial prototypes
    cwd = os.getcwd()
    shutil.copy(cwd + '/' + args.prot, cwd + '/prototypes0.txt')

    nomove = False  # Stores if there has been changes in the current iteration
    for i in range(args.iter):
        tinit = time.time()  # For timing the iterations

        # Configures the script
        print('Iteration %d ...' % (i + 1))
        # The --file flag tells to MRjob to copy the file to HADOOP
        # The --prot flag tells to MRKmeansStep where to load the prototypes from
        mr_job1 = MRKmeansStep(args=['-r', 'local', args.docs,
                                     '--file', cwd + '/prototypes%d.txt' % i,
                                     '--prot', cwd + '/prototypes%d.txt' % i,
                                     '--num-cores', str(args.ncores)])

        # Runs the script
        with mr_job1.make_runner() as runner1:
            fichero.write("ITERACION\n")
            runner1.run()
            new_assign = {}
            new_proto = {}
            # Process the results of the script iterating the (key,value) pairs
            for key, value in mr_job1.parse_output(runner1.cat_output()):
                # You should store things here probably in a datastructure
                new_assign[key] = value[0]
                new_proto[key] = value[1]

            # fichero.write(str(new_assign))
            
            # If your scripts returns the new assignments you could write them in a file here
            f = open("assignments%d.txt" % (i+1), 'w')
            for key, val in new_assign.items():
                data = ""
                # fichero.write(str(val))
                for doc in val:
                    # fichero.write(str(word) + "  " + str(freq   ))
                    data += doc + " "
                f.write(key + ":" + data + "\n")
            f.close()
            
            # You should store the new prototypes here for the next iteration
            f = open("prototypes%d.txt" % (i + 1), 'w')
            for key, docs in new_proto.items():
                data = ""
                elems = docs[0]

                docDict = {}
                for doc in docs:
                    docDict[doc[0]] = doc[1]

                
                docDict = collections.OrderedDict(sorted(docDict.items()))


                fichero.write(str(list(docDict.keys()))+"\n")

                for word, freq in docDict.items():
                    data += word + '+' + str(freq)+ " "
                f.write(str(key) + ":" + data + "\n")
            f.close()
            # If you have saved the assignments, you can check if they have changed from the previous iteration
            nomove = i > 0 and assign == new_assign
            assign = new_assign
                

        print(f"Time= {(time.time() - tinit)} seconds")

        if nomove:  # If there is no changes in two consecutive iteration we can stop
            print("Algorithm converged")
            break

    # Now the last prototype file should have the results

    fichero.close()
