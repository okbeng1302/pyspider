#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-07-17 14:06:43
# Project: Xdf_Spider_v1
import json 
from pyspider.libs.base_handler import *
import pymongo
import datetime
import re
import time
import urllib
from urllib import unquote

DB_IP = 'localhost'
DB_PORT = 27017

class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://souke.xdf.cn', callback=self.index_page)

    @config(priority=5,age=12 * 60)
    def index_page(self, response):
        print '访问',response.url
        base_url = "http://souke.xdf.cn/Category/"
   
        # 城市列表
        ul_cities = response.doc('.area_school >ul').items()
        for ul in ul_cities:
            for a_href in ul('a').items():
               # 城市名字
               city_name = a_href.text()
               # 城市 cid
               cid = a_href.attr.cid
               # print city_name,cid
               self.crawl(base_url+cid+'.html',callback=self.parse_city_category)
    @config(priority=6,age=12 * 60) 
    def parse_city_category(self,response):
        print '访问',response.url
        
        # 城市类别 div
        category_divs = response.doc('#divMain > div[class="box4 fix mb10"]').items()
        for cd in category_divs:
            category_dls = cd('div[class="class_all fix"] > div > div > dl').items()
            # 大类
            category_name = cd('div[class="class_all fix"] > div > div > h3').text()
            # print '大类',category_name
            for dl in category_dls:
                # 一级类别
                filter_attr1 = dl('dt > a').text()
                if filter_attr1 == '':
                    filter_attr1 = dl('dt').text()
                print '一级类别',filter_attr1
                # 二级类别
                filter_attr2_dds = dl('dd > span > a').items()
                for dd in filter_attr2_dds:
                    # 二级类别
                    filter_attr2 = dd.text()
                    # print '二级分类',filter_attr2
                    # print category_name,filter_attr1,filter_attr2
                    # 二级类别链接
                    f_c_href = dd.attr.href
                    if f_c_href.find('html?') != -1:
                        # print f_c_href
                        # 五个参数
                        if f_c_href.find(';') != -1:
                            pattern = (r'Category\/(.*?)-(.*?)-(.*?);(.*?)-(.*?)\.html')
                            params = re.findall(pattern,f_c_href)[0]
                            url = 'http://souke.xdf.cn/Search?cid=%s&ccc=%s&attr=%s;%s&gc=%s&applystate=0&hide=0' % (params[0],params[1],params[2],params[3],params[4])
                            self.crawl(url,timeout=300,connect_timeout=100,callback=self.parse_course1,save={'category_name':category_name,'filter_attr1':filter_attr1,'filter_attr2':filter_attr2})                            
                        # 中学
                        elif f_c_href.find('MiddleSchool') != -1:
                            req_url = f_c_href + '&applystate=0&hide=0'
                            self.crawl(req_url,timeout=300,connect_timeout=100,callback=self.parse_course2,save={'category_name':category_name,'filter_attr1':filter_attr1,'filter_attr2':filter_attr2})
                        # 课程
                        elif f_c_href.find(r'Course') != -1:
                           # print f_c_href
                            self.crawl(f_c_href,fetch_type='js',timeout=300,connect_timeout=100,callback=self.parse_course3,save={'category_name':category_name,'filter_attr1':filter_attr1,'filter_attr2':filter_attr2,'PageNumber':1})
                        # 四个参数  
                        else:
                            # print f_c_href
                            pattern = (r'Category\/(.*?)-(.*?)-(.*?)-(.*?)\.html?')
                            url_params = re.findall(pattern,f_c_href)
                            if len(url_params) == 0:
                                print f_c_href
                                pass
                            else:
                                cag_url = 'http://souke.xdf.cn/Search'
                                url_params = url_params[0]
                               # print url_params
                                formdata = {
                                    'cid':url_params[0],
                                    'ccc':url_params[1],
                                    'attr':url_params[2],
                                    'gc':url_params[3],
                                    'applystate':'0',
                                    'hide':'0'
                                }
                                f_c_href = self.gen_url(cag_url,formdata)
                                # print f_c_href
                                self.crawl(f_c_href,timeout=300,connect_timeout=100,callback=self.parse_course4,save={'category_name':category_name,'filter_attr1':filter_attr1,'filter_attr2':filter_attr2})
                                # print f_c_href
                    else:
                        #print f_c_href
                        if 'publish' in f_c_href:
                            pass
                        else:
                            if 'Course' in f_c_href:
                                # print filter_attr2,f_c_href
                                pattern = (r'-(.*?)-(.*?)\.html')
                                pattern1 = (r'Course\/(.*?)-(.*?)\.html')
                                params = re.findall(pattern,f_c_href)
                                if len(params) == 0:
                                    params = re.findall(pattern1,f_c_href)
                                # 城市id
                                cid = params[0][0]
                                # 课程 id
                                Coursecode = params[0][1]
                    
                                self.crawl(f_c_href,fetch_type='js',timeout=300,connect_timeout=100,callback=self.parse_course5,save={'category_name':category_name,'filter_attr1':filter_attr1,'filter_attr2':filter_attr2,'PageNumber':1,'Coursecode':Coursecode})
                            else:
                                # print f_c_href
                                if 'kw' in f_c_href:
                                    f_c_href = f_c_href + '&applystate=0&hide=0'
                                    # print f_c_href
                                    self.crawl(f_c_href,timeout=300,connect_timeout=100,callback=self.parse_course6,save={'category_name':category_name,'filter_attr1':filter_attr1,'filter_attr2':filter_attr2})
                                else:
                                    if 'bjuu' in f_c_href:
                                        pass
                                    else:
                                        if f_c_href.find('hide') == -1:
                                            f_c_href = f_c_href + '&applystate=0&hide=0'
                                        self.crawl(f_c_href,timeout=300,connect_timeout=100,callback=self.parse_course1,save={'category_name':category_name,'filter_attr1':filter_attr1,'filter_attr2':filter_attr2})  
                                            
                                            
                                

                        # pass
                    # print filter_attr1,filter_attr2,f_c_href
    # 包含检索词
    @config(priority=8,age=12 * 60)
    def parse_course6(self,response):
        print '访问',response.url
        
        course_list = response.doc('#divSearchResult > div.m-courselist').items()
        for div in course_list:
            # 课程 code 
            course_id = div.attr.code
            print course_id
            # 课程名称
            course_name = div('div[class="m-courselist-l pr"] > h2 > a').text().replace(' ','')
            print '课程名称',course_name
            # kw 检索词
            keyword = div('div[class="m-courselist-l pr"] > h2 > a >font').text()
            print '检索词',keyword
            # 课程链接
            course_href = div('div[class="m-courselist-l pr"] > h2 > a').attr.href
            print '课程链接',course_href
            self.crawl(course_href,timeout=300,connect_timeout=100,fetch_type='js',callback=self.parse_course6_detail,save
                       ={'category_name':response.save['category_name'],'filter_attr1':response.save['filter_attr1'],'keyword':keyword,'filter_attr2':response.save['filter_attr2'],'Coursecode':course_id,'course_name':course_name,'PageNumber':1})      
        # 翻页
        next_page = response.doc('.m-page > div > a.nextlink').attr.href
        print "下一页",next_page
        if next_page == None:
            next_page = ''
            print "下一页：" + next_page
        # 访问下一页
        if next_page == '':
            print "翻页结束"
        else:
            self.crawl(next_page,timeout=300,connect_timeout=100,callback = self.parse_course6,save={'category_name':response.save['category_name'],'filter_attr1':response.save['filter_attr1'],'filter_attr2':response.save['filter_attr2']})
    @config(priority=10,age=12 * 60)
    def parse_course6_detail(self,response):
        print '访问',response.url
        PageNumber = response.save['PageNumber']
        Coursecode = response.save['Coursecode']
        if PageNumber == 1:
            # 城市
            city_name = response.doc('#cityName').text()
            # 城市 ID
            cid = response.doc('#cityName').attr.cid
            # 课程名称
            course_name = response.doc('h2.m-coursedetails-h2').text()
            
        else:
            city_name = response.save['city_name']
            cid = response.save['cid']
            course_name = response.save['course_name'] 
        # 大类
        category_name = response.save['category_name']
        # 一级分类
        filter_attr1 = response.save['filter_attr1']
        # 二级分类
        filter_attr2 = response.save['filter_attr2']
        # 检索词
        keyword = response.save['keyword']
        print course_name
        class_list = response.doc('div[class="m-classlist mt10"]').items()
        for div in class_list:
            
            # 班级编号
            course_code = div('div[class="m-classlist-l class-list"] >div.m-class-info > h3 > a > em').text()
            if course_code == '':
                course_code = div('div[class="m-classlist-l  class-list"] >div.m-class-info > h3 > a > em').text()
            print '班级编号',course_code
            # 班级 ID
            pattern_class_id = (r'\/Class\/(.*?)\.html')
            class_href = div('div[class="m-classlist-l  class-list"] > div.m-class-info > h3 > a').attr.href
            if class_href == None:
                class_href = div('div[class="m-classlist-l class-list"] > div.m-class-info > h3 > a').attr.href
            if class_href == None:
                class_href = div('div[class="m-classlist-l class_list"] > div.m-class-info > h3 > a').attr.href
            class_id = re.findall(pattern_class_id,class_href)[0]
            # print class_href,class_id
            # 班级状态
            
            course_status = div('div[class="m-classlist mt10"] > div.m-classlist-r > div[class="u-tip1 u-tip2"]').text().split(' ')[0]
            if course_status == '':
                course_status = div('div[class="m-classlist mt10"] > div.m-classlist-r > div[class="u-tip1"]').text()
                if course_status == '':
                    course_status = '尚未报满'
            print '班级状态',course_status
            # 课程 ID
            course_id = Coursecode
            print '课程ID',course_id
            # 时间
            p_text = div('div[class="m-classlist mt10"] > div > div.m-class-info > p').text()
            print p_text
            # 课时
            pattern = (r'.*?,共计(.*?)次课')
            lesson_times = re.findall(pattern,p_text.encode('utf-8'))
            if len(lesson_times) == 0:
                 lesson_times = None
            else:
                lesson_times = lesson_times[0]
            print lesson_times
            # 上课地点
            pattern_space = (r'.*?地点： (.*?) ')
            learn_space = re.findall(pattern_space,p_text.encode('utf-8'))
            if len(learn_space) == 0:
                loc_space1 = p_text.encode('utf-8').find('地点：')
                learn_space = p_text.encode('utf-8')[loc_space1:]
                loc_space2 = learn_space.find(' ')
                learn_space = learn_space[loc_space2:].strip()
            else:
                learn_space = learn_space[0]
            print '上课地点',learn_space
            # 上课时间: 开始时间 终止时间 持续时间
            pattern_time = (r'.*?时间： (.*?) 至 (.*?) ')
            start_and_stop_time = re.findall(pattern_time,p_text.encode('utf-8'))[0]
             # 开始时间
            start_date = start_and_stop_time[0].replace('/','-',2)
            # print "开课时间:",start_date
            # 终止时间
            end_date = start_and_stop_time[1].replace('/','-',2)
            # print "结课时间:",end_date
            # 班级容量
            capacity = div('div[class="m-classlist-l  class-list"] > div.m-class-num > div.u-people').text()
            if capacity == '':
                capacity = div('div[class="m-classlist-l class-list"] > div.m-class-num > div.u-people').text()
            print '班级容量',capacity
            # 班级状况
            course_condition = div('div[class="m-classlist-l class-list"] > div.m-class-num > div.u-few').text()
            if course_condition == '':
                course_condition = div('div[class="m-classlist-l  class-list"] > div.m-class-num > div.u-few').text()
            if course_condition == '':
                course_condition = None
            print '班级状况',course_condition
                # 价格
            TPU = div('div[class="m-classlist mt10"] > div.m-classlist-r > div.u-price > span').text()
            print TPU
                # 总价
            if capacity.encode('utf-8') == '1对1班':
                capacity_revenue = TPU
                print "1对1班"
            else:
                capacity_num = re.findall(r'(\w*[0-9]+)\w*',capacity)
                if len(capacity_num) == 0:
                    capacity_revenue = '已开课(大班)'
                else: 
                    capacity_revenue = int(TPU)*int(capacity_num[0])
            print capacity_revenue
            enrollment = None
            actual_revenue = None
            yield {
                'city':city_name,
                'category_name':category_name,
                'filter_attr1':filter_attr1,
                'filter_attr2':filter_attr2,
                'TPU':TPU,
                'course_code':course_code,
                'course_id':class_id,
                'capacity':capacity,
                'actual_revenue':actual_revenue,
                'start_date':start_date,
                'end_date':end_date,
                'lesson_times':lesson_times,
                'learn_space':learn_space,
                'course_name':course_name,
                'enrollment':enrollment,
                'capacity_revenue':capacity_revenue,
                'course_status':course_status,
                'course_condition':course_condition
            }
        next_page = response.doc('.coli_page > a.nextlink').attr.href
        print "下一页",next_page
        if next_page == None:
            print "翻页结束"
        else:
            base_next_url = 'http://souke.xdf.cn/Course/CourseClassList?CityId=%s&SchoolId=%s&CourseCode=%s&Keyword=%s&Sort=0&Hide=0&ApplyState=0&MinDate=2000-01-01&MaxDate=3000-01-01&MinPrice=0&MaxPrice=2147483647&BusinessDistrictCode=&AreaCodes=&ClassTimeCode=&ClassModeCode=&ClassCapacityCode=&TeachingContentCode=&BookVersionCode=&PageNumber=%s&PageSize=10&_=%s' %(cid,cid,Coursecode,keyword,PageNumber,self.current_time())
            print base_next_url
            self.crawl(base_next_url,timeout=300,connect_timeout=100,fetch_type='js',callback=self.parse_course6_detail,save={'category_name':category_name,'PageNumber':PageNumber+1,'city_name':city_name,'cid':cid,'Coursecode':Coursecode,'filter_attr1':filter_attr1,'filter_attr2':filter_attr2,'course_name':course_name,'keyword':keyword})
        
        
        
        
        
    # 课程   
    @config(priority=10,age=12 * 60)                
    def parse_course5(self,response):
        print '访问',response.url
        PageNumber = response.save['PageNumber']
        Coursecode = response.save['Coursecode']
        if PageNumber == 1:
            # 城市
            city_name = response.doc('#cityName').text()
            # 城市 ID
            cid = response.doc('#cityName').attr.cid
            # 课程名称
            course_name = response.doc('h2.m-coursedetails-h2').text()
            
        else:
            city_name = response.save['city_name']
            cid = response.save['cid']
            course_name = response.save['course_name']    
        # 大类
        category_name = response.save['category_name']
        # 一级分类
        filter_attr1 = response.save['filter_attr1']
        # 二级分类
        filter_attr2 = response.save['filter_attr2']
        
        print course_name
        class_list = response.doc('div[class="m-classlist mt10"]').items()
        for div in class_list:

            # 班级编号
            course_code = div('div[class="m-classlist-l  class-list"] >div.m-class-info > h3 > a > em').text()
            if course_code == '':
                course_code = div('div[class="m-classlist-l class-list"] >div.m-class-info > h3 > a > em').text()
            print '班级编号',course_code
            # 班级 ID
            pattern_class_id = (r'\/Class\/(.*?)\.html')
            class_href = div('div[class="m-classlist-l  class-list"] > div.m-class-info > h3 > a').attr.href
            if class_href == None:
                class_href = div('div[class="m-classlist-l class-list"] > div.m-class-info > h3 > a').attr.href
            if class_href == None:
                class_href = div('div[class="m-classlist-l class_list"] > div.m-class-info > h3 > a').attr.href
            class_id = re.findall(pattern_class_id,class_href)[0]
            # print class_href,class_id
            # 班级状态
            
            course_status = div('div[class="m-classlist mt10"] > div.m-classlist-r > div[class="u-tip1 u-tip2"]').text().split(' ')[0]
            if course_status == '':
                course_status = div('div[class="m-classlist mt10"] > div.m-classlist-r > div[class="u-tip1"]').text()
                if course_status == '':
                    course_status = '尚未报满'
            print '班级状态',course_status
            # 课程 ID
            course_id = Coursecode
            print '课程ID',course_id
            # 时间
            p_text = div('div[class="m-classlist mt10"] > div > div.m-class-info > p').text()
            print p_text
            # 课时
            pattern = (r'.*?,共计(.*?)次课')
            lesson_times = re.findall(pattern,p_text.encode('utf-8'))
            if len(lesson_times) == 0:
                lesson_times = None
            else:
                lesson_times = lesson_times[0]
            print lesson_times
            # 上课地点
            pattern_space = (r'.*?地点： (.*?) ')
            learn_space = re.findall(pattern_space,p_text.encode('utf-8'))
            if len(learn_space) == 0:
                loc_space1 = p_text.encode('utf-8').find('地点：')
                learn_space = p_text.encode('utf-8')[loc_space1:]
                loc_space2 = learn_space.find(' ')
                learn_space = learn_space[loc_space2:].strip()
            else:
                learn_space = learn_space[0]
            print '上课地点',learn_space
            # 上课时间: 开始时间 终止时间 持续时间
            pattern_time = (r'.*?时间： (.*?) 至 (.*?) ')
            start_and_stop_time = re.findall(pattern_time,p_text.encode('utf-8'))[0]
             # 开始时间
            start_date = start_and_stop_time[0].replace('/','-',2)
            # print "开课时间:",start_date
            # 终止时间
            end_date = start_and_stop_time[1].replace('/','-',2)
            # print "结课时间:",end_date
            # 班级容量
            capacity = div('div[class="m-classlist-l  class-list"] > div.m-class-num > div.u-people').text()
            if capacity == '':
                capacity = div('div[class="m-classlist-l class-list"] > div.m-class-num > div.u-people').text()
            print '班级容量',capacity
            # 班级状况
            course_condition = div('div[class="m-classlist-l class-list"] > div.m-class-num > div.u-few').text()
            if course_condition == '':
                course_condition = div('div[class="m-classlist-l  class-list"] > div.m-class-num > div.u-few').text()
            if course_condition == '':
                course_condition = None
            print '班级状况',course_condition
                # 价格
            TPU = div('div[class="m-classlist mt10"] > div.m-classlist-r > div.u-price > span').text()
            print TPU
                # 总价
            if capacity.encode('utf-8') == '1对1班':
                capacity_revenue = TPU
                print "1对1班"
            else:
                capacity_num = re.findall(r'(\w*[0-9]+)\w*',capacity)
                if len(capacity_num) == 0:
                    capacity_revenue = '已开课(大班)'
                else: 
                    capacity_revenue = int(TPU)*int(capacity_num[0])
            print capacity_revenue
            enrollment = None
            actual_revenue = None
            yield {
                'city':city_name,
                'category_name':category_name,
                'filter_attr1':filter_attr1,
                'filter_attr2':filter_attr2,
                'TPU':TPU,
                'course_code':course_code,
                'course_id':class_id,
                'capacity':capacity,
                'actual_revenue':actual_revenue,
                'start_date':start_date,
                'end_date':end_date,
                'lesson_times':lesson_times,
                'learn_space':learn_space,
                'course_name':course_name,
                'enrollment':enrollment,
                'capacity_revenue':capacity_revenue,
                'course_status':course_status,
                'course_condition':course_condition
            }
                
        next_page = response.doc('.coli_page > a.nextlink').attr.href
        print "下一页",next_page
        if next_page == None:
            print "翻页结束"
        else:
            base_next_url = 'http://souke.xdf.cn/Course/CourseClassList?CityId=%s&SchoolId=%s&CourseCode=%s&Keyword=&Sort=0&Hide=0&ApplyState=0&MinDate=2000-01-01&MaxDate=3000-01-01&MinPrice=0&MaxPrice=2147483647&BusinessDistrictCode=&AreaCodes=&ClassTimeCode=&ClassModeCode=&ClassCapacityCode=&TeachingContentCode=&BookVersionCode=&PageNumber=%s&PageSize=10&_=%s' %(cid,cid,Coursecode,PageNumber,self.current_time())
            print base_next_url
            self.crawl(base_next_url,timeout=300,connect_timeout=100,fetch_type='js',callback=self.parse_course5,save={'PageNumber':PageNumber+1,'city_name':city_name,'cid':cid,'category_name':response.save['category_name'],'Coursecode':Coursecode,'filter_attr1':filter_attr1,'filter_attr2':filter_attr2,'course_name':course_name})
        
    # 课程 1 5 个参数
    @config(priority=8,age=12 * 60) 
    def parse_course1(self,response):
        print '访问',response.url
        courses_div = response.doc('#divSearchResult > div.m-courselist').items()
        for div in courses_div:
            # 课程code
            course_code = div.attr.code
            # print course_code
            # 课程链接
            course_href = div('div.m-courselist > div[class="m-courselist-l pr"] > h2 > a').attr.href
            # 课程名称
            course_name = div('div.m-courselist > div[class="m-courselist-l pr"] > h2 > a').text()
            print course_name,course_href
            self.crawl(course_href,callback=self.parse_course1_detail,save={'category_name':response.save['category_name'],'filter_attr1':response.save['filter_attr1'],'filter_attr2':response.save['filter_attr2'],'course_name':course_name,'course_code':course_code,'PageNumber':1})
        next_page = response.doc('.m-page > div > a.nextlink').attr.href
        print "下一页",next_page
        if next_page == None:
            next_page = ''
            print "下一页：" + next_page
        # 访问下一页
        if next_page == '':
            print "翻页结束"
        else:
            self.crawl(next_page,timeout=300,connect_timeout=100,callback = self.parse_course1,save={'category_name':response.save['category_name'],'filter_attr1':response.save['filter_attr1'],'filter_attr2':response.save['filter_attr2']})

    # 课程 MiddleSchool 中学
    @config(priority=8) 
    def parse_course2(self,response):
        print '访问',response.url
        
        course_divs = response.doc('div[class="col_left w780"] > div[class="m-classlist mt10"]').items()
        for div in course_divs:
            # 科目名称
            course_name = div('div.m-classlist-l > h3 > a').text()
            # 科目链接
            course_href = div('div.m-classlist-l > h3 > a').attr.href
            print course_name,course_href
            # 课程 code
            pattern = (r'-(.*?)\.html')
            course_code = re.findall(pattern,course_href)[0]
            print course_code
            self.crawl(course_href,fetch_type='js',timeout=300,connect_timeout=100,callback=self.parse_course2_detail,save={'category_name':response.save['category_name'],'filter_attr1':response.save['filter_attr1'],'filter_attr2':response.save['filter_attr2'],'course_name':course_name,'course_code':course_code,'PageNumber':1})
            next_page = response.doc('.m-page > div > a.nextlink').attr.href
            print "下一页",next_page
            if next_page == None:
                next_page = ''
                print "下一页：" + next_page
            # 访问下一页
            if next_page == '':
                print "翻页结束"
            else:
                self.crawl(next_page,timeout=300,connect_timeout=100,callback = self.parse_course2,save={'category_name':response.save['category_name'],'filter_attr1':response.save['filter_attr1'],'filter_attr2':response.save['filter_attr2']})
    @config(priority=10,age=12 * 60)       
    def parse_course2_detail(self,response):
        print "访问",response.url
        # 课程 ID
        class_id_v = response.save['course_code']
        # print response.text
        loc_coursecode = response.text.find('courseCode')
        # print loc_coursecode
        PageNumber = response.save['PageNumber']
        if PageNumber == 1:
            Coursecode = response.text[loc_coursecode+14:loc_coursecode+19]
            # 城市名称
            city_name = response.doc('#cityName').text()
        else:
            city_name = response.save['city_name']
            Coursecode = response.save['Coursecode']
        print '课程ID:',Coursecode


        # 城市ID
        cid = response.doc('#cityName').attr.cid
        # 大类
        category_name = response.save['category_name']
        # 一级分类
        filter_attr1 = response.save['filter_attr1']
        # 二级分类
        filter_attr2 = response.save['filter_attr2']
        # 科目名称
        course_name = response.save["course_name"]
        
        course_list_div = response.doc('#course_other_class_list > div.tabCont').items()
        for div in course_list_div:
            # 课程编号
            course_code = div('div[class="m-classlist mt10"] > div > div.m-class-info > h3 > a > em').text()
            print course_code
            # 班级 ID
            pattern_class_id = (r'\/Class\/(.*?)\.html')
            class_href = div('div[class="m-classlist mt10"] > div[class="m-classlist-l  class-list"] > div.m-class-info > h3 > a').attr.href
            if class_href == None:
                class_href = div('div[class="m-classlist mt10"] > div[class="m-classlist-l class_list"] > div.m-class-info > h3 > a').attr.href
            if class_href == None:
                class_href = div('div[class="m-classlist mt10"] > div[class="m-classlist-l class-list"] > div.m-class-info > h3 > a').attr.href
            class_id = re.findall(pattern_class_id,class_href)[0]
            # print class_href,class_id
            # 班级状态
            
            course_status = div('div[class="m-classlist mt10"] > div.m-classlist-r > div[class="u-tip1 u-tip2"]').text().split(' ')[0]
            if course_status == '':
                course_status = div('div[class="m-classlist mt10"] > div.m-classlist-r > div[class="u-tip1"]').text()
                if course_status == '':
                    course_status = '尚未报满'
            print '班级状态',course_status
            # 时间
            p_text = div('div[class="m-classlist mt10"] > div > div.m-class-info > p').text()
            print p_text
             # 课时
            pattern = (r'.*?,共计(.*?)次课')
            lesson_times = re.findall(pattern,p_text.encode('utf-8'))
            if len(lesson_times) == 0:
                lesson_times = None
            else:
                lesson_times = lesson_times[0]
            print lesson_times
            # 上课地点
            pattern_space = (r'.*?地点： (.*?) ')
            learn_space = re.findall(pattern_space,p_text.encode('utf-8'))
            if len(learn_space) == 0:
                loc_space1 = p_text.encode('utf-8').find('地点：')
                learn_space = p_text.encode('utf-8')[loc_space1:]
                loc_space2 = learn_space.find(' ')
                learn_space = learn_space[loc_space2:].strip()
            else:
                learn_space = learn_space[0]
            # print learn_space
            # 上课时间: 开始时间 终止时间 持续时间
            pattern_time = (r'.*?时间： (.*?) 至 (.*?) ')
            start_and_stop_time = re.findall(pattern_time,p_text.encode('utf-8'))[0]
            # 开始时间
            start_date = start_and_stop_time[0].replace('/','-',2)
            # print "开课时间:",start_date
            # 终止时间
            end_date = start_and_stop_time[1].replace('/','-',2)
            # print "结课时间:",end_date
            # 班级容量
            
            capacity = div('div[class="m-classlist mt10"] > div[class="m-classlist-l class_list"] > div.m-class-num > div.u-people').text()
            if capacity == '':
                capacity = div('div[class="m-classlist mt10"] > div[class="m-classlist-l  class-list"] > div.m-class-num > div.u-people').text()
            print capacity
            # 班级状况
            course_condition = div('div[class="m-classlist-l class-list"] > div.m-class-num > div.u-few').text()
            if course_condition == '':
                course_condition = div('div[class="m-classlist-l  class-list"] > div.m-class-num > div.u-few').text()
            if course_condition == '':
                course_condition = None
            print '班级状况',course_condition
            # 价格
            TPU = div('div[class="m-classlist mt10"] > div.m-classlist-r > div.u-price > span').text()
            print TPU
            # 总价
            if capacity.encode('utf-8') == '1对1班':
                capacityl_revenue = TPU
                print "1对1班"
            else:
                capacity_num = re.findall(r'(\w*[0-9]+)\w*',capacity)
                if len(capacity_num) == 0:
                    capacity_revenue = '已开课(大班)'
                else: 
                    capacity_revenue = int(TPU)*int(capacity_num[0])
            print capacity_revenue
            enrollment = None
            actual_revenue = None
            yield {
                'city':city_name,
                'category_name':category_name,
                'filter_attr1':filter_attr1,
                'filter_attr2':filter_attr2,
                'TPU':TPU,
                'course_code':course_code,
                'course_id':class_id,
                'capacity':capacity,
                'actual_revenue':actual_revenue,
                'start_date':start_date,
                'end_date':end_date,
                'lesson_times':lesson_times,
                'learn_space':learn_space,
                'course_name':course_name,
                'enrollment':enrollment,
                'capacity_revenue':capacity_revenue,
                'course_status':course_status,
                'course_condition':course_condition
            }
        next_page = response.doc('.coli_page > a.nextlink').attr.href
        print "下一页",next_page
        if next_page == None:
            print "翻页结束"
        else:
            # 下一页请求 url
            base_next_page_url = 'http://souke.xdf.cn/Class/CourseOtherClass'
            PageNumber = response.save['PageNumber']
            formdata_middle = {
                'CityId':cid,
                'SchoolId':cid,
                'CourseCode':Coursecode,
                'ClassId':class_id_v,
                'Sort':'0',
                'Hide':'0',
                'ApplyState':'0',
                'MinDate':'2000-01-01',
                'MaxDate':'3000-01-01',
                'MinPrice':'0',
                'MaxPrice':'10000000',
                'BusinessDistrictCode':'',
                'AreaCodes':'',
                'ClassTimeCode':'',
                'ClassModeCode':'',
                'ClassCapacityCode':'',
                'TeachingContentCode':'',
                'BookVersionCode':'',
                'PageNumber':PageNumber,
                'PageSize':'10',
                '_':self.current_time()
            }
            next_page_url = self.gen_url(base_next_page_url,formdata_middle)
            print next_page_url
            self.crawl(next_page_url,timeout=300,connect_timeout=100,callback=self.parse_course2_detail,save={'category_name':response.save['category_name'],'course_code':class_id_v,'filter_attr1':response.save['filter_attr1'],'filter_attr2':response.save['filter_attr2'],'Coursecode':Coursecode,'course_name':course_name,'PageNumber':PageNumber+1,'city_name':city_name})
            
            
            
    # 不需参数 直接就是课程（）
    @config(priority=10,age=12 * 60) 
    def parse_course3(self,response):
        print '访问',response.url
        PageNumber = response.save['PageNumber']
        loc_coursecode = response.text.find('courseCode')
        # print loc_coursecode
        if PageNumber == 1:
            # 城市
            city_name = response.doc('#cityName').text()
            # 城市 ID
            cid = response.doc('#cityName').attr.cid
            Coursecode = response.text[loc_coursecode+14:loc_coursecode+19]
            keyword_loc = response.url.find('=')
            keyword = response.url[keyword_loc+1:]
            keyword = unquote(keyword.encode('utf-8')).replace(' ','+').decode('utf-8')
            # 课程名称
            course_name = response.doc('h2.m-coursedetails-h2').text()
            
        else:
            city_name = response.save['city_name']
            cid = response.save['cid']
            Coursecode = response.save['Coursecode']
            keyword = response.save['keyword']
            course_name = response.save['course_name']
            
        print '关键词',keyword
        # 大类
        category_name = response.save['category_name']
        # 一级分类
        filter_attr1 = response.save['filter_attr1']
        # 二级分类
        filter_attr2 = response.save['filter_attr2']
        
        print course_name
        if PageNumber == 1:
            class_list = response.doc('#classlist_container > div[class="m-classlist mt10"]').items()
            for div in class_list:

                # 班级编号
                course_code = div('div[class="m-classlist-l  class-list"] > div.m-class-info > h3 > a > em').text()
                if course_code == '':
                    course_code = div('div[class="m-classlist-l class-list"] >div.m-class-info > h3 > a > em').text()
                print course_code
                # 班级 ID
                pattern_class_id = (r'\/Class\/(.*?)\.html')
                class_href = div('div[class="m-classlist-l  class-list"] > div.m-class-info > h3 > a').attr.href
                if class_href == None:
                    class_href = div('div[class="m-classlist-l class-list"] > div.m-class-info > h3 > a').attr.href
                if class_href == None:
                    class_href = div('div[class="m-classlist-l class_list"] > div.m-class-info > h3 > a').attr.href
                class_id = re.findall(pattern_class_id,class_href)[0]
                # print class_href,class_id
                # 班级状态

                course_status = div('div[class="m-classlist mt10"] > div.m-classlist-r > div[class="u-tip1 u-tip2"]').text().split(' ')[0]
                if course_status == '':
                    course_status = div('div[class="m-classlist mt10"] > div.m-classlist-r > div[class="u-tip1"]').text()
                    if course_status == '':
                        course_status = '尚未报满'
                print '班级状态',course_status
                # 课程 ID
                course_url = div('div[class="m-classlist-l  class-list"] > div.m-class-info > h3 > a').attr.href
                if course_url == '':
                    course_url = div('div[class="m-classlist-l class-list"] > div.m-class-info > h3 > a').attr.href
                print course_url
                pattern_course_id = (r'-(.*?)\.html')
                course_id = re.findall(pattern_course_id,course_url)[0]
                print '课程ID',course_id
                # 时间
                p_text = div('div[class="m-classlist mt10"] > div > div.m-class-info > p').text()
                print p_text
                 # 课时
                pattern = (r'.*?,共计(.*?)次课')
                lesson_times = re.findall(pattern,p_text.encode('utf-8'))
                if len(lesson_times) == 0:
                    lesson_times = None
                else:
                    lesson_times = lesson_times[0]
                print lesson_times
                # 上课地点
                pattern_space = (r'.*?地点： (.*?) ')
                learn_space = re.findall(pattern_space,p_text.encode('utf-8'))
                if len(learn_space) == 0:
                    loc_space1 = p_text.encode('utf-8').find('地点：')
                    learn_space = p_text.encode('utf-8')[loc_space1:]
                    loc_space2 = learn_space.find(' ')
                    learn_space = learn_space[loc_space2:].strip()
                else:
                    learn_space = learn_space[0]
                print '上课地点',learn_space
                # 上课时间: 开始时间 终止时间 持续时间
                pattern_time = (r'.*?时间： (.*?) 至 (.*?) ')
                start_and_stop_time = re.findall(pattern_time,p_text.encode('utf-8'))[0]
                # 开始时间
                start_date = start_and_stop_time[0].replace('/','-',2)
                # print "开课时间:",start_date
                # 终止时间
                end_date = start_and_stop_time[1].replace('/','-',2)
                # print "结课时间:",end_date
                # 班级容量
                # 班级状况
                course_condition = div('div[class="m-classlist-l class-list"] > div.m-class-num > div.u-few').text()
                if course_condition == '':
                    course_condition = div('div[class="m-classlist-l  class-list"] > div.m-class-num > div.u-few').text()
                if course_condition == '':
                    course_condition = None
                print '班级状况',course_condition
                capacity = div('div[class="m-classlist-l class-list"] > div.m-class-num > div.u-people').text()
                if capacity == '':
                    capacity = div('div[class="m-classlist-l  class-list"] > div.m-class-num > div.u-people').text()
                print capacity
                # 价格
                TPU = div('div[class="m-classlist mt10"] > div.m-classlist-r > div.u-price > span').text()
                print TPU
                # 总价
                if capacity.encode('utf-8') == '1对1班':
                    capacity_revenue = TPU
                    print "1对1班"
                else:
                    capacity_num = re.findall(r'(\w*[0-9]+)\w*',capacity)
                    if len(capacity_num) == 0:
                        capacity_revenue = '已开课(大班)'
                    else: 
                        capacity_revenue = int(TPU)*int(capacity_num[0])
                print capacity_revenue
                enrollment = None
                actual_revenue = None
                yield {
                'city':city_name,
                'category_name':category_name,
                'filter_attr1':filter_attr1,
                'filter_attr2':filter_attr2,
                'TPU':TPU,
                'course_code':course_code,
                'course_id':class_id,
                'capacity':capacity,
                'actual_revenue':actual_revenue,
                'start_date':start_date,
                'end_date':end_date,
                'lesson_times':lesson_times,
                'learn_space':learn_space,
                'course_name':course_name,
                'enrollment':enrollment,
                'capacity_revenue':capacity_revenue,
                'course_status':course_status,
                'course_condition':course_condition
            }
        else:
            class_list = response.doc('div[class="m-classlist mt10"]').items()
            for div in class_list:

                # 班级编号
                course_code = div('div[class="m-classlist-l class-list"] >div.m-class-info > h3 > a > em').text()
                if course_code == '':
                    course_code = div('div[class="m-classlist-l  class-list"] >div.m-class-info > h3 > a > em').text()
                print course_code
                # 班级 ID
                pattern_class_id = (r'\/Class\/(.*?)\.html')
                class_href = div('div[class="m-classlist-l  class-list"] > div.m-class-info > h3 > a').attr.href
                if class_href == None:
                    class_href = div('div[class="m-classlist-l class-list"] > div.m-class-info > h3 > a').attr.href
                if class_href == None:
                    class_href = div('div[class="m-classlist-l class_list"] > div.m-class-info > h3 > a').attr.href
                class_id = re.findall(pattern_class_id,class_href)[0]
                # print class_href,class_id
                # 班级状态

                course_status = div('div[class="m-classlist mt10"] > div.m-classlist-r > div[class="u-tip1 u-tip2"]').text().split(' ')[0]
                if course_status == '':
                    course_status = div('div[class="m-classlist mt10"] > div.m-classlist-r > div[class="u-tip1"]').text()
                    if course_status == '':
                        course_status = '尚未报满'
                print '班级状态',course_status
                # 课程 ID
                course_url = div('div[class="m-classlist-l class-list"] >div.m-class-info > h3 >a ').attr.href
                if course_url == '':
                    course_url = div('div[class="m-classlist-l  class-list"] > div.m-class-info > h3 > a').attr.href
                print course_url
                pattern_course_id = (r'-(.*?)\.html')
                course_id = re.findall(pattern_course_id,course_url)[0]
                print '课程ID',course_id
                # 时间
                p_text = div('div[class="m-classlist mt10"] > div > div.m-class-info > p').text()
                print p_text
                 # 课时
                pattern = (r'.*?,共计(.*?)次课')
                lesson_times = re.findall(pattern,p_text.encode('utf-8'))
                if len(lesson_times) == 0:
                    lesson_times = None
                else:
                    lesson_times = lesson_times[0]
                print lesson_times
                # 上课地点
                pattern_space = (r'.*?地点： (.*?) ')
                learn_space = re.findall(pattern_space,p_text.encode('utf-8'))
                if len(learn_space) == 0:
                    loc_space1 = p_text.encode('utf-8').find('地点：')
                    learn_space = p_text.encode('utf-8')[loc_space1:]
                    loc_space2 = learn_space.find(' ')
                    learn_space = learn_space[loc_space2:].strip()
                else:
                    learn_space = learn_space[0]
                print '上课地点',learn_space
                # 上课时间: 开始时间 终止时间 持续时间
                pattern_time = (r'.*?时间： (.*?) 至 (.*?) ')
                start_and_stop_time = re.findall(pattern_time,p_text.encode('utf-8'))[0]
                # 开始时间
                start_date = start_and_stop_time[0].replace('/','-',2)

                # print "开课时间:",start_date
                # 终止时间
                end_date = start_and_stop_time[1].replace('/','-',2)
                # print "结课时间:",end_date
                #　课程持续时间
                # 班级容量
                # 班级状况
                course_condition = div('div[class="m-classlist-l class-list"] > div.m-class-num > div.u-few').text()
                if course_condition == '':
                    course_condition = div('div[class="m-classlist-l  class-list"] > div.m-class-num > div.u-few').text()
                if course_condition == '':
                    course_condition = None
                print '班级状况',course_condition
                capacity = div('div[class="m-classlist-l class-list"] > div.m-class-num > div.u-people').text()
                if capacity == '':
                    capacity = div('div[class="m-classlist-l  class-list"] > div.m-class-num > div.u-people').text()
                print capacity
                # 价格
                TPU = div('div[class="m-classlist mt10"] > div.m-classlist-r > div.u-price > span').text()
                print TPU
                # 总价
                if capacity.encode('utf-8') == '1对1班':
                    capacity_revenue = TPU
                    print "1对1班"
                else:
                    capacity_num = re.findall(r'(\w*[0-9]+)\w*',capacity)
                    if len(capacity_num) == 0:
                        capacity_revenue = '已开课(大班)'
                    else: 
                        capacity_revenue = int(TPU)*int(capacity_num[0])
                print capacity_revenue
                enrollment = None
                actual_revenue = None
                yield {
                'city':city_name,
                'filter_attr1':filter_attr1,
                'filter_attr2':filter_attr2,
                'TPU':TPU,
                'course_code':course_code,
                'course_id':class_id,
                'capacity':capacity,
                'actual_revenue':actual_revenue,
                'start_date':start_date,
                'end_date':end_date,
                'lesson_times':lesson_times,
                'learn_space':learn_space,
                'course_name':course_name,
                'enrollment':enrollment,
                'capacity_revenue':capacity_revenue,
                'course_status':course_status,
                'course_condition':course_condition
                }
        next_page = response.doc('.coli_page > a.nextlink').attr.href
        print "下一页",next_page
        if next_page == None:
            print "翻页结束"
        else:
            base_next_url = 'http://souke.xdf.cn/Course/CourseClassList?Sort=0&SchoolId=%s&Hide=0&PageSize=10&Keyword=%s&TeachingContentCode=&MaxDate=3000-01-01&BusinessDistrictCode=&MaxPrice=2147483647&CityId=%s&ClassCapacityCode=&PageNumber=%d&ClassTimeCode=&CourseCode=%s&ApplyState=0&AreaCodes=&MinPrice=0&ClassModeCode=&BookVersionCode=&_=%s&MinDate=2000-01-01' %(cid,keyword,cid,PageNumber,Coursecode,self.current_time())
            print base_next_url
            self.crawl(base_next_url,timeout=300,connect_timeout=100,fetch_type='js',callback=self.parse_course3,save={'PageNumber':PageNumber+1,'keyword':keyword,'city_name':city_name,'cid':cid,'Coursecode':Coursecode,'category_name':response.save['category_name'],'filter_attr1':filter_attr1,'filter_attr2':filter_attr2,'course_name':course_name})
        
    # 四个参数
    @config(priority=8,age=12 * 60) 
    def parse_course4(self,response):
        print '访问',response.url
        # 课程 list
        course_div = response.doc('#divSearchResult > div.m-courselist').items()
        for div in course_div:
            # 课程 code
            course_code = div.attr.code
            print '课程 id',course_code
            # 课程 名称
            course_name = div('div[class="m-courselist-l pr"] > h2 > a').text()
            print '课程名称',course_name
            # 课程链接
            course_href = div('div[class="m-courselist-l pr"] > h2 > a').attr.href
            print '课程链接',course_href
            self.crawl(course_href,timeout=300,connect_timeout=100,callback=self.parse_course4_detail,save={'category_name':response.save['category_name'],'filter_attr1':response.save['filter_attr1'],'filter_attr2':response.save['filter_attr2'],'course_name':course_name,'course_code':course_code,'PageNumber':1})
            
        # 翻页
        next_page = response.doc('.m-page > div > a.nextlink').attr.href
        print "下一页",next_page
        if next_page == '':
            print "翻页结束"
        else:
            self.crawl(next_page,timeout=300,connect_timeout=100,callback = self.parse_course4,save={'category_name':response.save['category_name'],'filter_attr1':response.save['filter_attr1'],'filter_attr2':response.save['filter_attr2']})
    
    @config(priority=10,age=12 * 60) 
    def parse_course4_detail(self,response):
        print '访问',response.url
        PageNumber = response.save['PageNumber']
        if PageNumber == 1:
            # 城市
            city_name = response.doc('#cityName').text()
            # 城市 ID
            cid = response.doc('#cityName').attr.cid
        else:
            city_name = response.save['city_name']
            cid = response.save['cid']
        # 大类
        category_name = response.save['category_name']
        # 一级分类
        filter_attr1 = response.save['filter_attr1']
        # 二级分类
        filter_attr2 = response.save['filter_attr2']
        # 科目名称
        course_name = response.save['course_name']
        # 科目 ID
        course_id = response.save['course_code']
        class_list = response.doc('div[class="m-classlist mt10"]').items()
        for div in class_list:

            # 班级编号
            course_code = div('div[class="m-classlist-l  class-list"] > div.m-class-info > h3 > a > em').text()
            if course_code == '':
                course_code = div('div[class="m-classlist-l class-list"] >div.m-class-info > h3 > a > em').text()
            # print course_code
            # 班级 ID
            pattern_class_id = (r'\/Class\/(.*?)\.html')
            class_href = div('div[class="m-classlist-l  class-list"] > div.m-class-info > h3 > a').attr.href
            if class_href == None:
                class_href = div('div[class="m-classlist-l class-list"] > div.m-class-info > h3 > a').attr.href
            if class_href == None:
                class_href = div('div[class="m-classlist-l class_list"] > div.m-class-info > h3 > a').attr.href
            class_id = re.findall(pattern_class_id,class_href)[0]
            # print class_href,class_id
            # 班级状态
            
            course_status = div('div[class="m-classlist mt10"] > div.m-classlist-r > div[class="u-tip1 u-tip2"]').text().split(' ')[0]
            if course_status == '':
                course_status = div('div[class="m-classlist mt10"] > div.m-classlist-r > div[class="u-tip1"]').text()
                if course_status == '':
                    course_status = '尚未报满'
            print '班级状态',course_status
            # 时间
            p_text = div('div[class="m-classlist mt10"] > div > div.m-class-info > p').text()
            print p_text
             # 课时
            pattern = (r'.*?,共计(.*?)次课')
            lesson_times = re.findall(pattern,p_text.encode('utf-8'))
            if len(lesson_times) == 0:
                lesson_times = None
            else:
                lesson_times = lesson_times[0]
            print lesson_times
            # 上课地点
            pattern_space = (r'.*?地点： (.*?) ')
            learn_space = re.findall(pattern_space,p_text.encode('utf-8'))
            if len(learn_space) == 0:
                loc_space1 = p_text.encode('utf-8').find('地点：')
                learn_space = p_text.encode('utf-8')[loc_space1:]
                loc_space2 = learn_space.find(' ')
                learn_space = learn_space[loc_space2:].strip()
            else:
                learn_space = learn_space[0]
            # print learn_space
            # 上课时间: 开始时间 终止时间 持续时间
            pattern_time = (r'.*?时间： (.*?) 至 (.*?) ')
            start_and_stop_time = re.findall(pattern_time,p_text.encode('utf-8'))[0]
            # 开始时间
            start_date = start_and_stop_time[0].replace('/','-',2)
            # print "开课时间:",start_date
            # 终止时间
            end_date = start_and_stop_time[1].replace('/','-',2)
            # print "结课时间:",end_date
            # 班级容量
            capacity = div('div[class="m-classlist-l class-list"] > div.m-class-num > div.u-people').text()
            if capacity == '':
                capacity = div('div[class="m-classlist-l  class-list"] > div.m-class-num > div.u-people').text()
            print '班级容量',capacity
            # 班级状况
            course_condition = div('div[class="m-classlist-l class-list"] > div.m-class-num > div.u-few').text()
            if course_condition == '':
                course_condition = div('div[class="m-classlist-l  class-list"] > div.m-class-num > div.u-few').text()
            if course_condition == '':
                course_condition = None
            print '班级状况',course_condition
            # 价格
            TPU = div('div[class="m-classlist mt10"] > div.m-classlist-r > div.u-price > span').text()
            print TPU
            # 总价
            if capacity.encode('utf-8') == '1对1班':
                capacity_revenue = None
                print "1对1班"
            else:
                capacity_num = re.findall(r'(\w*[0-9]+)\w*',capacity)
                if len(capacity_num) == 0:
                    capacity_revenue = TPU
                else: 
                    capacity_revenue = int(TPU)*int(capacity_num[0])
            print capacity_revenue
            enrollment = None
            actual_revenue = None
            yield {
                'city':city_name,
                'category_name':category_name,
                'filter_attr1':filter_attr1,
                'filter_attr2':filter_attr2,
                'TPU':TPU,
                'course_code':course_code,
                'course_id':class_id,
                'capacity':capacity,
                'actual_revenue':actual_revenue,
                'start_date':start_date,
                'end_date':end_date,
                'lesson_times':lesson_times,
                'learn_space':learn_space,
                'course_name':course_name,
                'enrollment':enrollment,
                'capacity_revenue':capacity_revenue,
                'course_status':course_status,
                'course_condition':course_condition
            }
        next_page = response.doc('.coli_page > a.nextlink').attr.href
        print "下一页",next_page
        if next_page == None:
            print "翻页结束"
        else:
            PageNumber = response.save['PageNumber']
            base_next_url = 'http://souke.xdf.cn/Course/CourseClassList'
            formdata = {
                'CityId':cid,
                'SchoolId':cid,
                'CourseCode':course_id,
                'Keyword':'',
                'Sort':'0',
                'Hide':'0',
                'ApplyState':'0',
                'MinDate':'2000-01-01',
                'MaxDate':'3000-01-01',
                'MinPrice':'0',
                'MaxPrice':'2147483647',
                'BusinessDistrictCode':'',
                'AreaCodes':'',
                'ClassTimeCode':'',
                'ClassModeCode':'',
                'ClassCapacityCode':'',
                'TeachingContentCode':'',
                'BookVersionCode':'',
                'PageNumber':PageNumber,
                'PageSize':'10',
                '_':self.current_time()
            }
            next_page_url = self.gen_url(base_next_url,formdata)
            print next_page_url
            self.crawl(next_page_url,timeout=300,connect_timeout=100,callback=self.parse_course4_detail,save={'city_name':city_name,'cid':cid,'category_name':response.save['category_name'],'filter_attr1':filter_attr1,'filter_attr2':filter_attr2,'course_name':course_name,'course_code':course_id,'PageNumber':PageNumber+1})
                        
   
    @config(priority=10,age=12 * 60)  
    def parse_course1_detail(self,response):
        print '访问',response.url
        PageNumber = response.save['PageNumber']
        if PageNumber == 1:
            # 城市
            city_name = response.doc('#cityName').text()
            # 城市 ID
            cid = response.doc('#cityName').attr.cid
        else:
            city_name = response.save['city_name']
            cid = response.save['cid']
        # 大类
        category_name = response.save['category_name']
        # 一级分类
        filter_attr1 = response.save['filter_attr1']
        # 二级分类
        filter_attr2 = response.save['filter_attr2']
        # 科目名称
        course_name = response.save['course_name']
        # 科目id
        CourseCode = response.save['course_code']
        class_list = response.doc('#classlist_container > div[class="m-classlist mt10"]').items()
        for div in class_list:

            # 班级编号
            course_code = div('div[class="m-classlist-l  class-list"] > div.m-class-info > h3 > a > em').text()
            if course_code == '':
                course_code = div('div[class="m-classlist-l class-list"] >div.m-class-info > h3 > a > em').text()
            print course_code
            # 班级 ID
            pattern_class_id = (r'\/Class\/(.*?)\.html')
            class_href = div('div[class="m-classlist-l  class-list"] > div.m-class-info > h3 > a').attr.href
            if class_href == None:
                class_href = div('div[class="m-classlist-l class-list"] > div.m-class-info > h3 > a').attr.href
            if class_href == None:
                class_href = div('div[class="m-classlist-l class_list"] > div.m-class-info > h3 > a').attr.href
            class_id = re.findall(pattern_class_id,class_href)[0]
            # print class_href,class_id
            # 班级状态
            
            course_status = div('div[class="m-classlist mt10"] > div.m-classlist-r > div[class="u-tip1 u-tip2"]').text().split(' ')[0]
            if course_status == '':
                course_status = div('div[class="m-classlist mt10"] > div.m-classlist-r > div[class="u-tip1"]').text()
                if course_status == '':
                    course_status = '尚未报满'
            print '班级状态',course_status
            # 时间
            p_text = div('div[class="m-classlist mt10"] > div > div.m-class-info > p').text()
            print p_text
             # 课时
            pattern = (r'.*?,共计(.*?)次课')
            lesson_times = re.findall(pattern,p_text.encode('utf-8'))
            if len(lesson_times) == 0:
                lesson_times = None
            else:
                lesson_times = lesson_times[0]
            print '课时',lesson_times
            # 上课地点
            pattern_space = (r'.*?地点： (.*?) ')
            learn_space = re.findall(pattern_space,p_text.encode('utf-8'))
            if len(learn_space) == 0:
                loc_space1 = p_text.encode('utf-8').find('地点：')
                learn_space = p_text.encode('utf-8')[loc_space1:]
                loc_space2 = learn_space.find(' ')
                learn_space = learn_space[loc_space2:].strip()
            else:
                learn_space = learn_space[0]
            # print learn_space
            # 上课时间: 开始时间 终止时间 持续时间
            pattern_time = (r'.*?时间： (.*?) 至 (.*?) ')
            start_and_stop_time = re.findall(pattern_time,p_text.encode('utf-8'))[0]
            # 开始时间
            start_date = start_and_stop_time[0].replace('/','-',2)

            # print "开课时间:",start_date
            # 终止时间
            end_date = start_and_stop_time[1].replace('/','-',2)
            
            # print "结课时间:",end_date
            
            # 班级容量
            # 班级状况
            course_condition = div('div[class="m-classlist-l class-list"] > div.m-class-num > div.u-few').text()
            if course_condition == '':
                course_condition = div('div[class="m-classlist-l  class-list"] > div.m-class-num > div.u-few').text()
            if course_condition == '':
                course_condition = None
            print '班级状况',course_condition
            capacity = div('div[class="m-classlist-l class-list"] > div.m-class-num > div.u-people').text()
            if capacity == '':
                capacity = div('div[class="m-classlist-l  class-list"] > div.m-class-num > div.u-people').text()
            print '班级容量',capacity
            # 价格
            TPU = div('div[class="m-classlist mt10"] > div.m-classlist-r > div.u-price > span').text()
            print TPU
            # 总价
            if capacity.encode('utf-8') == '1对1班':
                capacity_revenue = TPU
                print "1对1班"
            else:
                capacity_num = re.findall(r'(\w*[0-9]+)\w*',capacity)
                if len(capacity_num) == 0:
                    capacity_revenue = '已开课(大班)'
                else: 
                    capacity_revenue = int(TPU)*int(capacity_num[0])
            print capacity_revenue
            enrollment = None
            actual_revenue = None
            yield {
                'city':city_name,
                'category_name':category_name,
                'filter_attr1':filter_attr1,
                'filter_attr2':filter_attr2,
                'TPU':TPU,
                'course_code':course_code,
                'course_id':class_id,
                'capacity':capacity,
                'actual_revenue':actual_revenue,
                'start_date':start_date,
                'end_date':end_date,
                'lesson_times':lesson_times,
                'learn_space':learn_space,
                'course_name':course_name,
                'enrollment':enrollment,
                'capacity_revenue':capacity_revenue,
                'course_status':course_status,
                'course_condition':course_condition
            }
        next_page = response.doc('.coli_page > a.nextlink').attr.href
        print "下一页",next_page
        if next_page == None:
            print "没有下一页"
        else:
            base_url = 'http://souke.xdf.cn/Course/CourseClassList'
            formdata = {
                'CityId':cid,
                'SchoolId':cid,
                'CourseCode':CourseCode,
                'Keyword':'',
                'Sort':'0',
                'Hide':'0',
                'ApplyState':'0',
                'MinDat':'2000-01-01',
                'MaxDate':'3000-01-01',
                'MinPrice':'0',
                'MaxPrice':'2147483647',
                'BusinessDistrictCode':'',
                'AreaCodes':'',
                'ClassTimeCode':'',
                'ClassModeCode':'',
                'ClassCapacityCode':'',
                'TeachingContentCode':'',
                'BookVersionCode':'',
                'PageNumber':PageNumber,
                'PageSize':'10',
                '_':self.current_time()
            }
            req_url = self.gen_url(base_url,formdata)
            self.crawl(req_url,timeout=300,connect_timeout=100,callback=self.parse_course1_detail,save={'city_name':city_name,'cid':cid,'category_name':response.save['category_name'],'filter_attr1':filter_attr1,'filter_attr2':filter_attr2,'course_name':course_name,'course_code':CourseCode,'PageNumber':PageNumber+1})

        
    # 生成url
    def gen_url(self,url,params):
        url = url + '?' + urllib.urlencode(params)
        return url
    # 生成 13 位时间戳
    def current_time(self):
        current_milli_time = lambda: int(round(time.time() * 1000))
        return current_milli_time()
    def on_result(self,result):
        super(Handler, self).on_result(result)
        if not result:
            return 
        client = pymongo.MongoClient(DB_IP,DB_PORT)
        db = client.research
        xdf_courses_web = db.xdf_courses_web

        course = {}
        # 当前时间
        now = datetime.datetime.now() # 这是数组时间格式
        now_time = now.strftime('%Y-%m-%d %H:%M:%S')
        now_time = time.strptime(now_time, "%Y-%m-%d %H:%M:%S")
        y,m,d,h,mm,s = now_time[0:6]
        update_time = datetime.datetime(y,m,d,h,mm,s)
        course['city'] = result['city']
        course['category_name'] = result['category_name']
        course['filter_attr1'] = result['filter_attr1']
        course['filter_attr2'] = result['filter_attr2']
        course['TPU'] = result['TPU']
        course['course_code'] = result['course_code']
        course['capacity'] = result['capacity']
        course['actual_revenue'] = result['actual_revenue']

        # 开课时间
        t = time.strptime(result['start_date'], "%Y-%m-%d")
        y,m,d = t[0:3]
        start_date = datetime.datetime(y,m,d)
        course['start_date'] = start_date
        # 结课时间
        t_s = time.strptime(result['end_date'], "%Y-%m-%d")
        y_s,m_s,d_s = t_s[0:3]
        end_date = datetime.datetime(y_s,m_s,d_s)
        course['end_date'] = end_date
        course['lesson_times'] = result['lesson_times']
        # 课程持续时间
        last_days = (end_date-start_date).days
        course['last_days'] = last_days
        course['update_time'] = update_time
        course['learn_space'] = result['learn_space']
        course['enrollment'] = result['enrollment']
        course['capacity_revenue'] = result['capacity_revenue']
        course['course_id'] = result['course_id']
        course['course_name'] = result['course_name']
        course['course_status'] = result['course_status']
        course['course_condition'] = result['course_condition']
        xdf_courses_web.insert(course)
