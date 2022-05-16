from typing import Dict, Type
from pydear import imnodes as ImNodes
from pydear.utils.node_editor.node import PinStyle, color_int
from .time_node import TimeNode
from .bvh_node import BvhNode
from .view_node import ViewNode
from .mmd_pose_node import MmdPoseNode
from .mmd_model_node import MmdModelNode
from .gltf_node import GltfNode
from .tpose_node import TPoseNode
from .pose_muxer import PoseMuxerNode
from .skeleton_muxer import SkeletonMuxerNode
from .network_node import TcpClientNode
from ...humanoid.pose import Pose
from ...humanoid.humanoid_skeleton import HumanoidSkeleton

TYPES = [
    TimeNode,
    BvhNode,
    MmdPoseNode,
    MmdModelNode,
    GltfNode,
    TPoseNode,
    ViewNode,
    TcpClientNode,
    PoseMuxerNode,
    SkeletonMuxerNode,
]

PIN_STYLE_MAP: Dict[Type, PinStyle] = {
    HumanoidSkeleton: PinStyle(
        ImNodes.ImNodesPinShape_.QuadFilled, color_int(64, 64, 255)),
    Pose: PinStyle(ImNodes.ImNodesPinShape_.TriangleFilled, color_int(64, 255, 64)),
}
