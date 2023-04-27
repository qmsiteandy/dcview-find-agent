import requests
from bs4 import BeautifulSoup
import pandas as pd


def GrabDCview():
    # 抓取DCview首頁資料，並解析儲存

    # 步驟一：
    result = requests.get("http://market.dcview.com/")  # get 該網址的 HTML

    # 步驟二：
    # 將網頁資料以 html.parser 解析器來解析
    soup = BeautifulSoup(result.text, "html.parser")
    # print(soup) #印出至畫面

    # 步驟三：
    datas = soup.find('table', 'table').tbody.find_all(
        class_="data-list-xs visible-xs")

    # 紀錄商品資訊
    column = ['id', 'mode', 'location', 'name', 'price', 'href']
    df = pd.DataFrame(columns=column)

    for data in datas:
        # 商品連結&ID
        s_href = data.find('a').get('href')
        splitHref = s_href.split('/')
        s_id = splitHref[len(splitHref)-1]
        # 徵或售
        s_mode = data.find(class_='btn-xs').text
        # 縣市&品項名稱
        s_topic = data.find(class_='h5').text.strip()
        s_location = s_topic.split(']')[0].replace("[", "")
        s_name = s_topic.split(']')[1].strip()
        # 價格
        s_price = data.find(class_='price').text.split()[0].replace(",", "")
        i_price = int(s_price)

        df = df._append({'id': s_id, 'mode': s_mode, 'location': s_location,
                         'name': s_name, 'price': i_price, 'href': s_href}, ignore_index=True)

    # 回傳商品
    return df


def FindProduct(df, mode, target_names, budget, locations):
    # 比對商品有無符合條件項目
    # 帶入參數：收&售、名稱關鍵字、預算、交易區域

    # 篩選符合條件：收&售、預算、交易區域
    df.query("mode == @mode & \
              price <= @budget & \
              location in @locations",
             inplace=True)

    # 將每一項 target 轉為 regex，regex 功能偵測擁有所有關鍵字的項目(關鍵字順序不限)
    # ->  /(?=.*Apple)(?=.*Bat)(?=.*Car).*/
    target_regex = []
    for target in target_names:
        target_split = target.split()
        regex = "(?=.*" + ")(?=.*".join(target_split) + ").*"
        target_regex.append(regex)

    # 篩選符合條件：名稱關鍵字
    df.query("name.str.contains('|'.join(@target_regex))", inplace=True)

    # 返回過濾後的 DF
    return df


def SendLineMsg(token, msg):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = {"message": msg}

    r = requests.post("https://notify-api.line.me/api/notify",
                      headers=headers, params=params)
