import calendar
import parameter


def formation(inputtime):
    try:
        outputtime = inputtime[:-4]
    except:
        return ""
    if inputtime[-2:] == '00':
        outputtime = inputtime
    elif inputtime[-2:] == '30':
        outputtime = inputtime
    elif 0 < int(inputtime[-2:]) < 15:
        outputtime += inputtime[-4:-2]+'00'
    elif 15 < int(inputtime[-2:]) < 30:
        outputtime += inputtime[-4:-2]+'30'
    elif 30 < int(inputtime[-2:]) < 45:
        outputtime += inputtime[-4:-2]+'30'
    else:
        outputtime += str(int(inputtime[-4:-2])+1)+'00'

    return outputtime


def date_trasition(date):
    strdate=str(date)
    output = str(int(strdate[5:7]))+'/'+str(int(strdate[8:10]))

    return output


def check_day(date):
    if '-' in str(date):
        date = str(date)[:10].split('-')
        day = calendar.weekday(parameter.year, int(date[1]), int(date[2]))

    if '/' in str(date):
        date = date.split('/')
        day = calendar.weekday(parameter.year, int(date[0]), int(date[1]))

    return day


def mark_sunday(opsheet):
    for row in opsheet['日期'].index:
        cell = opsheet.loc[row, '日期']
        if type(cell) == type(''):
            if calendar.weekday(parameter.year, int(cell.split('/')[0]), int(cell.split('/')[1])) == 6:
                opsheet.loc[row, '日期'] = '例假日'
                if opsheet.loc[row, '項目'] != '星期日出工':
                    opsheet.loc[row, '項目'] = '例假日'

    return opsheet


def identify_interval(time):
    # 大夜 1700後/到隔天
    # 開始時間 2400前
    if int(time[:2]) >= 17:
        return 4
    # 開始時間 2400後
    if int(time[:2]) < 8 and int(time[5:7]) <= 8 and time[5:] != '0830':
        return 4

# 區間含800 含1900
    if int(time[:2]) < 8 and int(time[5:7]) >= 19 and time[5:] != '1900':
        return 3

# 區間含800
    if int(time[:2]) < 8 and int(time[5:7]) <= 19 and time[5:] != '1930':
        return 1

# 區間含1900
    if int(time[:2]) >= 8 and int(time[5:7]) >= 19 and time[5:] != '1900':
        return 2
# 日班
    if int(time[:2]) >= 8 and int(time[5:7]) <= 19 and time[5:] != '1930':
        return 0
# error
    return 5


