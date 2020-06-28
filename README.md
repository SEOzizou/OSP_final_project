# OSP_final_project
1조 오픈소스프로그래밍_final_project 입니다


## 참고사항

- 실행시 엘라스틱서치 폴더가 st.sh와 같은 OSP_final_project 폴더안에 있어야 합니다  

![엘라스틱](https://user-images.githubusercontent.com/44471240/85949290-e19fd900-b990-11ea-8469-95de5a284463.PNG)
  ./elasticsearch-7.6.2/bin/elasticsearch ## 그에대한 bash 파일에서의 코드입니다.
 

- text 파일의 구분은 ','(comma) & '\n'(white_space)입니다.


## 1.다중 URL 분석 결과

### 1) 분석 결과 1
![다중URL](https://user-images.githubusercontent.com/44471240/85948909-77863480-b98e-11ea-8152-3778e41d4981.PNG)

### 2) 분석결과 2
![다중분석결과](https://user-images.githubusercontent.com/44471240/85948931-a7353c80-b98e-11ea-87c8-e32e841edc62.png)


## 2. 단일 URL
단일의 경우 버튼이 활성화 되어있지 않아 단어분석(TF-IDF) 유사도 분석(Co-similarity)를 눌러도 어떠한 이벤트도 발생하지 않습니다.

### 1) 분석결과 1(성공)
![단일_URL(성공)](https://user-images.githubusercontent.com/44471240/85948973-e19ed980-b98e-11ea-9d98-e9b18ea05cb4.PNG)

### 2) 분석결과 2(실패)
![단일실퓨ㅐ](https://user-images.githubusercontent.com/44471240/85948976-e3689d00-b98e-11ea-9a34-553a17dbe42d.PNG)
