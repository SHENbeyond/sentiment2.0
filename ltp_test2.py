# -*- coding:utf8 -*-
import urllib2
import json
import os,sys
import re
import time
path = os.path.join(os.path.dirname(__file__), os.pardir)
path_property = open("/data0/shenyanjun/sentiment2.0/car_entity_property.txt",'r')
path_sentiment = open("/data0/shenyanjun/sentiment2.0/car_sentiment_dic.txt",'r')
path_degree = open("/data0/shenyanjun/sentiment2.0/car_degree_dic.txt",'r')

path_corpus = open("/data0/shenyanjun/lexicon/car_review_split.txt")

path_out1 = open("/data0/shenyanjun/sentiment2.0/shuchu1.txt",'w')
path_out2 = open("/data0/shenyanjun/sentiment2.0/shuchu2.txt",'w')
path_out3 = open("/data0/shenyanjun/sentiment2.0/shuchu3.txt",'w')
# path_corpus = open("H:\sina\sentiment\car_review_split_300_new.txt")
#属性词
def fun_property_set(path):
    property_set = []
    for line in path.readlines():
        property_set.append((line.strip().split('\t')[0]).decode('utf-8'))
    return property_set

#程度词
def fun_degree_set(path):
    degree_set = []
    for line in path.readlines():
        degree_set.append((line.strip().split('\t')[0]).decode('utf-8'))
    return degree_set

#情感词
def fun_emotion_set(path):
    emotion_set = []
    for line in path.readlines():
        emotion_set.append((line.strip().split('\t')[0]).decode('utf-8'))
    return emotion_set

#读取语料
def read_corpus(path):
    aa = 0
    corpus = []
    while aa< 200000:
        line = path.readline().strip()
        corpus.append(line)
        aa+=1
    return corpus

#分析每行句子
def parse(line):
    print 'line1:',line
    line = re.sub('#','。',line)
    print 'line2:',line
    url_get_base = "http://ltpapi.voicecloud.cn/analysis/?"
    api_key = 'z4I4d0X6YULu7XljSjhQbSgCXI8fry7YyQ2n2soH'
    text = re.sub('\s'+,'。',line)
    print 'line3:',text
    format = 'json'
    pattern = 'all'
    result = urllib2.urlopen("%sapi_key=%s&text=%s&format=%s&pattern=%s" % (url_get_base,api_key,text,format,pattern))
    content = result.read().strip()
    # print content
    return json.loads(content)[0]

#输出每个词的句法path
def digui(parse_sentence,parse_word,patten):
    kk = 0
    while kk<10:
        patten.append(parse_word["id"]),patten.append(parse_word["relate"])
        if parse_word["parent"] == -1:
            break
        else:
            parse_word = parse_sentence[parse_word["parent"]]
            kk+=1
    return patten

#组合给定的两个句子path
def path_zuhe(path1,path2):
    path_after_zuhe = []
    if abs(path1[0]-path2[0]) > 5:
        return path_after_zuhe
    else:
        # print path1,path2
        k1 = 0
        k2 = 0
        while max(k1,k2) < max(len(path1),len(path2)):
            if path1[k1] == path2[k2]:
                path_after_zuhe = path1[:k1+1]
                nixu = path2[:k2][::-1]
                path_after_zuhe.extend(nixu)
                break
            elif len(path1) > len(path2):
                k1 += 2
            elif len(path1) < len(path2):
                k2 += 2
            else:
                k1 += 2
                k2 += 2
    return path_after_zuhe

