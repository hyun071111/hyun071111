import urllib.request
import tarfile

# 모델 파일 다운로드
url = 'http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz'
output_path = 'ssd_mobilenet_v2_coco_2018_03_29.tar.gz'

urllib.request.urlretrieve(url, output_path)

# tar.gz 파일 추출
tar = tarfile.open(output_path)
tar.extractall(path='C:/Users/admin/Desktop/hackerton')
tar.close()
