# WI-API

### 개요
+ Python FastAPI를 이용한 MSA(Micro Service Architecture) 
+ package manager 는 **Poetry**를 사용.
+ MSA 운영 / 관리를 위해 **Poetry** 를 사용한 monorepo 구성.
---

### Directory
+ api : RestAPI의 MSA Projects
+ lib : MSA 에서 사용될 공통 Lib
---

### Base Stack
1. Python 3.10.11
2. poetry 1.8.4
3. black 25.1.0
-----

#### develop 실행
auth-v1 : poetry run python -m api-v1.auth