def guize_check(sentence_pro,sentence_sen,sentence_deg):
    path_all_in = []
    path_sen_pro = []
    path_sen_deg = []
    if len(sentence_sen) > 0:
        if len(sentence_deg) > 0:
            #程度句法，需要保留
            check_deg_path = []
            #情感句法，需要删除
            check_sen_path = []
            for deg_path in sentence_deg:
                for sen_path in sentence_sen:
                    if len(deg_path) > len(sen_path) and sen_path == deg_path[-(len(sen_path)):]:
                        check_sen_path.append(sen_path)
                        check_deg_path.append(deg_path)
                    else:
                        pass
            sentence_deg = check_deg_path
            for ii in check_sen_path:
                if ii in sentence_sen:
                    sentence_sen.remove(ii)
            #通过上面部分从新组合了情感句法和属性句法
            if len(sentence_pro) > 0 and len(sentence_deg) > 0:
                for path1_pro in sentence_pro:
                    for path1_deg in sentence_deg:
                        path_zuhe1_after = path_zuhe(path1_deg,path1_pro)
                        if path_zuhe1_after:
                            path_all_in.append(path_zuhe1_after)
            elif len(sentence_pro) > 0 and len(sentence_sen) > 0:
                for path2_pro in sentence_pro:
                    for path2_sen in sentence_sen:
                        path_zuhe2_after = path_zuhe(path2_pro,path2_sen)
                        if path_zuhe2_after:
                            path_sen_pro.append(path_zuhe2_after)
            else:
                if len(sentence_deg) > 0:
                    for one_deg in sentence_deg:
                        path_sen_deg.append(one_deg[:-1])
                # elif len(sentence_sen) > 0:
                #     path_sen_deg.extend(sentence_sen[:-1])
                else:
                    pass
        else:
            if len(sentence_pro) > 0:
                for path3_pro in sentence_pro:
                    for path3_sen in sentence_sen:
                        path_zuhe3_after = path_zuhe(path3_pro,path3_sen)
                        if path_zuhe3_after:
                            path_sen_pro.append(path_zuhe3_after)
    else:
        pass
    return path_all_in,path_sen_pro,path_sen_deg

#筛选句法结构、词性的模板
def select_patten(property_list,sentiment_list,degree_list,parse_sentence):
    sentence_pro = []
    sentence_sen = []
    sentence_deg = []
    for parse_word in parse_sentence:
        patten=[]
        if parse_word["cont"] in property_list:
            patten = digui(parse_sentence,parse_word,patten)
            sentence_pro.append(patten)
            # print "属性：",parse_word["cont"],parse_word["pos"]
            # print patten
        elif parse_word["cont"] in sentiment_list:
            patten = digui(parse_sentence,parse_word,patten)
            sentence_sen.append(patten)
            # print "情感：",parse_word["cont"],parse_word["pos"]
            # print patten
        elif parse_word["cont"] in degree_list:
            patten = digui(parse_sentence,parse_word,patten)
            sentence_deg.append(patten)
            # print "程度：",parse_word["cont"],parse_word["pos"]
            # print patten
        else:
            pass
    return sentence_pro,sentence_sen,sentence_deg

if __name__ == '__main__':
    property_list = fun_property_set(path_property)
    sentiment_list = fun_emotion_set(path_sentiment)
    degree_list = fun_degree_set(path_degree)
    corpus = read_corpus(path_corpus)
    patten_pro = []
    patten_sen = []
    patten_deg = []
    for line in corpus:
        time.sleep(0.01)
        #print line
        parse_line = parse(line)
        for parse_sentence in parse_line:
            juzi_pro,juzi_sen,juzi_deg = select_patten(property_list,sentiment_list,degree_list,parse_sentence)
            path_all_in,path_sen_pro,path_sen_deg = guize_check(juzi_pro,juzi_sen,juzi_deg)
            for path_all_in_one in path_all_in:
                for index1,element_1 in enumerate(path_all_in_one):
                    if isinstance(element_1,int):
                        path_all_in_one[index1] = parse_sentence[element_1]['pos']
                patten_pro.append(path_all_in_one)
                s1 = '\t'.join(path_all_in_one)
                print 's1:',s1
                path_out1.write(s1+'\n')
            for path_sen_pro_one in path_sen_pro:
                for index2,element_2 in enumerate(path_sen_pro_one):
                    if isinstance(element_2,int):
                        path_sen_pro_one[index2] = parse_sentence[element_2]['pos']
                patten_sen.append(path_sen_pro_one)
                s2 = '\t'.join(path_sen_pro_one)
                print 's2:',s2
                path_out2.write(s2+'\n')
            for path_sen_deg_one in path_sen_deg:
                for index3,element_3 in enumerate(path_sen_deg_one):
                    if isinstance(element_3,int):
                        path_sen_deg_one[index3] = parse_sentence[element_3]['pos']
                patten_deg.append(path_sen_deg_one)
                s3 = '\t'.join(path_sen_deg_one)
                print 's3',s3
                path_out3.write(s3+'\n')
    print "path_all_in:",patten_pro
    print "path_sen_pro:",patten_sen
    print "path_sen_deg:",patten_deg
    path_out1.close()
    path_out2.close()
    path_out3.close()
