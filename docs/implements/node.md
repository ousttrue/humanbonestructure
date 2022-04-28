# Node操作

## Skinning

```{math}
Skinning = Root \cdots Local \cdot InverseBindMatrix

Local = Init \cdot Pose
```

## ローカル軸を追加

```{math}
Skinning = Root \cdots Local \cdot InverseBindMatrix

Local = Init \cdot Pose

Pose = ToLocalAxis \cdot OriginalPose \cdot ToLocalAxis^{-1}
```

## 厳格T-Poseにする

```python
def force_axis(head: Node, tail: Node, world_to: glm.vec3):
    local_matrix = glm.inverse(head.world_matrix) * tail.world_matrix
    local_src = glm.normalize(local_matrix[3].xyz)
    local_to = glm.inverse(glm.quat(head.world_matrix)) * world_to
    axis = glm.normalize(glm.cross(local_src, local_to))
    cos = glm.dot(src, to)
    r = glm.angleAxis(glm.acos(cos), axis)
    head.pose = Transform.from_rotation(r)
```
