# HumanBoneStructure

<https://github.com/ousttrue/humanbonestructure>

{term}`ヒューマノイド` 向け {term}`ポーズ` の標準化の調査と python 実装。

厳格なTPoseを介したポーズ転送 (retarget) について。

TODO: ポーズの右手左手の変換の考慮。quaternion ではなく axis + angle 記述？

* ローカル軸要るかね？
  * 手だけとか、上半身だけなどの部分モーションを合体するときにローカル軸あった方が管理しやすい予感(実際にやってないので不明)
  * 一軸関節の表現を float にするときにわかりやすい
  * 指モーションの生成とかするときにわかりやすい(ような気がする)

```{graphviz}
digraph tpose {
  "vpd/vmd(A stance + world coord)" -> "strict tpose";
  "motion capture / bvh (T stance + world coord)" -> "strict tpose";
  "mediapipe / kinect (position based)" -> "strict tpose";
  "strict tpose" -> "vrm-0.x (T stance world coord)";
  "strict tpose" -> "vrm-1.0 (T stance local coord)";
}
```

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
