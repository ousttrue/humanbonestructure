# 姿勢

## 姿勢

各 Joint の `ワールド回転 + 位置`。

## 初期姿勢とポーズ

### 初期姿勢とは

VRM では TPose を採用しているが、各モデルの TPose は同一ではない。

### ポーズとは

3D CG における `Pose` とは、各 Joint の初期姿勢からの回転の差分である。

`Pose = DeltaFromInitial`

## 厳格TPose を初期姿勢にする

`Initial = InitialFromStrictT`

となるので

`StrictTPose = InitialFromStrictT + DeltaFromInitial`

となります。

各モデルの具体的なポーズは `Pose = StrictTPose - InitialFromStrictT` で表現できるので、
初期姿勢の差分を加味できる。

`InitialFromStrictT` に親指のロールのずれなどを含ませることを想定
