import os
import cfbd
from cfbd.rest import ApiException
from pprint import pprint

# Configure API key authorization
configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = os.environ['CFBD_API_KEY']
configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
drives_api_instance = cfbd.DrivesApi(cfbd.ApiClient(configuration))

try:
    # Betting lines
    api_response = drives_api_instance.get_drives(year=2023,season_type="both",team="Iowa")
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DrivesApi->get_drives: %s\n" % e)