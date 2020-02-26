# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# from main.models import Quote

from scrapy_app.settings import DATABASE_URL
import psycopg2
from scrapy_app.models import db_connect
from scrapy.exceptions import DropItem
from scrapy_app.models import Quote, URL_details, TimeToCrawl, db_connect
from sqlalchemy.orm import sessionmaker
import random
import requests
from datetime import datetime
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from .tasks import process_urls_async

def retry_session(retries, session=None, backoff_factor=0.3, status_forcelist=(500, 502, 503, 504)):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

class ScrapyAppPipeline(object):

    def __init__(self):
        engine = db_connect()
        self.Session = sessionmaker(bind=engine)
        self.item_scraped_count = 0



    def open_spider(self,spider):
        spider.started_on = datetime.now() # To calculate the time of calling

        session = self.Session()

        try:
            session.execute('''TRUNCATE TABLE main_quote''')
            session.execute('''TRUNCATE TABLE main_url_details''')
            session.commit()

        except:
            session.rollback()
            raise

        finally:
            session.close()
        


    def process_item(self, item, spider):
        
        # session = self.Session()

        # quote = Quote()

        # quote.job_data_id = spider.job_data_id

        # quote.url_content = item["extracted_url"]

        # try:
        #     session.add(quote)
        #     session.commit()

        # except:
        #     session.rollback()
        #     raise

        # finally:
        #     session.close()


        if self.item_scraped_count % 10 == 0 :

            print("Scraped Item count", self.item_scraped_count)

            process_urls_async.delay(item["extracted_url"], spider.job_data_id)


        self.item_scraped_count += 1

        return item


    def close_spider(self, spider):

        # work_time = datetime.now() - spider.started_on (Time to Crawl)

        end_time = datetime.now() - spider.started_on

        # session = self.Session()

        time_to_crawl = TimeToCrawl()

        time_to_crawl.job_data_id = spider.job_data_id

        time_to_crawl.domain_name = spider.domain

        time_to_crawl.time_to_crawl = end_time

        try:
                session.add(time_to_crawl)
                # session.commit()

        except:
                session.rollback()
                raise

        session.close()


        # session = self.Session()

        # session_retry = retry_session(retries=5)

        # quote = ["%s" % v for v in session.query(
        #     Quote.url_content).filter_by(job_data_id=spider.job_data_id)] # removed .all() here to filter records for that code

        # score_urls = random.sample(quote, 10)

        # for value in iter(score_urls):

        #     url = "http://axe.checkers.eiii.eu/export-jsonld/pagecheck2.0/?url=" + value

            # process_urls_async.delay(url)




        # for value in iter(score_urls):

            # url = "http://axe.checkers.eiii.eu/export-jsonld/pagecheck2.0/?url=" + value

            # # print("URL Value",url)

            # headers = {'User-Agent': 'Mozilla/5.0'}

            # # r = requests.get(url=url,headers=headers)

            # r = session_retry.get(url=url, headers=headers)

            # if r.status_code == 504:
            #     continue
            # # retry mechanism : test it in pycharm 

            # data = r.json()

            # total_violations = 0
            # total_verify = 0
            # total_pass = 0

            # for violations in data['result-blob']['violations']:

            #     if any("wcag" in w for w in violations['tags']):

            #         total_violations += len(violations['nodes'])

            # for incomplete in data['result-blob']['incomplete']:

            #     if any("wcag" in w for w in incomplete['tags']):

            #         total_verify += len(incomplete['nodes'])

            # for passes in data['result-blob']['passes']:

            #     if any("wcag" in w for w in passes['tags']):

            #         total_pass += len(passes['nodes'])

            
            # url_details = URL_details()

            # url_details.job_data_id = spider.job_data_id

            # url_details.site_name = value

            # url_details.total_violations = total_violations

            # url_details.total_verify = total_verify

            # url_details.total_pass = total_pass

            # url_details.total_score = str(float("{0:.5f}".format(data['score'])))

            # try:
            #     session.add(url_details)
            #     # session.commit()

            # except:
            #     session.rollback()
            #     raise

            # calculated_score = URL_Details(
            #     site_name=value, total_violations=total_violations, total_verify=total_verify, total_pass=total_pass)
            # calculated_score.save()

        # print("Quote",quote)    

        # session.close()

    
    # work_time = datetime.now() - spider.started_on



