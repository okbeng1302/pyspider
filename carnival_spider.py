#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-07-25 16:58:45
# Project: Carnival_spider

from pyspider.libs.base_handler import *
import json
import time
import pymongo
#import datetime
from datetime import datetime, timedelta, tzinfo
# 本地 mongodb 地址
MONGODB_IP = 'localhost'
MONGODB_PORT = 27017

class FixedOffset(tzinfo):
    """offset_str: Fixed offset in str: e.g. '-0400'"""
    def __init__(self, offset_str):
        sign, hours, minutes = offset_str[0], offset_str[1:3], offset_str[3:]
        offset = (int(hours) * 60 + int(minutes)) * (-1 if sign == "-" else 1)
        self.__offset = timedelta(minutes=offset)
        # NOTE: the last part is to remind about deprecated POSIX GMT+h timezones
        # that have the opposite sign in the name;
        # the corresponding numeric value is not used e.g., no minutes
        '<%+03d%02d>%+d' % (int(hours), int(minutes), int(hours)*-1)
    def utcoffset(self, dt=None):
        return self.__offset
    def tzname(self, dt=None):
        return self.__name
    def dst(self, dt=None):
        return timedelta(0)
    def __repr__(self):
        return 'FixedOffset(%d)' % (self.utcoffset().total_seconds() / 60)

class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl(
            'https://www.carnival.com/cruisesearch/api/search?numAdults=2&pageNumber=1&pageSize=8&showBest=true&sort=fromprice&useSuggestions=true',
            timeout=300, connect_timeout=100, callback=self.index_page, validate_cert=False, save={'PageIndex': 1})

    @config(priority=5, age=12 * 60)
    def index_page(self, response):
        totalPageNumber = response.json['results']['lastPage']
        print totalPageNumber
        for i in range(1, totalPageNumber + 1):
            req_url = 'https://www.carnival.com/cruisesearch/api/search?numAdults=2&pageNumber=' + str(
                i) + '&pageSize=8&showBest=true&sort=fromprice&useSuggestions=true'
            self.crawl(req_url, callback=self.parse_detail, validate_cert=False)

    @config(priority=6, age=12 * 60)
    def parse_detail(self, response):
        print response.url

        travel_contents = response.json['results']['itineraries']
        for con in travel_contents:
            # 出发港口
            departurePortName = con['departurePortName']
            # print '出发港口',departurePortName
            # 目的地
            regionName = con['regionName']
            # print '目的地',regionName
            # 持续天数
            dur_days = con['dur']
            # print '持续天数',dur_days
            # 船名
            shipName = con['shipName']
            # print '船名',shipName
            # 途径港口
            portsToDisplay = con['portsToDisplay']
            # print '途径港口',portsToDisplay
            # 最低价格
            fromPrice = con['leadSailing']['fromPrice']
            # print '最低价格',fromPrice

            # print '所有日期',len(con['sailings'])

            for room in con['sailings']:
                # 出发时间
                departureDate = room['departureDate']
                # 到达时间
                arrivalDate = room['arrivalDate']
                # 房间信息
                # 普通
                interior_price = room['rooms']['interior']['price']
                # 海景
                oceanview_price = room['rooms']['oceanview']['price']
                # 包房
                balcony_price = room['rooms']['balcony']['price']
                # 豪华包房
                suite_price = room['rooms']['suite']['price']

                yield {
                    'departurePortName': departurePortName,
                    'regionName': regionName,
                    'dur_days': dur_days,
                    'shipName': shipName,
                    'portsToDisplay': portsToDisplay,
                    'fromPrice': fromPrice,
                    'departureDate': departureDate,
                    'arrivalDate': arrivalDate,
                    'interior_price': interior_price,
                    'oceanview_price': oceanview_price,
                    'balcony_price': balcony_price,
                    'suite_price': suite_price
                }


    def on_result(self, result):
        super(Handler, self).on_result(result)
        if not result:
            return
        client = pymongo.MongoClient(MONGODB_IP, MONGODB_PORT)
        db = client.research
        carnival_trip_info = db.carnival_trip_info
        # 当前时间
        now = datetime.now()  # 这是数组时间格式
        now_time = now.strftime('%Y-%m-%d %H:%M:%S')
        print now_time,type(now_time)
        now_time = time.strptime(now_time, "%Y-%m-%d %H:%M:%S")
        y, m, d, h, mm, s = now_time[0:6]
        update_time = datetime(y, m, d, h, mm, s)
        trip = {}
        trip['departurePortName'] = result['departurePortName']
        trip['regionName'] = result['regionName']
        trip['dur_days'] = result['dur_days']
        trip['shipName'] = result['shipName']
        trip['portsToDisplay'] = result['portsToDisplay']
        trip['fromPrice'] = result['fromPrice']
        trip['interior_price'] = result['interior_price']
        trip['oceanview_price'] = result['oceanview_price']
        trip['balcony_price'] = result['balcony_price']
        trip['suite_price'] = result['suite_price']
        trip['update_time'] = update_time
        # 出发时间
        departureDate = str(result['departureDate']).replace('Z','').replace('T',' ')[:-4]
        departureDate = time.strptime(departureDate, "%Y-%m-%d %H:%M:%S")
        y, m, d, h, mm, s = now_time[0:6]
        departureDate = datetime(y, m, d, h, mm, s)
        # print '出发时间',type(departureDate)
        trip['departureDate'] = departureDate
        # 到达时间
        arrivalDate = str(result['arrivalDate']).replace('Z','').replace('T',' ')[:-4]
        arrivalDate = time.strptime(arrivalDate, "%Y-%m-%d %H:%M:%S")
        y, m, d, h, mm, s = now_time[0:6]
        arrivalDate = datetime(y, m, d, h, mm, s)
        # print '到达时间',arrivalDate
        trip['arrivalDate'] = arrivalDate
        carnival_trip_info.insert(trip)
