%%writefile buildozer.spec

[app]

# 애플리케이션 이름
title = Yeyein

# 애플리케이션 버전
version = 1.0

# 패키지 이름 (모든 소문자, 하이픈(-) 포함)
package.name = yeyein

# 메인 Python 파일
package.domain = org.yourdomain

# 배너 아이콘 (마스터 레지스트리 경로)
icon.filename = icon.png

# Kivy 버전
requirements = kivy==2.0.0

# 필요한 모듈 추가
# TensorFlow, TensorFlow Hub, OpenCV는 다음과 같이 포함할 수 있습니다.
requirements = python3,kivy,tensorflow==2.6.0,tensorflow_hub,cv2,pyttsx3

# 배경 실행 모드 설정
orientation = portrait

# Android 관련 설정
osx.python_version = 3.8.0
osx.kivy_version = 2.0.0

# Android SDK 경로 설정
android.sdk = /content/android-sdk

# Android NDK 경로 설정
android.ndk = /content/android-ndk-r21e

# Android API 레벨
android.api = 29

# Android 빌드 도구 버전
android.build_tools = 29.0.2

# Android 최소 SDK 버전
android.minapi = 21

# 빌드 설정 종류 (debug, release)
# release 시 코드 최적화 및 패키징
# debug 시 디버그 정보 포함
# 빌드 완료 후 생성되는 APK 파일이 release 위치에 저장됩니다.
buildozer.build_dir = /content/build

# 빌드 타겟 설정 (android, ios, macos, windows 등)
target = android

# Android 권한 설정
android.permissions = CAMERA,INTERNET,ACCESS_NETWORK_STATE,ACCESS_FINE_LOCATION

# Android 앱 아이콘 설정
android.icon = icon.png

# Android 앱 라벨 설정
android.label = Yeyein

# Android 런처 이름 설정
android.entrypoint = org.yourdomain/.MainActivity

# 추가적인 포함 파일 설정 (폰트 파일 등)
include_patterns = assets/*, fonts/*
