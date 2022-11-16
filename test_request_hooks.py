"""
We want to make a request for a document on the web
if this fails then we want to find and return the locally stored copy

1) Find out if the request has been successful
2) Return the url of what we were looking for
3) return the local equivelant file

"""

import requests

from csvcubed.readers.cubeconfig.utils import get_url_to_file_path_map
from csvcubed.utils.cache import session

get_local_version_instead = get_url_to_file_path_map()

#http = session

def print_status_code(response: requests.Response, *args, **kwargs):
    print(f"The status code is: {response.status_code}")
    if response.status_code >= 200 and response.status_code <= 399:
        print("This was successful")
    else:
        print("Not successful")
        #print(f"could not retrieve the document at: {response.url}")
        trimmed_url = str(response.url).removeprefix("https:")
        somthing = get_local_version_instead[trimmed_url[:len(trimmed_url)-1]]
        print(f"This is something {somthing}")
        response.url = somthing


#http.hooks["response"] = [print_status_code]

#http.get("https://purl.org/csv-cubed/qube-config/v1.1X")
thingy = session.get(
    "https://raw.githubusercontent.com/GSS-Cogs/csvcubed/main/src/csvcubed/readers/cubeconfig/v1_0/templates/calendar-week.jsonX",
    hooks={"response": [print_status_code]}
    )
print(thingy.url)