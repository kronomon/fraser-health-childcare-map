import requests
from requests.adapters import HTTPAdapter, Retry


def requests_retry_session():
    session = requests.Session()
    retry = Retry(total=5,
                  backoff_factor=0.5,
                  status_forcelist=[ 500, 502, 503, 504 ])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session