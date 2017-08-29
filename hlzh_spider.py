#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-08-25 10:27:22
# Project: hlzh_flight_data

from pyspider.libs.base_handler import *
import re
import pymongo
import datetime
import time
import requests
from datetime import timedelta


def format_time_dep(day,formattime):
    time_temp = time.strptime(day, "%Y-%m-%d")
    y,m,d = time_temp[0:3]
    time_temp = datetime.datetime(y,m,d)
    time_temp = datetime.datetime.strftime(time_temp,"%Y-%m-%d")
    formattime = time_temp + ' ' + formattime + ':00'
    return formattime

def format_time_arr(day,formattime):
    time_temp = time.strptime(day, "%Y-%m-%d")
    y,m,d = time_temp[0:3]
    pattern = ('(.*?):.*?')
    day_time = re.findall(pattern,formattime)[0]
    if '00' in day_time:
        time_temp = datetime.datetime(y,m,d+1)
    else:
        time_temp = datetime.datetime(y,m,d)
    time_temp = datetime.datetime.strftime(time_temp,"%Y-%m-%d")
    # print time_temp
    # ptime = formattime.split(' ')[1]
    formattime = time_temp + ' ' + formattime + ':00'
    return formattime
def local_time():
    local_time = time.strftime('%Y%m%d',time.localtime(time.time()))
    return local_time
# 获取前两天的时间
def get_lastdays():
	now = datetime.datetime.now() # 这是数组时间格式
	now_time = now.strftime('%Y-%m-%d')
	now_time = time.strptime(now_time, "%Y-%m-%d")
	y,m,d= now_time[0:3]
	#print y,m,d,h,mm,type(s)
	update_time = datetime.datetime(y,m,d)
	one_day = (update_time-timedelta(days=1))
	two_day = (update_time-timedelta(days=2))
	last_one_day = datetime.datetime.strftime(one_day,'%Y-%m-%d')
	last_two_day = datetime.datetime.strftime(two_day,'%Y-%m-%d')
	days = []
	days.append(last_one_day)
	days.append(last_two_day)
	return days
city_list = {
    "兰州中川":"LHW","重庆江北":"CKG","成都双流":"CTU","大连国际":"DLC","昆明长水":"KMG",
    "西安咸阳":"XIY","郑州新郑":"CGO","武汉天河":"WUH","贵阳龙洞堡":"KWE","哈尔滨太平":"HRB",
    "青岛流亭":"TAO","济南遥墙":"TNA","长沙黄花":"CSX","沈阳桃仙":"SHE","南宁吴圩":"NNG",
    "海口美兰":"HAK","三亚凤凰":"SYX","天津滨海":"TSN","广州白云":"CAN","上海浦东":"PVG",
    "深圳宝安":"SZX","福州长乐":"FOC","北京首都":"PEK","杭州萧山":"HGH","南京禄口":"NKG",
    "上海虹桥":"SHA","厦门高崎":"XMN","西双版纳嘎洒":"JHG","西宁曹家堡":"XNN","丽江三义":"LJG",
    "银川河东":"INC","拉萨贡嘎":"LXA","南昌昌北":"KHN","桂林两江":"KWL","烟台蓬莱":"YNT",
    "北京南苑":"NAY","太原武宿":"TYN","揭阳潮汕":"SWA","长春龙嘉":"CGQ","呼和浩特白塔":"HET",
    "合肥新桥":"HFE","温州龙湾":"WNZ","石家庄正定":"SJW","宁波栎社":"NGB","泉州晋江":"JJN",
    "绵阳南郊":"MIG","珠海金湾":"ZUH","无锡硕放":"WUX","南京禄口":"NKG","广州白云":"CAN",
    "杭州萧山":"HGH","上海浦东":"PVG","温州龙湾":"WNZ","中国台湾高雄":"KHH","中国西宁曹家堡":"XNN",
    "中国台湾台北松山国际":"TSA","中国乌鲁木齐地窝堡":"URC","中国台湾马公":"MZG",
}

headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    'Host':'www.umetrip.com',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
}
# 数据库连接
MONGODB_IP = 'localhost'
MONGODB_PORT = 27017

