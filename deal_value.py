import numpy as np

import deal_time
import parameter


def table_overtime_fee(opindex, inindex, opsheet, insheet, title):
    if not opsheet.loc[opindex, '日期'].isnull().any():
        opsheet = table1_overtime_fee(opindex, opsheet, title)

    if not opsheet.loc[opindex, '　日期　'].isnull().any():
        opsheet = table2_overtime_fee(opindex, inindex, opsheet, insheet, title)

    return opsheet


def table1_overtime_fee(opindex, opsheet, title):
    time = list(opsheet.loc[opindex, '工作時間'])[0]

    if str(time) == '' or str(time) == 'nan':
        return opsheet

    if int(time[5:7]) >= 17 and time[5:] != '1700':
        sparehour = int(time[5:7]) - 17
        if time[7:] == '30':
            sparehour += 0.5
        opsheet.loc[opindex, '加班時間'] = sparehour

        if title == '吊車司機':
            title += str(list(opsheet.loc[opindex, '噸數'])[0])

        opsheet.loc[opindex, '加班鐘點費'] = parameter.fee[title]
        opsheet.loc[opindex, '小計'] = parameter.fee[title] * sparehour

    return opsheet


def table2_overtime_fee(opindex, inindex, opsheet, insheet, title):
    src_time = list(opsheet.loc[opindex, '　工作時間　'])[0]
    time_list = src_time.split('/')
    sparehour = 0
    for time in time_list:
        # 凌晨工時轉換
        if int(time[5:]) <= int(time[:4]):
            time = time[:5] + str(int(time[5:7])+24) + time[7:]

        lasth = int(time[5:7])
        lastm = int(time[7:])
        starh = int(time[0:2])
        starm = int(time[2:4])

        sparehour += lasth-starh
        if lastm-starm > 0:
            sparehour += 0.5
        elif lastm-starm < 0:
            sparehour -= 0.5

    if insheet.loc[inindex, '扣餐'] == 'V':
        sparehour -= 0.5

    opsheet.loc[opindex, '　加班時間　'] = sparehour

    if title == '吊車司機':
        title += str(list(opsheet.loc[opindex, '　噸數　'])[0])

    opsheet.loc[opindex, '　加班鐘點費　'] = parameter.fee[title]
    opsheet.loc[opindex, '　小計　'] = parameter.fee[title] * sparehour

    return opsheet


def sunday_overtime(opindex, ipindex, opsheet, ipsheet, title, dairyfee):
    sparehour = 0
    time = list(opsheet.loc[opindex, '　工作時間　'])[0]

    formated_time = time
    if int(time[5:]) <= int(time[:4]):
        formated_time = time[:5] + str(int(time[5:7])+24) + time[7:]

    # 中午加班
    if ipsheet.loc[ipindex, '中午未休'] == 'V':
        sparehour += 1

    time_index = deal_time.identify_interval(formated_time)

    # 早上加班
    if time_index == 1 or time_index == 3:
        sparehour += 8 - int(time[:2])
        if time[2:4] == '30':
            sparehour -= 0.5

    # 晚上加班
    if time_index == 2 or time_index == 3:
        sparehour += int(time[5:7]) - 17
        if time[7:9] == '30':
            sparehour += 0.5

    # 夜班
    if time_index == 4:
        lasth = int(time[5:7])
        lastm = int(time[7:])
        starh = int(time[0:2])
        starm = int(time[2:4])

        sparehour += lasth-starh
        if lastm-starm > 0:
            sparehour += 0.5
        elif lastm-starm < 0:
            sparehour -= 0.5

    if time_index != 4 and int(time[5:7]) >= 17 and time[5:] != '1700' and int(time[5:7]) <= 19 and time[5:] != '1930':
        sparehour += int(time[5:7]) - 17
        if time[7:9] == '30':
            sparehour += 0.5

    if ipsheet.loc[ipindex, '扣餐'] == 'V':
        sparehour -= 0.5

    opsheet.loc[opindex, '　加班時間　'] = sparehour

    if title == '吊車司機':
        title += str(list(opsheet.loc[opindex, '　噸數　'])[0])

    opsheet.loc[opindex, '　加班鐘點費　'] = parameter.fee[title]
    opsheet.loc[opindex, '　小計　'] = parameter.fee[title] * sparehour

    if int(list(opsheet.loc[opindex, '　工作時間　'])[0][:2]) >= 13:
        opsheet.loc[opindex, '　小計　'] += list(dairyfee)[0] / 2
    else:
        opsheet.loc[opindex, '　小計　'] += list(dairyfee)[0]

    return opsheet


def sat(opsheet, wage):
    before2 = wage / 30 / 8 * 1.33
    after2 = wage / 30 / 8 * 1.66
    workday = 0
    for i in opsheet['日期'].index:
        if str(opsheet.loc[i, '日期']) != 'nan':
            if deal_time.check_day(opsheet.loc[i, '日期']) == 5:
                if opsheet.loc[i, '項目'] != '休息日' and opsheet.loc[i, '項目'] != 'covid-19病假':
                    workday += 1

    opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '加班時間'] = 2 * workday
    opsheet.loc[opsheet['項目'] == '休息日出工(兩小時後)', '加班時間'] = 6 * workday
    opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '加班鐘點費'] = before2
    opsheet.loc[opsheet['項目'] == '休息日出工(兩小時後)', '加班鐘點費'] = after2
    opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '小計'] = round(2 * workday * before2)
    opsheet.loc[opsheet['項目'] == '休息日出工(兩小時後)', '小計'] = round(6 * workday * after2)

    return opsheet


def deligent(opsheet, title):
    for row in opsheet['項目']:
        if row != '':
            if row == '事假' or row == '病假' or row == '休息日' or row == '公假' or row == '特休-定檢' or row == '曠職':
                return opsheet

    if title != '行政人員':
        opsheet.loc[opsheet['項目'] == '全勤', '小計'] = 3000
    else:
        opsheet.loc[opsheet['項目'] == '全勤', '小計'] = 2000

    return opsheet


def rest(opsheet, wage):
    daycost = round(wage / 30)
    halfdaycost = round(wage / 30 / 2)
    busy = 0
    sick = 0
    skip = 0
    for row in opsheet['項目']:
        if row != '':
            if '事假' in row:
                busy += 1
            elif '病假' in row:
                sick += 1
            elif '曠職' in row:
                skip += 1

    total_day = busy + sick/2 + 2*skip
    sum = -1 * (daycost * busy + sick * halfdaycost + 2 * daycost * skip)
    opsheet.loc[opsheet['項目'] == '請假', '小計'] = sum
    opsheet.loc[opsheet['項目'] == '請假', '加班時間'] = total_day

    return opsheet


def repair_time_count(src):
    sparehour = 0
    timelist = src.split(',')
    for time in timelist:
        if int(time[5:]) <= int(time[:4]):
            time = time[:5] + str(int(time[5:7])+24) + time[7:]

        sparehour += int(time[5:7]) - int(time[0:2])
        if int(time[7:]) - int(time[2:4]) > 0:
            sparehour += 0.5
        elif int(time[7:]) - int(time[2:4]) < 0:
            sparehour -= 0.5

    return sparehour

