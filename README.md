# Домашнее задание по курсу веб-разработки

### Описание
В качестве домашнего задания предлагается выполнить проект «Вопросы и Ответы». Этот сервис позволит пользователям Интернета задавать вопросы и получать на них ответы. Возможности комментирования и голосования формируют сообщество и позволяет пользователям активно помогать другим.
# Результат первого домашнего задания
Созданы файлы разметки и стиля -- базовый внешний вид веб-приложения.
### Файлы разметки и файлы стиля
`html`-файлы расположены в директории `public`:
- ask.html -- страница создания вопроса;
- base.html -- "обёртка" всего сайта;
- index.html -- главная страница, список вопросов;
- login.html -- страница входа;
- signup.html -- страница регистрации;
- question.html -- страница отдельного вопроса;
- tag.html -- страница списка вопрос по теме;
- settings.html -- страница настроек аккаунта.
<br>В `static` находятся `css` файлы с именами, соответствующими таким же `html` файлам.

# Результат второго домашнего задания

С помощью фреймворка Django реализовано динамическое изменение страницы (генерация) при разных данных посредством использований шаблонов, а также настроена маршрутизация.<br>
Создана пагинация.
### Django
Сделана следующая структура проекта:
```
ask_pupkin            - директория проекта
    |--- app          - директория приложения (создается командой manage.py startapp)
    |--- ask_pupkin   - библиотеки проекта (будут созданы django-admin.py)
    |--- manage.py    - скрипт управления (будет создан django-admin.py)
    |--- templates    - шаблоны
    |--- static       - статические файлы (JS, CSS, картинки)
    └--- uploads      - файлы загруженные юзером
```
Настроена маршрутизация проекта по разным страницам (`urls.py`)
- cписок новых вопросов (главная страница) (URL = /)
- cписок “лучших” вопросов (URL = /hot/)
- cписок вопросов по тэгу (URL = /tag/blablabla/)
- cтраница одного вопроса со списком ответов (URL = /question/35/)
- форма логина (URL = /login/)
- форма регистрации (URL = /signup/)
- форма создания вопроса (URL = /ask/)

Пагинация была реализована следующим образом:
```python
def paginate(objects_list, request, per_page=5):
    page_num = request.GET.get('page')
        
    p = Paginator(objects_list, per_page)
    try:
        question_page = p.page(page_num)
    except (EmptyPage, PageNotAnInteger, InvalidPage) as e:
        question_page = p.page(1)
        
    return question_page
```
### Данные
Тестовые данные были созданы простым `for` циклом.

# Результат третьего домашнего задания

### База данных
В качестве базы данных был выбран `PostgreSQL` в `Docker`-контейнере. Описание контейнера находится в корне проекта в `Dockerfile`.
### Заполнение БД тестовыми данными
Заполнение базы данных кажется достаточно простой задачей: требуется лишь описать тестовые данные и написать скрипт для их генерации и отправлять каждую сущность в базу данных.<br>
Однако, при попытке реализации данной задачи на любом языке, скорее всего, можно упереться в две проблемы, особенно в случае большого количества тестовых данных ( > 3.000.000 в моём случае):
1. Генерация данных занимает очень много времени, требует больших вычислительных мощностей и занимает очень много оперативной памяти;
2. Даже при достаточно быстрой генерации данных, сами сущности очень медленно добавляются в базу данных.

