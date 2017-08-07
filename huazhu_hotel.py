#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-08-07 11:21:59
# Project: huazhu_hotel

from pyspider.libs.base_handler import *
import re
import pymongo
import datetime
import time
from datetime import timedelta


# 生成 13 位时间戳
def current_time():
    current_milli_time = lambda: int(round(time.time() * 1000))
    return current_milli_time()


def local_time():
    local_time = time.strftime('%Y-%m-%d', time.localtime())
    return local_time


def next_day():
    now = datetime.datetime.now()  # 这是数组时间格式
    now_time = now.strftime('%Y-%m-%d')
    now_time = time.strptime(now_time, "%Y-%m-%d")
    y, m, d = now_time[0:3]
    update_time = datetime.datetime(y, m, d)
    update_time += timedelta(days=1)
    now_time = update_time.strftime('%Y-%m-%d')
    return now_time


headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Connection': 'keep-alive',
    'Host': 'hotels.huazhu.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}


class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://hotels.huazhu.com/', fetch_type='js', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        print '访问', response.url
        # 获取__v_t
        pattern = (r"__v_t = \'(.*?)\';<\/script>")
        __v_t = re.findall(pattern, response.text)[0]
        headers['__v_t'] = __v_t
        req_url = 'http://hotels.huazhu.com/Basic/NativeCityOverView?_=' + str(current_time())
        self.crawl(req_url, callback=self.parse_city, headers=headers, save={'headers': headers})

    # 获取城市名称和城市ID
    def parse_city(self, response):
        print '访问', response.url
        headers = response.save['headers']
        city_list = response.json['CityList']
        for city in city_list:
            # 城市名称 
            city_name = city['CityName']
            # 城市ID
            city_id = city['CityID']
            print city_name, city_id
            city_href = 'http://hotels.huazhu.com/Search/HotelList?CityID=' + city_id + '&CheckInDate=' + local_time() + '&CheckOutDate=' + next_day() + '&HotelStyleList=4&PageIndex=1&_=' + str(
                current_time())
            self.crawl(city_href, callback=self.parse_hotel, headers=headers,
                       save={'city_name': city_name, 'city_id': city_id, 'PageIndex': 2, 'headers': headers})

    # 获取酒店ID 和酒店名称
    def parse_hotel(self, response):
        print '访问', response.url
        PageIndex = response.save['PageIndex']
        city_name = response.save['city_name']
        city_id = response.save['city_id']
        headers = response.save['headers']
        # 酒店列表
        hotellist = response.json['HotelList']
        # 翻页
        if len(hotellist) == 0:
            print "翻页结束"
        else:
            req_url = 'http://hotels.huazhu.com/Search/HotelList?CityID=' + str(
                city_id) + '&CheckInDate=' + local_time() + '&CheckOutDate=' + next_day() + '&HotelStyleList=4&PageIndex=' + str(
                PageIndex) + '&_=' + str(current_time())
            self.crawl(req_url, callback=self.parse_hotel, headers=headers,
                       save={'city_name': city_name, 'city_id': city_id, 'headers': headers,
                             'PageIndex': PageIndex + 1})

        for hotel in hotellist:
            # 酒店名称
            hotel_name = hotel['HotelName']
            # 酒店地址
            hotel_space = hotel['HotelAddress']
            # 酒店评分
            hotel_score = hotel['HotelScore']
            # 酒店 id
            hotel_id = hotel['HotelID']
            print hotel_name, hotel_id
            hotel_href = 'http://hotels.huazhu.com/hotel/detail?HotelId=' + hotel_id + '&CheckInDate=' + local_time() + '&CheckOutDate=' + next_day()
            self.crawl(hotel_href, fetch_type='js', callback=self.parse_hotel_detail, headers=headers,
                       save={'city_name': city_name, 'city_id': city_id, 'headers': headers, 'hotel_name': hotel_name,
                             'hotel_space': hotel_space, 'hotel_score': hotel_score, 'hotel_id': hotel_id})

    def parse_hotel_detail(self, response):
        print '访问', response.url
        room_list = response.doc('div.roomtype > table > tbody > tr').items()
        '''
        flag = True
        # 房间类型
        room_type = ''
        # 会员类型
        price_type = ''
        # 床型
        bed_type = ''
        # 门市价
        now_price = ''
        # 房价（会员价）
        room_price = ''
        '''
        for room in room_list:
            # 房型
            if room('tr[class="roominfo Ldn"]'):
                pass
            else:

                room_types = room('tr[class="room first"] > td.roomtd > div > h3').text()
                if room_types != '':
                    room_type = room_types
                else:
                    room_type = room_type
                print room_type
                if '会员价' in str(room('tr').text().encode('utf-8')):
                    if str(room('td')[1].text.encode('utf-8')) == '会员价':
                        price_type = '会员价'
                        bed_type = str(room('td')[2].text.encode('utf-8'))
                        print bed_type
                        # 房间状态
                        room_status = room('td[class="bookbox"] > a[class="Cbtn orderbtn gray"]').text()
                        if room_status == '':
                            room_status = room('td[class="bookbox"] > a[class="Cbtn orderbtn"]').text()
                        print room_status
                        room_condition = room('td[class="bookbox"] > span[class="remain remain1 Lfll"]').text()
                        if room_condition == '':
                            room_condition = None
                        print room_condition
                    if str(room('td')[0].text.encode('utf-8')) == '会员价':
                        price_type = '会员价'
                        bed_type = str(room('td')[1].text.encode('utf-8'))
                        print bed_type
                        # 房间状态
                        room_status = room('td[class="bookbox"] > a[class="Cbtn orderbtn gray"]').text()
                        if room_status == '':
                            room_status = room('td[class="bookbox"] > a[class="Cbtn orderbtn"]').text()
                        print room_status
                        room_condition = room('td[class="bookbox"] > span[class="remain remain1 Lfll"]').text()
                        if room_condition == '':
                            room_condition = None
                        print room_condition
                            

    def on_result(self, result):
        pass
