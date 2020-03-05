from celery import shared_task
from celery.app.base import Celery
from scrapy_app import celeryconfig
from scrapy_app.retry_mechanism import retry_session
from scrapy_app.models import URL_details
from sqlalchemy.orm import sessionmaker
from scrapy_app.models import db_connect

# from scrapy_app.djangoitem import URLDetails_Item


app = Celery('scrapy_app', broker='amqp://guest@localhost//')
app.config_from_object(celeryconfig)

session_retry = retry_session(retries=5)
headers = {'User-Agent': 'Mozilla/5.0'}


class ProcessTask(object):

    def __init__(self):

        engine = db_connect()
        self.Session = sessionmaker(bind=engine)

    def run(self, base_url, job_data_id):

        url = "http://axe.checkers.eiii.eu/export-jsonld/pagecheck2.0/?url=" + base_url
        
        r = session_retry.get(url=url, headers=headers)

        data = r.json()

        total_violations = 0
        total_verify = 0
        total_pass = 0

        for violations in data['result-blob']['violations']:

            if any("wcag" in w for w in violations['tags']):

                total_violations += len(violations['nodes'])

        for incomplete in data['result-blob']['incomplete']:

            if any("wcag" in w for w in incomplete['tags']):

                total_verify += len(incomplete['nodes'])

        for passes in data['result-blob']['passes']:

            if any("wcag" in w for w in passes['tags']):

                total_pass += len(passes['nodes'])

        print("TOTAL")
    
    # def on_success(self, retval, task_id, *args, **kwargs):

        # print("TASK ID", task_id)

        session = self.Session()

        url_details = URL_details()

        url_details.job_data_id = job_data_id

        url_details.site_name = base_url

        url_details.total_violations = total_violations

        url_details.total_verify = total_verify

        url_details.total_pass = total_pass

        url_details.total_score = str(float("{0:.5f}".format(data['score'])))

        try:
            session.add(url_details)
            session.commit()

        except:
            session.rollback()
            raise

        session.close()


@app.task
def process_urls_async(url, job_data_id):
    ProcessTask().run(url, job_data_id)



# @app.task
# def process_urls_async(url, job_data_id):

#     url = "http://axe.checkers.eiii.eu/export-jsonld/pagecheck2.0/?url=" + url
    
#     r = session_retry.get(url=url, headers=headers)

#     data = r.json()

#     total_violations = 0
#     total_verify = 0
#     total_pass = 0

#     for violations in data['result-blob']['violations']:

#         if any("wcag" in w for w in violations['tags']):

#             total_violations += len(violations['nodes'])

#     for incomplete in data['result-blob']['incomplete']:

#         if any("wcag" in w for w in incomplete['tags']):

#             total_verify += len(incomplete['nodes'])

#     for passes in data['result-blob']['passes']:

#         if any("wcag" in w for w in passes['tags']):

#             total_pass += len(passes['nodes'])

#     print("Total Violations", total_violations)
#     print("Total Verify", total_verify)
#     print("Total Pass", total_pass)

    # url_details_item = URLDetails_Item()

    # url_details_item['job_data_id'] = job_data_id

    # url_details_item['site_name'] =  url

    # url_details_item['total_violations'] = total_violations

    # url_details_item['total_verify'] = total_verify

    # url_details_item['total_pass'] = total_pass

    # url_details_item.save()

    # url_details = URL_details()

    # url_details.job_data_id = job_data_id

    # url_details.site_name = url

    # url_details.total_violations = total_violations

    # url_details.total_verify = total_verify

    # url_details.total_pass = total_pass

    # url_details.total_score = str(float("{0:.5f}".format(data['score'])))

    # try:
    #     session.add(url_details)
    #     session.commit()

    # except:
    #     session.rollback()
    #     raise

    # calculated_score = URL_Details(
    #     site_name=value, total_violations=total_violations, total_verify=total_verify, total_pass=total_pass)
    # calculated_score.save()