Эта проблема решается, к примеру, последовательной генерацией сущностей и разбиением данных на части. В контексте этого домашнего задания сущности создавались в таком порядке: пользователи, профили пользователей, тэги, посты, комментарии и лайки к комментариям и постам. Далее каждый тип данных ещё разбивается на куски (по 10.000 элементов, например) и отправляется в базу данных "большими кусками" вместо отправки каждой сущности в базу данных, а сами данные удаляются из оперативной памяти.<br>
Такой подход идеально поддерживает многопоточность, что позволяет в разы ускорить этот процесс.<br>
Ещё одним эффективным решением стало изменение способа генерации лайков пользователей. Вместо генерации лайка по алгоритму случайный пользователь и случайный пост (что приводило к аварийным ситуациям, например, совпадению пользователя и поста, и требовало время), использовалась генерация по пользователю: функция получала "срез" пользователей, проходила по каждому пользователю и создавала ему по 100 лайков на посты и 100 лайков на комментарии (случайные, конечно). Такой способ, даже при использовании случайного выбора постов и комментариев, работал в разы быстрее, потреблял меньше памяти и при этом упрощал обработку ситуации совпадения постов и комментариев.<br> 
Таким образом, удалось сократить время заполнения базы данных (даже без параллелизации) с нескольких часов до около двух минут и понизить потребление оперативной памяти до всего около 400 мегабайт (до этого программа потребляла всю доступную оперативную память и приводила к аварийному завершению системы).
### Отображение данных, сущности и миграции
Сущности были описаны в `app/models.py`, созданы миграции `python3 manage.py makemigrations && python3 manage.py migrate` и реализованы менеджеры для некоторых моделей.<br>
Далее методы менеджеров были использованы в `views.py` и слегка переделаны шаблоны отображения.

# Результат четвертого домашнего задания

## Авторизация
Свёрстаны формы, в шаблонах используется CSRF-токены. Обработаны ситуации пустых полей как на фронт, так и на бекэнде.
Ошибки выводятся для пользователя в случае чего. Не конфидециальные данные (не пароли), не удаляются при ошибках.
Оформление форм не Bootstrap'ом, а собственное.

## Добавление данных
Добавление вопросов `/ask` и добавление комментариев (со скроллингом до нового комментария) `/question/{id}`.
Обработка разных ошибок.

# Результат шестого домашнего задания

## Результаты замеров

### Статический файл `/uploads/default.png`

Напрямую через `gunicorn`:

```
λ ab -n 100000 -c 100 127.0.0.1:8000/uploads/default.png
This is ApacheBench, Version 2.3 <$Revision: 1913912 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient)
Completed 10000 requests
Completed 20000 requests
Completed 30000 requests
Completed 40000 requests
Completed 50000 requests
Completed 60000 requests
Completed 70000 requests
Completed 80000 requests
Completed 90000 requests
Completed 100000 requests
Finished 100000 requests


Server Software:        gunicorn
Server Hostname:        127.0.0.1
Server Port:            8000

Document Path:          /uploads/default.png
Document Length:        10609 bytes

Concurrency Level:      100
Time taken for tests:   109.660 seconds
Complete requests:      100000
Failed requests:        0
Total transferred:      1093500000 bytes
HTML transferred:       1060900000 bytes
Requests per second:    911.91 [#/sec] (mean)
Time per request:       109.660 [ms] (mean)
Time per request:       1.097 [ms] (mean, across all concurrent requests)
Transfer rate:          9738.06 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.1      0       4
Processing:     3  110  43.8     88     428
Waiting:        3  109  43.8     87     428
Total:          7  110  43.9     88     428

Percentage of the requests served within a certain time (ms)
  50%     88
  66%    114
  75%    133
  80%    141
  90%    162
  95%    193
  98%    248
  99%    281
 100%    428 (longest request)
```

Напрямую через `nginx`:

```
λ ab -n 100000 -c 100 127.0.0.1/uploads/default.png
This is ApacheBench, Version 2.3 <$Revision: 1913912 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient)
Completed 10000 requests
Completed 20000 requests
Completed 30000 requests
Completed 40000 requests
Completed 50000 requests
Completed 60000 requests
Completed 70000 requests
Completed 80000 requests
Completed 90000 requests
Completed 100000 requests
Finished 100000 requests


Server Software:        nginx/1.22.1
Server Hostname:        127.0.0.1
Server Port:            80

Document Path:          /uploads/default.png
Document Length:        10609 bytes

Concurrency Level:      100
Time taken for tests:   4.361 seconds
Complete requests:      100000
Failed requests:        0
Total transferred:      1094000000 bytes
HTML transferred:       1060900000 bytes
Requests per second:    22930.81 [#/sec] (mean)
Time per request:       4.361 [ms] (mean)
Time per request:       0.044 [ms] (mean, across all concurrent requests)
Transfer rate:          244983.46 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    2   0.4      2       6
Processing:     0    3   0.6      3       8
Waiting:        0    1   0.4      1       6
Total:          0    4   0.7      4      13

Percentage of the requests served within a certain time (ms)
  50%      4
  66%      4
  75%      5
  80%      5
  90%      5
  95%      6
  98%      7
  99%      8
 100%     13 (longest request)
```

