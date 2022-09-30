import numpy as np
import pandas as pd
from openpyxl.utils import get_column_letter

import parameter
import deal_value
import deal_time
import special_deal


def rest_fill(opsheet, ipsheet):
    for row in ipsheet.index:
        datelist = str(ipsheet.loc[row, '日期'])[5:10].split('-')
        date = str(int(datelist[0])) + '/' + str(int(datelist[1]))

        if '特休' in ipsheet.loc[row, '假別'] and ipsheet.loc[row, '假別'] != '特休-定檢':
            opsheet.loc[opsheet['日期'] == date, '項目'] = '特休'
        if '換休' in ipsheet.loc[row, '假別']:
            opsheet.loc[opsheet['日期'] == date, '項目'] = '特休'
        if ipsheet.loc[row, '假別'] == '特休-定檢':
            opsheet.loc[opsheet['日期'] == date, '項目'] = '特休-定檢'
        if '事假' in ipsheet.loc[row, '假別']:
            opsheet.loc[opsheet['日期'] == date, '項目'] = '事假'
        if '病假' in ipsheet.loc[row, '假別'] and ipsheet.loc[row, '假別'] != 'covid-19病假':
            opsheet.loc[opsheet['日期'] == date, '項目'] = '病假'
        if 'covid-19病假' in ipsheet.loc[row, '假別']:
            opsheet.loc[opsheet['日期'] == date, '項目'] = 'coivid-19病假'
        if '休息日' in ipsheet.loc[row, '假別']:
            opsheet.loc[opsheet['日期'] == date, '項目'] = '休息日'
        if '公假' in ipsheet.loc[row, '假別']:
            opsheet.loc[opsheet['日期'] == date, '項目'] = '公假'
        if '曠職' in ipsheet.loc[row, '假別']:
            opsheet.loc[opsheet['日期'] == date, '項目'] = '曠職'

    return opsheet


def work_fill(opindex, ipindex, opsheet, ipsheet, title, day):
    if str(title) != 'nan':
        if '助手' in title:
            title = '助手'

    opsheet.loc[opindex, '項目'] = "出車"
    opsheet.loc[opindex, '噸數'] = ipsheet.loc[ipindex, '噸數']
    opsheet.loc[opindex, '工作地點'] = ipsheet.loc[ipindex, '施工地點']

    special_deal.plus400(ipindex, ipsheet, opsheet, title)

    # 待優化結構
    if ipsheet.loc[ipindex, '中午未休'] == 'V':
        opsheet.loc[opindex, '　日期　'] = opsheet.loc[opindex, '日期']
        opsheet.loc[opindex, '　噸數　'] = ipsheet.loc[ipindex, '噸數']
        opsheet.loc[opindex, '　工作地點　'] = ipsheet.loc[ipindex, '施工地點']
        opsheet.loc[opindex, '　工作時間　'] = "1200-1300"

    opsheet = time_arrange(opindex, opsheet, ipsheet.loc[ipindex, '時間'])
    opsheet = deal_value.table_overtime_fee(opindex, ipindex, opsheet, ipsheet, title)

    return opsheet


