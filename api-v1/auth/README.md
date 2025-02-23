# Auth Api 0.1.0

### 인증용 API
+ __jwt /  password(hashing)__ 를 사용한 **OAuth2** .
+ 외부(소셜) 인증 module 연동 인증 처리.

### 처리 구조 
1. 최초 사용자 인증 정보를 받아서 단방향 암호화 적용해서 저장.
2. 저장된 데이터 기준으로 jwt 발급 (인증 처리)
3. 저장 정보 변경 시 추가 인증 (phone/mail) 연동
4. 외부(소셜) 인증 처리

### package
+ FastAPI 0.115.8 
+ uvicorn 0.34.0
+ PyJWT 2.10.1
+ passLib[bcrypt] 1.7.4
+ sqlalchemy 2.0.38

### Directory Format
- server : api 서버 
- controller : api router 
- service : api 실제 로직 구현 
- model : api data (response,request) model Interface

