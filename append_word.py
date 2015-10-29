#coding:utf-8
__author__ = 'syj'
import sys, os
path = os.path.abspath(os.path.dirname(sys.argv[0]))
path_property = open(path+"/car_entity_property.txt",'a')
path_sentiment = open(path+"/car_sentiment_dic.txt",'a')
path_degree = open(path+"/car_degree_dic.txt",'a')


propery_app = []
sentiment_app =['质感']
degree_app =[]
dictionary_app = []

for word_pro in propery_app:
    path_property.write(word_pro+'\t'+ "附加" + '\n')
path_property.close()

for word_sen in sentiment_app:
    path_sentiment.write(word_sen+'\t'+ "附加" + '\n')
path_sentiment.close()

for word_deg in degree_app:
    path_degree.write(word_deg+'\t'+ "附加" + '\n')
path_degree.close()
