# %%
# ================================================================================
# Importing Application Dependencies
# ================================================================================
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from dateutil import tz

from typing import List

import os
import json
import requests
import bs4
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
# %%
# ================================================================================
# Configuring requesting data and constants
# ================================================================================

# ----------------------------------------
# Setting constants
# ----------------------------------------

# today = datetime.datetime.now()
today = date.today()

year = (today - relativedelta(months=1)).strftime('%Y')
mon =  (today - relativedelta(months=1)).strftime('%m')
#C:\GitClone\Crawling_Study
path = f'Crawling_Study/Data/collection/{year}/{mon}/'
if not os.path.exists(path):
  os.makedirs(path)

file_name = f"naver-{year}{mon}"
file_ext = "csv"
file = "{}/{}.{}".format(path, file_name, file_ext)
# %%
# FIND LASTPAGE -> int
def FIND_LASTPAGE(DATE: str) -> int:
  headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}
  NAVER_NEWS_RES = requests.get("https://news.naver.com/main/list.nhn?mode=LS2D&mid=shm&sid2=252&sid1=102&date=" + DATE, headers = headers)
  SOUP = BeautifulSoup(NAVER_NEWS_RES.content, "html.parser")

  NOW_PAGE = SOUP.select_one('#main_content > div.paging > strong')
  NEXT_PAGE = SOUP.select_one('#main_content > div.paging > a')
  LAST_PAGE = "0"
  try:
    if(NEXT_PAGE.get_text() == "2"):
      LIST_PAGE = SOUP.select('#main_content > div.paging > a')
      for page in LIST_PAGE:
        LAST_PAGE = page.get_text()
      return int(LAST_PAGE)
  except:
    LAST_PAGE = NOW_PAGE.get_text()
    return int(LAST_PAGE)
# %%
# Crawling NAVER NEWS -> List
def CRAWLING_NAVER(today: date) -> List:
  # Set user -> except DISCONNECT ERROR
  headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}
  # 전달의 마지막 날 구하기
  last_day_month_ago = today.replace(day=1) - timedelta(days=1)
  # 전달의 첫째 날 구하기
  URL_DATE = last_day_month_ago.replace(day=1)

  headline_list = []
  writing_list = []
  data = []

  # loop range first_day -> last_day
  for DATE in range(int(URL_DATE.strftime('%d')), int(last_day_month_ago.strftime('%d')) + 1):
    URL_DATE = URL_DATE.replace(day=int(DATE))
    LAST_PAGE = FIND_LASTPAGE(URL_DATE.strftime('%Y%m%d'))
    # loop range 1 -> LAST_PAGE
    for PAGE in range(1, int(LAST_PAGE) + 1):
      headline_list.clear()
      writing_list.clear()
      URL = "https://news.naver.com/main/list.nhn?mode=LS2D&mid=shm&sid2=252&sid1=102&date=" + URL_DATE.strftime('%Y%m%d') + "&page=" + str(PAGE)
      NAVER_NEWS_RES = requests.get(URL, headers = headers)
      SOUP = BeautifulSoup(NAVER_NEWS_RES.content, "html.parser")

      # FIND HEADLINE
      HEADLINE_TAG = SOUP.select('dt a')
      for headline in HEADLINE_TAG:
        TITLE = str(headline.get_text()
        .replace("\t", "")
        .replace("\n", "")
        .replace("\r", ""))
        if(TITLE != "" and TITLE != "동영상기사"):
          headline_list.append(TITLE)

      # FIND WRITING
      WRITING_class = SOUP.select('.writing')
      for writing in WRITING_class:
        writing_list.append(writing.get_text())
      
      # MAKE DATA LIST
      if(len(headline_list) == len(writing_list)):
        for i in range(0, len(headline_list)):
          data.append([str(writing_list[i]), str(headline_list[i]), URL_DATE.strftime('%Y-%m-%d')])
  
  print("저장된 rows : " + str(len(data)))
  return data
# %%
# MAKE CSV FILE - using PANDAS
def MAKE_CSV_FILE(data_list: List) -> None:
    df = pd.DataFrame(data=data_list,
                      columns=['언론사', '제목', '등록일'])
    df = df.replace('', np.nan)                                 # 공백을 NaN으로 변경
    df = df.dropna(axis=0)                                      # 결측값 있는 행 제거
    df = df.drop_duplicates(['제목']).reset_index(drop=True)    # 중복된 타이틀 제거

    df.to_csv(file, index=False)
# %%
# ================================================================================
# Main function
# ================================================================================
def main() -> None:
    pass
# %%
# Running Python script using the command-line interface (CLI)
if __name__ == "__main__":
    MAKE_CSV_FILE(CRAWLING_NAVER(today))
