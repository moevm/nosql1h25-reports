# nosql_template


## Предварительная проверка заданий

<a href=" ./../../../actions/workflows/1_helloworld.yml" >![1. Согласована и сформулирована тема курсовой]( ./../../actions/workflows/1_helloworld.yml/badge.svg)</a>

<a href=" ./../../../actions/workflows/2_usecase.yml" >![2. Usecase]( ./../../actions/workflows/2_usecase.yml/badge.svg)</a>

<a href=" ./../../../actions/workflows/3_data_model.yml" >![3. Модель данных]( ./../../actions/workflows/3_data_model.yml/badge.svg)</a>

<a href=" ./../../../actions/workflows/4_prototype_store_and_view.yml" >![4. Прототип хранение и представление]( ./../../actions/workflows/4_prototype_store_and_view.yml/badge.svg)</a>

<a href=" ./../../../actions/workflows/5_prototype_analysis.yml" >![5. Прототип анализ]( ./../../actions/workflows/5_prototype_analysis.yml/badge.svg)</a> 

<a href=" ./../../../actions/workflows/6_report.yml" >![6. Пояснительная записка]( ./../../actions/workflows/6_report.yml/badge.svg)</a>

<a href=" ./../../../actions/workflows/7_app_is_ready.yml" >![7. App is ready]( ./../../actions/workflows/7_app_is_ready.yml/badge.svg)</a>

## Запуск БД

1. Запустить `Docker Desktop`, если используется Windows/MacOS
2. `docker compose up -d` (`docker-compose up -d` для Linux)
3. БД будет доступна по [bolt://localhost:7687](bolt://localhost:7687), веб-интерфейс по [http://localhost:7474](http://localhost:7474)
4. `docker compose down` для завершения работы
5. Если нужно очистить место (при использовании `Docker Desktop`). *очищаются все доп. данные Docker*
   1. Зайти в `Troubleshoot` (иконка жучка в меню-баре)
   2. `Clean / Purge Data`
   3. Выбрать всё - `Delete`
   4. При необходимости ввести `wsl --shutdown` (на Windows)