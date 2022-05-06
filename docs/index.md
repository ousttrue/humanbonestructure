# HumanBoneStructure

<https://github.com/ousttrue/humanbonestructure>

{term}`ヒューマノイド` 向け {term}`ポーズ` の標準化の調査と python 実装。

厳格なTPoseを介したポーズ転送 (retarget) について。

```{graphviz}
digraph tpose {
  "vpd/vmd(A stance + world coord)" -> "strict tpose";
  "motion capture / bvh (T stance + world coord)" -> "strict tpose";
  "mediapipe / kinect (position based)" -> "strict tpose";
  "strict tpose" -> "vrm-0.x (T stance world coord)";
  "strict tpose" -> "vrm-1.0 (T stance local coord)";
}
```

## 作業予定

### 1. 厳格TPose + ワールド軸 によるポーズの相互変換

* 正規化前後での変化
  * それに伴うポーズ、コンストレイント、スプリングのパラメーター変化の追随

主に、同一モデルでの初期ポーズ、ローカル軸変化への対応を扱う。

### 2. 厳格TPose + ローカル軸 によるポーズの操作

`厳格TPose + ローカル軸` に対する `ポーズ` の運用テスト。

* ポーズの手付け
* ポーズの生成(手など)
* ポーズの合成(部位別のポーズを統合する)、ブレンド、スイッチング
* 他モデルへのリターゲット実験
* ポーズ単体でのアセット化、フォーマット

```json
{
  "BONE0": {
    "xzy": [10, 20, 30],
  },
  "BONE2": {
    "x": [10],
  },
  "BONE1": {
    "quat": [0, 0, 0, 1],
  },
}
```

## メモ

```
D = TPOSE_DELTA
A = LOCAL_AXIS_DELTA
P = POSE
```

```{math}
P' = D^{-1} \cdot A^{-1} \cdot P \cdot A
```

```{toctree}
:maxdepth: 2
retarget/index
humanbone/index
implements/index
appendix/index
glossary
```

# Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
