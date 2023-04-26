import function as fn


mode = '售'
target_names = ['28-75', '17-55', '24-70']
budget = 50000
locations = ['台北市', '新北市', '高雄市']
token = 'eXcB8Q9b6OT7fggGcOAE2UZzDwis3WSEBd7QOxCEXgF'

# 取得產品資訊
products_df = fn.GrabDCview()
# filt 符合條件商品
find_df = fn.FindProduct(products_df, mode, target_names, budget, locations)
# 如果有符合的商品，建立訊息並傳送至 Line Notifiy
if (find_df.shape[0] > 0):
    print(find_df)
    for index, row in find_df.iterrows():
        msg = f"【{row['mode']}】 {row['location']} \n\n {row['name']} \n\n {row['price']}元 \n\n -----------\n{row['href']}"
        fn.SendLineMsg(token, msg)
else:
    print('無符合條件商品')


# schedule.every(5).minutes.at(":00").do(FindInDCview)
# while True:
#     schedule.run_pending()
#     time.sleep(10)
