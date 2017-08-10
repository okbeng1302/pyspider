#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-08-08 16:31:02
# Project: xiecheng_data

from pyspider.libs.base_handler import *
import pymongo
import datetime
import time
import requests
from datetime import timedelta
import re
city_list = {
    "上海":"SHA","北京":"BJS","香港":"HKG","广州":"CAN","杭州":"HGH",
    "厦门":"XMN","南京":"NKG","澳门":"MFM","成都":"CTU","青岛":"TAO",
    "台北":"TPE","福州":"FOC","天津":"TSN","深圳":"SZX","大连":"DLC",
    "沈阳":"SHE","昆明":"KMG","武汉":"WUH","宁波":"NGB","无锡":"WUX",
    "晋江":"JJN","重庆":"CKG","三亚":"SYX","西安":"SIA"
}
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
	last_one_day = datetime.datetime.strftime(one_day,'%Y%m%d')
	last_two_day = datetime.datetime.strftime(two_day,'%Y%m%d')
	days = []
	days.append(last_one_day)
	days.append(last_two_day)
	return days
# mongodb 数据库连接
MONGODB_IP = 'localhost'
MONGODB_PORT = 27017

headers = {
    'Accept':'*/*',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Cache-Control':'max-age=0',
    'Content-Type':'application/x-www-form-urlencoded; charset=utf-8',
    'If-Modified-Since':'Thu, 01 Jan 1970 00:00:00 GMT',
    'Host':'flights.ctrip.com',
    'Proxy-Connection':'keep-alive',
    'Referer':'http://flights.ctrip.com/actualtime/SHA-BJS/t20170809',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
}
class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        days = get_lastdays()
        for city_name_from in city_list:
            # print city_name_one,city_list[city_name_one]
            for city_name_to in city_list:
                if city_name_from == city_name_to:
                    continue
                else:                    
                    for day in days:                        
                        referer = 'http://flights.ctrip.com/actualtime/%s-%s/t%s' % (city_list[city_name_from],city_list[city_name_to],day)
                        headers['Referer'] = referer
                        base_url = 'http://flights.ctrip.com/Process/FlightStatus/FindByCityWithJson?from=%s&to=%s&date=%s&searchKey=' % (city_list[city_name_from],city_list[city_name_to],day)
                        self.crawl(base_url, callback=self.index_page,headers=headers)

    @config(age=60 * 60)
    def index_page(self, response):
        list = response.json['List']
        for trip in list:                      
            # 到达城市名称
            if 'ACityName'in trip:                
                ACityName = trip['ACityName']
            # 到达机场名称
            if 'AAirportName' in trip:
                AAirportName = trip['AAirportName']
            # 到达机场编号
            if 'AAirportCode' in trip:
                AAirportCode = trip['AAirportCode']
            # 到达城市编号
            if 'ACityCode' in trip:
                ACityCode = trip['ACityCode']
            # 到达机场出口
            if 'ATerminal' in trip:
                ATerminal = trip['ATerminal']
            # 出发城市名称
            if 'DCityName' in trip:
                DCityName = trip['DCityName']
            # 出发机场名称
            if 'DAirportName' in trip:
                DAirportName = trip['DAirportName']
            # 出发机场编号
            if 'DAirportCode' in trip:
                DAirportCode = trip['DAirportCode']
            # 出发城市编号
            if 'DCityCode' in trip:
                DCityCode = trip['DCityCode']
            # 出发机场出口
            if 'DTerminal' in trip:
                DTerminal = trip['DTerminal']
            # 实际到达时间
            if 'ActADateTime' in trip:
                ActADateTime = trip['ActADateTime']
            # 实际出发时间
            if 'ActDDateTime' in trip:
                ActDDateTime = trip['ActDDateTime']
            # 延误状态时间分析
            if 'Analysis' in trip:
                Analysis = trip['Analysis']
            # 预计到达时间
            if 'ExpADateTime' in trip:
                ExpADateTime = trip['ExpADateTime']
            # 预计出发时间
            if 'ExpDDateTime' in trip:
                ExpDDateTime = trip['ExpDDateTime']
            # 航空公司名称
            if 'FlightCompany' in trip:
                FlightCompany = trip['FlightCompany']
            # 飞行距离
            if 'FlightDuration' in trip:
                FlightDuration = trip['FlightDuration']
            # 航班号
            if 'FlightNo' in trip:
                FlightNo = trip['FlightNo']
            # 按时率
            if 'OnTimeRate' in trip:
                OnTimeRate = trip['OnTimeRate']
            # 计划到达时间
            if 'PlanADateTime' in trip:
                PlanADateTime = trip['PlanADateTime']
            # 计划出发时间
            if 'PlanDDateTime' in trip:
                PlanDDateTime = trip['PlanDDateTime']
            # 航班状态
            if 'Status' in trip:
                Status = trip['Status']
            # 航班信息更新时间
            if 'UpdateTime' in trip:
                UpdateTime = trip['UpdateTime']
            yield {
                'ACityName':ACityName,
                'AAirportName':AAirportName,
                'AAirportCode':AAirportCode,
                'ACityCode':ACityCode,
                'ATerminal':ATerminal,
                'DCityName':DCityName,
                'DAirportName':DAirportName,
                'DAirportCode':DAirportCode,
                'DCityCode':DCityCode,
                'DTerminal':DTerminal,
                'ActADateTime':ActADateTime,
                'ActDDateTime':ActDDateTime,
                'Analysis':Analysis,
                'ExpADateTime':ExpADateTime,
                'ExpDDateTime':ExpDDateTime,
                'FlightCompany':FlightCompany,
                'FlightDuration':FlightDuration,
                'FlightNo':FlightNo,
                'OnTimeRate':OnTimeRate,
                'PlanADateTime':PlanADateTime,
                'PlanDDateTime':PlanDDateTime,
                'Status':Status,
                'UpdateTime':UpdateTime,
                'air_url':response.url
            }
                

    def on_result(self,result):
        super(Handler, self).on_result(result)
        if not result:
            return
        client = pymongo.MongoClient(MONGODB_IP,MONGODB_PORT)
        db = client.research
        xc_airport_data = db.xc_airport_data
        airport_info = {}
        airport_info['ACityName'] = result['ACityName']
        airport_info['AAirportName'] = result['AAirportName']
        airport_info['AAirportCode'] = result['AAirportCode']
        airport_info['ACityCode'] = result['ACityCode']
        airport_info['ATerminal'] = result['ATerminal']
        airport_info['DCityName'] = result['DCityName']
        airport_info['DAirportName'] = result['DAirportName']
        airport_info['DAirportCode'] = result['DAirportCode']
        airport_info['DCityCode'] = result['DCityCode']
        airport_info['DTerminal'] = result['DTerminal']
        # 实际到达时间
        if '0001-01-01 00:00:00' in str(result['ActADateTime'].encode('utf-8')):
            ActADateTime = None
        else:
            ActADateTime = datetime.datetime.strptime(str(result['ActADateTime'].encode('utf-8')),"%Y-%m-%d %H:%M:%S")
        airport_info['ActADateTime'] = ActADateTime
        # 实际出发时间
        if '0001-01-01 00:00:00' in str(result['ActDDateTime'].encode('utf-8')):
            ActDDateTime = None
        else:
            ActDDateTime = datetime.datetime.strptime(str(result['ActDDateTime'].encode('utf-8')),"%Y-%m-%d %H:%M:%S")
        airport_info['ActDDateTime'] = ActDDateTime
        airport_info['Analysis'] = result['Analysis']
        # 预计到达时间
        if '0001-01-01 00:00:00' in str(result['ExpADateTime'].encode('utf-8')):
            ExpADateTime = None
        else:
            ExpADateTime = datetime.datetime.strptime(str(result['ExpADateTime'].encode('utf-8')),"%Y-%m-%d %H:%M:%S")                                           
        airport_info['ExpADateTime'] = ExpADateTime
        # 预计出发时间
        if '0001-01-01 00:00:00' in str(result['ExpDDateTime'].encode('utf-8')):
            ExpDDateTime = None
        else:
            ExpDDateTime = datetime.datetime.strptime(str(result['ExpDDateTime'].encode('utf-8')),"%Y-%m-%d %H:%M:%S")   
        airport_info['ExpDDateTime'] = ExpDDateTime
        airport_info['FlightCompany'] = result['FlightCompany']
        airport_info['FlightDuration'] = result['FlightDuration']
        airport_info['FlightNo'] = result['FlightNo']
        airport_info['OnTimeRate'] = result['OnTimeRate']
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
        if '0001-01-01 00:00:00' in str(result['UpdateTime'].encode('utf-8')):
            UpdateTime = None
        else:
            UpdateTime = datetime.datetime.strptime(str(result['UpdateTime'].encode('utf-8')),"%Y-%m-%d %H:%M:%S")
        airport_info['UpdateTime'] = UpdateTime
        
        # 当前时间
        now = datetime.datetime.now() # 这是数组时间格式
        now_time = now.strftime('%Y-%m-%d %H:%M:%S')
        now_time = time.strptime(now_time, "%Y-%m-%d %H:%M:%S")
        y,m,d,h,mm,s = now_time[0:6]
        #print y,m,d,h,mm,type(s)
        update_time = datetime.datetime(y,m,d,h,mm,s)
        airport_info['update_time'] = update_time
        airport_info['air_url'] = result['air_url']
        if xc_airport_data.find_one({"FlightNo":result['FlightNo'],"PlanADateTime":PlanADateTime}):
            xc_airport_data.update({"FlightNo":result['FlightNo'],"PlanADateTime":PlanADateTime},{'$set':{
                'ACityName':result['ACityName'],
                'AAirportName':result['AAirportName'],
                'AAirportCode':result['AAirportCode'],
                'ACityCode':result['ACityCode'],
                'ATerminal':result['ATerminal'],
                'DCityName':result['DCityName'],
                'DAirportName':result['DAirportName'],
                'DAirportCode':result['DAirportCode'],
                'DCityCode':result['DCityCode'],
                'DTerminal':result['DTerminal'],
                'ActADateTime':ActADateTime,
                'ActDDateTime':ActDDateTime,
                'Analysis':result['Analysis'],
                'ExpADateTime':ExpADateTime,
                'ExpDDateTime':ExpDDateTime,
                'FlightCompany':result['FlightCompany'],
                'FlightDuration':result['FlightDuration'],
                'FlightNo':result['FlightNo'],
                'OnTimeRate':result['OnTimeRate'],
                'PlanADateTime':PlanADateTime,
                'PlanDDateTime':PlanDDateTime,
                'Status':result['Status'],
                'UpdateTime':UpdateTime,
                'air_url':result['air_url'],
                'update_time':update_time
            }})
        else:
            xc_airport_data.insert(airport_info)
        
        
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
                