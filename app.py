import os
import cv2
import threading
import pyttsx3
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from queue import Queue
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.graphics.texture import Texture

LabelBase.register(name='NanumGothic', fn_regular='NanumGothic.ttf')

engine = pyttsx3.init()
engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_KO-KR_HANNA_11.0')

class ObjectDetectionApp(App):
    def build(self):
        self.main_box = BoxLayout(orientation='vertical', padding=10)

        self.image_view = Image(size_hint=(1, 0.6))
        self.toggle_button = Button(text='시작', on_press=self.toggle_detection, size_hint=(1, None), height=40)
        self.switch_camera_button = Button(text='카메라 전환', on_press=self.switch_camera, size_hint=(1, None), height=40)
        self.explain_button = Button(text='설명', on_press=self.describe_objects_button, disabled=True, size_hint=(1, None), height=40)
        self.info_label = Label(text='객체를 감지하려면 "시작" 버튼을 누르세요.', size_hint=(1, None), height=40)

        self.toggle_button.font_name = 'NanumGothic'
        self.switch_camera_button.font_name = 'NanumGothic'
        self.explain_button.font_name = 'NanumGothic'
        self.info_label.font_name = 'NanumGothic'

        self.toggle_button.background_normal = ''
        self.toggle_button.background_color = (0, 0.5, 0.8, 1)
        self.switch_camera_button.background_normal = ''
        self.switch_camera_button.background_color = (0, 0.5, 0.8, 1)
        self.explain_button.background_normal = ''
        self.explain_button.background_color = (0, 0.5, 0.8, 1)

        self.main_box.add_widget(self.image_view)
        self.main_box.add_widget(self.toggle_button)
        self.main_box.add_widget(self.switch_camera_button)
        self.main_box.add_widget(self.explain_button)
        self.main_box.add_widget(self.info_label)

        self.cap = cv2.VideoCapture(0)
        self.camera_index = 0
        self.running = False
        self.frame = None
        self.detections = None
        self.labels = None
        self.model = self.load_model()
        self.label_names = self.load_label_names()
        self.frame_queue = Queue(maxsize=1)

        return self.main_box

    def load_model(self):
        model_url = "https://tfhub.dev/tensorflow/efficientdet/d0/1"
        model_path = "efficientdet_d0"
        if not os.path.exists(model_path):
            model = hub.load(model_url)
            tf.saved_model.save(model, model_path)
        return tf.saved_model.load(model_path)

    def load_label_names(self):
        return [
            '배경', '사람', '자전거', '차', '오토바이', '버스', '트럭', '보트', 
            '신호등', '소화전', '정지 표지판', '주차 계량기', '벤치', '개', '고양이',
            '쓰레기통', '버스 정류장', '간판', '가로등', '건물', '휴대폰', '노트북', 
            '책', '컵', '가방', '키보드', '마우스', '리모컨', '헤드폰', '시계', '안경', 
            '의자', '테이블', '텔레비전'
        ]

    def toggle_detection(self, instance):
        if self.running:
            self.stop_detection()
        else:
            self.start_detection()

    def start_detection(self):
        self.running = True
        threading.Thread(target=self.detect_objects_from_camera).start()
        self.toggle_button.text = "멈춤"
        self.explain_button.disabled = False
        self.info_label.text = '객체를 감지하려면 "설명" 버튼을 누르세요.'
        Clock.schedule_interval(self.update_gui, 1.0 / 30.0)

    def stop_detection(self):
        self.running = False
        self.toggle_button.text = "시작"
        self.explain_button.disabled = True
        self.info_label.text = "객체 검출을 멈춥니다."

    def switch_camera(self, instance):
        self.camera_index = (self.camera_index + 1) % 2
        self.cap.release()
        self.cap = cv2.VideoCapture(self.camera_index)

    def detect_objects_from_camera(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            frame_resized = cv2.resize(frame, (320, 240))
            self.frame_queue.put(frame_resized)
        self.cap.release()

    def detect_objects(self, frame, model):
        frame_resized = cv2.resize(frame, (512, 512))
        input_tensor = tf.convert_to_tensor(frame_resized, dtype=tf.uint8)
        input_tensor = input_tensor[tf.newaxis, ...]
        infer = model.signatures['serving_default']
        detections = infer(input_tensor)
        return detections

    def get_detected_labels(self, detections, confidence_threshold=0.3):
        labels = []
        for i in range(len(detections['detection_boxes'][0])):
            class_id = int(detections['detection_classes'][0][i])
            score = float(detections['detection_scores'][0][i])
            if score >= confidence_threshold:
                labels.append(class_id)
        return labels

    def describe_objects_button(self, instance):
        self.describe_objects(self.labels)

    def describe_objects(self, labels):
        if not labels:
            self.info_label.text = "감지된 객체 없음."
            self.speak("감지된 객체가 없습니다.")
            return
        objects = [self.label_names[label] for label in labels if label < len(self.label_names)]
        description = ", ".join(objects) + "을(를) 감지했습니다."
        self.info_label.text = description
        self.speak(description)

    def speak(self, text):
        engine.say(text)
        engine.runAndWait()

    def update_gui(self, dt):
        if self.running:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                detections = self.detect_objects(frame, self.model)
                labels = self.get_detected_labels(detections)
                self.labels = labels
                self.display_frame(frame, detections, labels)

    def display_frame(self, frame, detections, labels):
        display_frame = frame.copy()
        if not labels:
            cv2.putText(display_frame, "감지된 객체 없음.", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
        else:
            for i in range(len(labels)):
                class_id = labels[i]
                if class_id < len(self.label_names):
                    score = detections['detection_scores'][0][i]
                    label = self.label_names[class_id]
                    box = detections['detection_boxes'][0][i]
                    height, width, _ = display_frame.shape
                    ymin, xmin, ymax, xmax = box
                    ymin, xmin, ymax, xmax = int(ymin * height), int(xmin * width), int(ymax * height), int(xmax * width)
                    cv2.rectangle(display_frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                    text = f"{label}: {score:.2f}"
                    cv2.putText(display_frame, text, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2, cv2.LINE_AA)
        frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (640, 480))
        image_texture = self.texture_from_frame(frame_resized)
        self.image_view.texture = image_texture

    def texture_from_frame(self, frame):
        buf = cv2.flip(frame, 0).tostring()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        return texture

if __name__ == '__main__':
    ObjectDetectionApp().run()
