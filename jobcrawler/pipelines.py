# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
# from pymongo import MongoClient
from scrapy.exceptions import DropItem
from scrapy import log
# import sqlite3 as dbi # uncomment if using sqlite3
import pg8000 as dbi
import app.config as config
import datetime
#import traceback


class ItemPrintingPipeline(object):
    def process_item(self, item, spider):
        log.msg('[%s] Job Title: %s' % (spider.name, item.get('job_title', '--')))
        return item


# class ItemDuplicationCheckPipeline(object):
#     def process_item(self, item, spider):
#         job_title = item.get('job_title')
#         job_details_link = item.get('job_details_link')
#         if job_title is not None and job_details_link is not None:
#             job_item_count = db.crawled_jobs.find({"job_details_link": job_details_link}).count()
#
#             if job_item_count == 0:
#                 return item
#
#         raise DropItem('Duplicated Job title: %s' % job_title)

class ItemRecuritValidationPipeline(object):
    def process_item(self, item, spider):
        pattern = config.JOB_RULE_OUT_PATTERN
        match = re.search(pattern, item.get('job_title', ''))
        if match is None:
            return item
        else:
            raise DropItem('Job is not posted by recuriter. Removing...')


class ItemPostedByAgentPipeline(object):
    def process_item(self, item, spider):
        pattern = config.AGENT_RULE_OUT_PATTERN
        match = re.search(pattern, item.get('job_title', ''))
        if match is None:
            return item
        else:
            raise DropItem('Job is posted by Agent. Removing...')

class ItemPublishDateFilterPipeline(object):
    def process_item(self, item, spider):
        publish_date = item.get('publish_date', None)
        if publish_date is None:
            raise DropItem('Job has no publish_date...')

        #log.msg('Time Delta:' + str((datetime.datetime.now() - publish_date).days))
        
        if (datetime.datetime.now() - publish_date).days > int(config.HOUSEKEEPING_RECORD_ORDLER_THAN):
            raise DropItem('Job is published order than %s days' % str(config.HOUSEKEEPING_RECORD_ORDLER_THAN))
        
        return item

class ItemSaveToDBPipeline(object):
    def process_item(self, item, spider):
        try:
            #conn = dbi.connect(config.DB_FILE)
            conn = dbi.connect(host=config.DB_HOST, database=config.DATABASE, user=config.DB_USER, password=config.DB_PASSWORD)
            c = conn.cursor()
            # c.execute('INSERT INTO CRAWLED_JOBS '
            #           '('
            #           'job_title, job_desc, job_details_link, job_location, job_country,'
            #           'salary, employer_name, publish_date, contact, source, crawled_date'
            #           ') '
            #           'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
            #           (
            #               item.get('job_title', None),
            #               item.get('job_desc', None),
            #               item.get('job_details_link', None),
            #               item.get('job_location', None),
            #               item.get('job_country', None),
            #               item.get('salary', None),
            #               item.get('employer_name', None),
            #               item.get('publish_date', None),
            #               item.get('contact', None),
            #               spider.name,
            #               datetime.datetime.now()

            #           ))

            c.execute('INSERT INTO CRAWLED_JOBS '
                      '('
                      'job_title, job_desc, job_details_link, job_location, job_country,'
                      'salary, employer_name, publish_date, contact, source, crawled_date'
                      ') '
                      'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, current_date);',
                      (
                          item.get('job_title', None),
                          item.get('job_desc', None),
                          item.get('job_details_link', None),
                          item.get('job_location', None),
                          item.get('job_country', None),
                          item.get('salary', None),
                          item.get('employer_name', None),
                          item.get('publish_date', None),
                          item.get('contact', None),
                          spider.name

                      ))

            conn.commit()
            conn.close()
        except:
          #traceback.print_exc()
          raise DropItem('Job is duplicate.')

        return item