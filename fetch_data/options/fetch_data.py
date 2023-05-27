import requests
import json
from .data_cleaner import clean_options_data

def get_api_data(url:str,month:str):
    headers={"user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "refere":"https://www.nseindia.com/option-chain",
    "cookie":'nseQuoteSymbols=[{"symbol":"BANKNIFTY","identifier":"OPTIDXBANKNIFTY01-06-2023CE44000.00","type":"equity"}]; AKA_A2=A; ak_bmsc=5D7E8DA9847C53B563243A18107C526D~000000000000000000000000000000~YAAQDD/LF1gR2UyIAQAAqRIPXRMgeKoHIrLqQefAOuIPWgJomMQqUkUG88pjPTaJ81HpbjunxkYxdM7U7Qbrtd9aaEuHhnKoxXD0zbI5t4q5ZggOdusoLH3RazKKgRjfqRxWVmM5pgKUi704FpkaY8xD/zyqts0R5uepLMyjo1jPJGqqyiSdF7K4uPRihv7/VMZFEHsJlO8foL7qKaNbF98oy+I0MlD6q74LEMFPf6mUvfMEh5aR2wAGmCB6IzBWNfy5ujJbVB8UR0BllS2/It5yEUS8FVhuZCUDpQsBTInkQF1J3szpPvG+Q8C5gteWLZuGa/2QIpM9ilWisdNfZrJ0wssDQD2eoV/J7CaUplLIlHCesHW5oogTyvp2AoJdrTV8EoMulvsEXTKkZw==; nsit=GYKYsOH3KmT3LvhMbhwc6-DC; defaultLang=en; nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTY4NTE5MTkwOCwiZXhwIjoxNjg1MTk5MTA4fQ.tb2l_YgZ_Yim8oJmiE4hTY5kAcP2P0z5SUr1tru4Bzs; bm_mi=261DA7BDBC82886C80AA4384C4B771BE~YAAQDj/LF1KMd0mIAQAA/tpDXRN40S3t61b2F+U1yT89Aj5qoxAHMJ5bFKnlc03h9ZbO44zeDo/z/lIoAtQRcGTZoe5Ao0IZ9CfEWmEYTu5JNl6Ml3vICbGngmzvJPUEWfUYzdh7RFTDbe7sihg+kR/1C6SnEJ9QBPZTb3mnUxqpp7PMg2Y6gptNljqgtlunxp7ebAQJDG80Jq2ndL2lX3yGnwwxfmv/rRKAmX0P+l7Hiyy0FT4Ig4TvVrZF3zJ84Aaap8kwVhmyl/tDxX5LhvFfiGnHQGUy+VfcbKEhXdVkkMjmTkkHc3wKNWRxYc5eylM0znOKDfTKVkc=~1; bm_sv=6CD64B703868927841D904C2F615CDE6~YAAQDj/LF3iNd0mIAQAA0+lDXRO/fEevIccr/KlXURFhpv8PHlK++WFR7izk30j0vo9OMLcbzkO4TJNIUbz6EShMq+vahXLQ52y/XTJlHElvhnoZE8AO3G1YjO+gBiHRkVmnOJUA6TF7uzqMWIctjjlsn0sfMR+WItPkS4oPlOpolEbFNv6i84NIeH/y2dVSpSpjIb/2aA1NTscWfS7F5YUwrfV37ZROncTPiOYMqwW2jG3wyiElUdYvdFGa3XCbKFvc~1'}
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        response=response.text
        return clean_options_data(response=response,month=month)
    else:
        return response.headers