class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=12 * 60)
    def on_start(self):
        days = get_lastdays()
        for city_name_from in city_list:
            # print city_name_one,city_list[city_name_one]
            for city_name_to in city_list:
                if city_name_from == city_name_to:
                    continue
                else:                    
                    for day in days:
                        flight_url = 'http://www.umetrip.com/mskyweb/fs/fa.do?dep=%s&arr=%s&date=%s&channel=' % (city_list[city_name_from],city_list[city_name_to],day)
                        self.crawl(flight_url,fetch_type='js',headers=headers, callback=self.index_page,save={'day':day,'ACityName':city_name_to,'DCityName':city_name_from})

    @config(age=60 * 60)
    def index_page(self, response):
        
        print response.url
        day = response.save['day']
        if '共有0个结果' in response.doc('div[class="list_com"] > div.tit > h1 > span').text().encode('utf-8'):
            print "无航班信息"
        else:
            city_temp = response.doc('div[class="list_com"] > div.tit > h1').text().replace('\t','').replace('\n','')
            print city_temp
            loc_temp = city_temp.find('-')
            loc_tmp = city_temp.find('（'.decode('utf-8'))
            dep_place = city_temp[:loc_temp]
            # 出发城市
            DCityName = dep_place.split(' ')[0]
            # 出发机场
            DAirportName = dep_place.split(' ')[1]
            print DCityName,DAirportName
            arr_place = city_temp[loc_temp+3:loc_tmp-1]
            # 到达城市
            ACityName = arr_place.split(' ')[0]
            # 到达机场
            AAirportName = arr_place.split(' ')[1]
            print ACityName,AAirportName
            
            flight_list = response.doc('#list > li').items()
            for flight in flight_list:

                span_list = flight('div > span').items()
                index = 0
                for span in span_list:
                    if index == 0:
                        # 航空公司名称
                        FlightCompany = span('a').text().split(" ")[1]
                        # 航班号
                        FlightNo = span('a').text().split(" ")[0]
                        print FlightCompany,FlightNo
                    # 计划起飞时间
                    if index == 1:
                        PlanDDateTime = format_time_dep(day,span.text())
                        print "计划起飞时间",PlanDDateTime
                    # 实际起飞时间
                    if index == 2:
                        if ':'in span.text().encode('utf-8'):
                            ActDDateTime = format_time_dep(day,span.text())
                        else:
                            ActDDateTime = None
                        print "实际起飞时间",ActDDateTime
                    # 计划达到时间
                    if index == 4:
                        PlanADateTime = format_time_arr(day,span.text())
                        print "计划到达时间",PlanADateTime
                    if index == 5:
                        if ':'in span.text().encode('utf-8'):
                            ActADateTime = format_time_arr(day,span.text())
                        else:
                            ActADateTime = None
                        print "实际到达时间",ActADateTime
                    # 航班状态
                    if index == 6:
                        Status = span.text()
                        print "航班状态",Status

                    index = index + 1
                    
                yield {
                    "DCityName":DCityName,
                    "DAirportName":DAirportName,
                    "ACityName":ACityName,
                    "AAirportName":AAirportName,
                    "FlightCompany":FlightCompany,
                    "FlightNo":FlightNo,
                    "PlanDDateTime":PlanDDateTime,
                    "ActDDateTime":ActDDateTime,
                    "PlanADateTime":PlanADateTime,
                    "ActADateTime":ActADateTime,
                    "Status":Status,
                    "air_url":response.url
                }
    
    def on_result(self,result):
        super(Handler, self).on_result(result)
        if not result:
            return
        client = pymongo.MongoClient(MONGODB_IP,MONGODB_PORT)
        db = client.research
        hlzh_airport_data = db.hlzh_airport_data
        airport_info = {}
        airport_info['ACityName'] = result['ACityName']
        airport_info['AAirportName'] = result['AAirportName']
        airport_info['DCityName'] = result['DCityName']
        airport_info['DAirportName'] = result['DAirportName']
        airport_info['FlightCompany'] = result['FlightCompany']
        airport_info['FlightNo'] = result['FlightNo']
        # 实际出发时间
        if result['ActDDateTime'] == None:
            ActDDateTime = None
        else:
            ActDDateTime = datetime.datetime.strptime(str(result['ActDDateTime'].encode('utf-8')),"%Y-%m-%d %H:%M:%S")   
        airport_info['ActDDateTime'] = ActDDateTime
        # 实际到达时间
        if result['ActADateTime'] == None:
            ActADateTime = None
        else:
            ActADateTime = datetime.datetime.strptime(str(result['ActADateTime'].encode('utf-8')),"%Y-%m-%d %H:%M:%S")   
        airport_info['ActADateTime'] = ActADateTime
        # 计划到达时间
        if '0001-01-01 00:00:00' in str(result['PlanADateTime'].encode('utf-8')):
            PlanADateTime = None
        else:
            PlanADateTime = datetime.datetime.strptime(str(result['PlanADateTime'].encode('utf-8')),"%Y-%m-%d %H:%M:%S")  
        airport_info['PlanADateTime'] = PlanADateTime
        # 计划出发时间
        if '0001-01-01 00:00:00' in str(result['PlanDDateTime'].encode('utf-8')):
            PlanDDateTime = None
        else:
            PlanDDateTime = datetime.datetime.strptime(str(result['PlanDDateTime'].encode('utf-8')),"%Y-%m-%d %H:%M:%S")
        airport_info['PlanDDateTime'] = PlanDDateTime
        airport_info['Status'] = result['Status']
        
        # 当前时间
        now = datetime.datetime.now() # 这是数组时间格式
        now_time = now.strftime('%Y-%m-%d %H:%M:%S')
        now_time = time.strptime(now_time, "%Y-%m-%d %H:%M:%S")
        y,m,d,h,mm,s = now_time[0:6]
        #print y,m,d,h,mm,type(s)
        update_time = datetime.datetime(y,m,d,h,mm,s)
        airport_info['update_time'] = update_time
        airport_info['air_url'] = result['air_url']
        if hlzh_airport_data.find_one({"FlightNo":result['FlightNo'],"PlanADateTime":PlanADateTime}):
            fcz_airport_data.update({"FlightNo":result['FlightNo'],"PlanADateTime":PlanADateTime},{'$set':{
                'ACityName':result['ACityName'],
                'AAirportName':result['AAirportName'],
                'DCityName':result['DCityName'],
                'DAirportName':result['DAirportName'],
                'FlightCompany':result['FlightCompany'],
                'FlightNo':result['FlightNo'],
                'PlanADateTime':PlanADateTime,
                'PlanDDateTime':PlanDDateTime,
                'Status':result['Status'],
                'air_url':result['air_url'],
                'ActADateTime':ActADateTime,
                'ActDDateTime':ActDDateTime,
                'update_time':update_time
            }})
        else:
            hlzh_airport_data.insert(airport_info)
