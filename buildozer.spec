[app]

# 애플리케이션 이름
title = Yeyein

# 애플리케이션 버전
version = 1.0

# 패키지 이름 (모든 소문자, 하이픈(-) 포함)
package.name = yeyein

# 패키지 도메인
package.domain = org.yourdomain

# 메인 Python 파일
source.dir = .

# 배너 아이콘 (마스터 레지스트리 경로)
icon.filename = icon.png

# Kivy 버전
requirements = python3, kivy==2.0.0, tensorflow==2.6.0, tensorflow_hub, opencv-python-headless, pyttsx3

# 배경 실행 모드 설정
orientation = portrait

# Android 관련 설정
android.sdk = C:/Users/YourUsername/AppData/Local/Android/Sdk
android.ndk = C:/android-ndk-r21e
android.api = 29
android.build_tools = 29.0.2
android.minapi = 21

# 빌드 설정 종류 (debug, release)
buildozer.build_dir = C:/Users/admin/Desktop

# 빌드 타겟 설정 (android, ios, macos, windows 등)
target = android

# Android 권한 설정
android.permissions = CAMERA, INTERNET, ACCESS_NETWORK_STATE, ACCESS_FINE_LOCATION

# Android 앱 아이콘 설정
android.icon = icon.png

# Android 앱 라벨 설정
android.label = Yeyein

# Android 런처 이름 설정
android.entrypoint = org.yourdomain/.MainActivity

# 추가적인 포함 파일 설정 (폰트 파일 등)
include_patterns = assets/*, fonts/*
