# Dcview 商品爬蟲功能
## 專案說明
本專案針對 [攝影器材二手交易網站 Dcview](http://market.dcview.com/) 進行商品爬蟲，偵測是否有符合條件 (關鍵字、買或賣、交易區域、金額預算) 的商品，並以 Line notify 通知使用者。
## 情境補充
此拍賣網站有大量用戶出售或徵求想要的攝影器材，而通常好商品會在極短時間被預訂。然而總不可能一直盯著網頁等待想要的商品出現，因此開發這個程式，用來自動化偵測符合的商品並進行通知。

## 使用工具
項目       |工具
----------|----------------
開發語言   | Python
爬蟲套件   | BeautifulSoup
訊息通知     | [Line Notify](https://notify-bot.line.me/zh_TW/)


# 專案建置&使用
## 環境變數 .env
```
LINE_NOTYFY_TOKEN = {自己的 LINE NOTYFY 權證}
```
## 搜尋項目設定
此專案目前還沒建置前端 UI 畫面，針對所需的商品條件，需要直接修改  `app.py` 中的程式碼：
```python
# 售 or 徵
mode = '售'
# 想要的商品關鍵字，可以同時搜尋多項商品，同一商品若有多項關鍵字可用空白區隔
target_names = ['35 1.4', '5d4']
# 預算上限
budget = 50000
# 可以的交易區域
locations = ['台北市', '新北市', '高雄市']
```
## 專案執行
```
python app.py
```
## 備註
目前此專案只會撈取並偵測 Dcview 首頁商品。  
並且 1 小時偵測一次 (如果需要調整頻率可以在 `app.js` 中修改)

# 功能架構說明
## 功能拆分
本專案將功能拆分為三項：撈取、搜尋、通知
> [程式碼](https://github.com/qmsiteandy/dcview-find-agent/blob/master/function.py)

### 撈取資料 GrabDCview 函式
1. 呼叫 Dcview 網站取得回傳的 HTML。
2. 使用 BeautifulSoup 套件解析 HTML。
3. 找到 Table 以及底下的 datas，並用 HTML Id 找到各項產品的 id、名稱、徵或售、區域、價格、連結。
4. 將資訊存入 Pandas Dataframe 並回傳。

Dataframe 內容：
![](https://i.imgur.com/OKBlxBI.png)

### 搜尋商品 FindProduct 函式
需要帶入五項參數：`df`, `mode`, `target_names`, `budget`, `locations`
1. 先將 `df` (dataframe) 進行 query ，篩出「收&售、預算、交易區域」符合的項目。設定 `inplace=True` 可以讓 df 進行 query 後直接取代原有資料。
    ```python
    # 篩選符合條件：收&售、預算、交易區域
    df.query("mode == @mode & \
                price <= @budget & \
                location in @locations",
                inplace=True)
    ```
2. 商品關鍵字轉換成 Regex 標準表達式  
    考量使用者可能需要同時搜尋多項商品，並且同一樣商品可能會有多個關鍵字，須設計一組 Regex 可以一次搜尋所有內容。
    > 例如關鍵字內容 `target_names = ['A73', '55 1.8']` 代表兩項商品，並且第二項商品須同時擁有 55 和 1.8 兩個關鍵字。
3. 將每一項要找的商品名稱依空格切割，再組合成 Regex `/(?=.*Key1)(?=.*Key2)(?=.*Key3).*/` 的格式 (每一個 Regex 都表示一項商品的關鍵字)，並存入陣列中。
    ```python
    target_regex = []
    for target in target_names:
        target_split = target.split()
        regex = "(?=.*" + ")(?=.*".join(target_split) + ").*"
        target_regex.append(regex)
    ```
4. 將 dataframe 使用 str.contains 進行 query，取出符合關鍵字的項目。  
    >其中 `'|'.join(@target_regex)` 可以將 target_regex 陣列組成 `regex1 | regex2 | regex3` 的形式。

    ```python
    df.query("name.str.contains('|'.join(@target_regex))", inplace=True)
   ```
5. 回傳過濾後的 Dataframe   
    >如果沒有符合的商品，Dataframe 會是空陣列。

### 傳送訊息 SendLineMsg 函式
需要帶入兩個參數：token (Line Notify 的權證)、msg (要傳送的訊息)
呼叫 Line Notify API 傳送訊息到 Line。

<img src="https://i.imgur.com/ELrtpR3.png" width="300px">

## 定時呼叫偵測
### 設定工作
設定一個函式規劃工作內容，包含上述的功能
1. 抓取產品資訊
2. 過濾符合條件商品
3. 如果有符合商品，建立 msg 內容
4. 傳送 Line notify

```python
def ScheduleJob():

    print("FindInDCview:", time.ctime(time.time()))

    # 取得產品資訊
    products_df = fn.GrabDCview()
    print(products_df)
    # filt 符合條件商品
    find_df = fn.FindProduct(
        products_df, mode, target_names, budget, locations)
    # 如果有符合的商品，建立訊息並傳送至 Line Notifiy
    if (find_df.shape[0] > 0):
        for index, row in find_df.iterrows():
            msg = f"【{row['mode']}】 {row['location']} \n\n {row['name']} \n\n {row['price']}元 \n\n -----------\n{row['href']}"
            fn.SendLineMsg(os.getenv("LINE_NOTYFY_TOKEN"), msg)
    else:
        print('無符合條件商品')
```
### 定時執行
使用 schedule 套件，設定每一小時整點時呼叫 ScheduleJob 函式。
```python
schedule.every().hour.at(":00").do(ScheduleJob)
while True:
    schedule.run_pending()
    time.sleep(10)
```

# 後記
目前這個系統是透過 while 迴圈不斷運行，以此達到在定點時間偵測商品功能，缺點就是需要電腦開著持續運作程式。並且只能在自己電腦使用，無法成為一個 Server 服務。

原本想要將程式放到 Heroku 運行，並利用 heroku 內建 Scheduler 定期呼叫 function (理想狀況下應該就不需要用無限的 While 迴圈了) ；再加入資料庫及前端畫面，變成一個雲端服務：

1. 使用者在前端設定商品條件及自己的 Line notify token
2. Server 寫入資料庫
3. 於定期的偵測工作時，取得 Database 中所有商品條件資料
4. 如果有符合項目，使用對應的 token 通知該使用者

然而目前 Heroku 取消免費方案，且進階使用的費用不便宜...，待未來找到好用便宜的雲端部屬方式再來實現這個系統。