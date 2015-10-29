__author__ = 'syj'
# -*- coding:utf8 -*-
import urllib2
import json
import os,sys
import re
import copy
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller
ROOTDIR = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(os.path.join(ROOTDIR, "lib"))
# 设置模型文件的路径
MODELDIR=os.path.join(ROOTDIR, "ltp_data")

path = os.path.abspath(os.path.dirname(sys.argv[0]))
print path
#path_property = open("H:\sina\sentiment_word2vec\car_entity_property.txt",'r')
#path_sentiment = open("H:\sina\sentiment_word2vec\car_sentiment_dic.txt",'r')
#path_degree = open("H:\sina\sentiment_word2vec\car_degree_dic.txt",'r')

# path_corpus = open("H:\sina\corpus\shiyanyuliao.txt")
# path_corpus = open(path+"/car_weibo_after.txt",'r')
path_corpus = open(path+"/flag_sentence.txt",'r')

path_model1 = open(path+"/count_shuchu1_weibo.txt",'r')
path_model2 = open(path+"/count_shuchu2_weibo.txt",'r')
path_model3 = open(path+"/count_shuchu3_weibo.txt",'r')


path_property = open(path+"/car_entity_property.txt",'r')
path_sentiment = open(path+"/car_sentiment_dic.txt",'r')
path_degree = open(path+"/car_degree_dic.txt",'r')

path_out = open(path+'/jieguo_long_15_weibo_pro_necessary_test200.txt','w')
# path_corpus = open("/data0/shenyanjun/lexicon/car_review_split.txt")

#读取模板
def read_model(path):
    path_count = []
    path_lab = []
    for line in path.readlines():
        line_list = line.strip().split('\t')
        if int(line_list[0]) > 15:
            path_count.append(int(line_list[0]))
            path_lab.append(line_list[1:])
    return path_lab,path_count

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
    while aa < 400:
        line = path.readline().strip()
        #print line
        #if  len(line)>5:
        #    line = path.readline().strip().split('\001')[1]
        #line = path.readline().strip()
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
    #line  = re.sub('！|。|#|\?|？|!|；|;|，|,', ' ', line) #short sentence
    line  = re.sub('！|。|#|\?|？|!|；|;', ' ', line) #long sentence
    #line = re.sub(',')
    #print line
    #line  = re.sub('！|。|#|？|\?|!|；|;|.', ' ', line)
    line  = re.sub('[\s]+', '。',line)
    line_split = line.split('。')
    for sentence_one in line_split:
        if len(sentence_one) > 5 and len(sentence_one) < 300:
            sentence_parse = callLTP(sentence_one)
            line_parse.append(sentence_parse)
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
        # print 'chuli_zuhe_3:'
        # print path1,path2
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
            elif len(path1)-k1 > len(path2)-k2 :
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
            # print "guocheng1:",sentence_sen
            # print "guocehng2:",sentence_deg
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
    location_sen = [kk[0] for kk in sentence_sen]
    location_pro = [jj[0] for jj in sentence_pro]
    location_deg = [ll[0] for ll in sentence_deg]
    locations = list(set(location_deg)^set(location_sen)^set(location_pro))
    return sentence_pro,sentence_sen,sentence_deg,locations,location_sen,location_pro

def check_out(path_X,model_X,parse_sentence,locations):
    sentence_path_x = []
    for path_one in path_X:
        path_x_one = []
        path_one_copy = copy.deepcopy(path_one)
        for index1,element_1 in enumerate(path_one):
            if isinstance(element_1,int):
                path_one[index1] = parse_sentence[element_1]['pos']
        if path_one in model_X:
            print path_one
            for location,element_x in enumerate(path_one_copy):
                if isinstance(element_x,int) and element_x in locations:
                    # print parse_sentence[element_x]['cont']
                    path_x_one.append(parse_sentence[element_x]['cont'])
        if path_x_one:
            sentence_path_x.append(path_x_one)
    return sentence_path_x

if __name__ == '__main__':
    model1,count_1 = read_model(path_model1)
    model2,count_2 = read_model(path_model2)
    model3,count_3 = read_model(path_model3)
    print len(model1),len(model2),len(model3)
    # print sum(count_1)
    # print sum(count_2)
    # print sum(count_3)
    property_list = fun_property_set(path_property)
    if "好评率" in property_list:
        print "propery_list:ok"
    sentiment_list = fun_emotion_set(path_sentiment)
    if "齐全" in sentiment_list:
        print "sentiment:ok"
    degree_list = fun_degree_set(path_degree)
    if "非常" in degree_list:
        print "degree_list:ok"
    corpus = read_corpus(path_corpus)
    patten_1 = []
    patten_2 = []
    patten_3 = []
    jieguo_count = 0
    for line in corpus:
        parse_line = parse(line.strip())
        #print parse_line
        path_line_out = []
        for parse_sentence in parse_line:
            path_sentence_out = []
            juzi_pro,juzi_sen,juzi_deg,locations,location_sen,location_pro = select_patten(property_list,sentiment_list,degree_list,parse_sentence)
            juzi_pro = path_zishai(juzi_pro)
            juzi_sen = path_zishai(juzi_sen)
            juzi_deg = path_zishai(juzi_deg)
            # print 'juzi_pro:',juzi_pro
            # print 'juzi_sen:',juzi_sen
            # print 'juzi_deg:',juzi_deg
            path_all_in,path_sen_pro,path_sen_deg = guize_check(juzi_pro,juzi_sen,juzi_deg,location_sen)
            #print 'path_1:',path_all_in
            #print 'path_2',path_sen_pro
            #print 'path_3',path_sen_deg
            path_1_out = check_out(path_all_in,model1,parse_sentence,locations)
            #print 'path_1_out:',path_1_out
            path_2_out = check_out(path_sen_pro,model2,parse_sentence,locations)
            path_3_out = check_out(path_sen_deg,model3,parse_sentence,locations)
            if path_1_out and path_1_out not in path_sentence_out:
                path_sentence_out.extend(path_1_out)
            if path_2_out and path_2_out not in path_sentence_out:
                path_sentence_out.extend(path_2_out)
            #if path_3_out and path_3_out not in path_sentence_out:
            #    path_sentence_out.extend(path_3_out)
            if path_sentence_out:
                path_line_out.extend(path_sentence_out)
        if path_line_out:
            path_out.write(line+'\n')
            print line
            jieguo_count += 1
            print '----propery-----'
            #path_out.write('----propery-----'+'\n')
            for pro in location_pro:
                print parse_sentence[pro]['cont']
                #path_out.write(parse_sentence[pro]['cont']+'\t')
            print '----result------'
            path_out.write('\n')
            for hh in path_line_out:
                print  '\t'.join(hh)
                path_out.write('\t\t')
                path_out.write('\t'.join(hh)+'\n')
                #for hh_one in hh:
                #    print hh_one
            print '\n'
            path_out.write('\n')
    print 'jieguo_count:',jieguo_count
    path_out.write("call_back:"+str(jieguo_count))
    path_model1.close()
    path_model2.close()
    path_model3.close()
    path_property.close()
    path_sentiment.close()
    path_degree.close()
    path_out.close()
