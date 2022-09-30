import numpy as np
import pandas as pd
import calendar
import parameter

c = calendar.Calendar()


def create_table(name):
    # 根據輸入內容月份加入輸出表的日期
    a = list(c.itermonthdays2(parameter.year, parameter.month))  # 日期+星期
    date = []
    for row in a:
        if row[0] != 0:
            # if(row[1]!= 6):
            date.append(str(parameter.month)+'/'+str(row[0]))
            # else:
            #    date.append("例假日")

    items = []
    for i in range(len(date)):
        items.append("待命")
    items.append("")
    items.append("")
    items.append("底薪")
    items.append("職務加級")
    items.append("全勤")
    items.append("休息日出工(前兩小時)")
    items.append("休息日出工(兩小時後)")
    items.append("請假")
    items.append("勞保費")
    items.append("健保費")
    items.append("租屋津貼")
    items.append("久任津貼")
    items.append("瑞勵點工")
    items.append("")
    items.append("總計")

    while len(date) < len(items):
        date.append(np.NAN)

    initial = pd.DataFrame({
        '項目': items,
        '日期': date,
        '噸數': np.NAN,
        '工作地點': np.NAN,
        '工作時間': np.NAN,
        '加班時間': np.NAN,
        '加班鐘點費': np.NAN,
        '小計': np.NAN,
        '　': np.NAN,
        '　日期　': np.NAN,
        '　噸數　': np.NAN,
        '　工作地點　': np.NAN,
        '　工作時間　': np.NAN,
        '　日薪　': np.NAN,
        '　加班時間　': np.NAN,
        '　加班鐘點費　': np.NAN,
        '　小計　': np.NAN
    })
    return initial
