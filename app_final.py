#!/usr/bin/python
#-*- coding: utf-8 -*-

import math
from flask import Flask, request
from flask import render_template 
from elasticsearch import Elasticsearch
import re
import requests
import time
from bs4 import BeautifulSoup
import numpy

app = Flask(__name__)
es_host = "127.0.0.1"
es_port = "9200"
word_freq = {} #전체 단어, 빈도수 dict
idf = {}  #전체 단어의 idf dict
num = 0
def crawling(url):
	e = {
		'url':url,
		'words':[],
		'freq':[],
		'df':[],
		'tf':[],
		'idf':[],
		'tf-idf':{},
		'top10words':[],
		'cos-similarity':{},
		'top3urls':[],
		'percentage':[],
		'time':0,
		'total':0,
		'result':"",
		'overlap':0,
	}
	try:
		url = requests.get(url)
		html = BeautifulSoup(url.content, 'html.parser')
		sentences = html.find_all('p')
		for i in range(0, len(sentences)):
			word_list = re.sub(u'[^\w\s]','',sentences[i].get_text()) #특수문자 제거
			word_list = re.sub(r'\b[0-9]+\b\s*','',word_list)
			for word in word_list.split():
				if word.lower() in e['words']:
					index = e['words'].index(word.lower())
					freq = e['freq'][index]
					e['freq'][index]+=1
					e['words'].remove(word.lower())
					e['freq'].sort(reverse=True)
					e['words'].insert(e['freq'].index(freq+1),word.lower())
				else:
					e['words'].append(word.lower())
					e['freq'].append(1)
	except:
		return e	
	return e;

def words_freq_list(e):  #전체 word_freq list , idf생성 함수
	for i in range(0, len(e['words'])):
		word = e['words'][i]
		if word not in word_freq.keys():
			word_freq[word] = e['freq'][i]
			idf[word] = 1
		else:
			word_freq[word] += e['freq'][i]
			idf[word] += 1
			
def tf(e):
	sum = 0
	for i in range(0, len(e["words"])):
		sum += (e["freq"][i])
	for i in range(0, len(e["words"])):
		e['tf'].append(round((e["freq"][i])/sum, 4))
	return e

def idf_e(e, n):
	for i in e['words']:
		e['idf'].append(idf.get(i))
	return e
		 
def tf_idf(e): # tf-idf 구하고 내림차순 정렬
	temp = {}
	for i in e['words']:
		index = e['words'].index(i)
		temp[i] = round(e['tf'][index] * e['idf'][index], 4)
	e['tf-idf'].update(sorted(temp.items(), key = (lambda x : x[1]), reverse = True))
	return e
	

@app.route('/one_output', methods=["POST"])
def name1_check():
	if request.method=="POST":
		url = str(request.form['name'])
		es = Elasticsearch([{'host':es_host, 'port':es_port}], timeout = 30)
		start = time.time()  # 시작 시간 저장
		e = crawling(url)
		if len(e['words']) == 0:
			e['result'] = '크롤링 실패'
			return render_template('one_output.html', e = e)
		e['time'] = round(time.time()-start,4)
		e['total'] = len(e["words"])
		e['result'] = '크롤링 성공'
		global num
		res = es.index(index = num, id = num, body = e)
		num += 1
			
		return render_template('one_output.html', e = e)


@app.route('/multi_output', methods=["POST"])
def name2_check():
	if request.method=="POST":
		txtfile = request.files['profile'].read()
		# urls=[]
		txtfile = ",".join(txtfile.decode("utf-8").split()).split(",")
		urls = [x for x in txtfile if x.strip()]
		
		#for x in txtfile.decode("utf-8").split():
		#	urls.append(x.rstrip())
	
		es = Elasticsearch([{'host':es_host, 'port':es_port}], timeout = 30)
		global num
		res = []
		fail_list = []
		n = 0
		valid = []
		for url in urls:
			start = time.time()  # 시작 시간 저장
			e = crawling(url)
			if len(e['words']) == 0:
				e['result'] = "url이 유효하지 않습니다"
				fail_list.append(e)
				continue
			e['time'] = round(time.time()-start,4)
			e['total'] = len(e['words'])
			words_freq_list(e)
			e = tf(e)
			e['result'] = "크롤링 성공"
			valid.append(e['url'])
			
			if valid.index(e['url']) != n:
				e['overlap'] = 1
				res[valid.index(e['url'])]['overlap'] = 1
			res.append(e)
			n += 1
		for i in idf.keys():  #전체 단어의 idf값 구하기
			idf[i] = round(math.log10(len(urls)/idf[i]), 4)
		
		for i in res: 	#df(벡터) 구하기, tf-idf구하기
			i = idf_e(i, len(res))
			i = tf_idf(i)
			for j in word_freq:
				if j not in i['words']:
					i['df'].append(0)
				else:
					i['df'].append(i['freq'][i['words'].index(j)])
		for i in range(0, len(res)):
			temp_similarity = {}
			for j in range(0, len(res)): #url별 cos-similarity값 구하고 내림차순 정렬
				if j != i:
					similarity = round(numpy.dot(res[i]['df'], res[j]['df'])/(numpy.linalg.norm(res[i]['df'])*numpy.linalg.norm(res[j]['df']))*100, 2)
					temp_similarity[res[j]['url']] = similarity
			res[i]['cos-similarity'].update(sorted(temp_similarity.items(), key = (lambda x : x[1]), reverse = True))
			
		for i in range(0, len(res)):
			wordlist = res[i]['tf-idf'].keys()
			for j in wordlist:
				if len(res[i]['top10words']) == 10:
					break
				res[i]['top10words'].append(j)
			urllist = res[i]['cos-similarity'].keys()
			percentlist = res[i]['cos-similarity'].values()
			for j in urllist:
				res[i]['top3urls'].append(j)
			for j in percentlist:
				res[i]['percentage'].append(j)
			
		for i in range(0, len(res)): #elasticsearch에 저장
			if len(res[i]['words']) != 0:
				e = {
		'url':res[i]['url'],
		'words':res[i]['words'],
		'freq':res[i]['freq'],
		'top10words':res[i]['top10words'],
		'top3urls':res[i]['top3urls'],
		'percentage':res[i]['percentage'],
		'time':res[i]['time'],
		'total':res[i]['total'],
		'result':res[i]['result'],
		'overlap':res[i]['overlap'],
	}
				es.index(index=num, id = 1, body=e)
				num += 1
				
		return render_template('multi_output.html', res=res, n = n, fail = fail_list)



@app.route('/', methods=['GET'])
def hello_hw():
	return render_template('default.html')

if __name__== '__main__':
	app.run()
