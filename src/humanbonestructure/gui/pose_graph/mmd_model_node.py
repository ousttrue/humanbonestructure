from typing import Optional, List
import pathlib
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized
from .file_node import FileNode


class MmdSkeletonOutputPin(OutputPin):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'skeleton')

    def process(self, node: 'MmdModelNode', input: InputPin):
        if node.pmd_pmx:
            raise NotImplementedError()


class MmdModelNode(FileNode):
    def __init__(self, id: int, pose_pin_id: int, path: Optional[pathlib.Path] = None) -> None:
        super().__init__(id, 'pmd/pmx', path,
                         [],
                         [
                             MmdSkeletonOutputPin(pose_pin_id)
                         ], '.pmd', '.pmx')
        self.pmd_pmx = None

    def to_json(self) -> Serialized:
        return Serialized(self.__class__.__name__, {
            'id': self.id,
            'path': str(self.path) if self.path else None,
            'skeleton_pin_id': self.outputs[0].id,
        })
