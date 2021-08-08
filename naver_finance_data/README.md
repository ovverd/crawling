# 1. 네이버 금융에서 주가데이터 가져오기

```

get_price_data(path, startDate, endDate, timeframe, number = 0 ):

```

+ path : 종목코드 엑셀파일 경로
+ startTime : 가져오고 싶은 주가데이터의 시작 날짜   ex) 20210803
+ endTime : 가져오고 싶은 주가데이터의 마지막 날짜
+ timeframe : 일별 (day), 주별(week), 월별 (month)
+ number : 앞에 몇개 종목수 만 가져오고 싶을 때 / 전종목은 안넣으면 됨 




<br><br>
# 2. 코드 설명

## 2.1 import 문

```
import json
import requests
import time
import pandas as pd
```
<br>


+ json : 네이버에서 크롤링한 데이터가 [[1,2,3],[3,5,4]] 이런식으로 리스트의 리스트 형태이긴 하지만 str문자열로 들어오기 때문에 json.loads를 사용하여 다시 리스트로 변환하여 저장하기 위해 사용
+ requests : 웹 요청할 때 필요한 모듈
+ time : 1초에 한번만 요청하기위해 time.sleep(1)을 사용함
+ pandas : 판다스 데이터프레임  

<br>

## 2.2 내장 함수들

```python

def make_code(x):
    x = str(x)
    return x

```
<br>
종목 코드를 받아올 때 005380 같은 것을 숫자로 인식해서 5380 같이 되지 않기 위해 문자열로 변환하여 시리즈에 apply() 시키기 위한 함수  

<br><br><br>


```python
def make_price_dataframe(code, startTime, endTime, name = '기업이름',  timeframe = 'day'):

    url = 'https://api.finance.naver.com/siseJson.naver?requestType=1'
    price_url = url + '&symbol=' + code + '&startTime=' + startTime + '&endTime=' + endTime + '&timeframe=' + timeframe
    
    price_data = requests.get(price_url)
    text_data = price_data.text
    text_data = text_data.strip()           # 맨 앞, 맨 뒤 공백 제거
    text_data = text_data.split('\n\t\t\n') # 공백기준으로 데이터 스플릿
    text_data[-2] = text_data[-2] + ','     # for문을 돌릴 때 일관성을 지키기 위해 마지막 행에는 ','를 추가


    # 날짜, 시가, 고가, 저가, 종가, 거래량 별로 각각 판다스 시리즈에 들어갈 리스트에 담기 
    date_list = []
    open_list = []
    high_list = []
    low_list = []
    close_list = []
    volume_list = []
    
    for row in text_data[1:-1]:           # 맨 앞과 맨 뒤 더미데이터 제거하고 시작
    
        if row[-4] == ',':                    # 데이터들이 두가지형식으로 되어있어서 알맞게 정제
            row = row[:-4] + (']')
        else:
            row = row[:-1]                    # 스플릿을 했을 때 맨 뒤에 ','가 붙어있는 것을 제거하고 시작
        
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


```

<br>
requests 모듈로 네이버 금융에 요청 후 받은 데이터를 정제해서 데이터프레임 만드는 함수 ( 한번에 하나의 종목 )
<br>


<br><br>


```python

def get_price_data(path, startDate,endDate,timeframe, number = 0):

    
    code_data = pd.read_excel(path)
    code_data = code_data[['단축코드','한글 종목명']]                    # 종목코드와 종목명만 남김
    code_data['단축코드'] = code_data['단축코드'].apply(make_code)      # 단축코드 시리즈를 문자열 타입으로 변환

    if number == 0:
        number = len(code_data)
        
    for num, code, name in zip(range(1, number+1), code_data['단축코드'][:number+1], code_data['한글 종목명'][:number+1]):

        try:
            print(num, code, name)
            time.sleep(1)
            try:
                price_df = make_price_dataframe(code, startDate, endDate, name = name, timeframe = timeframe)
            
            # 커넥션 예외처리, 에러 시 종료하지않고 60초 후 재시도 
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

    total_price.index = pd.to_datetime(total_price.index)
    
    return total_price

```


<br>

 모든 요청 종목 데이터를 취합하여 데이터프레임으로 만드는 함수
 
<br>




## 2.3 실행하기

```python

path = r'/Users/종목데이터 있는 파일 경로.xlsx'

# number = 4 => 앞에 4개종목 가져옴

price_result = get_price_data(path, '20210805','20210807', timeframe='day', number = 4)

price_result.to_excel(r'/Users/jinyounglee/Documents/price_result_exxxxx.xlsx')

```

<br>


<a href="http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020201" target="_blank">


한국거래소 KRX 정보데이터시스템에서 엑셀파일로 종목코드를 받을 수 있습니다.
    
+ 전종목, 모든날짜(1990년부터), 일자별 데이터를 엑셀로 저장할 때까지 기다리려면 3~4시간 이상 걸립니다.    

<br><br><br>
    
---








