from typing import List, NamedTuple
import ctypes
from pydear import imgui as ImGui
# from mediapipe.python.solutions import hands as mp_hands


class Item(NamedTuple):
    id: int
    label: str
    score: float
    x: float
    y: float
    z: float


class HandLandMarkTable:
    def __init__(self) -> None:
        self.landmark: List[Item] = []

    def update(self, results):
        self.landmark.clear()

        # update vertices
        # if results.multi_hand_landmarks:
        #     for hand_landmarks in results.multi_hand_landmarks:
        #         # self.landmark = hand_landmarks.landmark
        #         self.capture.points.update(hand_landmarks.landmark)
        # if results.multi_handedness:
        #     for classification in results.multi_handedness:
        #         # self.handedness.append(handedness)

        if results.multi_hand_world_landmarks:
            for h_id, hand in enumerate(results.multi_hand_world_landmarks):

                for c_id, hand_class in enumerate(results.multi_handedness[h_id].classification):
                    assert c_id == 0
                    # {
                    #     'index': hand_class.index,
                    #     'label': hand_class.label,
                    #     'score': hand_class.score,
                    # })

                for landmark in hand.landmark:

                    self.landmark.append(Item(
                        hand_class.index,
                        hand_class.label,
                        hand_class.score,
                        landmark.x,
                        landmark.y,
                        landmark.z,
                    ))

            pass

    def show(self, p_open: ctypes.Array):
        if ImGui.Begin('landmarks', p_open):
            flags = (
                ImGui.ImGuiTableFlags_.BordersV
                | ImGui.ImGuiTableFlags_.BordersOuterH
                | ImGui.ImGuiTableFlags_.Resizable
                | ImGui.ImGuiTableFlags_.RowBg
                | ImGui.ImGuiTableFlags_.NoBordersInBody
            )

            headers = (
                'index',
                'id',
                'label',
                'score',
                'x',
                'y',
                'z',
            )
            if ImGui.BeginTable("tiles", len(headers), flags):
                # header
                # ImGui.TableSetupScrollFreeze(0, 1); // Make top row always visible
                for label in headers:
                    ImGui.TableSetupColumn(label)
                ImGui.TableHeadersRow()

                # body
                for i, p in enumerate(self.landmark):
                    ImGui.TableNextRow()
                    # index
                    ImGui.TableNextColumn()
                    ImGui.TextUnformatted(f'{i}')
                    #
                    ImGui.TableNextColumn()
                    ImGui.TextUnformatted(f'{p.id}')
                    ImGui.TableNextColumn()
                    ImGui.TextUnformatted(f'{p.label}')
                    ImGui.TableNextColumn()
                    ImGui.TextUnformatted(f'{p.score:.2f}')
                    #
                    ImGui.TableNextColumn()
                    ImGui.TextUnformatted(f'{p.x:.2f}')
                    ImGui.TableNextColumn()
                    ImGui.TextUnformatted(f'{p.y:.2f}')
                    ImGui.TableNextColumn()
                    ImGui.TextUnformatted(f'{p.z:.2f}')

                ImGui.EndTable()
            # ImGui.SliderFloat4('clear color', app.clear_color, 0, 1)
            # ImGui.ColorPicker4('color', app.clear_color)
        ImGui.End()
