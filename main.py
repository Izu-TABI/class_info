import requests
import time
import os
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage


def main():
  CHANNEL_ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
  line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

  years = '2023'
  month = '06'

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

  f_changes = open('class_changes.txt', 'r', encoding='UTF-8')
  changes_old_data = f_changes.read()
  if class_changes != changes_old_data:
    print("授業変更の情報が更新されました。")
    f = open('class_changes.txt', 'w')
    f.write(class_changes)
    f.close()

  f_canceled = open('canceled_class.txt', 'r', encoding='UTF-8')
  canceled_old_data = f_canceled.read()
  if canceled_class != canceled_old_data:
    print("休講の情報が更新されました。")
    f = open('canceled_class.txt', 'w')
    f.write(canceled_class)
    f.close()
  class_changes = class_changes[1:]

  massages = TextSendMessage(text=class_changes + canceled_class)
  line_bot_api.broadcast(messages=massages)

if __name__ == "__main__":
    main()