def time_arrange(opindex, opsheet, time):
    if time == "":
        return opsheet

    formated_time = time
    if int(time[5:]) <= int(time[:4]):
        formated_time = time[:5] + str(int(time[5:7])+24) + time[7:]

    interval_index = deal_time.identify_interval(formated_time)

    if interval_index == 0:
        opsheet.loc[opindex, '工作時間'] = time

    if interval_index == 1 or interval_index == 3:
        sparetime = time[:5]+"0800"
        time = "0800-"+time[5:]
        opsheet.loc[opindex, '工作時間'] = time
        opsheet.loc[opindex, '　日期　'] = opsheet.loc[opindex, '日期']
        opsheet.loc[opindex, '　噸數　'] = opsheet.loc[opindex, '噸數']
        opsheet.loc[opindex, '　工作地點　'] = opsheet.loc[opindex, '工作地點']

        if opsheet.loc[opindex, '　工作時間　'].isnull().any():
            opsheet.loc[opindex, '　工作時間　'] = sparetime
        else:
            opsheet.loc[opindex, '　工作時間　'] += '/' + sparetime

    if interval_index == 2 or interval_index == 3:
        sparetime = "1700-"+time[5:]
        time = time[:5]+"1700"
        opsheet.loc[opindex, '工作時間'] = time
        opsheet.loc[opindex, '　日期　'] = opsheet.loc[opindex, '日期']
        opsheet.loc[opindex, '　噸數　'] = opsheet.loc[opindex, '噸數']
        opsheet.loc[opindex, '　工作地點　'] = opsheet.loc[opindex, '工作地點']

        if opsheet.loc[opindex, '　工作時間　'].isnull().any():
            opsheet.loc[opindex, '　工作時間　'] = sparetime
        else:
            opsheet.loc[opindex, '　工作時間　'] += '/' + sparetime

    if interval_index == 4:
        opsheet.loc[opindex, '　日期　'] = opsheet.loc[opindex, '日期']
        opsheet.loc[opindex, '　噸數　'] = opsheet.loc[opindex, '噸數']
        opsheet.loc[opindex, '　工作地點　'] = opsheet.loc[opindex, '工作地點']
        opsheet.loc[opindex, '項目'] = '待命'
        opsheet.loc[opindex, '噸數'] = ''
        opsheet.loc[opindex, '工作地點'] = ''

        if opsheet.loc[opindex, '　工作時間　'].isnull().any():
            opsheet.loc[opindex, '　工作時間　'] = time
        else:
            opsheet.loc[opindex, '　工作時間　'] += '/' + time

    if interval_index == 5:
        print("date error")

    return opsheet


def others(item, opsheet, ipsheet):
    opsheet.loc[opsheet['項目'] == item, '小計'] = ipsheet.loc[ipsheet.index[0], item]

    return opsheet


def sunday(opindex, ipindex, opsheet, ipsheet, fee, title):
    if str(title) != 'nan':
        if '助手' in title:
            title = '助手'

    opsheet.loc[opindex, '項目'] = '星期日出工'
    opsheet.loc[opindex, '　日薪　'] = list(fee)[0]
    opsheet.loc[opindex, '　日期　'] = opsheet.loc[opindex, '日期']
    opsheet.loc[opindex, '　噸數　'] = ipsheet.loc[ipindex, '噸數']
    opsheet.loc[opindex, '　工作地點　'] = ipsheet.loc[ipindex, '施工地點']
    opsheet.loc[opindex, '　工作時間　'] = ipsheet.loc[ipindex, '時間']

    special_deal.plus400(ipindex, ipsheet, opsheet, title)

    opsheet = deal_value.sunday_overtime(opindex, ipindex, opsheet, ipsheet, title, fee)

    return opsheet


