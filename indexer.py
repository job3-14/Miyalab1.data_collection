#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
転置インデックスで索引を作り、バイナリデータとして保存するプログラム
"""

__author__ = 'Ayumu Sakai'
__version__ = '1.0.0'
__date__ = '2023/10/25 (Created: 2023/10/25)'

#import json
#import os
import sys
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
            pass
        except KeyboardInterrupt:
            print('インデックスの作成を終了します')


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
