import re
import requests
import pandas as pd
import mysql.connector
from bs4 import BeautifulSoup

months = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12,
}

data = pd.read_excel('~') # 文件来源见readme
df = pd.DataFrame(data)
row_num = df.shape[0] #读取行数
for m in range(0, row_num): #报错时修改这里
    case_id = int(df.iloc[m, 1])

    profile_url = df.iloc[m, 2]
    print(case_id, profile_url, 'start')
    req = requests.get(url = profile_url).text
    soup = BeautifulSoup(req, features = "lxml")

    # headline
    headline = soup.find('h1', {'class': 'span24'}).text

    # stats
    stats_div = soup.find('div', {'class': "stats"})
    funded_per = stats_div.find('dl', {'class': 'funded'}).text.replace('%', '')
    remaining_ul = stats_div.find('ul', {'class': 'remaining'})
    remaining_li = remaining_ul.find('li').text.replace(',', '')
    remaining_pattern = re.compile(r'\d+')
    remaining_match = remaining_pattern.findall(remaining_li)
    raised_amount = remaining_match[0]
    togo_amount = remaining_match[1]
    try:
        funded_banner = soup.find('div', {'class': 'funded_banner'}).text
        date_str = funded_banner.split(' on ')
        fully_funded_date = str(date_str[1]).replace(',', '').replace('.', '')
        fully_funded_date_split = fully_funded_date.split(' ')
        fully_funded_date_month = months[fully_funded_date_split[0]]
        fully_funded_date_day = fully_funded_date_split[1]
        fully_funded_date_year = fully_funded_date_split[2]
    except AttributeError:
        fully_funded_date_day = 0
        fully_funded_date_month = 0
        fully_funded_date_year = 0

    # donor
    try:
        donor_div = soup.find('div', {'class': 'donor_list_web_view'})
        donor_h2 = donor_div.find('h2', {'class': 'detail_header'}).text
        donor_pattern = re.compile(r'\d+')
        donor_match = donor_pattern.findall(donor_h2)
        donor_num = donor_match[0]
    except IndexError:
        donor_num = 0
    except AttributeError:
        donor_num = 0

    # story
    story_div = soup.find('div', {'id': 'story'})
    story_date = story_div.find('div', {'class': 'timestamp'}).text.replace(',', '')
    story_date_split = story_date.split(' ')
    story_date_month = months[story_date_split[0]]
    story_date_day = story_date_split[1]
    story_date_year = story_date_split[2]
    story_content = story_div.find('div', {'class': 'full'}).text

    # update
    try:
        update_div = soup.find('div', {'id': 'update'})
        update_date = update_div.find('div', {'class': 'timestamp'}).text.replace(',', '')
        update_date_split = update_date.split(' ')
        update_date_month = months[update_date_split[0]]
        update_date_day = update_date_split[1]
        update_date_year = update_date_split[2]
        update_treatment_text = update_div.find_all('p')[1].text
        update_content = update_div.find('div', {'class': 'full'}).text
    except AttributeError:
        update_date_day = 0
        update_date_month = 0
        update_date_year = 0
        update_treatment_text = None
        update_content = None

    # timeline
    timeline_div = soup.find('div', {'class': 'timeline'})
    timeline_cards = timeline_div.find_all('li')
    timeline_dict = {}
    for card in timeline_cards:
        timeline_date = card.find('div', {'class': 'timeline_date'}).text
        timeline_title = card.find('div', {'class': 'timeline_title'}).text
        timeline_description = card.find('p', {'class': 'timeline_description'}).text
        timeline_detail_dict = {}
        timeline_detail_dict['timeline_date'] = timeline_date
        timeline_detail_dict['timeline_description'] = timeline_description
        timeline_dict[timeline_title] = timeline_detail_dict
    timeline_dict = str(timeline_dict)

    # treatment
    treatment_info_name = soup.find('div', {'class': 'treatment_info_name'}).text

    # cost breakdown
    cost_breakdown_dict = {}
    try:
        cost_breakdown = soup.find('div', {'id': 'breakdown'})
        average_treatment_cost_text = cost_breakdown.find('div', {'class': 'breakdown_title'}).text
        average_treatment_cost_pattern = re.compile(r'\d+')
        average_treatment_cost_match = average_treatment_cost_pattern.findall(average_treatment_cost_text)
        cost_breakdown_average_treatment_cost_num = average_treatment_cost_match[0]
        invoice_categories = cost_breakdown.find_all('div', {'class': ['invoice_category', 'invoice_category no_expense']})
        for i in invoice_categories:
            cost_breakdown_category_name = i.find('div', {'class': 'category_name'}).text
            cost_breakdown_category_cost = i.find('div', {'class': 'category_cost'}).text
            cost_breakdown_dict[cost_breakdown_category_name] = cost_breakdown_category_cost
        cost_breakdown_dict = str(cost_breakdown_dict)
    except AttributeError:
        cost_breakdown_average_treatment_cost_num = None
        cost_breakdown_dict = None

    # diagnosis
    try:
        diagnosis = soup.find('div', {'id': 'diagnosis'})
        diagnosis_info_section = diagnosis.find('div', {'class': 'info_section'})
        diagnosis_symptoms_text = diagnosis_info_section.find('p', {'id': 'dx_presentation'}).text
        diagnosis_impact_on_patients_life_text = diagnosis_info_section.find('p', {'id': 'dx_impact'}).text
        diagnosis_cultural_or_regional_significance_text = diagnosis_info_section.find('p', {'id': 'dx_culture'}).text
    except AttributeError:
        diagnosis_symptoms_text = None
        diagnosis_impact_on_patients_life_text = None
        diagnosis_cultural_or_regional_significance_text = None

    # procedure
    try:
        procedure = soup.find('div', {'id': 'treatment'})
        procedure_info_section = procedure.find('div', {'class': 'info_section'})
        procedure_process_text = procedure_info_section.find('p', {'id': 'tx_process'}).text
        procedure_impact_on_patients_life_text = procedure_info_section.find('p', {'id': 'tx_impact'}).text
        procedure_risks_and_side_effects_text = procedure_info_section.find('p', {'id': 'tx_risks'}).text
        procedure_accessibility_text = procedure_info_section.find('p', {'id': 'tx_access'}).text
        procedure_alternatives_text = procedure_info_section.find('p', {'id': 'tx_alternatives'}).text
    except AttributeError:
        procedure_process_text = None
        procedure_impact_on_patients_life_text = None
        procedure_risks_and_side_effects_text = None
        procedure_accessibility_text = None
        procedure_alternatives_text = None

    DB = mysql.connector.connect(host = 'localhost', user = 'root', password = '~', db = 'watsi')
    DBO = DB.cursor()
    sql = ("INSERT INTO patient "
                "(case_id, profile_url, headline, funded_per, raised_amount, togo_amount, fully_funded_date_day, fully_funded_date_month, fully_funded_date_year, donor_num, story_date_day, story_date_month, story_date_year, story_content, update_date_day, update_date_month, update_date_year, update_treatment_text, update_content, timeline_dict, treatment_info_name, cost_breakdown_average_treatment_cost_num, cost_breakdown_dict, diagnosis_symptoms_text, diagnosis_impact_on_patients_life_text, diagnosis_cultural_or_regional_significance_text, procedure_process_text, procedure_impact_on_patients_life_text, procedure_risks_and_side_effects_text, procedure_accessibility_text, procedure_alternatives_text) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")  
    try:
        DBO.execute(sql,
            (
                case_id,
                profile_url,
                headline,
                funded_per,
                raised_amount,
                togo_amount,
                fully_funded_date_day,
                fully_funded_date_month,
                fully_funded_date_year,
                donor_num,
                story_date_day,
                story_date_month,
                story_date_year,
                story_content,
                update_date_day,
                update_date_month,
                update_date_year,
                update_treatment_text,
                update_content,
                timeline_dict,
                treatment_info_name,
                cost_breakdown_average_treatment_cost_num,
                cost_breakdown_dict,
                diagnosis_symptoms_text,
                diagnosis_impact_on_patients_life_text,
                diagnosis_cultural_or_regional_significance_text,
                procedure_process_text,
                procedure_impact_on_patients_life_text,
                procedure_risks_and_side_effects_text,
                procedure_accessibility_text,
                procedure_alternatives_text,
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
