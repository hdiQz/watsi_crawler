import requests
import pandas as pd
import mysql.connector
from bs4 import BeautifulSoup

data = pd.read_excel('~') # 文件来源见readme
df = pd.DataFrame(data)
row_num = df.shape[0] #读取行数
for m in range(0, row_num): #报错时修改这里
    case_id = int(df.iloc[m, 1])
    profile_url = df.iloc[m, 2]
    print(case_id, profile_url, 'start')
    #profile_url = 'https://watsi.org/profile/7f77d956f5cd'
    #case_id = int(25957)
    req = requests.get(url = profile_url).text
    soup = BeautifulSoup(req, features = "lxml")

    # update
    try:
        update_div = soup.find('div', {'id': 'update'})
        update_treatment_text = update_div.find_all('p')[1].text
    except AttributeError:
        update_treatment_text = None
    
    DB = mysql.connector.connect(host = 'localhost', user = 'root', password = '~', db = 'watsi')
    DBO = DB.cursor()
    sql = ("UPDATE patient SET update_treatment_text = %s WHERE case_id = %s")  
    try:
        DBO.execute(sql,
            (
                update_treatment_text,
                case_id,
            )
        )
        DB.commit()
        DBO.close()
        DB.close()
    except Exception as err:
        print(err)
        exit()
    print(case_id, ' done')
print('运行结束')
# 需要后续验证第二个<p>是否就是update_treatment_text：验证开头是否为patient的名字
