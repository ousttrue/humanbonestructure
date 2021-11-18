# HumanBoneStructure

<https://github.com/ousttrue/bonestructure>

```{blockdiag}
blockdiag {
  MoCap -> Pose-Euler -> Pose;
  PoseEstimation -> Pose-Euler;
  Blender -> Pose-Euler;
  AnimationClip -> Pose-Quaternion -> Pose;

  Pose[color = pink];
}
```

```{blockdiag}
blockdiag {
  Pose[color = pink];

  Pose -> Pose-Quaternion -> Hierarchy;
  Hierarchy -> Skinning[label = matrix];
}
```

```{toctree}
:maxdepth: 2
implements/index
appendix/index
glossary
```

# Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
