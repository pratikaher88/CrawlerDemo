import os.io
# os.environ['CELERY_CONFIG_MODULE'] = 'sdtcrawler.celeryconfig'


PORT = os.environ['PORT']
with io.open("scrapyd.conf", 'r+', encoding='utf-8') as f:
    f.read()
    f.write(u'\nhttp_port = %s\n' % PORT)