# -*- coding:utf8 -*-
import urllib2
import json
import os,sys
import re
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller
ROOTDIR = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(os.path.join(ROOTDIR, "lib"))
# 设置模型文件的路径
MODELDIR=os.path.join(ROOTDIR, "ltp_data")


# path = os.path.join(os.path.dirname(__file__), os.pardir)
# path_property = open("H:\sina\sentiment_word2vec\car_entity_property.txt",'r')
# path_sentiment = open("H:\sina\sentiment_word2vec\car_sentiment_dic.txt",'r')
# path_degree = open("H:\sina\sentiment_word2vec\car_degree_dic.txt",'r')
#
# # path_corpus = open("H:\sina\corpus\shiyanyuliao.txt")
# path_corpus = open("H:\sina\corpus\car_review_split.txt")
#
# path_out1 = open("H:\sina\corpus\shuchu1.txt",'w')
# path_out2 = open("H:\sina\corpus\shuchu2.txt",'w')
# path_out3 = open("H:\sina\corpus\shuchu3.txt",'w')


path = os.path.join(os.path.dirname(__file__), os.pardir)
path_property = open("/data0/shenyanjun/sentiment2.0/car_entity_property.txt",'r')
path_sentiment = open("/data0/shenyanjun/sentiment2.0/car_sentiment_dic.txt",'r')
path_degree = open("/data0/shenyanjun/sentiment2.0/car_degree_dic.txt",'r')
#path_corpus = open("/data0/shenyanjun/lexicon/car_review_split.txt")
path_out1 = open("/data0/shenyanjun/sentiment2.0/shuchu1.txt",'w')
path_out2 = open("/data0/shenyanjun/sentiment2.0/shuchu2.txt",'w')
path_out3 = open("/data0/shenyanjun/sentiment2.0/shuchu3.txt",'w')
path_corpus = open("/data0/shenyanjun/sentiment2.0/000000_0_1.txt",'r')
#属性词
def fun_property_set(path):
    property_set = []
    for line in path.readlines():
        property_set.append((line.strip().split('\t')[0]))
    return property_set

#程度词
def fun_degree_set(path):
    degree_set = []
    for line in path.readlines():
        degree_set.append((line.strip().split('\t')[0]))
    return degree_set

#情感词
def fun_emotion_set(path):
    emotion_set = []
    for line in path.readlines():
        emotion_set.append((line.strip().split('\t')[0]))
    return emotion_set

#读取语料
def read_corpus(path):
    aa = 0
    corpus = []
    while aa< 96115:
        print aa
        #line = path.readline()
        #print line
        line = path.readline().strip().split('\001')[1]
        if line not in corpus:
            corpus.append(line)
        else:
            pass
        aa+=1
    path.close()
    return corpus

#分析每行
def parse1(line):
    if len(line) > 1:
        url_get_base = "http://ltpapi.voicecloud.cn/analysis/?"
        api_key = 'z4I4d0X6YULu7XljSjhQbSgCXI8fry7YyQ2n2soH'
        text = re.sub('\s','。',line)
        format = 'json'
        pattern = 'all'
        result = urllib2.urlopen("%sapi_key=%s&text=%s&format=%s&pattern=%s" % (url_get_base,api_key,text,format,pattern))
        content = result.read().strip()
    # print content
        return json.loads(content)[0]
    else:
        aa= []
        return aa


segmentor = Segmentor()
segmentor.load_with_lexicon(os.path.join(MODELDIR,"cws.model"),"/data0/dm/dict/dict.txt")
postagger = Postagger()
postagger.load(os.path.join(MODELDIR, "pos.model"))
parser = Parser()
parser.load(os.path.join(MODELDIR, "parser.model"))



#分析每句
def callLTP(sentence):
    words = segmentor.segment(sentence)
    postags = postagger.postag(words)
    arcs = parser.parse(words, postags)
    resultJson=[]
    for index in range(len(words)):
        resultJson.append({'id':index,'cont':words[index],'pos':postags[index],'relate':arcs[index].relation,'parent':arcs[index].head - 1})
    return resultJson

#分析每行，调用callLTP
def parse(line):
    line_parse = []
    line = re.sub('【|】',' ',line)
    line  = re.sub('！|。|#|\?|？|!|；|;', ' ', line)
    #line  = re.sub('！|。|#|？|\?|!|；|;|.', ' ', line)
    line  = re.sub('[\s]+', '。',line)
    print line
    #print 'juzi_after:',line
    line_split = line.split('。')
    #print "line_split:",len(line_split)
    for sentence_one in line_split:
        #print len(sentence_one)
        if len(sentence_one) > 5 and len(sentence_one) < 300:
            sentence_parse = callLTP(sentence_one)
            line_parse.append(sentence_parse)
    #print "line_parse:",len(line_parse)
    return line_parse

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

#组合给定的两个句子path,path为不同类型词的路径
def path_zuhe3(path1,path2,location_sen):
    path_after_zuhe = []
    if abs(path1[0]-path2[0]) > 30:
        return path_after_zuhe
    else:
        print "chuli_zuhe_3:"
        print path1,path2
        k1 = 0
        k2 = 0
        while max(k1,k2) < max(len(path1),len(path2)):
            if path1[k1] == path2[k2] and sum([k1,k2]) > 2:
                path_after_zuhe = path1[:k1+1]
                nixu = path2[:k2][::-1]
                path_after_zuhe.extend(nixu)
                break
            elif path1[k1] == path2[k2] and sum([k1,k2]) < 3:
                if k1 > k2 and path1[k1+2] in location_sen:
                    path_after_zuhe = path1[:k1+3]
                elif k1 < k2 and path2[k2+2] in location_sen:
                    path_after_zuhe = path2[:k2+3]
                else:
                    pass
                break
            elif len(path1)-k1 > len(path2)-k2:
                k1 += 2
            elif len(path1)-k1 < len(path2)-k2:
                k2 += 2
            else:
                k1 += 2
                k2 += 2
        return path_after_zuhe

