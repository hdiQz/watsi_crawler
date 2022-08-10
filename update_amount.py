import re
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
    req = requests.get(url = profile_url).text
    soup = BeautifulSoup(req, features = "lxml")

    # stats
    stats_div = soup.find('div', {'class': "stats"})
    funded_per = stats_div.find('dl', {'class': 'funded'}).text.replace('%', '')
    remaining_ul = stats_div.find('ul', {'class': 'remaining'})
    remaining_li = remaining_ul.find('li').text.replace(',', '')
    remaining_pattern = re.compile(r'\d+')
    remaining_match = remaining_pattern.findall(remaining_li)
    raised_amount = remaining_match[0]
    togo_amount = remaining_match[1]
    
    DB = mysql.connector.connect(host = 'localhost', user = 'root', password = '~', db = 'watsi')
    DBO = DB.cursor()
    sql = ("UPDATE patient SET raised_amount = %s, togo_amount = %s WHERE case_id = %s")  
    try:
        DBO.execute(sql,
            (
                raised_amount,
                togo_amount,
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
