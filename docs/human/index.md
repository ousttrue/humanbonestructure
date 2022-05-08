# Humanoid

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
| 右腕             | rightShoulder, rightUpperArm, rightLowerArm, rightHand, endSite(もしくはrightMiddleFinger) | 右               | 前            |
| 左脚             | leftUpperLeg, leftLowerLeg, leftFoot, endSite                                              | 下               | 後            |
| 右脚             | rightUpperLeg, rightLowerLeg, rightFoot, endSite                                           | 下               | 後            |
|                  |                                                                                            |                  |
| 左つま先         | leftToes, endSite                                                                          | 前               | 上            |
| 右つま先         | rightToes, endSite                                                                         | 前               | 上            |
|                  |                                                                                            |                  |
| 左親指以外の四指 | index, middle, ring, little の proximal, intermediate, distal, endSite                     | 左               | 下            | 2,1,1くらいの長さ比      |
| 左親指           | metaCarpal, proximal, distal, endSite                                                      | 左               | 後            |
| 右親指以外の四指 | index, middle, ring, little, endSite                                                       | 右               | 下            |
| 右親指           | metaCarpal, proximal, distal, endSite                                                      | 右               | 後            |

### Core (19ボーン)

体幹, 左右腕、左右脚で 19 ボーン

### Option: つま先(2ボーン)

左右ひとつずつ

### Option: 指(30ボーン)

1指3関節 x 5本 x 左右 で 30 ボーン

## データ表現

```c++
struct Part
{
  vec3 position;
  std::vector<float> length;
};

struct Skeleton
{
  Part trunk; // hips, spine, chest, neck, head, head-end
  Part leftArm; // shoulder, upper, lower, hand, hand-end or middle-finger  
  Part rightArm; // shoulder, upper, lower, hand, hand-end or middle-finger  
  Part leftLeg; // upper, lower, foot, foot-end(heel)
  Part rightLeg; // upper, lower, foot, foot-end(heel)
  Part lefToes;
  Part rightToes;
  Part leftFingerThumbnail;
  Part leftFingerIndex;
  Part leftFingerMiddle;
  Part leftFingerRing;
  Part leftFingerLittle;
  Part rightFingerThumbnail;
  Part rightFingerIndex;
  Part rightFingerMiddle;
  Part rightFingerRing;
  Part rightFingerLittle;
};
```

```{toctree}
body
arm
leg
fingers
```
