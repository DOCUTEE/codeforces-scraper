import requests
import json
from system_helper import (
    read_file,
    save_file
)

class CodeforcesAPI:

    def __init__(self):
        self.problemset_url = "https://codeforces.com/api/problemset.problems"
    def fetch_problems(self):
        response = requests.get(self.problemset_url)
        try:
            data = response.json()
            if data['status'] == 'OK':
                data = data['result']['problems']
            else:
                raise Exception("API returned an error status")
        except Exception as e:
            print(f"Error fetching problems: {e}")
            data = []
        return data
    def save_problems_to_file(self, filename):
        problems = self.fetch_problems()
        save_file(filename, problems)

    def get_headers_list(self):
        list_of_headers = [
                    {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            # 'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://codeforces.com/problemset/status/2151/problem/C',
            'X-Csrf-Token': '1e50808953c9918a8ab7a4ba9b55fd41',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://codeforces.com',
            'Sec-GPC': '1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Connection': 'keep-alive',
            'Alt-Used': 'codeforces.com',
            # 'Cookie': '39ce7=CF64mM9o; cf_clearance=n8ihvQjzm3ijPnLAaG6EG_puG8.FceE6HPZkmh.aRw8-1758983028-1.2.1.1-pY2304bcG7MXQZUinU7M9YoNAaaEZ0B6cTR1mLl0S3An2aLXN4sO4NBcppLTTkME3VbrwU0Vbr_gsRXeJNSNR15LfTlLvc0h2pRP64gN0gycXfqrKr4j9.rtU8t4EsXnoXA9RxvI6k213I_36PHd6svSds.MTQDjdMJv7VzzIMfiKeY3_hF4tInv3hOmoMAfpLGPINcwFZJJiAH1d.yopEAy1U6T8fSri8XV82UO98jRH4bTR8mCtBzFh6WntLPQ; X-User-Sha1=2cbd93dcb5c3914a6622898f5bbfbf5e9d730485; X-User=dadc641edc79636dcd04d8235bdd06aacafbe89974ac26e720fe012c8e0db1b94da31bf8a2603fd3; 70a7c28f3de=ylfy6kv3d1j2ojmlby; pow=a18ccf0821ce641b857bfc6396db80249ebf0cc3; JSESSIONID=02E8986D6C0D06AA00D6D2F8940FB06B; lastOnlineTimeUpdaterInvocation=1758971870164; evercookie_png=ylfy6kv3d1j2ojmlby; evercookie_etag=ylfy6kv3d1j2ojmlby; evercookie_cache=ylfy6kv3d1j2ojmlby',
            'Priority': 'u=0',
            # Requests doesn't support trailers
            # 'TE': 'trailers',
        }
        ]
        return list_of_headers
    
    def get_cookies_list(self):
        cookies_list = [
             {
    '39ce7': 'CF64mM9o',
    'cf_clearance': 'n8ihvQjzm3ijPnLAaG6EG_puG8.FceE6HPZkmh.aRw8-1758983028-1.2.1.1-pY2304bcG7MXQZUinU7M9YoNAaaEZ0B6cTR1mLl0S3An2aLXN4sO4NBcppLTTkME3VbrwU0Vbr_gsRXeJNSNR15LfTlLvc0h2pRP64gN0gycXfqrKr4j9.rtU8t4EsXnoXA9RxvI6k213I_36PHd6svSds.MTQDjdMJv7VzzIMfiKeY3_hF4tInv3hOmoMAfpLGPINcwFZJJiAH1d.yopEAy1U6T8fSri8XV82UO98jRH4bTR8mCtBzFh6WntLPQ',
    'X-User-Sha1': '2cbd93dcb5c3914a6622898f5bbfbf5e9d730485',
    'X-User': 'dadc641edc79636dcd04d8235bdd06aacafbe89974ac26e720fe012c8e0db1b94da31bf8a2603fd3',
    '70a7c28f3de': 'ylfy6kv3d1j2ojmlby',
    'pow': 'a18ccf0821ce641b857bfc6396db80249ebf0cc3',
    'JSESSIONID': '02E8986D6C0D06AA00D6D2F8940FB06B',
    'lastOnlineTimeUpdaterInvocation': '1758971870164',
    'evercookie_png': 'ylfy6kv3d1j2ojmlby',
    'evercookie_etag': 'ylfy6kv3d1j2ojmlby',
    'evercookie_cache': 'ylfy6kv3d1j2ojmlby',
}

        ]
        return cookies_list

    def get_csrf_token_list(self):
        csrf_tokens_list = [
            '1e50808953c9918a8ab7a4ba9b55fd41'
        ]
        return csrf_tokens_list
