# human bone

```{figure} ../retarget/logic.jpg
```

* ローカル軸要るかね？
  * 手だけとか、上半身だけなどの部分モーションを合体するときにローカル軸あった方が管理しやすい予感(実際にやってないので不明)
  * 一軸関節の表現を float にするときにわかりやすい
  * 指モーションの生成とかするときにわかりやすい(ような気がする)

## 厳格TPose 向けの HumanBone 定義

* ボーンローカル座標をXYZではなく、Yaw,Pitch,Roll で抽象的に規定する。+で右手系の方向に回転することにしよう(Yaw+左,Pitch+上,Roll+右)
* ボーンを TPose のときに連続して同じ方向に進むものに分類
  * 連続の最後に末端ボーンが必要(bvhのendSite)
  * hand を中指に接続していたが、hand と finger 分離したほうがよさそう(中指の開始位置が厳格TPoseで変わらない方がよい)
  * 同じ分類のものは同じローカル軸を持つ

| 分類             | bone                                                                   | Roll軸(進行方向) | Yaw軸(UP方向) |
| ---------------- | ---------------------------------------------------------------------- | ---------------- | ------------- |
| 体幹             | hips, spine, chest, neck, head, endSite                                | 上               | 前            |
| 左腕             | leftShoulder, leftUpperArm, leftLowerArm, leftHand, endSite            | 左               | 前            |
| 左脚             | leftUpperLeg, leftLowerLeg, leftFoot, leftToes, endSite                | 下               | 後            |
| 右腕             | rightShoulder, rightUpperArm, rightLowerArm, rightHand, endSite        | 右               | 前            |
| 右脚             | rightUpperLeg, rightLowerLeg, rightFoot, rightToes, endSite            | 下               | 後            |
|                  |                                                                        |                  |
| 左親指以外の四指 | index, middle, ring, little の proximal, intermediate, distal, endSite | 左               | 下            |
| 左親指           | metaCarpal, proximal, distal, endSite                                  | 左               | 後            |
| 右親指以外の四指 | index, middle, ring, little, endSite                                   | 右               | 下            |
| 右親指           | metaCarpal, proximal, distal, endSite                                  | 右               | 後            |

* 体で5分類、21ボーン
* 指で10分類, 30ボーン
* 各分類ごとに先頭の位置が必要で、後続は長さだけで良い
  * 体で 5 pos, 21 length (float 36)
  * 指で 10 pos, 30 length (float 60)

## XYZ

実装に向けて、Yaw, Pitch, Roll の XYZ 割当をきめる。

```{figure} roll_up.jpg

Blender 流にしよう。
ロール軸(+Y)
UP(+Z)
```

とする。

```{toctree}
body
arm
leg
fingers
```
