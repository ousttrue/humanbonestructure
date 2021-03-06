# 用語集

```{glossary}
Node
ジョイント
Joint
  position + rotation。簡単のために本記事では scale は除外する。

骨格
Skeleton
  Joint の集合。
  各Joint は初期姿勢として World 位置を持つ。
  初期姿勢に回転が含まれるなら、それをローカル軸と言う。

モデル
  スキニングモデルのことを指すかもしれないが、注意する。

ボーンローカル軸
ローカル軸
  初期姿勢での Joint の向き。
  ヒューマンボーンの稼働方向とローカル軸が一致しているデータ表現がありうるが、
  保証されておらず、判定する方法も無い。誤判定してローカル軸をヒューマンボーンとして使ってしまうと、
  ワールド軸から推定するよりも結果が悪化することもありえる。
  もし、有効なローカル軸から厳格TPoseを作ることができれば、精度を高めることができて、
  親指の斜めさを解決することが期待できる。
  ユーザーモデルに決まった軸付けを要求するのは難しい(技量的、使用ツール的にできない可能性)。
  厳格TPoseでは `Blender流` に割り当てるので ロール軸がY、yaw 軸が Z である1種類しか考慮しない。

ボーン
Bone
ヒューマンボーン
HumanBone
  Bone は Joint を拡張して、tail と up を決めることにより３次元の空間を明示する。
  ヒューマノイドを構成する。
  本記事では、joint(node) と bone を明確に区別する。

ヒューマノイド
Humanoid
  決まったボーン構成を持つ骨格。
  必須ボーンと必須ボーン同士の親子関係が決まっている。
  ヒューマノイドは、hips 以外は移動せずに回転しかしない。

ポーズ
Pose
  hipsの移動と各ヒューマンボーンの回転のセット。
  skeleton の初期姿勢からの相対値で表される。

姿勢
  骨格にポーズを適用した状態。
  本記事では骨格の見た目全体を姿勢と呼び、ポーズはモーションの１フレーム分のデータというニュアンスで使い分ける。
  `boneの姿勢` は、Transform(pos + rot)という意味で使うかも。

TPose
  モーションキャプチャーの初期ポーズとして使われることが多い。
  直立して、両腕を水平にして、手の平を下向きにする。
  モーションキャプチャーでは指を扱わないことが多いこともあり、指はあいまい。

リターゲット
  同一体格の初期姿勢、ローカル軸違いのリターゲット。これは座標変換で、変換前後で同じ姿勢を取ることができるはずである。
  異なる体格に対する体格差リターゲット。IKなどでモーションを補正する(回転を変更する)需要が発生しうる。
  本記事では、２種類のリターゲットを区別する。
  前者はモデルを扱いやすいように変換する前後で発生し、後者はポーズを異なるモデル間でやり取りするときに発生する。
  単にリターゲットと言ったときに２つは区別されてないので、内容に注意する。
  vrmの正規化は前者である。
  Unity の mecanim、モーションビルダーのキャラクタライズは両者が混ざっているんでないか。
  具体的には、(元モデルの座標系)=>座標変換=>(TPose的な処理用の座標系)=>ポーズ転送=>座標変換=>(対象モデルの座標系)
  というような一連の操作がパイプラインのようになっている。

初期姿勢
姿勢の個性
  初期姿勢が、TPoseから大きく逸脱するような骨格のサポートを想定した場合になにか必要そう。
  厳格TPoseからの差分回転を適用すると変になるかもしれない。
```
