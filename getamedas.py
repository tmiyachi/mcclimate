#!/usr/bin/env python
#coding:utf-8
import urllib2
from BeautifulSoup import BeautifulSoup

#-------------------------------------------------------------------------------
#観測開始からの毎年の値をデータを1列読んでリストに返す。
#必要な引数。(地点番号,読みたいデータの列番号,データの詳細)
#-------------------------------------------------------------------------------
def getannualy(spotnum, data, elm=""):
#set basic url

    #取得したいデータの基本URL
    url = "http://www.data.jma.go.jp/obd/stats/etrn/view/annually_s.php?&block_no=SPOT&year=YEAR&month=&day=&elm=ELM&view="           #毎年の値

    #set url
    url = url.replace("SPOT", str(spotnum))
    url = url.replace("ELM", elm)
    print url

    res = urllib2.urlopen(url)
    html = res.read()
    soup = BeautifulSoup(html)
    
    rec = []
    for tr in soup('tr', {'class':'mtx'}):
        #年の取得
        for a in tr('a'):
            year = a.string
           # print year
        
        i = 1
        for td in tr('td'):
            if i % 28 == data:
                if td.get('class').find('1t') != -1:
                    #以降観測データの不均一がある場合の処理。
                    pass
                var = td.string
                var = var.strip(" ]") #" )"の除去
                var = var.strip(" )") #" ]"の除去
                rec.append(var)
#                print var
            i = i + 1
    return rec

#-------------------------------------------------------------------------------
#観測開始からの月ごとの値をデータを1列読んでリストに返す。
#必要な引数。(地点番号,月,データの詳細)
#-------------------------------------------------------------------------------
def getmonthly3(spotnum, data, elm=""):
#set basic url

    #取得したいデータの基本URL
    url = "http://www.data.jma.go.jp/obd/stats/etrn/view/monthly_s3.php?&block_no=SPOT&year=&month=&day=&elm=ELM&view="           #観測開始から月ごとの値

    #set url
    url = url.replace("SPOT", str(spotnum))
    url = url.replace("ELM", elm)
    print url

    res = urllib2.urlopen(url)
    html = res.read()
    soup = BeautifulSoup(html)
    
    rec = []
    for tr in soup('tr', {'class':'mtx'}):
        #年の取得
        for th in tr('div'):
            year = th.string
            #print year
        
        i = 1
        for td in tr('td'):
            if i % 12 == data:
                if td.get('class').find('1t') != -1:
                    #以降観測データの不均一がある場合の処理。
                    pass
                var = td.string
                var = var.strip(" ]") #" )"の除去
                var = var.strip(" )") #" ]"の除去
                rec.append(var)
#                print var
            i = i + 1
    return rec
    
#-------------------------------------------------------------------------------
#月の日ごとの値をデータを1列読んでリストに返す。
#必要な引数。(地点番号,年,月,データの列)
#-------------------------------------------------------------------------------
def getdaily(spotnum, year, month, data, elm=""):
#set basic url

    #取得したいデータの基本URL
    url = "http://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php?&block_no=SPOT&year=YEAR&month=MONTH&day=DAY&elm=ELM&view="           #月ごとの値

    #set url
    url = url.replace("SPOT", str(spotnum))
    url = url.replace("YEAR", str(year))
    url = url.replace("MONTH", str(month))
    url = url.replace("ELM", elm)
    print url

    res = urllib2.urlopen(url)
    html = res.read()
    soup = BeautifulSoup(html)
    
    rec = []
    for tr in soup('tr', {'class':'mtx'}):
        i = 1
        for td in tr('td'):
            if i % 21 == data:
                if td.get('class').find('1t') != -1:
                    #以降観測データの不均一がある場合の処理。
                    pass
                var = td.string
                var = var.strip(" ]") #" )"の除去
                var = var.strip(" )") #" ]"の除去
                rec.append(var)
#                print var
            i = i + 1
    return rec



#--------------------------------------------------
#CSVに出力
#--------------------------------------------------
#rfile = open('titen.txt', 'r')
#csvw = csv.writer(open('temp.csv', 'w'), lineterminator='\n')
#for spot in csv.reader(rfile):
#    result = []
#    print spot[0]
#    result.append(spot[0])
#    rec = getdaily(spot[1].strip(), 2010, 8, 12)
#    result = result + rec
#    csvw.writerow(result)
#rfile.close()

