#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ニュース記事をスクレイピングするプログラム

[参考URL]
https://docs.python.org/3/library/index.html
https://requests.readthedocs.io/en/latest/
https://www.crummy.com/software/BeautifulSoup/bs4/doc/
"""

__author__ = 'HAYASHI Tomokazu, Ayumu Sakai'
__version__ = '1.0.3'
__date__ = '2023/10/20 (Created: 2023/9/12)'

import json
import os
import re
import sys
import time
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
import requests
from bs4 import BeautifulSoup


class Crawler:
    """
    カテゴリごとに記事をスクレイピングするためのクラス
    """
    def __init__(self, args, domains, sleep_time=3):
        """
        初期化します
        """
        self.args = args
        self.domains = domains
        self.sleep_time = sleep_time

    def run(self, category_name, start_urls, url_pattern):
        """
        スクレイピングを実行します
        """
        try:
            print(f'\ncategory: {category_name}')
            output_path = self.join_path(self.args.output_path, category_name)
            self.make_directories(output_path)
            urls = self.crawl_top_page(start_urls, url_pattern)
            self.crawl_article_page(category_name, urls, output_path)
        except KeyboardInterrupt:
            print(f'\n{category_name}カテゴリのスクレイピングを終了します')

    @staticmethod
    def join_path(*a_tuple):
        """
        ファイルを保存するディレクトリを返す。
        引数(*a_tuple)は複数の引数をタプルとして受け取る
        """
        return os.path.join(*a_tuple)

    def crawl_top_page(self, start_urls, url_pattern):
        """
        start_urlsから記事のurlセットを作成し、返す。
        もし見つからなかった場合は空のセットを返す。
        """
        url_set = set()
        for start_url in start_urls:
            print(f'Top page URL: {start_url}', end='')
            html_document = self.get_html_document(start_url)
            if html_document:          # 変数html_ducmentに値が入っていればSuccess、入っていなければFailureでreturn
                print(' -> Success')
            else:
                print(' -> Failure')
                return url_set
            url_set |= self.extract_urls(url_pattern, html_document) #重複しないように
        return url_set

    def get_html_document(self, url):
        """
        urlからテキストをダウンロードし、テキスト本文(html)を返す
        """
        time.sleep(self.sleep_time)
        try:
            response = requests.get(url, timeout=(6.0, 6.0)) # ダウンロード
        except OSError:
            return None
        if response.status_code != 200:
            return None
        # response.encoding = response.apparent_encoding
        return response.text

    @staticmethod
    def extract_urls(url_pattern, html_document):
        """
        BeatifulSoupを使用して解析する。引数のdocumentからurlリストのみを抽出し返す。
        """
        soup = BeautifulSoup(html_document, "html.parser")
        url_set = set()
        for each in soup.find('ul', class_='widget_boxlist_set').find_all('a'): # soupから<ul>(widget_boxlist_setクラス)を検索しその中から<a>の内容を繰り返す
            url = each.get('href') #urlのみを抽出
            if url_pattern.match(url): # 指定されたurlパターンと正しければ
                url_set.add(url) #urlのセットに追加する
        return url_set

    def crawl_article_page(self, category_name, urls, output_path):
        """
        指定された回数だけ記事をサーバーから取得し、jsonファイルとして書き込みを行う
        """
        article_count = 0
        for url in urls:
            if not url.startswith(self.domains): # domainsのurlが不完全であれば、完全なurl形式に変換する
                url = f'{self.domains}{url}'
            print(f'  Article page URL: {url}', end='')
            article_id = self.get_article_id(url)
            file_name = self.join_path(               # パスとファイル名で出力先のパスを指定
                output_path, f"{article_id}.json"
            )
            if os.path.isfile(file_name):     #ファイルが既に存在すればcontinue
                print(' -> Already exists')
                continue
            html_document = self.get_html_document(url) #urlから記事のhtmlを取得
            if html_document: # ドキュメントが存在すれば
                article_count += 1 # 記事数カウント
                progress = f'({article_count} / {self.args.article_nums})'  # 現在の取得数 / 設定された取得数
                print(f' -> Success {progress}')
            else:
                print(' -> Failure')   # ドキュメントが変数内に入っていないためcontinue
                continue
            article = self.extract_title_and_body(html_document)
            article_dict = self.define_format(
                article_id, category_name, url, article,
            )
            self.write_json_file(file_name, article_dict)
            if article_count >= self.args.article_nums:
                return

    def extract_title_and_body(self, html_document):
        """
        入力された記事htmlからタイトルと本文を返す
        """
        soup = BeautifulSoup(html_document, "html.parser")
        title = soup.title.string
        body = soup.find('body').find('div', class_='article_body').get_text()
        return title, body

    def define_format(self, article_id, category_name, url, article):
        """
        id,category,url,title,bodyを辞書型にして返す
        """
        return {
            'id': article_id,
            'category': category_name,
            'url': url,
            'title': article[0],
            'body': article[1],
        }

    @staticmethod
    def get_article_id(url):
        """
        urlから最後の/の後の記事idのみをreturnする。
        """
        return url.rstrip('/').rsplit('/', 1)[-1]

    @staticmethod
    def make_directories(path):
        """
        出力するディレクトリを作成する
        """
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def write_json_file(file_name, a_dict):
        """
        入力された辞書をjsonファイルとして保存
        """
        with open(file_name, 'w', encoding='utf-8') as a_file:
            json.dump(a_dict, a_file, ensure_ascii=False, indent=2)


def get_args():
    """
    コマンドライン引数を応答します
    """
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--article_nums", type=int, required=False, default=100,
        help="取得するニュース記事の件数を指定します",
    )
    parser.add_argument(
        "-o", "--output_path", type=str, required=False, default='output',
        help="出力ディレクトリ名を指定します",
    )
    return parser.parse_args()


def configure_society():
    """
    社会(society)の設定をします
    """
    category_name = 'society'
    base_url = 'https://news.nifty.com/domestic/society/'
    start_urls = (f'{base_url}{x}' for x in range(1, 5))
    url_pattern = re.compile(r'/article/domestic/society/.+')
    return category_name, start_urls, url_pattern


def configure_government():
    """
    政治(government)の設定をします
    """
    category_name = 'government'
    base_url = 'https://news.nifty.com/domestic/government/'
    start_urls = (f'{base_url}{x}' for x in range(1, 5))
    url_pattern = re.compile(r'/article/domestic/government/.+')
    return category_name, start_urls, url_pattern


def configure_sports():
    """
    スポーツ(sports)の設定をします
    """
    category_name = 'sports'
    base_url = 'https://news.nifty.com/sports/athletic/'
    start_urls = (f'{base_url}{x}' for x in range(1, 5))
    url_pattern = re.compile(r'/article/sports/athletic/.+')
    return category_name, start_urls, url_pattern


def configure_technology():
    """
    IT(technology)の設定をします
    """
    category_name = 'technology'
    base_url = 'https://news.nifty.com/technology/techall/'
    start_urls = (f'{base_url}{x}' for x in range(1, 5))
    url_pattern = re.compile(r'/article/technology/techall/.+')
    return category_name, start_urls, url_pattern


def configure_entame():
    """
    エンタメ(entame)の設定をします
    """
    category_name = 'entame'
    base_url = 'https://news.nifty.com/entame/showbizd/'
    start_urls = (f'{base_url}{x}' for x in range(1, 5))
    url_pattern = re.compile(r'/article/entame/showbizd/.+')
    return category_name, start_urls, url_pattern


def configure_movie():
    """
    映画(movie)の設定をします
    """
    category_name = 'movie'
    base_url = 'https://news.nifty.com/entame/movie/'
    start_urls = (f'{base_url}{x}' for x in range(1, 5))
    url_pattern = re.compile(r'/article/entame/movie/.+')
    return category_name, start_urls, url_pattern


def configure_music():
    """
    音楽(music)の設定をします
    """
    category_name = 'music'
    base_url = 'https://news.nifty.com/entame/music/'
    start_urls = (f'{base_url}{x}' for x in range(1, 5))
    url_pattern = re.compile(r'/article/entame/music/.+')
    return category_name, start_urls, url_pattern


def configure_anime():
    """
    アニメ(anime)の設定をします
    """
    category_name = 'anime'
    base_url = 'https://news.nifty.com/entame/anime/'
    start_urls = (f'{base_url}{x}' for x in range(1, 5))
    url_pattern = re.compile(r'/article/entame/anime/.+')
    return category_name, start_urls, url_pattern


def configure_gourmet():
    """
    グルメ(gourmet)の設定をします
    """
    category_name = 'gourmet'
    base_url = 'https://news.nifty.com/item/gourmet/'
    start_urls = (f'{base_url}{x}' for x in range(1, 5))
    url_pattern = re.compile(r'/article/item/gourmet/.+')
    return category_name, start_urls, url_pattern


def main():
    """
    メイン（main）プログラムです
    常に0を応答します
    """
    args = get_args()
    app = Crawler(args, domains='https://news.nifty.com')
    app.run(*configure_society())
    app.run(*configure_government())
    app.run(*configure_sports())
    app.run(*configure_technology())
    app.run(*configure_entame())
    app.run(*configure_movie())
    app.run(*configure_music())
    app.run(*configure_anime())
    app.run(*configure_gourmet())
    return 0


if __name__ == '__main__':
    sys.exit(main())
