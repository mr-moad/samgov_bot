import sqlite3
import urllib3
import time
from selenium import webdriver

#
# from selenium import webdriver
#
#
#
# daomains = {
#     "All Domains" : "_all",
#     "Contract Opportunities" : "opp",
#     "Assistance Listings" : "cfda",
#     "Entity Information" : "ei",
#     "Federal Hierarchy" : "fh",
#     "Wage Determinations" : "wd"
# }
# dates1 = "10/12/2022"
# dates2 = "12/12/2022"
# start_month = 10
# start_day = "08"
# end_day = 15
# end_month = "08"
# end_year = start_year = 2022
#
# # sort_date = f"&sfm[dates][publishedDate][publishedDateSelect]=customDate&sfm[dates][publishedDate][publishedDateFrom]={start_year}-{start_month}-{start_day}T07:00:00.000Z&sfm[dates][publishedDate][publishedDateTo]={end_year}-{end_month}-{end_day}T07:00:00.000Z"
# sort_date = f"&sfm%5Bdates%5D%5BpublishedDate%5D%5BpublishedDateSelect%5D=customDate&sfm%5Bdates%5D%5BpublishedDate%5D%5BpublishedDateFrom%5D={start_year}-{start_day}-{start_month}T07:00:00.000Z&sfm%5Bdates%5D%5BpublishedDate%5D%5BpublishedDateTo%5D={end_year}-{end_month}-{end_day}T07:00:00.000Z"
# driver = webdriver.Chrome(executable_path="chromedriver.exe")
#
#
# # driver.get(f"https://sam.gov/search/?index={daomains['Assistance Listings']}&sort=-modifiedDate&page=1&pageSize=25&sfm[simpleSearch][keywordRadio]=ALL&sfm[status][is_active]=true" + )
# driver.get(f"https://sam.gov/search/?index={daomains['Assistance Listings']}&sort=-modifiedDate&page=1&pageSize=25&sfm%5BsimpleSearch%5D%5BkeywordRadio%5D=ALL&sfm%5Bstatus%5D%5Bis_active%5D=true" + sort_date)
# time.sleep(2000)
from utils import save_to_excel

domains = {
    "All Domains" : "_all",
    "Contract Opportunities" : "opp",
    "Assistance Listings" : "cfda",
    "Entity Information" : "ei",
    "Federal Hierarchy" : "fh",
    "Wage Determinations" : "wd"
}

notice_type = {
    "Special Notice": "s",
    "Sources Sought": "r",
    "Presolicitation": "p",
    "Intent to Bundle Requirements": "i",
    "Solicitation": "o",
    "Combined Synopsis/Solicitation": "k",
    "Award Notice": "a",
    "Justification": "u",
    "Sale of Surplus Property": "g"
}


aside_object = {
    "Total Small Business Set-Aside (FAR 19.5)": "SBA",
    "Partial Small Business Set-Aside (FAR 19.5)": "SBP",
    "8(a) Set-Aside (FAR 19.8)": "8A",
    "8(a) Sole Source (FAR 19.8)": "8AN",
    "Historically Underutilized Business (HUBZone) Set-Aside (FAR 19.13)": "HZC",
    "Historically Underutilized Business (HUBZone) Sole Source (FAR 19.13)": "HZS",
    "Service-Disabled Veteran-Owned Small Business (SDVOSB) Set-Aside (FAR 19.14)": "SDVOSBC",
    "Service-Disabled Veteran-Owned Small Business (SDVOSB) Sole Source (FAR 19.14)": "SDVOSBS",
    "Women-Owned Small Business (WOSB) Program Set-Aside (FAR 19.15)": "WOSB",
    "Women-Owned Small Business (WOSB) Program Sole Source (FAR 19.15)": "WOSBSS",
    "Economically Disadvantaged WOSB (EDWOSB) Program Set-Aside (FAR 19.15)": "EDWOSB",
    "Economically Disadvantaged WOSB (EDWOSB) Program Sole Source (FAR 19.15)": "EDWOSBSS",
    "Local Area Set-Aside (FAR 26.2)": "LAS",
    "Indian Economic Enterprise (IEE) Set-Aside (specific to Department of Interior)": "IEE",
    "Indian Small Business Economic Enterprise (ISBEE) Set-Aside (specific to Department of Interior)": "ISBEE",
    "Buy Indian Set-Aside (specific to Department of Health and Human Services, Indian Health Services)": "BICiv",
    "Veteran-Owned Small Business Set-Aside (specific to Department of Veterans Affairs)": "VSA",
    "Veteran-Owned Small Business Sole source (specific to Department of Veterans Affairs)": "VSS"
}

