from fastapi import FastAPI
import requests
import urllib.parse
from envReader import getEnv


def coordinateBusStopSearch(pointLati, pointLong) : # 좌표를 이용한 버스정류소 검색 함수
    queryParams = urllib.parse.urlencode(params) # 기존의 params 딕셔너리를 쿼리 문자열로 변환
    parsedParams = dict(urllib.parse.parse_qsl(queryParams)) # 변환된 쿼리 문자열을 딕셔너리로 다시 파싱
    parsedParams["gpsLati"] = pointLati # gpsLati 값을 받아온 lati값으로 수정
    parsedParams["gpsLong"] = pointLong # gpsLong 값을 받아온 long값으로 수정
    modifiedParam = urllib.parse.urlencode(parsedParams) # 새로운 쿼리 문자열을 생성

    response = requests.get(url, params=modifiedParam) # api 요청
    busstopBodyJson = response.json().get("response").get("body") # body에서 모든 데이터를 사용하므로 body값 데이터만 반환
    print("버스정류소 검색 body데이터 :", busstopBodyJson)
    if busstopBodyJson.get("totalCount") == 0:  # 검색결과가 없으면 범위를 500m씩 넓혀서 검색하는 알고리즘 실행 같이 보낸 링크참고
        successCount = 0
        numberOfImplementation = 1 #반복 횟수
        while successCount == 0 :   # 검색결과가 하나이상 나올경우 한바퀴 돌고나서 중단함 없으면 범위를 넓혀 반복
            firstCoordinateLati = pointLati - numberOfImplementation * (0.0045) # 500m당 위/경도 서울기준 약 0.0045도
            firstCoordinateLong = pointLong - numberOfImplementation * (0.0045)
            queryParams = urllib.parse.urlencode(params) # 쿼리
            parsedParams = dict(urllib.parse.parse_qsl(queryParams))
            parsedParams["gpsLati"] = firstCoordinateLati #원래 좌표기준 위/경도 -500m 한 좌표로 초기값을 잡음
            parsedParams["gpsLong"] = firstCoordinateLong
            modifiedParam = urllib.parse.urlencode(parsedParams)

            response = requests.get(url, params=modifiedParam)
            busstopBodyJson = response.json().get("response").get("body")
            print("버스정류소 재검색 body데이터 0:", busstopBodyJson) # 재검색 데이터 뒤에 숫자가 0이면 초기값 1이면 Lati에 +500m 2면 Long에 +500m -는 음수
            if busstopBodyJson.get("totalCount") == 1: #검색결과가 하나이면 배열값이 아니므로 따로 분리하였음
                successCount += 1
                busstopData = busstopBodyJson.get("items").get("item").get("nodenm") #버스정류장 정보
            elif busstopBodyJson.get("totalCount") != 0: # 검색결과가 여러개이면
                successCount += 1
                busstopData = busstopBodyJson.get("items").get("item")[0].get("nodenm") # 가장 가까운 0번 선택
            nowCoordinateLati = firstCoordinateLati + 0.0045
            nowCoordinateLong = firstCoordinateLong

            queryParams = urllib.parse.urlencode(params)# 쿼리
            parsedParams = dict(urllib.parse.parse_qsl(queryParams))
            parsedParams["gpsLati"] = nowCoordinateLati # gpsLati 값을 수정
            parsedParams["gpsLong"] = nowCoordinateLong # param값은 초기화되므로 값변동없어도 입력
            modifiedParam = urllib.parse.urlencode(parsedParams)

            response = requests.get(url, params=modifiedParam)
            busstopBodyJson = response.json().get("response").get("body")
            print("버스정류소 재검색 body데이터 1:", busstopBodyJson)
            if busstopBodyJson.get("totalCount") == 1:
                successCount += 1
                busstopData = busstopBodyJson.get("items").get("item").get("nodenm")
            elif busstopBodyJson.get("totalCount") != 0:
                successCount += 1
                busstopData = busstopBodyJson.get("items").get("item")[0].get("nodenm")
            while firstCoordinateLati != nowCoordinateLati or firstCoordinateLong != nowCoordinateLong : # 현재좌표가 초기값이면 루프종료
                for i in range(numberOfImplementation * 2 - 1):
                    nowCoordinateLati += 0.0045
                    #
                    queryParams = urllib.parse.urlencode(params)
                    parsedParams = dict(urllib.parse.parse_qsl(queryParams))
                    parsedParams["gpsLati"] = nowCoordinateLati
                    parsedParams["gpsLong"] = nowCoordinateLong
                    modifiedParam = urllib.parse.urlencode(parsedParams)

                    response = requests.get(url, params=modifiedParam)
                    busstopBodyJson = response.json().get("response").get("body")
                    print("버스정류소 재검색 body데이터 1:", busstopBodyJson)
                    if busstopBodyJson.get("totalCount") == 1:
                        successCount += 1
                        busstopData = busstopBodyJson.get("items").get("item").get("nodenm")
                    elif busstopBodyJson.get("totalCount") != 0:
                        successCount += 1
                        busstopData = busstopBodyJson.get("items").get("item")[0].get("nodenm")
                for i in range(numberOfImplementation * 2):
                    nowCoordinateLong += 0.0045

                    queryParams = urllib.parse.urlencode(params)
                    parsedParams = dict(urllib.parse.parse_qsl(queryParams))
                    parsedParams["gpsLati"] = nowCoordinateLati
                    parsedParams["gpsLong"] = nowCoordinateLong
                    modifiedParam = urllib.parse.urlencode(parsedParams)

                    response = requests.get(url, params=modifiedParam)
                    busstopBodyJson = response.json().get("response").get("body")
                    print("버스정류소 재검색 body데이터 2:", busstopBodyJson)
                    if busstopBodyJson.get("totalCount") == 1:
                        successCount += 1
                        busstopData = busstopBodyJson.get("items").get("item").get("nodenm")
                    elif busstopBodyJson.get("totalCount") != 0:
                        successCount += 1
                        busstopData = busstopBodyJson.get("items").get("item")[0].get("nodenm")
                for i in range(numberOfImplementation * 2):
                    nowCoordinateLati -= 0.0045

                    queryParams = urllib.parse.urlencode(params)
                    parsedParams = dict(urllib.parse.parse_qsl(queryParams))
                    parsedParams["gpsLati"] = nowCoordinateLati
                    parsedParams["gpsLong"] = nowCoordinateLong
                    modifiedParam = urllib.parse.urlencode(parsedParams)

                    response = requests.get(url, params=modifiedParam)
                    busstopBodyJson = response.json().get("response").get("body")
                    print("버스정류소 재검색 body데이터 -1:", busstopBodyJson)
                    if busstopBodyJson.get("totalCount") == 1:
                        successCount += 1
                        busstopData = busstopBodyJson.get("items").get("item").get("nodenm")
                    elif busstopBodyJson.get("totalCount") != 0:
                        successCount += 1
                        busstopData = busstopBodyJson.get("items").get("item")[0].get("nodenm")
                for i in range(numberOfImplementation * 2 - 1):
                    nowCoordinateLong -= 0.0045

                    queryParams = urllib.parse.urlencode(params)
                    parsedParams = dict(urllib.parse.parse_qsl(queryParams))
                    parsedParams["gpsLati"] = nowCoordinateLati
                    parsedParams["gpsLong"] = nowCoordinateLong
                    modifiedParam = urllib.parse.urlencode(parsedParams)

                    response = requests.get(url, params=modifiedParam)
                    busstopBodyJson = response.json().get("response").get("body")
                    print("버스정류소 재검색 body데이터 -2:", busstopBodyJson)
                    if busstopBodyJson.get("totalCount") == 1:
                        successCount += 1
                        busstopData = busstopBodyJson.get("items").get("item").get("nodenm")
                    elif busstopBodyJson.get("totalCount") != 0:
                        successCount += 1
                        busstopData = busstopBodyJson.get("items").get("item")[0].get("nodenm")
                nowCoordinateLong -= 0.0045 # 초기값으로 돌아가기
            numberOfImplementation += 1
    else :
        busstopData = busstopBodyJson.get("items").get("item")[0].get("nodenm")
    return busstopData # 지금은 마지막에 검색된 곳을 리턴해줌
                       # TODO pointLati와 버스정류장 거리를 피타고라스로 계산 후 가장 가까운 곳 추천

