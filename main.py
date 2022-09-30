import os

import numpy as np
import pandas as pd
from openpyxl.utils import get_column_letter

import deal_salary
import deal_time
import deal_value
import table_initial
import special_deal
import parameter
from create_all_table import all_salary

# 開檔
try:
    input_file = pd.read_excel("輸入檔案.xlsx", sheet_name='出車總表')
    parameter.employee_info = pd.read_excel("輸入檔案.xlsx", sheet_name='薪資結構')
    others_file = pd.read_excel("輸入檔案.xlsx", sheet_name='維修表')
    rest_info = pd.read_excel("輸入檔案.xlsx", sheet_name='假表')
except Exception:
    print("開檔發生問題")
    quit()

try:
    path = os.path.join(os.getcwd(), "員工薪資.xlsx")
    writer = pd.ExcelWriter(path, engine='openpyxl')

except Exception:
    print("請先關閉輸出檔")
    quit()

opsheet = pd.DataFrame()

try:
    parameter.year = int(str(input_file.loc[0, '日期'])[:4])
    parameter.month = int(str(input_file.loc[0, '日期'])[5:7])
except Exception:
    print("初始化時間發生問題")
    quit()

# 時間調整
try:
    for row in input_file.index:
        input_file.loc[row, "時間"] = deal_time.formation(input_file.loc[row, "時間"])

    for row in others_file.index:
        others_file.loc[row, '時間'] = deal_time.formation(others_file.loc[row, '時間'])

except Exception:
    print('時間出錯，注意出車表的時間欄')
    quit()

# each員工處理
for name in parameter.employee_info["姓名"]:
    title = list(parameter.employee_info[parameter.employee_info['姓名'] == name]['職稱'])[0]

    # 建初始表
    opsheet = table_initial.create_table(name)

    # 出勤處理
    opsheet = deal_salary.rest_fill(opsheet, rest_info[rest_info['姓名'] == name])

    # 單獨資料處理
    filted_table = input_file[(input_file['司機'] == name) | (input_file['助手'].str.contains(name)) | (input_file['板車'].str.contains(name))]

    if filted_table.size != 0:
        for i in filted_table.index:

            try:
                date = opsheet['日期'] == deal_time.date_trasition(filted_table.loc[i, '日期'])
                date_opindex = opsheet[date].index
                day = deal_time.check_day(filted_table.loc[i, '日期'])
            except Exception:
                print("日期轉換出錯，注意輸入日期")
                quit()

            try:
            # 平日
                if day != 6:
                    opsheet = deal_salary.work_fill(date_opindex, i, opsheet, filted_table, title, day)
                # 周日
                else:
                    sundayfee = parameter.employee_info.loc[parameter.employee_info['姓名'] == name, '星期日出工']
                    opsheet = deal_salary.sunday(date_opindex, i, opsheet, filted_table, sundayfee, title)
            except Exception :
                print("工作處理發生問題")
                quit()

            try:
                # 助手跟大車補貼
                if str(title) != 'nan':
                    if '助手' in title:
                        opsheet = deal_salary.crossing_asist_fee(i, opsheet, filted_table, title[:-2])
            except Exception:
                print("助手跟大車處理發生問題")
                quit()

    try:
        # 維修表
        others_table = others_file[others_file['姓名'].str.contains(name)]
        for i in others_table.index:
            opsheet = deal_salary.repair_fee(i, opsheet, others_table, name)
    except Exception:
        print("維修表處理發生問題")
        quit()

    try:
        # 其他金額添加
        info_selected = parameter.employee_info['姓名'] == name
        items = ['底薪', '職務加級', '勞保費', '健保費', '租屋津貼', '久任津貼']
        for item in items:
            opsheet = deal_salary.others(item, opsheet, parameter.employee_info[info_selected])

        wage = list(parameter.employee_info.loc[parameter.employee_info['姓名'] == name, '底薪'])[0]
        opsheet = deal_value.sat(opsheet, wage)  # 休息日出工
        opsheet = deal_value.deligent(opsheet, title)  # 全勤
        opsheet = deal_value.rest(opsheet, wage)  # 請假
    except Exception:
        print("薪資結構補貼發生問題")
        quit()

    opsheet = deal_time.mark_sunday(opsheet)

    try:
        # 休息日不算
        opsheet = special_deal.adjust(name, opsheet)

        # 特殊津貼
        if name == '陳儀杰':
            opsheet = special_deal.special_fee(opsheet)
        if name == '楊潮陽':
            opsheet = special_deal.special_fee2(opsheet)

    except Exception:
        print("特殊調整發生問題")
        quit()

    try:
        # 金額總計
        opsheet.loc[opsheet['項目'] == '總計', '　小計　'] = np.nansum(opsheet['　小計　'])
        opsheet.loc[opsheet['項目'] == '瑞勵點工', '小計'] = list(opsheet.loc[opsheet['項目'] == '總計', '　小計　'])[0]
        opsheet.loc[opsheet['項目'] == '總計', '小計'] = np.nansum(opsheet['小計'])
    except Exception:
        print("金額總計發生問題")
        quit()

    try:
        # 輸出檔案
        opsheet.to_excel(writer, sheet_name=name, index=False)
        # 欄寬調整
        for col in opsheet.columns:
            index = list(opsheet.columns).index(col)
            letter = get_column_letter(index+1)
            collen = opsheet[col].apply(lambda x: len(str(x).encode())).max()
            if collen <= 8:
                collen = 8

            writer.sheets[name].column_dimensions[letter].width = collen * 1.2
    except Exception:
        print("輸出檔案發生問題")
        quit()

writer.save()
print("薪資處理完成...")

all_salary.salary_table()

print('----------------')
print('全部處理完畢')

os.system('pause')

# 維修表 改 一行一行處理
# 祥毓加班14小以上多的移到瑞勵

