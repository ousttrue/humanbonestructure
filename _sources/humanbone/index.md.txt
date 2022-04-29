# Human bone

```{figure} logic.jpg
すべてのボーンが `完全に` ワールド軸平行
```

## 厳格TPose 向けの HumanBone 定義

* ボーンローカル座標をXYZではなく、Yaw,Pitch,Roll で抽象的に規定する。+で右手系の方向に回転することにしよう(Yaw+左,Pitch+上,Roll+右)
* ボーンを TPose のときに連続して同じ方向に進むものに分類
  * 連続の最後に末端ボーンが必要(bvhのendSite)
  * hand を中指に接続していたが、hand と finger 分離したほうがよさそう(中指の開始位置が厳格TPoseで変わらない方がよい)
    * やっぱり中指で良さそう。hand-end 追加するのめんどくさいし、中指になるでしょ。
  * 同じ分類のものは同じローカル軸を持つ

| 分類             | bone                                                                                       | Roll軸(進行方向) | Yaw軸(UP方向) | memo                     |
| ---------------- | ------------------------------------------------------------------------------------------ | ---------------- | ------------- | ------------------------ |
| 体幹             | hips, spine, chest, neck, head, endSite                                                    | 上               | 前            | あえてupperChest言及せず |
| 左腕             | leftShoulder, leftUpperArm, leftLowerArm, leftHand, endSite(もしくはleftMiddleFinger)      | 左               | 前            |
| 左脚             | leftUpperLeg, leftLowerLeg, leftFoot, endSite                                              | 下               | 後            |
| 右腕             | rightShoulder, rightUpperArm, rightLowerArm, rightHand, endSite(もしくはrightMiddleFinger) | 右               | 前            |
| 右脚             | rightUpperLeg, rightLowerLeg, rightFoot, endSite                                           | 下               | 後            |
|                  |                                                                                            |                  |
| 左つま先         | leftToes, endSite                                                                          | 前               | 上            |
| 右つま先         | rightToes, endSite                                                                         | 前               | 上            |
|                  |                                                                                            |                  |
| 左親指以外の四指 | index, middle, ring, little の proximal, intermediate, distal, endSite                     | 左               | 下            | 2,1,1くらいの長さ比      |
| 左親指           | metaCarpal, proximal, distal, endSite                                                      | 左               | 後            |
| 右親指以外の四指 | index, middle, ring, little, endSite                                                       | 右               | 下            |
| 右親指           | metaCarpal, proximal, distal, endSite                                                      | 右               | 後            |

* 体で7分類、21ボーン
* 手指10分類, 30ボーン

* 各分類ごとに先頭の位置が必要で、後続は長さだけで良い
  * 体で 7 pos, 21 length (float 36)
  * 指で 10 pos, 30 length (float 60)

厳密TPoseでこの数字が同じ骨格は同じ体格であると言えて、完全に同じ姿勢にすることができる。
この数字が違うも骨格では差異が生じる。
体格差リターゲットの必要性が生じる。

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
