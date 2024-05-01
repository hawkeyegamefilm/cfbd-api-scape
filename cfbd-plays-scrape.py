import os
import cfbd
from cfbd.rest import ApiException
from pprint import pprint

# Configure API key authorization
configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = os.environ['CFBD_API_KEY']
configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
plays_api_instance = cfbd.PlaysApi(cfbd.ApiClient(configuration))

try:
    api_response = plays_api_instance.get_plays(year=2023,season_type="both",week=1, team="Iowa")
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PlaysApi->get_plays: %s\n" % e)