def repair_fee(ipindex, opsheet, ipsheet, name):
    if '組/拆桿' in ipsheet.loc[ipindex, '工作名稱']:
        # 時間
        if str(list(opsheet.loc[opsheet['項目'] == '底薪', '　加班時間　'])[0]) == 'nan':
            opsheet.loc[opsheet['項目'] == '底薪', '　加班時間　'] = 1
        else:
            opsheet.loc[opsheet['項目'] == '底薪', '　加班時間　'] += 1

        # 日期
        if str(list(opsheet.loc[opsheet['項目'] == '底薪', '　日期　'])[0]) == 'nan':
            opsheet.loc[opsheet['項目'] == '底薪', '　日期　'] = deal_time.date_trasition(ipsheet.loc[ipindex, '日期'])
        else:
            opsheet.loc[opsheet['項目'] == '底薪', '　日期　'] += ',' + deal_time.date_trasition(ipsheet.loc[ipindex, '日期'])

        opsheet.loc[opsheet['項目'] == '底薪', '　工作地點　'] = '組/拆桿'
        opsheet.loc[opsheet['項目'] == '底薪', '　加班鐘點費　'] = 500
        opsheet.loc[opsheet['項目'] == '底薪', '　小計　'] = opsheet.loc[opsheet['項目'] == '底薪', '　加班時間　'] * opsheet.loc[opsheet['項目'] == '底薪', '　加班鐘點費　']

    elif '板車兼助手' in ipsheet.loc[ipindex, '工作名稱']:
        # 時間
        if str(list(opsheet.loc[opsheet['項目'] == '職務加級', '　加班時間　'])[0]) == 'nan':
            opsheet.loc[opsheet['項目'] == '職務加級', '　加班時間　'] = 1
        else:
            opsheet.loc[opsheet['項目'] == '職務加級', '　加班時間　'] += 1

        # 日期
        if str(list(opsheet.loc[opsheet['項目'] == '職務加級', '　日期　'])[0]) == 'nan':
            opsheet.loc[opsheet['項目'] == '職務加級', '　日期　'] = deal_time.date_trasition(ipsheet.loc[ipindex, '日期'])
        else:
            opsheet.loc[opsheet['項目'] == '職務加級', '　日期　'] += ',' + deal_time.date_trasition(ipsheet.loc[ipindex, '日期'])

        opsheet.loc[opsheet['項目'] == '職務加級', '　工作地點　'] = '板車兼助手'
        opsheet.loc[opsheet['項目'] == '職務加級', '　加班鐘點費　'] = 300
        opsheet.loc[opsheet['項目'] == '職務加級', '　小計　'] = opsheet.loc[opsheet['項目'] == '職務加級', '　加班時間　'] * opsheet.loc[opsheet['項目'] == '職務加級', '　加班鐘點費　']

    elif '維修' in ipsheet.loc[ipindex, '工作名稱']:
        # 日期
        if str(list(opsheet.loc[opsheet['項目'] == '全勤', '　日期　'])[0]) == 'nan':
            opsheet.loc[opsheet['項目'] == '全勤', '　日期　'] = deal_time.date_trasition(ipsheet.loc[ipindex, '日期'])
        else:
            opsheet.loc[opsheet['項目'] == '全勤', '　日期　'] += ',' + deal_time.date_trasition(ipsheet.loc[ipindex, '日期'])

        # 時間
        if str(list(opsheet.loc[opsheet['項目'] == '全勤', '　加班時間　'])[0]) == 'nan':
            opsheet.loc[opsheet['項目'] == '全勤', '　工作時間　'] = ipsheet.loc[ipindex, '時間']
        else:
            opsheet.loc[opsheet['項目'] == '全勤', '　工作時間　'] += ',' + ipsheet.loc[ipindex, '時間']

        opsheet.loc[opsheet['項目'] == '全勤', '　加班時間　'] = deal_value.repair_time_count(list(opsheet.loc[opsheet['項目'] == '全勤', '　工作時間　'])[0])
        opsheet.loc[opsheet['項目'] == '全勤', '　加班鐘點費　'] = 300
        if name == '蕭瑋榤':
            opsheet.loc[opsheet['項目'] == '全勤', '　加班鐘點費　'] = 500
        elif name == '楊宗澄':
            opsheet.loc[opsheet['項目'] == '全勤', '　加班鐘點費　'] = 400
        elif name == '凃政良':
            opsheet.loc[opsheet['項目'] == '全勤', '　加班鐘點費　'] = 400

        opsheet.loc[opsheet['項目'] == '全勤', '　工作地點　'] = '維修'
        opsheet.loc[opsheet['項目'] == '全勤', '　小計　'] = opsheet.loc[opsheet['項目'] == '全勤', '　加班時間　'] * opsheet.loc[opsheet['項目'] == '全勤', '　加班鐘點費　']

    elif '路程' in ipsheet.loc[ipindex, '工作名稱']:
        # 日期
        if str(list(opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '　日期　'])[0]) == 'nan':
            opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '　日期　'] = deal_time.date_trasition(ipsheet.loc[ipindex, '日期'])
        else:
            opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '　日期　'] += ',' + deal_time.date_trasition(ipsheet.loc[ipindex, '日期'])

        # 時間
        if str(list(opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '　工作時間　'])[0]) == 'nan':
            opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '　工作時間　'] = ipsheet.loc[ipindex, '時間']
        else:
            opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '　工作時間　'] += ',' + ipsheet.loc[ipindex, '時間']

        opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '　工作地點　'] = '路程'
        opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '　加班鐘點費　'] = 400
        opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '　加班時間　'] = deal_value.repair_time_count(list(opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '　工作時間　'])[0])
        opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '　小計　'] = opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '　加班時間　'] * opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '　加班鐘點費　']

    return opsheet


