import requests
import time
import os
import datetime
import re
import schedule
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage


def schedle_test():
  dt = datetime.datetime.now()
  CHANNEL_ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
  line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

  # 年月日を取得する
  years = str(dt.year)
  if dt.month < 10:
    month = "0" + str(dt.month)
  else:
    month = str(dt.month)

  today = int(dt.day)

  time.sleep(1)
  res = requests.get(
      f"https://www.tsuyama-ct.ac.jp/oshiraseVer4/renraku/renraku{years}{month}.html"
  )

  str_ju = years + month + 'ju'
  str_kyu = years + month + 'kyu'

  soup = BeautifulSoup(res.content, "html.parser")
  class_changes = soup.find('div', attrs={'id': str_ju}).get_text()
  canceled_class = soup.find('div', attrs={'id': str_kyu}).get_text()
  time.sleep(1)

  # 授業変更
  print(class_changes)
  # 休講情報
  print(canceled_class)

  # 授業変更情報の整理
  class_changes_split = class_changes.splitlines()
  class_changes_send_arr = ""
  # データを分割し、日付を取り出す。今日より後のものを配列に追加する。
  for data in range(2, len(class_changes_split)):
    split_month = re.split("\d月", class_changes_split[data])
    split_date = split_month[1].split("日")
    for date in range(0, len(split_date), 2):
      date_int = int(split_date[date])
      if date_int >= today:
        class_changes_send_arr += "\n" + class_changes_split[data]+"\n"
  print(class_changes_send_arr)

  # 休講情報の整理
  canceled_class_split = canceled_class.splitlines()
  canceled_class_send_arr = ""
  # データを分割し、日付を取り出す。今日より後のものを配列に追加する。
  for data in range(2, len(canceled_class_split)):
    split_month = re.split("\d月", canceled_class_split[data])
    split_date = split_month[1].split("日")
    for date in range(0, len(split_date), 2):
      date_int = int(split_date[date])
      if date_int >= today:
        canceled_class_send_arr += "\n" + canceled_class_split[data]+"\n"
  print(canceled_class_send_arr)

  is_change = False

  f_changes = open('class_changes.txt', 'r', encoding='UTF-8')
  changes_old_data = f_changes.read()
  if class_changes != changes_old_data:
    is_change = True
    print("授業変更の情報が更新されました。")
    f = open('class_changes.txt', 'w')
    f.write(class_changes)
    f.close()

  f_canceled = open('canceled_class.txt', 'r', encoding='UTF-8')
  canceled_old_data = f_canceled.read()
  if canceled_class != canceled_old_data:
    is_change = True
    print("休講の情報が更新されました。")
    f = open('canceled_class.txt', 'w')
    f.write(canceled_class)
    f.close()

  if is_change:
    class_changes = class_changes[1:]
    massages = TextSendMessage(
        text="授業情報が更新されましたので、お知らせします。\n\n" + "▪︎授業変更" + class_changes_send_arr +
        "\n\n▪︎休講" + canceled_class_send_arr)
    line_bot_api.broadcast(messages=massages)


schedule.every(7200).seconds.do(schedle_test)

while True:
  schedule.run_pending()
  time.sleep(1)
