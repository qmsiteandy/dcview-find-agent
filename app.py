import function as fn
import schedule
import time
import os
from dotenv import load_dotenv

load_dotenv()

# 售 or 徵
mode = '售'
# 想要的商品關鍵字，可以同時搜尋多項商品，同一商品若有多項關鍵字可用空白區隔
target_names = ['35 1.4', '5d4']
# 預算上限
budget = 50000
# 可以的交易區域
locations = ['台北市', '新北市', '高雄市']


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


# 設定定期執行時間
schedule.every().hour.at(":00").do(ScheduleJob)
while True:
    schedule.run_pending()
    time.sleep(10)
