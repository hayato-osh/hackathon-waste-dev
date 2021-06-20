from typing import List, Tuple
import re
from datetime import datetime
import os

import tweepy
from tweepy import api

from dotenv import load_dotenv


class TwitterAPI:
    # 認証に必要なキーとトークン

    load_dotenv()

    # 環境変数を参照
    API_KEY = os.getenv('API_KEY')
    API_SECRET = os.getenv('API_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

    # APIの認証
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    
    # APIオブジェクトの作成
    api = tweepy.API(auth)


    """
        特定のユーザーの特定のツイートを取得する

        return 
               ツイート内容とツイートされた時間
    """
    # first_main.pyで呼び出すメソッド
    def get_user_tweets(self, id:str, since:str, until:str) -> List[Tuple[str, datetime]]:

        # (1)リツイート、リプライのツイートは無視する。(2)「#今日の積み上げ」ツイートを抽出する
        tweets = [tweet for tweet in tweepy.Cursor(TwitterAPI.api.user_timeline, id=id).items(500) if (list(tweet.text)[:2]!=['R', 'T']) & (list(tweet.text)[0]!='@') & (re.search("#今日の積み上げ", str(tweet.text)) != None) & (float(tweet.created_at.timestamp()) >= float(since)) & (float(tweet.created_at.timestamp()) <= float(until))]

        # 各ツイートの内容と日付をlistに格納
        tweet_info = []
        for tweet in tweets:
            tweet_info.append((tweet.text, tweet.created_at))
        
        return tweet_info

    # second_main.pyで呼び出すメソッド
    def get_user_tweets_byTime(self, id:str, yd:float, dby:float, ago_31days:float, ago_32days:float) -> Tuple:
        
        # (1)リツイート、リプライのツイートは無視する。(2)「#今日の積み上げ」ツイートを抽出する
        tweets = [tweet for tweet in tweepy.Cursor(TwitterAPI.api.user_timeline, id=id).items(limit=500) if (list(tweet.text)[:2]!=['R', 'T']) & (list(tweet.text)[0]!='@') & (re.search("#今日の積み上げ", str(tweet.text)) != None)]

        # 昨日~31日前のツイートを抽出
        yd_31days_tweet = [tweet for tweet in tweets if (float(tweet.created_at.timestamp()) >= ago_31days) & (float(tweet.created_at.timestamp()) <= yd)]
        
        # 一昨日~32日前のツイートを抽出
        dby_32days_tweet = [tweet for tweet in tweets if (float(tweet.created_at.timestamp()) >= ago_32days) & (float(tweet.created_at.timestamp()) <= dby)]

        # 昨日~31日前の内容と日付をlistに格納
        yd_31days_tweet_info = []
        print(len(yd_31days_tweet))
        for tweet in yd_31days_tweet:
            yd_31days_tweet_info.append((tweet.text, tweet.created_at))

        # 一昨日~32日前の内容と日付をlistに格納
        dby_32days_tweet_info = []
        print(len(dby_32days_tweet))
        for tweet in dby_32days_tweet:
            dby_32days_tweet_info.append((tweet.text, tweet.created_at))
        
        return dby_32days_tweet_info, yd_31days_tweet_info

    # ツイートを投稿する
    def post_tweet(self, tweet:str) -> None:
        res = TwitterAPI.api.update_status(tweet)
        print(res)

    
    # DMを送る
    def send_directMessage(self, user_id:str, message:str) -> None:

        # user idからid(整数)を取得する
        recipient_id = TwitterAPI.api.get_user(user_id)

        # DMを送る
        res = TwitterAPI.api.send_direct_message(recipient_id=recipient_id.id_str, text=message)
        print(res)

    """
        tweet間の期間を計算

        return 
               二つのツイートされた時間の差
    """
    def clu_between_tweets_period(self, created_time1:datetime, created_time2:datetime) -> float:
        # unixtimeに変換する
        unix_time1 = created_time1.timestamp()
        unix_time2 = created_time2.timestamp()
        
        # 時間差を計算する
        dif_time = unix_time2 - unix_time1

        return dif_time


    """
        指定期間内に積み上げツイートをしているか判定する.

        return 
               積み上げツイートをしてるなら　　　 ->   True
               積み上げツイートをしていないなら　 ->   False 

    """
    def jud_kotsukotsu_load(self, dif_time:float, period:int):
        # 指定期間を秒に変換する。
        period_second = period * 86400

        if dif_time > period_second:
            return True
        
        return False