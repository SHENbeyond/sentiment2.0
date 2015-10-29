__author__ = 'syj'
import os
import sys
path = os.path.abspath(os.path.dirname(sys.argv[0]))
from collections import Counter
path_in1 = open(path+"/shuchu1_weibo.txt",'r')
path_in2 = open(path+"/shuchu2_weibo.txt",'r')
path_in3 = open(path+"/shuchu3_weibo.txt",'r')

path_out1 = open(path+"/count_shuchu1_weibo.txt",'w')
path_out2 = open(path+"/count_shuchu2_weibo.txt",'w')
path_out3 = open(path+"/count_shuchu3_weibo.txt",'w')

def read_model(path):
    aa = path.read().strip().split('\n')
    return aa

def write_counter(module,path):
    for key in sorted(module.keys(),reverse = True):
        path.write(str(module[key])+'\t'+key+'\n')
    path.close()


if __name__  == "__main__":
    module1 = Counter(read_model(path_in1))
    module2 = Counter(read_model(path_in2))
    module3 = Counter(read_model(path_in3))
    write_counter(module1,path_out1)
    write_counter(module2,path_out2)
    write_counter(module3,path_out3)

