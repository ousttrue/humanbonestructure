# HumanBoneStructure

<https://github.com/ousttrue/humanbonestructure>

```{blockdiag}
blockdiag {
  orientation = portrait

  // before  
  MoCap -> FK-T-Pose;
  Dedicated-Motion -> Rig -> Bone-Quaternion;
  Bone-Quaternion -> FK-T-Pose
  FK-T-Pose[color = pink];

  // after
  FK-T-Pose -> Hierarchy;
  Hierarchy -> Secondary;
  Secondary -> Skinning;

  //
  Bone-Quaternion -> Hierarchy[color = red, style = dashed]

  group {
      Dedicated-Motion; Rig; Bone-Quaternion
      label = "bone local axis";
      color = "#DDFFDD";
  }

  FK-T-Pose[color = pink];

  group {
      Hierarchy; Secondary; Skinning;
      label = "bone local axis";
      color = "#DDFFDD";
  }
}
```

```{note}
* bone local axis
  * モデル間の互換性は無い

* Rig
  * IK
  * Constraint

* Secondary
  * SpringBone
  * Constraint
    * LookAt
  * Cloth
  * Physics
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
