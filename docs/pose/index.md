# ポーズ

## ポーズとは

3D CG における `Pose` とは、各 Joint の初期姿勢からの回転の差分である。

`Pose = DeltaFromInitial`

## 初期姿勢とは

VRM では TPose を採用しているが、各モデルの TPose は同一ではない。

## 完全に共通の初期姿勢として、厳格TPose を提案したい

`Initial = InitialFromStrictT`

となるので

`StrictTPose = InitialFromStrictT + DeltaFromInitial`

となります。

各モデルの具体的なポーズは `Pose = StrictTPose - InitialFromStrictT` で表現できるので、
初期姿勢の差分を加味できる。

`InitialFromStrictT` に親指のロールのずれなどを含ませることを想定

## InitialFromStrictT をどうやって得るか

シンプル

* 厳格TPose になるように各ボーンをまっすぐに伸ばす
    * ロールがずれる可能性がある

オプション

* まっすぐに伸ばす前のモデルのローカル軸が (head-tail) + (up vector) を表しているとみなし、この座標系を利用して厳格TPose にする
    * ロールは正確になる
    * ローカル軸が正しく設定されているかどうかをコンピューターは判断できないので、正しいと信じて実行することになる
    * 自明、一意のローカル軸設定は無いので類推するようなファジーな動作になるであろう
