#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
転置インデックスで索引を作り、バイナリデータとして保存するプログラム
"""

__author__ = 'Ayumu Sakai'
__version__ = '1.0.0'
__date__ = '2023/10/25 (Created: 2023/10/25)'

import json
import os
import sys
import glob
import MeCab
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter


class Indexer:
    """
    転置インデックスを作成し、保存するクラス
    """
    def __init__(self, args):
        """
        初期化します
        """
        self.args = args

    def run(self):
        """
        インデックスの作成および保存を行う
        """
        try:
            input_path = self.join_path(self.args.input_path)
            output_path = self.join_path(self.args.output_path)
            json_list = self.read_json(self.open_file_list(input_path, self.args.category))
            self.morphological_analysis(json_list)
            

        except KeyboardInterrupt:
            print('インデックスの作成を終了します')
    
    @staticmethod
    def join_path(*a_tuple):
        """
        ファイルをのディレクトリを返す。
        引数(*a_tuple)は複数の引数をタプルとして受け取る
        """
        return os.path.join(*a_tuple)
    
    @staticmethod
    def open_file_list(input_path, category):
        """
        引数に指定されたファイルないのファイル名の配列を返す。
        input_path:　入力ディレクトリ
        category: 転置インデックスを作成する対象カテゴリ
        """
        file_path = [] # フォルダ一覧
        for list in category:
            path = os.path.join(input_path, list)
            for j in glob.iglob(f'{path}/*.json'):
                file_path.append(j)
        return file_path
    
    @staticmethod
    def read_json(path):
        """
        引数のパスの辞書からjsonを読み込む。
        jsonからtitleとbodyのみの辞書をリスト形式で返す。
        """
        json_list = []
        for tmp_path in path:
            with open(tmp_path) as f:
                json_raw_data = json.load(f)
            del json_raw_data['category'], json_raw_data['url']
            json_list.append(json_raw_data)
        return json_list
    
    @staticmethod
    def morphological_analysis(json_list):
        """
        入力の辞書リストから形態素解析を行う
        """
        text = json_list[0]['title'] + '\n' + json_list[0]['body']
        tagger = MeCab.Tagger('')
        tagger.parse('')
        node = tagger.parseToNode(text)
        word_set = set()
        while node:
            term = node.surface
            pos = node.feature.split(',')[0]
            if pos in '名詞':
                word_set.add(term)
            node = node.next
        print(word_set)




        


def get_args():
    """
    コマンドライン引数を応答します
    """
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--category", nargs='*', required=True,
        help="転置インデックスを作成するカテゴリーを指定する。２種類以上のカテゴリーを入力した場合には組み合わせたインデックスを作成する。",
    )
    parser.add_argument(
        "-o", "--output_path", type=str, required=False, default='index',
        help="出力ディレクトリ名を指定します",
    )
    parser.add_argument(
        "-i", "--input_path", type=str, required=False, default='output',
        help="入力ディレクトリ名を指定します",
    )
    return parser.parse_args()


def main():
    """
    メイン（main）プログラムです
    常に0を応答します
    """
    args = get_args()
    app = Indexer(args)
    app.run()
    return 0


if __name__ == '__main__':
    sys.exit(main())
