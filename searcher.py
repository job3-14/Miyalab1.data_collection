#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
サーチャー
バイナリデータとして保存した索引を読み込み検索をする。
"""

__author__ = 'Ayumu Sakai'
__version__ = '1.0.0'
__date__ = '2023/10/31'

from operator import inv
import os
from re import S
import sys
import pickle
import matplotlib.pyplot as plt
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter




class Searcher:
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
            input_path = self.join_path(self.args.input_path)     # inputパス
            inverted_index_path = self.join_path(input_path, 'inverted_index','inverted_index.pkl')     # 転置インデックスのパス
            inverted_index = self.load_pkl(inverted_index_path) # 転置インデックスをロード
            print(inverted_index)

        except KeyboardInterrupt:
            print('インデックスの作成を終了します')
    
    @staticmethod
    def join_path(*a_tuple):
        """
        ファイルをのディレクトリを返す。
        引数(*a_tuple)は複数の引数をタプルとして受け取る
        """
        return os.path.join(*a_tuple)
    

    def load_pkl(self, input_path):
        """
        バイナリファイルを読み込み辞書を返す。
        """
        print(input_path)
        with open(input_path, mode='rb') as f:
            dict = pickle.load(f)
        return dict

def get_args():
    """
    コマンドライン引数を応答します
    """
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-i", "--input_path", type=str, required=False, default='index.pkl',
        help="入力ファイルを指定します",
    )
    return parser.parse_args()


def main():
    """
    メイン（main）プログラムです
    常に0を応答します
    """
    args = get_args()
    app = Searcher(args)
    app.run()
    return 0


if __name__ == '__main__':
    sys.exit(main())
