# Armature to Unity

Blender の Armature のポーズを Unity 骨格に転送する実験 

## Blender

```{image} blender_euler.jpg 
```

```python
import bpy
import json

pose = bpy.context.active_object.pose
print(pose)
eulers = {}
for b in pose.bones:
    #print(b, b.rotation_euler)
    e = b.rotation_euler
    eulers[b.name] = (e.x, e.y, e.z)
print(json.dumps(eulers))
```

これが、bvhと同じになるかと思っていたのだが違う。
bvhから {term}`ボーンローカルEuler角`にする。

## Unity

euler角を右手系から左手系に変換する。

```
{x, -y, -z}
```

local軸のベクトルを得る。

```
Vector3 x_axis;
Vector3 y_axis;
Vector3 z_axis;
```

回転を作る。

```
var Rx = Quaternion.AngleAxis(x, x_axis)
var Ry = Quaternion.AngleAxis(y, y_axis)
var Rz = Quaternion.AngleAxis(z, z_axis)
```

YZXの順に乗算する。

```
var transofrm.localRotation = toTPose * Ry * Rz * Rx;
```

```{image} bl_to_uni.jpg 
```

