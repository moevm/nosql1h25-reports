# nosql_template


## Предварительная проверка заданий

<a href=" ./../../../actions/workflows/1_helloworld.yml" >![1. Согласована и сформулирована тема курсовой]( ./../../actions/workflows/1_helloworld.yml/badge.svg)</a>

<a href=" ./../../../actions/workflows/2_usecase.yml" >![2. Usecase]( ./../../actions/workflows/2_usecase.yml/badge.svg)</a>

<a href=" ./../../../actions/workflows/3_data_model.yml" >![3. Модель данных]( ./../../actions/workflows/3_data_model.yml/badge.svg)</a>

<a href=" ./../../../actions/workflows/4_prototype_store_and_view.yml" >![4. Прототип хранение и представление]( ./../../actions/workflows/4_prototype_store_and_view.yml/badge.svg)</a>

<a href=" ./../../../actions/workflows/5_prototype_analysis.yml" >![5. Прототип анализ]( ./../../actions/workflows/5_prototype_analysis.yml/badge.svg)</a> 

<a href=" ./../../../actions/workflows/6_report.yml" >![6. Пояснительная записка]( ./../../actions/workflows/6_report.yml/badge.svg)</a>

<a href=" ./../../../actions/workflows/7_app_is_ready.yml" >![7. App is ready]( ./../../actions/workflows/7_app_is_ready.yml/badge.svg)</a>

## Инструкция для запуска

1. `docker compose build –-no-cache && docker compose up -d`
2. Основное приложение будет доступно по [localhost:5000](http://127.0.0.1:5000/)
3. По умолчанию для входа на страницу ИМПОРТ/ЭКСПОРТ используется пароль `password`, который можно изменить через переменную окружения `ADMIN_PASSWORD` в [compose.yml](docker-compose.yml).  
   Данные импортируются и экспортируются в формате *JSON*.
4. Для отладки можно использовать [дипломные работы](src/diploma_processing/testkit/docx_examples)
5. Для отладки БД можно использовать [веб-интерфейс](http://localhost:7474) (по умолчанию: пользователь - `neo4j`, пароль - `password`)

## Запуск БД

1. Запустить `Docker Desktop`, если используется Windows/MacOS
2. `docker compose up -d`
3. БД будет доступна по [bolt://localhost:7687](bolt://localhost:7687), веб-интерфейс по [http://localhost:7474](http://localhost:7474)
4. `docker compose down` для завершения работы
5. Если нужно очистить место (при использовании `Docker Desktop`). *очищаются все доп. данные Docker*
   1. Зайти в `Troubleshoot` (иконка жучка в меню-баре)
   2. `Clean / Purge Data`
   3. Выбрать всё - `Delete`
   4. При необходимости ввести `wsl --shutdown` (на Windows)

## Информация о проекте

### Участники проекта:
1. Локосов Даниил 2300
2. Рогожин Константин 2300
3. Пахомов Степан 2300
4. Волков Иван 2303
5. Мышкин Николай 2303

### Тема проекта:
Анализатор студ отчётов по упоминаемости слов и фраз.

### Используемая БД: 
Neo4j

### Задача:
Сделать сервис, который принимает на вход дипломные работы (docx), парсит их содержмое и разбивает текст по разделам / подразделам, считает статистики (когда и какие слова употребляются, где много шумовых слов и тд), анализирует тексты на схожесть, водность, степень раскрытия отдельных тем / задач.
