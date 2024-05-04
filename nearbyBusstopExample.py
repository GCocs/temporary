from fastapi import FastAPI
import requests
import urllib.parse
from envReader import getEnv

COORDINATE_URL = "http://apis.data.go.kr/1613000/BusSttnInfoInqireService/getCrdntPrxmtSttnList"
COORDINATE_PARAMS = {
    # 인증키 부분을 지우고 공공데이터 포털 api 인증키(decode) 입력
    "serviceKey": getEnv("DATA_GO_KEY"),
    "gpsLati": None,
    "gpsLong": None,
    "numOfRows": "10",
    "pageNo": "1",
    "_type": "json"
}


def coordinateRequest(pointLati, pointLong):
    """
    위도, 경도를 기반으로 하는 버스 정류장 찾기를 위한 API 요청 함수

    :param pointLati: 목표 경도 - float
    :param pointLong: 목표 위도 - float
    :return: API 요청 결과 - json
    """
    global COORDINATE_URL
    global COORDINATE_PARAMS

    # 기존의 params 딕셔너리를 쿼리 문자열로 변환
    queryParams = urllib.parse.urlencode(COORDINATE_PARAMS)
    # 변환된 쿼리 문자열을 딕셔너리로 다시 파싱
    parsedParams = dict(urllib.parse.parse_qsl(queryParams))

    # gpsLati 값을 받아온 위치 값으로 수정
    parsedParams["gpsLati"] = pointLati
    parsedParams["gpsLong"] = pointLong

    # 새로운 쿼리 문자열을 생성
    modifiedParam = urllib.parse.urlencode(parsedParams)

    # api 요청
    response = requests.get(COORDINATE_URL, params=modifiedParam)

    busStopBodyJson = response.json().get("response").get("body")
    print("버스정류소 검색 body데이터 :", busStopBodyJson)

    return busStopBodyJson


def coordinateCheckResult(requestResult, successCount):
    """
    위도, 경도 기반 request에 대한 결과를 확인 함수

    :param requestResult: request 결과
    :param successCount: 현재 Count
    :return: list - [새로운 버스 정류장 정보, successCount + 1]
    """
    newResultBusStop = None

    if requestResult.get("totalCount") == 1:
        successCount += 1
        # 버스정류장 정보
        resultBusStop = requestResult.get("items").get("item").get("nodenm")
    elif requestResult.get("totalCount") != 0:
        # 검색결과가 여러개이면
        successCount += 1

        # 가장 가까운 0번 선택
        newResultBusStop = requestResult.get("items").get("item")[0].get("nodenm")

    return [newResultBusStop, successCount]


