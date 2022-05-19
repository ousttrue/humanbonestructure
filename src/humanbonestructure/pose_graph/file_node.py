from typing import Optional, List
import pathlib
from pydear import imgui as ImGui
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized


class FileNode(Node):
    def __init__(self, id: int, title: str, path: Optional[pathlib.Path],
                 inputs: List[InputPin],
                 outputs: List[OutputPin],
                 *extensions: str) -> None:
        super().__init__(id, title, inputs, outputs)
        if isinstance(path, str):
            path = pathlib.Path(path)
        self.path: Optional[pathlib.Path] = path
        self.extensions = extensions

    def load(self, path: pathlib.Path):
        pass

    def file_filter(self, path: pathlib.Path) -> bool:
        if not path.is_file():
            return True
        return path.suffix.lower() in self.extensions

    def show_content(self, graph):
        if ImGui.Button('open'):
            import asyncio

            async def open_task():
                from pydear.utils import filedialog
                dir = self.path.parent if self.path else graph.current_dir
                selected = await filedialog.open_async(asyncio.get_event_loop(), dir, filter=self.file_filter)
                if selected:
                    self.load(selected)
            asyncio.get_event_loop().create_task(open_task())

        if self.path:
            ImGui.TextUnformatted(f'{self.path.name}')