apiurl = "https://api.vworld.kr/req/search?"
params = { #장소검색 기준
    "service": "search",
    "request": "search",
    "crs": "EPSG:4326",
    "query": "경기대 수원캠", #목적지 설정
    "type": "place",
    "format": "json",
    "key": "인증키", #인증키 부분 지우고 V-world(디지털트윈국토)에서 발급받은 api 인증키 입력
}
response = requests.get(apiurl, params=params)
adressData = None
if response.status_code == 200:
    adressData = response.json()
    print("장소검색 데이터 :",response.json())

    destinationPointLong = float(adressData.get("response").get("result").get("items")[0].get("point").get("x")) #결과 값의 x,y좌표 꺼내기
    destinationPointLati = float(adressData.get("response").get("result").get("items")[0].get("point").get("y")) #중간에 배열 0은 첫번째 결과값을 꺼낸 것이므로 나중에 소비자가 선택가능하면 좋을 듯
    userPointLong = 126.93540006310809 #사용자위치는 임의설정(반경 500m내 버스정류장 없는 곳으로 하였음) 프론트에서 나중에 받을 예정
    userPointLati = 37.41909998804243

    # apiurl = "https://api.vworld.kr/req/address?"
    # params = { #도로명, 지번주소 검색은 사용하지 않을 것 같지만 혹시모르니 일단 남겨둠
    #     "service": "address",
    #     "request": "getcoord",
    #     "crs": "epsg:4326",
    #     "address": "광교산로 154-42",
    #     "format": "json",
    #     "type": "road",
    #     "key": "인증키"
    # }
    # response = requests.get(apiurl, params=params)
    # if response.status_code == 200:
    #     print("도로명주소 body검색 데이터 :",response.json())
    # 
    #     print("장소검색, 도로명검색별 좌표 :", destinationPointLati, destinationPointLong, response.json().get("response").get("result").get("point").get("y"), response.json().get("response").get("result").get("point").get("x"))

# API URL 및 파라미터 설정
url = "http://apis.data.go.kr/1613000/BusSttnInfoInqireService/getCrdntPrxmtSttnList"
params = {
    "serviceKey": "인증키", #인증키 부분을 지우고 공공데이터 포털 api 인증키(decode) 입력
    "gpsLati" : None,
    "gpsLong" : None,
    "numOfRows" : "10",
    "pageNo" : "1",
    "_type" : "json"
}

busstopData = coordinateBusStopSearch(userPointLati, userPointLong)

# 응답 출력
print("출발지 버스정류소 :", busstopData)

busstopData = coordinateBusStopSearch(destinationPointLati, destinationPointLong)
# 응답 출력
print("목적지 버스정류소 :", busstopData)