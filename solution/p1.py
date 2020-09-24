import requests
from pprint import pprint

url = 'http://localhost:8000'


def start(user, problem, count):
    uri = url + '/start' + '/' + user + '/' + str(problem) + '/' + str(count)
    return requests.post(uri).json()


def oncalls(token):
    uri = url + '/oncalls'
    return requests.get(uri, headers={'X-Auth-Token': token}).json()


def action(token, cmds):
    uri = url + '/action'
    return requests.post(uri, headers={'X-Auth-Token': token}, json={'commands': cmds}).json()




def p1_simulator():
    user = 'tester'
    problem = 1
    count = 1

    ret = start(user, problem, count)
    token = ret['token']
    print('Token for %s is %s' % (user, token))
    dic = {}
    for i in range(200):
        oncall_res = oncalls(token)
        response = action(token, [{'elevator_id': 0, 'command': 'STOP'}])
    # pprint(oncall_res)    
    oncall_res = oncalls(token)
    calls = oncall_res["calls"]
    elevators = oncall_res["elevators"]
    calls = sorted(calls, key=lambda call: (call['start'], call['end']))
    pprint(calls)
    pprint(elevators)
    pprint(response)

    cnt = 0
    # 태울곳
    while True:
        oncall_res = oncalls(token)
        calls = oncall_res["calls"]
        elevators = oncall_res["elevators"]
        calls = sorted(calls, key=lambda call: (call['start'], call['end']))
        print("------------------")
        print(cnt)
        pprint(calls)
        pprint(response)
        print("floor" , elevators[0]['floor'])
        if response["is_end"]:
            print('++++++++++++++fin+++++++++++++')
            break
        if len(elevators[0]["passengers"]): # 승객이 있다면
            floor = elevators[0]["floor"]
            passengers = elevators[0]["passengers"]

            if elevators[0]["status"] == "STOPPED":  # 멈췄을때
                print("승객있고, 멈춤")
                # 열지 말지 판단.
                
                for passenger in passengers:
                    if passenger['end'] == floor: # 내릴 사람이 있으면 열고
                        response = action(token, [{'elevator_id': 0, 'command': 'OPEN'}])
                        break
                else: # 내릴 사람이 없으면 태울 사람이 있는지 판단.
                    for call in calls: 
                        if len(passengers) < 8 and call["start"] == floor: # 탈사람이 있으면 열어라
                            response = action(token, [{'elevator_id': 0, 'command': 'OPEN'}])
                            break
                    else: # 내릴사람도 없고 태울 사람도 없다면
                        # 위로갈지 내려갈지 판단해라.()어떻게?
                        for passenger in passengers: # 엘리베이터 안에 있는 사람 중
                                if passenger['end'] > floor:  # 의 출발지를 기준으로 높으면 올라가고
                                    response = action(token, [{'elevator_id': 0, 'command': 'UP'}])
                                    break
                                else: # 출발지가 낮으면 내려가라
                                    response = action(token, [{'elevator_id': 0, 'command': 'DOWN'}])
                                    break
                        else: # 엘리베이터에 사람이 없다면
                            for call in calls: # 콜에서 태울 방향을 찾는다
                                if call["start"] > floor: # 탈사람이 있으면 위로 가라
                                    response = action(token, [{'elevator_id': 0, 'command': 'UP'}])
                                    break
                                else: # 출발지가 낮으면 내려가라
                                    response = action(token, [{'elevator_id': 0, 'command': 'DOWN'}])
                                    break
                            else: # 태울 방향도 없고, 타ㅏ고있는 사람도 없다면
                                print("말도안댐")
            elif elevators[0]["status"] == "OPENED":  # 열렸을때
                print("승객있고, 열림")
                call_ids = []
                for passenger in passengers: 
                    if passenger["end"] == floor:
                        call_ids.append(passenger["id"])
                if len(call_ids):  # 내릴 사람이 있으면 내리고
                    response = action(token, [{'elevator_id': 0, 'command': 'EXIT', 'call_ids':call_ids}])
                else:
                    call_ids = []
                    # print("pass nums: ", len(passengers))
                    for call in calls: # 탈사람 타라
                        if len(passengers) == 8:
                            break
                        if call["start"] == floor:
                            call_ids.append(call["id"])
                        if len(call_ids) + len(passengers) >= 8:
                            break
                    if len(call_ids): # 탈사람이 한명이라도 있으면 타고
                        response = action(token, [{'elevator_id': 0, 'command': 'ENTER', 'call_ids':call_ids}])    
                    else: # 내릴사람도 탈사람도 없으면 닫아라
                        response = action(token, [{'elevator_id': 0, 'command': 'CLOSE'}])
                    
            elif elevators[0]["status"] == "UPWARD":  # 위로 가는 중일때
                print("승객있고, 위로감")
                for passenger in passengers: 
                    # 내릴 승객이 있으면
                    if passenger['end'] == floor: # 내릴 사람이 있으면 열고,
                        #문을 열어라
                        response = action(token, [{'elevator_id': 0, 'command': 'STOP'}])
                        break
                # 없으면
                else:
                    # 올라가라
                    response = action(token, [{'elevator_id': 0, 'command': 'UP'}])
                    
            elif elevators[0]["status"] == "DOWNWARD":  # 내려가는 중일때
                print("승객있고, 아래로감")
                for passenger in passengers: 
                    # 내릴 승객이 있으면
                    if passenger['end'] == floor: # 내릴 사람이 있으면 열고,
                        #문을 열어라
                        response = action(token, [{'elevator_id': 0, 'command': 'STOP'}])
                        break
                # 없으면
                else:
                    # 내려가라
                    response = action(token, [{'elevator_id': 0, 'command': 'DOWN'}])
                    
        else: # 현재 승객이 없다면.
            floor = elevators[0]["floor"]
            if elevators[0]["status"] == "STOPPED":  # 멈췄을때
                print("승객없고, 멈춤")
                # 탈 사람이 있다면
                for call in calls: 
                    if call["start"] == floor: # 탈사람이 있으면 열어라
                        # 열어라
                        response = action(token, [{'elevator_id': 0, 'command': 'OPEN'}])
                        break
                else:  #탈사람 없다면 # 끝 아님?
                #내려갈지 판단해라.()어떻게?
                    for call in calls: # 콜중에
                        # 위로 갈 상황이면
                        if call['start'] > floor:  # 의 출발지를 기준으로 높으면 올라가고
                            response = action(token, [{'elevator_id': 0, 'command': 'UP'}])
                            break
                        # 아니면
                        else: # 출발지가 낮으면 내려가라
                            response = action(token, [{'elevator_id': 0, 'command': 'DOWN'}])
                            break
                    else:
                        response = action(token, [{'elevator_id': 0, 'command': 'STOP'}])

            elif elevators[0]["status"] == "OPENED":  # 열렸을때
                print("승객없고, 열림")
                call_ids = []
                for call in calls:
                    if call['start'] == floor:
                        call_ids.append(call['id'])
                    if len(call_ids) >= 8:
                        break
                if len(call_ids):  # 탈 사람이 있다면
                    response = action(token, [{'elevator_id': 0, 'command': 'ENTER', 'call_ids':call_ids}])
                else: # 탈 사람이 하나도 없으면
                    # 닫아라.
                    response = action(token, [{'elevator_id': 0, 'command': 'CLOSE'}])
            elif elevators[0]["status"] == "UPWARD":  # 위로 가는 중일때
                print("승객없고, 위로감")
                # 태울 사람이 있으면
                for call in calls:
                    if call['start'] == floor:
                        # 열어라
                        response = action(token, [{'elevator_id': 0, 'command': 'STOP'}])
                        break
                # 아니면
                else:
                    # 올라가라
                    response = action(token, [{'elevator_id': 0, 'command': 'UP'}])
                    
            elif elevators[0]["status"] == "DOWNWARD":  # 내려가는 중일때
                print("승객없고, 아래로감")
                # 태울 사람이 있으면
                for call in calls:
                    if call['start'] == floor:
                        # 열어라
                        response = action(token, [{'elevator_id': 0, 'command': 'STOP'}])
                        break
                # 아니면
                else:
                    #내려가라
                    response = action(token, [{'elevator_id': 0, 'command': 'DOWN'}])
                    
                # 태울사람 있으면
                    # 열어라
                # 아니면
        cnt += 1


if __name__ == '__main__':
    p1_simulator()
