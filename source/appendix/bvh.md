# BVH形式

* ヒエラルキー(初期ポーズ)
  * {term}`TPose` であることが多いがそうでないこともある
  * 距離の単位が不統一(cm, inch... etc)。
  * Z+, Z- どっち向きかも決まりなし(つま先の進行方向や、joint名の left, rightから類推できることが多い)。
  * ボーンに初期回転は無い。この状態に対する Euler角で ポーズが定義される。

* 各Jointのフレームごとの回転(Euler角)を記録。
  * Euler角の乗算順は自由。Hierarchy の Channels の順番に従う。

* Rootのみ移動も記録。

* 指は扱わない(フォーマット上、記録することは可能)

## Hierarchy

* Joint の木構造。
  * 各Jointは親に対する相対位置を記録する。

## Joint の計算式

`Root - joint_1 ... joint_n` のときの joint_n の姿勢行列。

```{math}

R = E_z \cdot E_x \cdot E_y

(Offset_0 \cdot T_0 \cdot R_0) (Offset_1 \cdot R_1) ... (Offset_n \cdot R_n)

```

## Frames

* 各フレームの回転(Euler角YXZ)を記録

## Download できるサイト

### github

* <https://github.com/wspr/bvh-matlab>
* <https://github.com/perfume-dev/example-openFrameworks/tree/master/example-bvh/bin/data>

### CGSpeed

* <https://sites.google.com/a/cgspeed.com/cgspeed/motion-capture>

* スケールが違う

#### Daz-friendly

`Zrotation Yrotation Xrotation`

#### 3dsMax-friendly

#### MotionBuilder-friendly

`Zrotation Yrotation Xrotation`

## BVH を作る

TODO:
