from scrapy_djangoitem import DjangoItem
from scrapy_app.models import URL_details as URLD

class URLDetails_Item(DjangoItem):
       class Meta:
           django_model = URLD
           fields = '__all__'

