
# 네이버 종목별 주가 가져오기

import json
import requests
import time
import pandas as pd


def make_code(x):
    x = str(x)
    return x


def make_price_dataframe(code, startTime, endTime, name = '기업이름',  timeframe = 'day'):

    url = 'https://api.finance.naver.com/siseJson.naver?requestType=1'
    price_url = url + '&symbol=' + code + '&startTime=' + startTime + '&endTime=' + endTime + '&timeframe=' + timeframe
    price_data = requests.get(price_url)
    text_data = price_data.text
    text_data = text_data.strip()
    text_data = text_data.split('\n\t\t\n')
    text_data[-2] = text_data[-2] + ','


    date_list = []
    open_list = []
    high_list = []
    low_list = []
    close_list = []
    volume_list = []
    
    for row in text_data[1:-1]:
        
        # 데이터형식이 다른 것들이 포함되어있어서 추가
        if row[-4] == ',':
            row = row[:-4] + (']')
        else:
            row = row[:-1]
            
        changed_to_list = json.loads(row)
        
        date_list.append(changed_to_list[0])
        open_list.append(changed_to_list[1])
        high_list.append(changed_to_list[2])
        low_list.append(changed_to_list[3])
        close_list.append(changed_to_list[4])
        volume_list.append(changed_to_list[5])

    price_df = pd.DataFrame({'시가':open_list,'고가':high_list,'저가':low_list,'종가':close_list, '거래량':volume_list }, index = date_list)
    price_df.columns = [[code + ' ' + name]*5, price_df.columns]

    return price_df



        

path = r'/Users/종목코드 데이터가 있는 엑셀파일 경로.xlsx'

code_data = pd.read_excel(path)
code_data = code_data[['단축코드','한글 종목명']]
code_data['단축코드'] = code_data['단축코드'].apply(make_code)


# 모든 종목 데이터 받으려면 zip( range(1, len(code_data)), code_data['단축코드'], code_data['한글 종목명'] 으로 수정

for num, code, name in zip(range(1, 10), code_data['단축코드'][:10], code_data['한글 종목명'][:10]):

    try:
        print(num, code, name)
        time.sleep(1)
        try:
            price_df = make_price_dataframe(code, '20210803','20210803', name = name)
        except requests.exceptions.Timeout:
            time.sleep(60)
            price_df = make_price_dataframe(code, name, '20210803','20210803', name = name)
        
        if num == 1:
            total_price = price_df
            
        else:
            total_price = pd.merge(total_price, price_df, how='outer', right_index=True, left_index=True)
    except ValueError:
        continue
    except KeyError:
        continue


total_price.index = pd.to_datetime(total_price.index)
total_price.to_excel(r'/Users/데이터 저장할 경로/total_price.xlsx')

