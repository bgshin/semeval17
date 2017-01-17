import argparse
from os import listdir
from os.path import isfile, join
from sklearn.utils import shuffle
import numpy as np
import collections



def list_dir(mypath):
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith('tsv') and f!="twitter-2016test-A.txt.tsv"]
    return onlyfiles


def split(files):
    i=0
    lines=[]

    for f in files:
        f_i=0
        with open(f, 'rt') as handle:
            for line in handle:
                num = line.split(' ')[0]
                cls = line.split(' ')[1]
                dat = ' '.join(line.split(' ')[2:])
                if "Not Available" not in dat:
                    newline = '\t'.join([num, cls, dat])
                    lines.append(newline)
                    i+=1
                    f_i+=1
        print f, f_i

    shuffled_lines = shuffle(lines, random_state=1)
    print i
    
    i=0
    i_trn=0
    i_dev=0
    with open('trn.clean', 'wt') as out_trn:
        with open('dev.clean', 'wt') as out_dev:
            for l in shuffled_lines:
                if i>=15385:
                    out_dev.write(l)
                    i_dev+=1
                else:
                    out_trn.write(l)
                    i_trn+=1
                i+=1


    print i, i_trn, i_dev
                    
        

        
        
        




    
def merge(files):
    i=0
    with open('merge.clean', 'wt') as output:
        for f in files:
            f_i=0
            with open(f, 'rt') as handle:
                for line in handle:
                    num = line.split(' ')[0]
                    cls = line.split(' ')[1]
                    dat = ' '.join(line.split(' ')[2:])
                    if "Not Available" not in dat:
                        newline = '\t'.join([num, cls, dat])
                        # print newline.replace('\n', '')
                        output.write(newline)
                        i+=1
                        f_i+=1
            print f, f_i

    print i

def main(fname):
    with open(fname, 'rt') as handle:
        with open('%s.clean'%fname, 'wt') as output:
            for line in handle:
                num = line.split(' ')[0]
                cls = line.split(' ')[1]
                dat = ' '.join(line.split(' ')[2:])
                if "Not Available" not in dat:
                    newline = '\t'.join([num, cls, dat])
                    print newline.replace('\n', '')
                    output.write(newline)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str)

    args = parser.parse_args()
    print args.f
    # main(args.f)

    files = list_dir('.')
    split(files)

    
