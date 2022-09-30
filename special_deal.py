import pandas as pd


def adjust(name, opsheet):
    name_list = ['蕭瑋榤', '楊宗澄', '楊潮陽', '林義翔', '陳憶如']
    if name in name_list:
        opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '加班鐘點費'] = 0
        opsheet.loc[opsheet['項目'] == '休息日出工(兩小時後)', '加班鐘點費'] = 0
        opsheet.loc[opsheet['項目'] == '休息日出工(前兩小時)', '小計'] = 0
        opsheet.loc[opsheet['項目'] == '休息日出工(兩小時後)', '小計'] = 0

    return opsheet


def plus400(ipindex, ipsheet, opsheet, title):
    if title != '吊車司機':
        return opsheet

    if ipsheet.loc[ipindex, '噸數'] == '400T':
        index = opsheet.loc[opsheet['項目'] == '底薪'].index[0] - 2
        opsheet.loc[index, '　工作地點　'] = '400T補貼'
        opsheet.loc[index, '　加班鐘點費　'] = 2000
        if str(opsheet.loc[index, '　加班時間　']) != 'nan':
            opsheet.loc[index, '　加班時間　'] += 1
        else:
            opsheet.loc[index, '　加班時間　'] = 1
        opsheet.loc[index, '　小計　'] = opsheet.loc[index, '　加班鐘點費　'] * opsheet.loc[index, '　加班時間　']

    if ipsheet.loc[ipindex, '噸數'] == '400T桿':
        index = opsheet.loc[opsheet['項目'] == '底薪'].index[0] - 1
        opsheet.loc[index, '　工作地點　'] = '400T桿補貼'
        opsheet.loc[index, '　加班鐘點費　'] = 3000
        if str(opsheet.loc[index, '　加班時間　']) != 'nan':
            opsheet.loc[index, '　加班時間　'] += 1
        else:
            opsheet.loc[index, '　加班時間　'] = 1
        opsheet.loc[index, '　小計　'] = opsheet.loc[index, '　加班鐘點費　'] * opsheet.loc[index, '　加班時間　']

    return opsheet


def special_fee(opsheet):
    T45_fee = 0
    T80_fee = 0

    for row in opsheet.index:
        if pd.notnull(opsheet.loc[row, '噸數']) or pd.notnull(opsheet.loc[row, '　噸數　']):
            if opsheet.loc[row, '噸數'] == '45T' or opsheet.loc[row, '噸數'] == '　45T　':
                T45_fee += 1
            elif opsheet.loc[row, '噸數'] == '80T' or opsheet.loc[row, '　噸數　'] == '　80T　':
                T80_fee += 1

        opsheet.loc[opsheet['項目'] == '勞保費', '　工作地點　'] = "45T津貼"
        opsheet.loc[opsheet['項目'] == '勞保費', '　加班時間　'] = T45_fee
        opsheet.loc[opsheet['項目'] == '勞保費', '　加班鐘點費　'] = 500
        opsheet.loc[opsheet['項目'] == '勞保費', '　小計　'] = T45_fee * 500

        opsheet.loc[opsheet['項目'] == '健保費', '　工作地點　'] = "80T津貼"
        opsheet.loc[opsheet['項目'] == '健保費', '　加班時間　'] = T80_fee
        opsheet.loc[opsheet['項目'] == '健保費', '　加班鐘點費　'] = 600
        opsheet.loc[opsheet['項目'] == '健保費', '　小計　'] = T80_fee * 600

    return opsheet


def special_fee2(opsheet):
    times = 0
    for row in opsheet.index:
        if opsheet.loc[row, '項目'] == '出車' or opsheet.loc[row, '項目'] == '星期日出工':
            times += 1

    opsheet.loc[opsheet['項目'] == '勞保費', '　工作地點　'] = "出車津貼"
    opsheet.loc[opsheet['項目'] == '勞保費', '　加班時間　'] = times
    opsheet.loc[opsheet['項目'] == '勞保費', '　加班鐘點費　'] = 300
    opsheet.loc[opsheet['項目'] == '勞保費', '　小計　'] = times * 300

    return opsheet

