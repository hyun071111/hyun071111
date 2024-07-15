import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

import tensorflow as tf
import tensorflow_hub as hub
import cv2
import pyttsx3
import numpy as np
import threading

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

        self.model = self.load_model()  # 여기에서 모델 초기화
        self.label_names = self.load_label_names()  # 라벨 이름 로드

        return self.main_box

    def load_model(self):
        # TensorFlow Hub에서 모델을 다운로드하고 로컬에 저장
        model_url = "https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2"
        model_path = "ssd_mobilenet_v2"  # 모델을 저장할 경로

        if not os.path.exists(model_path):
            print("모델을 다운로드하는 중...")
            model = hub.load(model_url)
            tf.saved_model.save(model, model_path)
        else:
            print("모델이 이미 다운로드되었습니다.")

        return tf.saved_model.load(model_path)

    def load_label_names(self):
        # COCO 데이터셋 라벨 이름을 로드하고 반환
        return [
            '배경', '사람', '자전거', '자동차', '오토바이', '비행기', '버스', '기차', '트럭', '보트', '신호등', '소화전', '정지 신호', 
            '주차 요금기', '벤치', '새', '고양이', '개', '말', '양', '코끼리', '곰', '얼룩말', '기린', '배낭', '우산', '핸드백', 
            '넥타이', '여행가방', '프리스비', '스키', '스노보드', '스포츠 볼', '연', '야구 방망이', '야구 글러브', '스케이트보드', 
            '서핑보드', '테니스 라켓', '병', '와인잔', '컵', '포크', '나이프', '숟가락', '그릇', '바나나', '사과', '샌드위치', 
            '오렌지', '브로콜리', '당근', '핫도그', '피자', '도넛', '케이크', '의자', '소파', '화분', '침대', '식탁', '화장실', 
            'TV', '노트북', '마우스', '리모컨', '키보드', '휴대폰', '전자레인지', '오븐', '토스터', '싱크대', '냉장고', '책', 
            '시계', '꽃병', '가위', '테디 베어', '헤어 드라이어', '칫솔'
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
        Clock.schedule_interval(self.update_gui, 1.0 / 60.0)

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
                print("카메라에서 프레임 캡처 실패. 종료합니다...")
                break

            self.frame = frame.copy()
            self.detections = self.detect_objects(frame, self.model)
            self.labels = self.get_detected_labels(self.detections)

        self.cap.release()

    def detect_objects(self, frame, model):
        input_tensor = tf.convert_to_tensor(frame)
        input_tensor = input_tensor[tf.newaxis, ...]

        infer = model.signatures['serving_default']
        detections = infer(tf.constant(input_tensor))

        return detections

    def get_detected_labels(self, detections, confidence_threshold=0.5):
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
            self.info_label.text = "객체를 감지하지 못했습니다."
            self.speak("객체를 감지하지 못했습니다.")
            return

        objects = [self.label_names[label] for label in labels if label < len(self.label_names)]
        description = ", ".join(objects) + "이 있습니다."
        self.info_label.text = description
        self.speak(description)

    def speak(self, text):
        engine.say(text)
        engine.runAndWait()

    def update_gui(self, dt):
        if self.running:
            if self.frame is not None and self.detections is not None and self.labels is not None:
                self.display_frame(self.frame, self.detections, self.labels)

    def display_frame(self, frame, detections, labels):
        display_frame = frame.copy()
        if not labels:
            cv2.putText(display_frame, "객체를 감지하지 못했습니다.", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
        else:
            for i in range(len(labels)):
                class_id = labels[i]
                if class_id < len(self.label_names):  # 범위 확인
                    score = detections['detection_scores'][0][i]
                    label = self.label_names[class_id]
                    text = f"{label}: {score:.2f}"
                    cv2.putText(display_frame, text, (50, 50 + i * 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

        frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (640, 480))
        image_texture = self.texture_from_frame(frame_resized)
        self.image_view.texture = image_texture

    def texture_from_frame(self, frame):
        buf = cv2.flip(frame, 0).tostring()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        return texture

def main():
    return ObjectDetectionApp()

if __name__ == '__main__':
    main().run()
