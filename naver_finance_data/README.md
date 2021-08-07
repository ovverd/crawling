# 1. 네이버 금융에서 주가데이터 가져오기

```

make_price_dataframe(code, startTime, endTime, name = '기업이름', timeframe = 'day')

```

+ code : 기업 종목 코드
+ startTime : 가져오고 싶은 주가데이터의 시작 날짜   ex) 20210803
+ endTime : 가져오고 싶은 주가데이터의 마지막 날짜
+ name : 안넣어도 됨
+ timeframe : 일별 (day), 주별(week), 월별 (month)




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

## 2.3 종목 데이터 가져오기

```python
path = r'/Users/종목데이터 있는 파일 경로.xlsx'

code_data = pd.read_excel(path)
code_data = code_data[['단축코드','한글 종목명']]                   # 종목코드와 종목명만 남김
code_data['단축코드'] = code_data['단축코드'].apply(make_code)      # 단축코드 시리즈를 문자열 타입으로 변환

```
<br>

<a href="http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020201" target="_blank">


한국거래소 KRX 정보데이터시스템에서 엑셀파일로 종목코드를 받을 수 있습니다.



<br>

## 2.4 전 종목 데이터 크롤링

```python

# 전 종목 데이터를 크롤링하려면 zip ( range(1,len(code_data), code_data['단축코드'], code_data['한글 종목명'] ) 으로 바꾸면 됨, 밑에는 실험으로 하기 좋게 10개만 함.

for num, code, name in zip(range(1, 10), code_data['단축코드'][:10], code_data['한글 종목명'][:10]):

    try:
        print(num, code, name)
        time.sleep(1)                 # 1초에 1번만 요청하기
        try:
            price_df = make_price_dataframe(code, '20210803','20210803', name = name)     # 원하는 시작날짜~종료날짜 입력해서 요청
        except requests.exceptions.Timeout:
            time.sleep(60)
            price_df = make_price_dataframe(code, name, '20210803','20210803', name = name)   # 요청이 오류가 났을 때 누락없게하기위해 60초후 재요청
        
        if num == 1:                  # 맨처음엔 total_price 데이터프레임 선언하기
            total_price = price_df
            
        else:
            total_price = pd.merge(total_price, price_df,how='outer', right_index=True, left_index=True)  # 그다음부터 전부다 종목별로 '오른쪽으로' merge 하기
    except ValueError:
        continue
    except KeyError:
        continue
        
```
<br>


## 2.5 데이터 엑셀로 저장하기

```python

total_price.index = pd.to_datetime(total_price.index)       # str로 되어있던 날짜들을 진짜 datetime 타입으로 변환하여 저장.
total_price.to_excel(r'/Users/저장할 경로/total_price.xlsx')


```


<br><br>
---