### Отдача динамического документа `/` (index.html):

Через `nginx` с проксированием на `gunicorn`:

```
λ ab -n 1000 -c 1 http://127.0.0.1/ 
This is ApacheBench, Version 2.3 <$Revision: 1913912 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Completed 600 requests
Completed 700 requests
Completed 800 requests
Completed 900 requests
Completed 1000 requests
Finished 1000 requests


Server Software:        nginx/1.22.1
Server Hostname:        127.0.0.1
Server Port:            80

Document Path:          /
Document Length:        10174 bytes

Concurrency Level:      1
Time taken for tests:   63.951 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      10434000 bytes
HTML transferred:       10174000 bytes
Requests per second:    15.64 [#/sec] (mean)
Time per request:       63.951 [ms] (mean)
Time per request:       63.951 [ms] (mean, across all concurrent requests)
Transfer rate:          159.33 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:    52   64  12.0     61     135
Waiting:       52   64  12.0     61     134
Total:         52   64  12.0     61     135

Percentage of the requests served within a certain time (ms)
  50%     61
  66%     62
  75%     64
  80%     65
  90%     73
  95%     90
  98%    111
  99%    123
 100%    135 (longest request)
```

Через `nginx` с проксированием через `gunicorn` с кэшированием:
```
λ ab -n 1000 -c 1 http://127.0.0.1/                     
This is ApacheBench, Version 2.3 <$Revision: 1913912 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Completed 600 requests
Completed 700 requests
Completed 800 requests
Completed 900 requests
Completed 1000 requests
Finished 1000 requests


Server Software:        nginx/1.22.1
Server Hostname:        127.0.0.1
Server Port:            80

Document Path:          /
Document Length:        10174 bytes

Concurrency Level:      1
Time taken for tests:   0.432 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      10434000 bytes
HTML transferred:       10174000 bytes
Requests per second:    2316.57 [#/sec] (mean)
Time per request:       0.432 [ms] (mean)
Time per request:       0.432 [ms] (mean, across all concurrent requests)
Transfer rate:          23604.56 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:     0    0   4.5      0     125
Waiting:        0    0   4.5      0     125
Total:          0    0   4.5      0     125

Percentage of the requests served within a certain time (ms)
  50%      0
  66%      0
  75%      0
  80%      0
  90%      0
  95%      0
  98%      1
  99%      1
 100%    125 (longest request)
```
Напрямую через `gunicorn`:

```
λ ab -n 1000 -c 1 http://127.0.0.1:8000/
This is ApacheBench, Version 2.3 <$Revision: 1913912 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Completed 600 requests
Completed 700 requests
Completed 800 requests
Completed 900 requests
Completed 1000 requests
Finished 1000 requests


Server Software:        gunicorn
Server Hostname:        127.0.0.1
Server Port:            8000

Document Path:          /
Document Length:        10174 bytes

Concurrency Level:      1
Time taken for tests:   63.902 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      10430000 bytes
HTML transferred:       10174000 bytes
Requests per second:    15.65 [#/sec] (mean)
Time per request:       63.902 [ms] (mean)
Time per request:       63.902 [ms] (mean, across all concurrent requests)
Transfer rate:          159.39 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:    50   64  13.2     60     133
Waiting:       50   63  13.1     59     131
Total:         50   64  13.2     60     133

Percentage of the requests served within a certain time (ms)
  50%     60
  66%     62
  75%     63
  80%     64
  90%     74
  95%    100
  98%    114
  99%    118
 100%    133 (longest request)
```

## Ответы на вопросы

- Насколько быстрее отдается статика по сравнению с WSGI?
Тесты WSGI заняли 109.99 секунд, в то время как Nginx справился за 4,361 секунд. Разница почти в 25 раз.
- Во сколько раз ускоряет работу proxy_cache?
Передача динамического файла через Nginx с proxy_cache заняло 0,432 секунды, в то время как без кеширования это заняло 63,951 секунд. Кеширование ускорило обработку запросов в 148 раз!
