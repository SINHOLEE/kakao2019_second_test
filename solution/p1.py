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


def get_calls(elevator_id, calls):
    calls = filter(lambda call: (int(call['start']) % 2 == elevator_id // 2, int(call['end']) % 2 == elevator_id % 2), calls)
    calls = sorted(calls, key=lambda call: (call['start'], call['end']))
    print("*************elevator_id: %s* start: %s, end: %s %s, %s *******" % (elevator_id, calls["start"], call["end"], elevator_id // 2, elevator_id % 2))
    print(calls)
    return calls

def p_simulator(n):
    user = 'tester'
    problem = n
    count = 4

    ret = start(user, problem, count)
    token = ret['token']
    print('Token for %s is %s' % (user, token))

    cnt = 0
    # 태울곳
    while True:
        oncall_res = oncalls(token)
        origin_calls = oncall_res["calls"]
        elevators = oncall_res["elevators"]
        action_bucket = []
        will_enter_by_calls = set()
        will_exit_by_passengers = set()
        for elevator_id in range(4):
            calls = get_calls(elevator_id, origin_calls)
            floor = elevators[elevator_id]['floor']
            passengers = elevators[elevator_id]["passengers"]
            status = elevators[elevator_id]["status"]
            print("------------------")
            print(cnt)
            pprint(calls)
            print("floor" , elevators[elevator_id]['floor'])
        
            if status == "STOPPED":  # 멈췄을때
                # 열지 말지 판단.
                for passenger in passengers:
                    if passenger['end'] == floor: # 내릴 사람이 있으면 열고
                        action_bucket.append({'elevator_id': elevator_id, 'command': 'OPEN'})
                        break
                else: # 내릴 사람이 없으면 태울 사람이 있는지 판단.
                    for call in calls: 
                        if len(passengers) < 8 and call["start"] == floor: # 탈사람이 있으면 열어라
                            action_bucket.append({'elevator_id': elevator_id, 'command': 'OPEN'})
                            break
                    else: # 내릴사람도 없고 태울 사람도 없다면
                        # 위로갈지 내려갈지 판단해라.()어떻게?
                        for passenger in passengers: # 엘리베이터 안에 있는 사람 중
                                if passenger['end'] > floor:  # 의 출발지를 기준으로 높으면 올라가고
                                    action_bucket.append({'elevator_id': elevator_id, 'command': 'UP'})
                                    break
                                else: # 출발지가 낮으면 내려가라
                                    action_bucket.append({'elevator_id': elevator_id, 'command': 'DOWN'})
                                    break
                        else: # 엘리베이터에 사람이 없다면
                            for call in calls: # 콜에서 태울 방향을 찾는다
                                if call["start"] > floor: # 탈사람이 있으면 위로 가라
                                    action_bucket.append({'elevator_id': elevator_id, 'command': 'UP'})
                                    break
                                else: # 출발지가 낮으면 내려가라
                                    action_bucket.append({'elevator_id': elevator_id, 'command': 'DOWN'})
                                    break
                            else: # 태울 방향도 없고, 타ㅏ고있는 사람도 없다면
                                action_bucket.append({'elevator_id': elevator_id, 'command': 'STOP'})
                                print("말도안댐")
            elif status == "OPENED":  # 열렸을때
                call_ids = []
                for passenger in passengers: 
                    if not passenger["id"] in will_exit_by_passengers and passenger["end"] == floor:
                        call_ids.append(passenger["id"])
                        will_exit_by_passengers.add(passenger["id"])
                if len(call_ids):  # 내릴 사람이 있으면 내리고
                    action_bucket.append({'elevator_id': elevator_id, 'command': 'EXIT', 'call_ids':call_ids})
                else:
                    call_ids = []
                    print("pass nums: ", len(passengers))
                    for call in calls: # 탈사람 타라
                        if len(passengers) == 8:
                            break
                        if not call["id"] in will_enter_by_calls and call["start"] == floor:
                            call_ids.append(call["id"])
                            will_enter_by_calls.add(call["id"])
                        if len(call_ids) + len(passengers) >= 8:
                            break
                    if len(call_ids): # 탈사람이 한명이라도 있으면 타고
                        
                        action_bucket.append({'elevator_id': elevator_id, 'command': 'ENTER', 'call_ids':call_ids})
                    else: # 내릴사람도 탈사람도 없으면 닫아라
                        action_bucket.append({'elevator_id': elevator_id, 'command': 'CLOSE'})
            elif status == "UPWARD":  # 위로 가는 중일때
                for passenger in passengers: 
                    # 내릴 승객이 있으면
                    if passenger['end'] == floor: # 내릴 사람이 있으면 열고,
                        #문을 열어라
                        action_bucket.append({'elevator_id': elevator_id, 'command': 'STOP'})
                        break
                # 없으면
                else:
                    for call in calls:
                        if call['start'] == floor:
                            # 열어라
                            action_bucket.append({'elevator_id': elevator_id, 'command': 'STOP'})
                            break
                    # 아니면
                    else:
                        # 올라가라
                        action_bucket.append({'elevator_id': elevator_id, 'command': 'UP'})
            elif status == "DOWNWARD":  # 내려가는 중일때
                for passenger in passengers: 
                    # 내릴 승객이 있으면
                    if passenger['end'] == floor: # 내릴 사람이 있으면 열고,
                        #문을 열어라
                        action_bucket.append({'elevator_id': elevator_id, 'command': 'STOP'})
                        break
                # 없으면
                else:
                    for call in calls:
                        if call['start'] == floor:
                            # 열어라
                            action_bucket.append({'elevator_id': elevator_id, 'command': 'STOP'})
                            break
                    # 아니면
                    else:
                        #내려가라
                        action_bucket.append({'elevator_id': elevator_id, 'command': 'DOWN'})
        cnt += 1
        print(action_bucket)
        response = action(token, action_bucket)
        pprint(response)
        if response["is_end"]:
            print('++++++++++++++fin+++++++++++++')
            break

if __name__ == '__main__':
    # p_simulator(0)
    # p_simulator(1)
    p_simulator(2)