def coordinateBusStopSearch(pointLati, pointLong):
    """
    좌표를 이용하여 근처의 버스정류소를 검색

    :param pointLati: 위도 데이터 - float
    :param pointLong: 경도 데이터 - float
    :return: 버스 정류장 데이터 -
    """

    busstopBodyJson = coordinateRequest(pointLati, pointLong)

    resultBusStop = None
    # 검색결과가 없으면 범위를 500m씩 넓혀서 검색하는 알고리즘 실행 같이 보낸 링크참고
    if busstopBodyJson.get("totalCount") == 0:
        successCount = 0
        # 반복 횟수
        numberOfImplementation = 1

        # 검색결과가 하나이상 나올경우 한바퀴 돌고나서 중단함 없으면 범위를 넓혀 반복
        while successCount == 0:
            # 500m당 위/경도 서울 기준 약 0.0045도
            firstCoordinateLati = pointLati - numberOfImplementation * 0.0045
            firstCoordinateLong = pointLong - numberOfImplementation * 0.0045

            nowLat = pointLati - numberOfImplementation * 0.0045
            nowLong = pointLong - numberOfImplementation * 0.0045

            # make gabLoc
            maxGab = numberOfImplementation * 0.0045 * 2
            gabList = [(0, 0), (maxGab, 0), (0, maxGab), (maxGab, maxGab)]
            for i in range(1, numberOfImplementation * 2):
                nowGab = i * 0.0045
                gabList.append((0, nowGab))
                gabList.append((maxGab, nowGab))
                gabList.append((nowGab, 0))
                gabList.append((nowGab, maxGab))

            for latGab, longGab in gabList:
                nowLat, nowLong = firstCoordinateLati - latGab, firstCoordinateLong - longGab

                busstopBodyJson = coordinateRequest(nowLat, nowLong)
                print("버스정류소 재검색 body데이터 1:", busstopBodyJson)

                resultBusStop, successCount = coordinateCheckResult(busstopBodyJson, successCount)
                if resultBusStop is not None and resultBusStop.find("경유") == -1:
                    break

            numberOfImplementation += 1

            #
            # busstopBodyJson = coordinateRequest(firstCoordinateLati, firstCoordinateLong)
            #
            # # 재검색 데이터 뒤에 숫자가 0이면 초기값 1이면 Lati에 +500m 2면 Long에 +500m -는 음수
            # # 검색결과가 하나이면 배열값이 아니므로 따로 분리하였음
            # resultBusStop, successCount = coordinateCheckResult(busstopBodyJson, successCount)
            # if resultBusStop is not None and resultBusStop.find("경유") == -1:
            #     break
            #
            # nowCoordinateLati = firstCoordinateLati + 0.0045
            # nowCoordinateLong = firstCoordinateLong
            #
            # busstopBodyJson = coordinateRequest(nowCoordinateLati, nowCoordinateLong)
            # print("버스정류소 재검색 body데이터 1:", busstopBodyJson)
            #
            # resultBusStop, successCount = coordinateCheckResult(busstopBodyJson, successCount)
            # if resultBusStop is not None and resultBusStop.find("경유") == -1:
            #     break
            #
            # # 현재좌표가 초기값이면 루프종료
            # while firstCoordinateLati != nowCoordinateLati or firstCoordinateLong != nowCoordinateLong:
            #     for i in range(numberOfImplementation * 2 - 1):
            #         nowCoordinateLati += 0.0045
            #
            #         busstopBodyJson = coordinateRequest(nowCoordinateLati, nowCoordinateLong)
            #         print("버스정류소 재검색 body데이터 1:", busstopBodyJson)
            #
            #         resultBusStop, successCount = coordinateCheckResult(busstopBodyJson, successCount)
            #         if resultBusStop is not None and resultBusStop.find("경유") == -1:
            #             break
            #
            #     for i in range(numberOfImplementation * 2):
            #         nowCoordinateLong += 0.0045
            #
            #         busstopBodyJson = coordinateRequest(nowCoordinateLati, nowCoordinateLong)
            #         print("버스정류소 재검색 body데이터 2:", busstopBodyJson)
            #
            #         resultBusStop, successCount = coordinateCheckResult(busstopBodyJson, successCount)
            #         if resultBusStop is not None and resultBusStop.find("경유") == -1:
            #             break
            #
            #     for i in range(numberOfImplementation * 2):
            #         nowCoordinateLati -= 0.0045
            #
            #         busstopBodyJson = coordinateRequest(nowCoordinateLati, nowCoordinateLong)
            #         print("버스정류소 재검색 body데이터 -1:", busstopBodyJson)
            #
            #         resultBusStop, successCount = coordinateCheckResult(busstopBodyJson, successCount)
            #         if resultBusStop is not None and resultBusStop.find("경유") == -1:
            #             break
            #
            #     for i in range(numberOfImplementation * 2 - 1):
            #         nowCoordinateLong -= 0.0045
            #
            #         busstopBodyJson = coordinateRequest(nowCoordinateLati, nowCoordinateLong)
            #         print("버스정류소 재검색 body데이터 -2:", busstopBodyJson)
            #
            #         resultBusStop, successCount = coordinateCheckResult(busstopBodyJson, successCount)
            #         if resultBusStop is not None and resultBusStop.find("경유") == -1:
            #             break
            #
            #     # 초기값으로 돌아가기
            #     nowCoordinateLong -= 0.0045
            numberOfImplementation += 1
    else:
        resultBusStop = busstopBodyJson.get("items").get("item")[0].get("nodenm")

    return resultBusStop  # 지금은 마지막에 검색된 곳을 리턴해줌
    # TODO pointLati와 버스정류장 거리를 피타고라스로 계산 후 가장 가까운 곳 추천


def getDestinationLoc(destination):
    """
    목적지명 기준으로 목저지의 위도, 경도을 알아냄. (이해한게 맞다면)

    :param destination: 목적지명 - string
    :return: 목적지 위도, 경도 - list(위도, 경도)
    """
    apiurl = "https://api.vworld.kr/req/search?"
    params = {
        # 장소검색 기준
        "service": "search",
        "request": "search",
        "crs": "EPSG:4326",
        # 목적지 설정 - destination으로 대체 되는 것 같음.
        "query": "경기대 수원캠퍼스",
        "type": "place",
        "format": "json",
        # 인증키 부분 지우고 V-world(디지털트윈국토)에서 발급받은 api 인증키 입력
        "key": getEnv("V_WORLD_KEY"),
    }
    response = requests.get(apiurl, params=params)
    res = [-1, -1]
    if response.status_code == 200:
        adressData = response.json()
        print("장소검색 데이터 :", response.json())

        # 결과 값의 x,y좌표 꺼내기
        # 중간에 배열 0은 첫번째 결과값을 꺼낸 것이므로 나중에 소비자가 선택가능하면 좋을 듯
        res[1] = float(adressData.get("response").get("result").get("items")[0].get("point").get("x"))
        res[0] = float(adressData.get("response").get("result").get("items")[0].get("point").get("y"))
    return res


# apiurl = "https://api.vworld.kr/req/address?"
# params = {
#     # 도로명, 지번주소 검색은 사용하지 않을 것 같지만 혹시모르니 일단 남겨둠
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
#     print("도로명주소 body검색 데이터 :", response.json())
#
#     print("장소검색, 도로명검색별 좌표 :", destinationPointLati, destinationPointLong,
#           response.json().get("response").get("result").get("point").get("y"),
#           response.json().get("response").get("result").get("point").get("x"))


if __name__ == "__main__":
    # 사용자위치는 임의설정(반경 500m내 버스정류장 없는 곳으로 하였음) 프론트에서 나중에 받을 예정
    userPointLong = 126.93540006310809
    userPointLati = 37.41909998804243
    busstopData = coordinateBusStopSearch(userPointLati, userPointLong)

    # 응답 출력
    print("출발지 버스정류소 :", busstopData)
    destinationPointLati, destinationPointLong = getDestinationLoc("")
    busstopData = coordinateBusStopSearch(destinationPointLati, destinationPointLong)
    # 응답 출력
    print("목적지 버스정류소 :", busstopData)
