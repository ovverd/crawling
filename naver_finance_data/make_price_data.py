
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
                
        if row[-4] == ',':                  # 문자열 데이터가 각각 달라서 정제하는 코드
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




def get_price_data(path, startDate,endDate,timeframe, number = 0):

    
    code_data = pd.read_excel(path)
    code_data = code_data[['단축코드','한글 종목명']]
    code_data['단축코드'] = code_data['단축코드'].apply(make_code)

    if number == 0:
        number = len(code_data)
        
    for num, code, name in zip(range(1, number+1), code_data['단축코드'][:number+1], code_data['한글 종목명'][:number+1]):

        try:
            print(num, code, name)
            time.sleep(1)
            try:
                price_df = make_price_dataframe(code, startDate, endDate, name = name, timeframe = timeframe)
            
            # 커넥션 에러 2가지 예외처리, 에러 났을 때 끊키지 않고 60초 후 재시도
            except requests.exceptions.Timeout:
                time.sleep(60)
                price_df = make_price_dataframe(code, startDate, endDate, name = name, timeframe = timeframe)
            except ConnectionResetError:
                time.sleep(60)
                price_df = make_price_dataframe(code, startDate, endDate, name = name, timeframe = timeframe)
            
            if num == 1:
                total_price = price_df
                
            else:
                total_price = pd.merge(total_price, price_df,how='outer', right_index=True, left_index=True)
        except ValueError:
            print( code, 'valueError')
            continue
        except KeyError:
            print( code, 'KeyError')
            continue
    
    # 인덱스에 '20210807'과 같은 문자열을 datetime 타입으로 변환하여 깔끔하게 저장
    total_price.index = pd.to_datetime(total_price.index)
    
    return total_price
        

    
    
    
    
    
# 종목코드 엑셀 경로
path = r'/Users/종목코드 파일 경로.xlsx'


# startDate = 시작 날짜
# endDate = 마지막 날짜
# timeframe = day: 일자별 / week: 주별 / month: 월별
# number = 연습용으로 앞에 몇개 종목만 실험하고 싶을 때 숫자를 넣을 수 있음

price_result = get_price_data(path, '20210805','20210807', timeframe='day', number = 4)


price_result.to_excel(r'/Users/가격데이터 저장할 파일 경로.xlsx')

