#from xlrd import open_workbook,cellname
import base
import urllib.request as urllib
import config, basket


def get_xls_data(file,user_id,username):
    xl = open("xl.xls", 'w')
    print()
    xl = open("xl.xls", 'rb')
    urllib.urlretrieve('https://api.telegram.org/file/bot'+config.token+'/'+file.file_path, "xl.xls")
    xl = open_workbook('xl.xls', 'rb')
    sheet = xl.sheet_by_index(0)
    for row_index in range(sheet.nrows):
        if row_index > 1:
            itm = basket.Item()
            itm.set_pro_data(sheet.cell(row_index, 1),
                             sheet.cell(row_index, 2),
                             sheet.cell(row_index, 3),
                             sheet.cell(row_index, 4),
                             sheet.cell(row_index, 5),
                             sheet.cell(row_index, 6),
                             user_id,
                             username)
            base.add_item(itm, user_id)