search_keyword = {
    "sfm[simpleSearch][keywordTags][0][key]": "36c25622q1399",
    "sfm[simpleSearch][keywordTags][0][value]": "36c25622q1399",
}


request_object = {
    "sort": "-modifiedDate",
    "page": 1,
    "pageSize": 100,
    "sfm[simpleSearch][keywordRadio]": "ALL",
    "sfm[status][is_active]": "true",

}

search_object = {
    "sfm[simpleSearch][keywordTags][0][key]": "36c25622q1399",
    "sfm[simpleSearch][keywordTags][0][value]": "36c25622q1399"
}


def create_db():
    con = sqlite3.connect('data.db')
    if con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS records
            (ID INTEGER PRIMARY KEY    AUTOINCREMENT,
            link           TEXT    NOT NULL,
            naics           TEXT ,
            description           TEXT,
            response_date           TEXT   ,
            published_date           TEXT ,
            solicitation           TEXT ,
            contact           TEXT)
            ;''')
        con.commit()
        con.close()


def save_data(data):
    create_db()
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO records (link, naics,response_date, published_date, solicitation, description, contact ) VALUES (?,?,?,?,?,?,?)",
        (data.get("link"),data.get("naics"),data.get("response_date"),data.get("published_date"),data.get("solicitation"),data.get("description"),data.get("contact"))
    )
    con.commit()
    con.close()
    try:
        save_to_excel(data)
    except Exception as e:
        print(e)


def get_data(link, driver, keyword=None):
        if "/opp/" not in link:
            print("skipped")
            return True
        driver.get(link)
        time.sleep(2)
        while True:
            try:
                response_date = None
                description = None

                while not driver.execute_script('return document.querySelector("#header-solicitation-number .description")'):
                    if driver.execute_script(
                            'return document.querySelector("#wd-print-link")') and driver.execute_script(
                            'return document.querySelector("#wd-print-link").innerText.includes("Agreement")'):
                        return True
                    time.sleep(0.2)
                solicitation = driver.execute_script('return document.querySelector("#header-solicitation-number .description").innerText')
                while not driver.execute_script('return document.querySelector("#general-original-published-date")'):
                    time.sleep(0.2)
                driver.execute_script('document.querySelector("#general-original-published-date strong").innerText = "";')
                published_date = driver.execute_script('return document.querySelector("#general-original-published-date").innerText')
                if driver.execute_script('return document.querySelector("#general-original-response-date")'):
                    driver.execute_script('document.querySelector("#general-original-response-date strong").innerText = "";')
                    response_date = driver.execute_script('return document.querySelector("#general-original-response-date").innerText')
                if driver.execute_script('return document.querySelector("#description")'):
                    description = driver.execute_script('return document.querySelector("#description").innerText')
                naics = None
                if driver.execute_script('return document.querySelector("#classification-naics-code li")'):
                    naics_res = driver.execute_script(
                                'return document.querySelector("#classification-naics-code li").innerText')
                    naics = naics_res.split(" ")[0]
                contact_info = None
                if driver.execute_script('return document.querySelector("#contact-primary-poc-full-name")'):
                    contact_info = driver.execute_script('return document.querySelector("#contact-primary-poc-full-name").parentElement.innerText')
                save_data({
                    "keyword": keyword,
                    "link": link,
                    "naics": naics,
                    "contact": contact_info,
                    "description":description,
                    "response_date": response_date,
                    "published_date": published_date,
                    "solicitation": solicitation
                })
                return True
            except:
                if driver.execute_script('return document.querySelector("#wd-print-link")') and driver.execute_script(
                        'return document.querySelector("#wd-print-link").innerText.includes("Agreement")'):
                    return True

def search_by_filters(domain, notice, aside, start_date, end_date):
    result_links = []
    if aside:
        request_object["sfm[setAside][0][key]"] =  aside_object[aside]
        request_object["sfm[setAside][0][value]"] = aside
    if notice:
        request_object["sfm[typeOfNotice][0][key]"] = notice_type.get(notice)
        request_object["sfm[typeOfNotice][0][value]"] = notice
    if domain:
        request_object["index"] = domains.get(domain)
    else:
        request_object["index"] = domains.get('All Domains')
    if start_date:
        request_object["sfm[dates][responseDue][responseDueSelect]"] = "customDate"
        request_object["sfm[dates][responseDue][responseDueFrom]"] = start_date + "T07:00:00.000Z"
        request_object["sfm[dates][responseDue][responseDueTo]"] = end_date + "T07:00:00.000Z"
    driver = webdriver.Chrome(executable_path="chromedriver.exe")
    driver.get("https://sam.gov/search/" + urllib3.request.urlencode(request_object))
    driver.execute_script('window.localStorage.setItem("mfeWelcome","mfeWelcome");')
    driver.get("https://sam.gov/search/?" + urllib3.request.urlencode(request_object))
    div_container = driver.execute_script('return document.querySelectorAll("sds-search-result-list > div")')
    while not div_container:
        if driver.execute_script('return document.querySelector("#wd-print-link")') and driver.execute_script(
                'return document.querySelector("#wd-print-link").innerText.includes("Agreement")'):
            return True
        div_container = driver.execute_script('return document.querySelectorAll("sds-search-result-list > div")')
        time.sleep(0.5)
    for i in range(len(div_container) - 1):
        result_links.append(driver.execute_script(f'return document.querySelectorAll("sds-search-result-list > div")[{i}].querySelector("a").href'))
    if len(result_links):
        number_of_pages = driver.execute_script("return document.querySelector('.sds-pagination__total').innerText.replace('of ','')")
        if number_of_pages != "1":
            for i in range(int(number_of_pages)):
                driver.execute_script('document.querySelector("#bottomPagination-nextPage").click()')
                div_container = driver.execute_script(
                    'return document.querySelectorAll("sds-search-result-list > div")')
                while not div_container:
                    div_container = driver.execute_script(
                        'return document.querySelectorAll("sds-search-result-list > div")')
                    time.sleep(0.3)
                for i in range(len(div_container) - 1):
                    result_links.append(driver.execute_script(
                        f'return document.querySelectorAll("sds-search-result-list > div")[{i}].querySelector("a").href'))


    for link in result_links:
        try:
            get_data(link, driver)
        except Exception as e:
            print(link)
            exit()
    driver.quit()

def search_by_all(custom_naics, keyword, domain, notice, aside, start_date, end_date):
    result_links = []
    if aside:
        request_object["sfm[setAside][0][key]"] = aside_object[aside]
        request_object["sfm[setAside][0][value]"] = aside
    if notice:
        request_object["sfm[typeOfNotice][0][key]"] = notice_type.get(notice)
        request_object["sfm[typeOfNotice][0][value]"] = notice
    if domain:
        request_object["index"] = domains.get(domain)
    else:
        request_object["index"] = domains.get('All Domains')
    if start_date:
        request_object["sfm[dates][responseDue][responseDueSelect]"] = "customDate"
        request_object["sfm[dates][responseDue][responseDueFrom]"] = start_date + "T07:00:00.000Z"
        request_object["sfm[dates][responseDue][responseDueTo]"] = end_date + "T07:00:00.000Z"
    request_object["sfm[simpleSearch][keywordTags][0][key]"] = keyword
    request_object["sfm[simpleSearch][keywordTags][0][value]"] = keyword
    if custom_naics:
        request_object["sfm[simpleSearch][keywordTags][1][key]"] = custom_naics
        request_object["sfm[simpleSearch][keywordTags][1][value]"] = custom_naics
    driver = webdriver.Chrome(executable_path="chromedriver.exe")
    driver.get("https://sam.gov/search/" + urllib3.request.urlencode(request_object))
    driver.execute_script('window.localStorage.setItem("mfeWelcome","mfeWelcome");')
    driver.get("https://sam.gov/search/?" + urllib3.request.urlencode(request_object))
    div_container = driver.execute_script('return document.querySelectorAll("sds-search-result-list > div")')
    while not div_container:
        if driver.execute_script('return document.querySelector("#wd-print-link")') and driver.execute_script(
                'return document.querySelector("#wd-print-link").innerText.includes("Agreement")'):
            return True
        div_container = driver.execute_script('return document.querySelectorAll("sds-search-result-list > div")')
        time.sleep(0.5)
    for i in range(len(div_container) - 1):
        result_links.append(driver.execute_script(
            f'return document.querySelectorAll("sds-search-result-list > div")[{i}].querySelector("a").href'))
    if len(result_links):
        number_of_pages = driver.execute_script(
            "return document.querySelector('.sds-pagination__total').innerText.replace('of ','')")
        if number_of_pages != "1":
            for i in range(int(number_of_pages)):
                driver.execute_script('document.querySelector("#bottomPagination-nextPage").click()')
                div_container = driver.execute_script(
                    'return document.querySelectorAll("sds-search-result-list > div")')
                while not div_container:
                    div_container = driver.execute_script(
                        'return document.querySelectorAll("sds-search-result-list > div")')
                    time.sleep(0.3)
                for i in range(len(div_container) - 1):
                    result_links.append(driver.execute_script(
                        f'return document.querySelectorAll("sds-search-result-list > div")[{i}].querySelector("a").href'))

    for link in result_links:
        try:
            get_data(link, driver,keyword=keyword)
        except Exception as e:
            print(link)
            exit()
    driver.quit()


def search_by_keyword(keyword):
    result_links = []
    search_object = {
        "sfm[simpleSearch][keywordTags][0][key]": keyword,
        "sfm[simpleSearch][keywordTags][0][value]": keyword
    }
    driver = webdriver.Chrome(executable_path="chromedriver.exe")
    driver.get("https://sam.gov/search/" + urllib3.request.urlencode(search_object))
    driver.execute_script('window.localStorage.setItem("mfeWelcome","mfeWelcome");')
    driver.get("https://sam.gov/search/?" + urllib3.request.urlencode(search_object))
    driver.execute_script('window.localStorage.setItem("mfeWelcome","mfeWelcome");')
    div_container = driver.execute_script('return document.querySelectorAll("sds-search-result-list > div")')
    while not div_container:
        if driver.execute_script('return document.querySelector("#wd-print-link")') and driver.execute_script('return document.querySelector("#wd-print-link").innerText.includes("Agreement")'):
            return True
        div_container = driver.execute_script('return document.querySelectorAll("sds-search-result-list > div")')
        time.sleep(0.5)
    for i in range(len(div_container) - 1):
        result_links.append(driver.execute_script(
            f'return document.querySelectorAll("sds-search-result-list > div")[{i}].querySelector("a").href'))
    if len(result_links):
        number_of_pages = driver.execute_script(
            "return document.querySelector('.sds-pagination__total').innerText.replace('of ','')")
        if number_of_pages != "1":
            for i in range(int(number_of_pages)):
                driver.execute_script('document.querySelector("#bottomPagination-nextPage").click()')
                div_container = driver.execute_script(
                    'return document.querySelectorAll("sds-search-result-list > div")')
                while not div_container:
                    print("cmh")
                    div_container = driver.execute_script(
                        'return document.querySelectorAll("sds-search-result-list > div")')
                    time.sleep(0.3)
                for i in range(len(div_container) - 1):
                    result_links.append(driver.execute_script(
                        f'return document.querySelectorAll("sds-search-result-list > div")[{i}].querySelector("a").href'))
    for link in result_links:
        try:
            get_data(link, driver,keyword=keyword)
        except Exception as e:
            print(link)
            exit()
    driver.quit()


