# Staxel_Korean
스타셀 한글 번역 스크립트

---

## 설명
이 프로젝트는 Staxel의 한글 번역 파일을 생성하는 파이썬 프로젝트입니다.

현재 배포되는 파일은 22년 7월 1일, Staxel 버전 1.5.63 (210927a) 기반으로 제작되었습니다.


---

## 주의 사항

1. 패치 진행에 따라서 최신 배포 파일은 미래에 정상작동 하지 않을 수 있습니다.
2. 이 번역은 일본어 번역을 한국어로 구글 번역기를 통해 직역했습니다.
3. 이 번역은 기존의 한국어 공식 번역을 덮어씁니다.

---

## 한글 패치 적용하기
1. Release 의 ko-KR 파일을 다운로드 받고, 스타셀 설치 경로의 한글 번역 리소스 경로에 압축을 해제하십시오.

기본 스팀 한글 번역 리소스 경로:
C:\Program Files (x86)\Steam\steamapps\common\Staxel\content\staxel\StaxelTranslations\ko-KR

---

## 번역 원리

1. 일본어 번역 파일을 추출합니다.
2. 추출한 파일에서 ^cXXXXXX; ^cpop; 형태의 색상 정보를 [^ 와 ^] 로 치환해서 임시 저장합니다.
3. 임시 저장된 파일을 Google Cloud Translation API 로 번역합니다.
4. 변역 결과중, [^ 와 ^] 를 기존에 저장한 색상 정보 ^c:XXXXXX; ^c:pop; 로 다시 치환합니다.
3. 결과를 한글 번역 파일 이름 형태에 맞게 이름을 고쳐 저장합니다.

---

## 개발 환경 설정

이 프로젝트는 Windows 10, Python 3.10.5 에서 작성되었습니다.
이 프로젝트 사용자는 Google Cloud Translation API 를 자신의 구글 개발자 아이디로 사용할 수 있는 개발 환경을 갖추고 있어야합니다.
라이브러리 설치 및 Credentail

1. PyCharm 최신버전을 설치하세요
2. Clone 받은 프로젝트를 PyCharm 에서 엽니다. venv 환경을 구성합니다.

파이참이 자동으로 환경 구성을 실패한 경우, 
파이참의 **명령 프롬프트**에서 다음의 명령을 수행하십시오.
```
C:\repo\Staxel_Korean>py -m venv venv
C:\repo\Staxel_Korean>venv\Scripts\activate.bat
(venv) C:\repo\Staxel_Korean>venv\Scripts\python.exe -m pip install --upgrade pip
(venv) C:\repo\Staxel_Korean>venv\Scripts\python.exe -m pip install -r requirements.txt
```

3. main.py 에서 사용되는 경로들을 절대 경로로, 알맞게 수정 합니다. 

```
# 원본 파일 경로입니다. 
# 스팀 원본 일본어 번역 파일 경로를 직접 사용하거나
# 스팀 원본 파일을 프로잭트 내 경로로 옮겨담아서 사용하십시오.
ORIGIN_PATH = 'C:/repo/Staxel_Korean/resources/ORIGIN'

# 원본 파일을 번역에 용이하도록 변환해서 저장하는 임시 경로입니다.
EXTRACT_SRC_PATH = 'C:/repo/Staxel_Korean/resources/ja-JP/'

# 최종 결과가 저장되는 경로입니다.
KO_DST_PATH = 'C:/repo/Staxel_Korean/resources/ko-KR/'
```

4. 번역을 하고 싶다면, main.py 의 마지막 부분에서 호출되는 main 호출의 첫번째 파라미터를 False 에서 True 로 수정합니다.

5. venv 환경에서 py main.py 를 호출합니다.
구글 API 실행 환경을 구축 후 사용하세요. (예 - Google 서비스 키 Credential 환경 변수 등록 등)

파이참의 **명령 프롬프트**에서 다음의 명령을 수행하십시오.

```
(venv) C:\repo\Staxel_Korean>py main.py
```
