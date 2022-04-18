from typing import Optional, List
import ctypes
import asyncio
from OpenGL import GL
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmark
import numpy
from mediapipe.python.solutions import hands as mp_hands
from pydear import imgui as ImGui
from pydear import glo


class HandLandmark:
    def __init__(self) -> None:
        self.landmark: List[NormalizedLandmark] = []

        from ..scene.scene_capture import CaptureScene
        self.capture = CaptureScene()

        from ..scene.scene_3d import Scene
        self.scene = Scene()

        from ..scene.scene_hand import HandScene
        self.hand = HandScene()

        from .video_capture import VideCapture
        self.video_capture = VideCapture()
        self.video_capture.frame_event += self.estimate

        self.hands = mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

    def show_table(self, p_open: ctypes.Array):
        if ImGui.Begin('landmarks', p_open):
            flags = (
                ImGui.ImGuiTableFlags_.BordersV
                | ImGui.ImGuiTableFlags_.BordersOuterH
                | ImGui.ImGuiTableFlags_.Resizable
                | ImGui.ImGuiTableFlags_.RowBg
                | ImGui.ImGuiTableFlags_.NoBordersInBody
            )

            if ImGui.BeginTable("tiles", 4, flags):
                # header
                # ImGui.TableSetupScrollFreeze(0, 1); // Make top row always visible
                ImGui.TableSetupColumn('index')
                ImGui.TableSetupColumn('x')
                ImGui.TableSetupColumn('y')
                ImGui.TableSetupColumn('z')
                ImGui.TableHeadersRow()

                # body
                for i, p in enumerate(self.landmark):
                    ImGui.TableNextRow()
                    # index
                    ImGui.TableNextColumn()
                    ImGui.TextUnformatted(f'{i}')
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

    def estimate(self, image: numpy.ndarray):
        assert isinstance(image, numpy.ndarray)
        self.capture.rect.update_capture_texture(image)

        results = self.hands.process(image)

        # update vertices
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # self.landmark = hand_landmarks.landmark
                self.capture.points.update(hand_landmarks.landmark)

        if results.multi_hand_world_landmarks:
            for hand_landmarks in results.multi_hand_world_landmarks:
                self.landmark = hand_landmarks.landmark
                self.scene.hand.update(hand_landmarks.landmark)
