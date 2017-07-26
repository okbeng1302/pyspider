#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-07-21 18:23:39
# Project: RCL_spider

from pyspider.libs.base_handler import *
import json
import time
import pymongo
import datetime
# 生成 13 位时间戳
def current_time():
    current_milli_time = lambda: int(round(time.time() * 1000))
    return current_milli_time()
headers = {
    ':authority':'secure.royalcaribbean.com',
    ':method':'GET',
    ':scheme':'https',
    'user-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    'x-requested-with':'XMLHttpRequest'
}
# 本地 mongodb 地址
MONGODB_IP = 'localhost'
MONGODB_PORT = 27017

class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=2 * 60)
    def on_start(self):
        self.crawl('https://secure.royalcaribbean.com/cruises',timeout=300,connect_timeout=100, callback=self.index_page,validate_cert=False)

    @config(age=1 * 60)
    def index_page(self, response):
        print response.url
        # 旅程 div
        curises_divs = response.doc('#search-results > div[class="row search-results"]').items()
        for div in curises_divs:
            # print div
            # 行程名称
            travel_name = div('div[class="search-result-top"] > div[class="columns small-12 medium-7 search-details"] > h3 > a').text()
            print "行程名称",travel_name
            # 出发地
            leaving_from = div('div[class="search-result-top"] > div[class="columns small-12 medium-7 search-details"] > p > strong').text()
            print "出发地",leaving_from.replace("\n","").replace("\t","")
            # 船名
            labels = div('div[class="search-result-top"] > div[class="columns small-12 medium-7 search-details"] > p > label').items()
            for label in labels:
                if label('span > strong').text():
                    onboard = label('span > strong').text()
                    print "船名",onboard
            # 途径港口
            via_ports = []
            port_lis = div('div[class="search-result-top"] > div[class="columns small-12 medium-7 search-details"] > div[class="cruise-visits"] > ul > li').items()
            for li in port_lis:
                if li('strong').text():
                    via_ports.append(li('strong').text().replace(',',''))
            print "途径港口",via_ports
            # 最低价格
            lowest_price = div('div[class="columns small-5 medium-4 payment-box-col"] > .currency > div[class="priceDetailsDisplayed show-for-medium-up"] > span[class="cruise-price"]').text()
            if lowest_price == '':
                lowest_price = div('div[class="columns small-5 medium-4 payment-box-col"] > .currency > span[class="cruise-price"]').text()
            print "最低价格",lowest_price
            
            # 获取出发时间 和 房间信息
            base_url = 'https://secure.royalcaribbean.com'
            ajax_data = div('div[class="medium-12 large-12 small-12 columns search-result-footer"] > div > a').attr('data-ajaxpath')
            print '出发时间和房间详细信息',ajax_data
            # 获取 13 位时间戳
            thrtime = current_time()
            # 请求url
            req_url = base_url + ajax_data + '&_'+ str(thrtime)
            print req_url
            self.crawl(req_url,timeout=300,connect_timeout=100,callback=self.parse_detail,save={'travel_name':travel_name,'leaving_from':leaving_from,'onboard':onboard,'via_ports':via_ports,'lowest_price':lowest_price},validate_cert=False)
        # 翻页
        next_page = response.doc('#pagination > div[class="pagination-action"] > a[class="pagination next"]').attr('data-page')
        print "翻页页码",next_page
        if next_page:
            next_page_url = 'https://secure.royalcaribbean.com/cruises?currentPage='+next_page+'&action=update'
            print next_page_url
            self.crawl(next_page_url,timeout=300,connect_timeout=100,callback=self.index_page,validate_cert=False)
        else:
            print '翻页结束'
    @config(priority=3,age=1 * 60)       
    def parse_detail(self,response):
        print "访问",response.url
        # 行程名称
        travel_name = response.save['travel_name']
        # 出发地
        leaving_from = response.save['leaving_from']
        # 船名
        onboard = response.save['onboard']
        # 途径港口
        via_ports = response.save['via_ports']
        # 最低价格
        lowest_price = response.save['lowest_price']
        # 获取出发时间的房间信息
        datas = response.json['inlinePricing']['rows']
        for data in datas:
                        
            # 出发时间
            leave_time = data['dateLabel']
            print '出发时间',leave_time
            # 房间信息
            # 普通
            interior_price = data['priceItems'][0]['price']
            if interior_price == None:
                interior_price = data['priceItems'][0]['noPriceText']
            print 'interior房间价格',interior_price
            # 标准
            outside_price = data['priceItems'][1]['price']
            if outside_price == None:
                outside_price = data['priceItems'][1]['noPriceText']
            print 'outside房间价格',outside_price
            # 包厢
            balcony_price = data['priceItems'][2]['price']
            if balcony_price == None:
                balcony_price = data['priceItems'][2]['noPriceText']
            print 'balcony_price房间价格',balcony_price
            # 豪华包房
            deluxe_price = data['priceItems'][3]['price']
            if deluxe_price == None:
                deluxe_price = data['priceItems'][3]['noPriceText']
            print 'deluxe_price房间价格',deluxe_price
                     
            yield {
                'travel_name':travel_name,
                'leaving_from':leaving_from,
                'onboard':onboard,
                'via_ports':via_ports,
                'lowest_price':lowest_price,
                'leave_time':leave_time,
                'interior_price':interior_price,
                'outside_price':outside_price,
                'balcony_price':balcony_price,
                'deluxe_price':deluxe_price
            }
            
    def on_result(self,result):
        super(Handler, self).on_result(result)
        if not result:
            return 
        client = pymongo.MongoClient(MONGODB_IP,MONGODB_PORT)
        db = client.research
        rcl_trip_info = db.rcl_trip_info
        # 当前时间
        now = datetime.datetime.now() # 这是数组时间格式
        now_time = now.strftime('%Y-%m-%d %H:%M:%S')
        now_time = time.strptime(now_time, "%Y-%m-%d %H:%M:%S")
        y,m,d,h,mm,s = now_time[0:6]
        update_time = datetime.datetime(y,m,d,h,mm,s)
        trip = {}
        trip['travel_name'] = result['travel_name']
        trip['leaving_from'] = result['leaving_from']
        trip['onboard'] = result['onboard']
        trip['via_ports'] = result['via_ports']
        trip['update_time'] = update_time
        trip['leave_time'] = result['leave_time']
        trip['interior_price'] = result['interior_price']
        trip['outside_price'] = result['outside_price']
        trip['balcony_price'] = result['balcony_price']
        trip['deluxe_price'] = result['deluxe_price']
        trip['lowest_price'] = result['lowest_price']
        rcl_trip_info.insert(trip)
        
            
        
            
            
        