#组合给定的两个句子path,path为不同类型词的路径
def path_zuhe2(path1,path2):
    path_after_zuhe = []
    if abs(path1[0]-path2[0]) > 30:
        return path_after_zuhe
    else:
        # print path1,path2
        k1 = 0
        k2 = 0
        while max(k1,k2) < max(len(path1),len(path2)):
            if path1[k1] == path2[k2] :
                path_after_zuhe = path1[:k1+1]
                nixu = path2[:k2][::-1]
                path_after_zuhe.extend(nixu)
                break
            elif len(path1)-k1 > len(path2)-k2:
                k1 += 2
            elif len(path1)-k1 < len(path2)-k2:
                k2 += 2
            else:
                k1 += 2
                k2 += 2
    return path_after_zuhe

def path_zishai(paths):
    paths_new = paths
    if len(paths) < 2:
        pass
    else:
        for index,path_one in enumerate(paths):
            if len(paths[index+1:]) > 0:
                for path_two in paths[index+1:]:
                    if len(path_one) > len(path_two) and path_two in paths_new and path_two == path_one[-len(path_two):]:
                        paths_new.remove(path_two)
                    elif len(path_one) < len(path_two) and path_one in paths_new and  path_one == path_two[-len(path_one):]:
                        paths_new.remove(path_one)
                    else:
                        pass
            else:
                pass
    return paths_new

def guize_check(sentence_pro,sentence_sen,sentence_deg,location_sen):
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
            # print "sentence_deg:",sentence_deg
            for ii in check_sen_path:
                if ii in sentence_sen:
                    sentence_sen.remove(ii)

            #通过上面部分从新组合了情感句法和属性句法
            #print "chuli_1_deg:",sentence_deg
            #print "chuli_1_sen:",sentence_sen
            if len(sentence_pro) > 0 and len(sentence_deg) > 0:
                for path1_pro in sentence_pro:
                    for path1_deg in sentence_deg:
                        path_zuhe1_after = path_zuhe3(path1_deg,path1_pro,location_sen)
                        if path_zuhe1_after:
                            path_all_in.append(path_zuhe1_after)
            elif len(sentence_pro) > 0 and len(sentence_sen) > 0:
                for path2_pro in sentence_pro:
                    for path2_sen in sentence_sen:
                        path_zuhe2_after = path_zuhe2(path2_pro,path2_sen)
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
                        path_zuhe3_after = path_zuhe2(path3_pro,path3_sen)
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
        if parse_word['cont'] in property_list:
            patten = digui(parse_sentence,parse_word,patten)
            sentence_pro.append(patten)
            # print "属性：",parse_word["cont"],parse_word["pos"]
            # print patten
        elif parse_word['cont'] in sentiment_list:
            patten = digui(parse_sentence,parse_word,patten)
            sentence_sen.append(patten)
            # print "情感：",parse_word["cont"],parse_word["pos"]
            # print patten
        elif parse_word['cont'] in degree_list:
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
    patten_1 = []
    patten_2 = []
    patten_3 = []
    for next,line in enumerate(corpus):
        print next,':',line
        parse_line = parse(line)
        #print parse_line
        for parse_sentence in parse_line:
            juzi_pro,juzi_sen,juzi_deg = select_patten(property_list,sentiment_list,degree_list,parse_sentence)
            #print 'juzi_pro:',juzi_pro
            #print 'juzi_sen:',juzi_sen
            #print 'juzi_deg:',juzi_deg
            location_sen = []
            for loc_sen in juzi_sen:
                location_sen.append(loc_sen[0])
            juzi_pro = path_zishai(juzi_pro)
            juzi_sen = path_zishai(juzi_sen)
            juzi_deg = path_zishai(juzi_deg)
            #print 'juzi_pro:',juzi_pro
            #print 'juzi_sen:',juzi_sen
            #print 'juzi_deg:',juzi_deg
            path_all_in,path_sen_pro,path_sen_deg = guize_check(juzi_pro,juzi_sen,juzi_deg,location_sen)
            print 'path_all:',path_all_in
            print 'path_2:',path_sen_pro
            print 'path_3:',path_sen_deg
            for path_all_in_one in path_all_in:
                for index1,element_1 in enumerate(path_all_in_one):
                    if isinstance(element_1,int):
                        path_all_in_one[index1] = parse_sentence[element_1]['pos']
                patten_1.append(path_all_in_one)
                s1 = '\t'.join(path_all_in_one)
                path_out1.write(s1+'\n')
            for path_sen_pro_one in path_sen_pro:
                for index2,element_2 in enumerate(path_sen_pro_one):
                    if isinstance(element_2,int):
                        path_sen_pro_one[index2] = parse_sentence[element_2]['pos']
                patten_2.append(path_sen_pro_one)
                s2 = '\t'.join(path_sen_pro_one)
                path_out2.write(s2+'\n')
            for path_sen_deg_one in path_sen_deg:
                for index3,element_3 in enumerate(path_sen_deg_one):
                    if isinstance(element_3,int):
                        path_sen_deg_one[index3] = parse_sentence[element_3]['pos']
                patten_3.append(path_sen_deg_one)
                s3 = '\t'.join(path_sen_deg_one)
                path_out3.write(s3+'\n')
    print "path_all_in:",patten_1
    print "path_sen_pro:",patten_2
    print "path_sen_deg:",patten_3
    path_out1.close()
    path_out2.close()
    path_out3.close()
