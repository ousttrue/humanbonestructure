# 厳格TPose化する手順

## ローカル軸キャンセル

```{figure} unitychan_axis_cancel.gif
```

* 元のモデルは TPose を取っていることとする
* 各ボーンの進行方向(head-tail)は自明
* 各ボーンのYaw軸方向を定数で定める

以下のような感じで各ボーンの正規直交座標を求めることができて、
これと各jointのワールド行列の回転差分を求める。

```py
roll_axis = normalize(tail - head)
pitch = normalize(cross(yaw, roll_axis))
yaw = normalize(cross(roll_axis, pitch))
```

この手順で得られる回転を `LocalAxis` から `A` とする。

## 初期姿勢キャンセル

```{figure} unitychan_strict.gif
```
```{figure} t_clear.gif
```

事前にローカル軸キャンセルを適用した骨格の各Jointのワールド行列の逆行列の回転が回転差分である。
この手順で得られる回転を `DeltaFromT` から `D` とする。

## 厳格TPose差分ポーズを任意のモデルに適用する

入力ポーズ を `P` とする。

```{math}
P' = D \cdot A \cdot P \cdot A^{-1}
```

```{figure} axis_delta.gif
厳格TPoseの左から、異なる軸設定、異なる初期姿勢を持つモデルポーズを転送。
```

* 直接
* ローカル軸のキャンセル
* ローカル軸のキャンセル + 初期姿勢のキャンセル
* 初期姿勢のキャンセル
