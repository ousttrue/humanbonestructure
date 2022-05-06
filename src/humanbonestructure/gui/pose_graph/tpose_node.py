from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized


class TPoseSkeletonOutputPin(OutputPin):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'skeleton')

    def process(self, node: 'TPoseNode', input: InputPin):
        input.value = node.root


class TPoseNode(Node):
    def __init__(self, id: int, skeleton_pin_id: int) -> None:
        super().__init__(id, 'strict TPose',
                         [],
                         [
                             TPoseSkeletonOutputPin(skeleton_pin_id)
                         ])
        from ...scene.builder import strict_tpose
        self.root = strict_tpose.create()

    def get_right_indent(self) -> int:
        return 80

    def to_json(self) -> Serialized:
        return Serialized(self.__class__.__name__, {
            'id': self.id,
            'skeleton_pin_id': self.outputs[0].id,
        })