def crossing_asist_fee(ipindex, opsheet, ipsheet, rank):
    rank2 = parameter.t_rank[ipsheet.loc[ipindex, '噸數']]
    rank1 = parameter.t_rank[rank]
    gap = rank2 - rank1
    if gap == 1:
        # 日期
        if str(list(opsheet.loc[opsheet['項目'] == '休息日出工(兩小時後)', '　日期　'])[0]) == 'nan':
            opsheet.loc[opsheet['項目'] == '休息日出工(兩小時後)', '　日期　'] = deal_time.date_trasition(ipsheet.loc[ipindex, '日期'])
        else:
            opsheet.loc[opsheet['項目'] == '休息日出工(兩小時後)', '　日期　'] += ',' + deal_time.date_trasition(ipsheet.loc[ipindex, '日期'])

        if str(list(opsheet.loc[opsheet['項目'] == '休息日出工(兩小時後)', '　加班時間　'])[0]) == 'nan':
            opsheet.loc[opsheet['項目'] == '休息日出工(兩小時後)', '　加班時間　'] = 1
        else:
            opsheet.loc[opsheet['項目'] == '休息日出工(兩小時後)', '　加班時間　'] += 1

        opsheet.loc[opsheet['項目'] == '休息日出工(兩小時後)', '　工作地點　'] = '跟大車'
        opsheet.loc[opsheet['項目'] == '休息日出工(兩小時後)', '　加班鐘點費　'] = 100
        opsheet.loc[opsheet['項目'] == '休息日出工(兩小時後)', '　小計　'] = opsheet.loc[opsheet['項目'] == '休息日出工(兩小時後)', '　加班時間　'] * 100

    elif gap >= 2:
        if str(list(opsheet.loc[opsheet['項目'] == '請假', '　日期　'])[0]) == 'nan':
            opsheet.loc[opsheet['項目'] == '請假', '　日期　'] = deal_time.date_trasition(ipsheet.loc[ipindex, '日期'])
        else:
            opsheet.loc[opsheet['項目'] == '請假', '　日期　'] += ',' + deal_time.date_trasition(ipsheet.loc[ipindex, '日期'])

        if str(list(opsheet.loc[opsheet['項目'] == '請假', '　加班時間　'])[0]) == 'nan':
            opsheet.loc[opsheet['項目'] == '請假', '　加班時間　'] = 1
        else:
            opsheet.loc[opsheet['項目'] == '請假', '　加班時間　'] += 1

        opsheet.loc[opsheet['項目'] == '請假', '　工作地點　'] = '跟大車'
        opsheet.loc[opsheet['項目'] == '請假', '　加班鐘點費　'] = 200
        opsheet.loc[opsheet['項目'] == '請假', '　小計　'] = opsheet.loc[opsheet['項目'] == '請假', '　加班時間　'] * 200

    return opsheet

