### Coin Trading bot Using Upbit API
> * 텔레그램과 연계한 코인 봇입니다.
>    * 자유롭게 사용하셔도 좋습니다.
>    * 좋은 트레이딩 로직이 있으면 같이 공유해요!
>    * 코인은 단타보다는 장투하는게 좋습니다.
>      
>   <br/>
> * 사용법
>    * 구동하기 : python3 bot_main.py    
>    * Process 구조 :           
>       * telegram control bot : 텔레그램 메시지 리스너 및 텔레그램 메시지로 코인 트레이딩 프로세스 컨트롤     
>          * main_bot : sell process와 buy process 상위 process로 main_bot off 시에는 buy bot과 sell bot이 동작하지않음        
>             * sell bot : 갖고 있는 코인을 판매하는 프로세스   
>             * buy bot  : 코인을 구매하는 프로세스  
>   
>    * 명령어    
>       command | 기능    
>       ----- | ------    
>       '/check' | main_bot, buy process, sell process on off 여부 확인     
>       '/start' | main_bot 실행    
>       '/stop' | main_bot 종료    
>       '/buyon' | buy process 실행    
>       '/buyoff' | buy process 중지    
>       '/sellon' | sell process 실행    
>       '/selloff' | sell process 중지    
>       '/exit' | 비상탈출, 갖고있는 코인 전체 다 팔기
>       '/except (코인명)' | 코인을 프로세스의 예외로 넣고 빼기 (예외 목록에 없으면 넣고, 있으면 뺀다.)
>       '/checkexcept' | 예외 코인 목록 check
>         
>      <br/>
>    
>       
>  * 텔레그램을 활용한 bot control 예제    
>  <img src = "https://user-images.githubusercontent.com/80157109/111898746-3fb6a400-8a6b-11eb-9170-c648fc669223.jpeg"  height = '50%'  width = '50%'></img>\
