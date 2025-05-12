# Инструкция по запуску

1. Собрать образ локально по основной инструкции проекта или спуллить готовый образ

   ```
   $ docker pull space27/codeplag-ubuntu22.04:latest
   ```

2. Запустить контейнер с `MongoDB` при помощи `docker compose`. При стандартных настройках БД будет развернута
   на `localhost:27017` с пользователем `root` и паролем `example`.  
   Данные настройки можно изменить при помощи изменения переменных окружения `MONGO_INITDB_ROOT_USERNAME`
   и `MONGO_INITDB_ROOT_PASSWORD`, а также изменением маппинга портов.

   ```
   $ docker compose -f docker/compose.yml up -d
   ```

3. Для взаимодействия непосредственно с БД через mongosh можно ввести данную команду

   ```
   $ docker exec -it mongodb mongosh --username root --password example
   ```

   Внутри после работы появится БД new_database с двумя коллекциями: features и compare_info. Прочесть их можно с
   помощью следующих команд

   ```
   test> use new_database
   new_database> db.getCollectionNames() # [ 'features', 'compare_info' ]
   new_database> db.features.find({}, {sha256: 1, modify_date: 1}) # для вывода основной информации о сохраненных ASTFeatures
   new_database> db.compare_info.find({}, {first_modify_date: 1, second_modify_date: 1, first_sha256: 1, second_sha256: 1}) # для вывода основной информации о FullCompareInfo
   ```

   Для очистки коллекций можно использовать

   ```
   new_database> db.features.drop()
   new_database> db.compare_info.drop()
   ```

4. Запустить контейнер.  
   - `-v <path-to-src>:/usr/src/codeplag` нужен для появления файлов для проверки работы утилиты 
   - `--add-host=host.docker.internal:host-gateway` необходим, если БД поднята на `localhost` на Linux
   - `docker-tag` следует заменить на тег собранного локально образа или `space27/codeplag-ubuntu22.04:latest`

   ```
   $ docker run --rm --tty --interactive -v <path-to-src>:/usr/src/codeplag --add-host=host.docker.internal:host-gateway "<docker-tag>" /bin/bash
   ```

5. Настроить утилиту

   ```
   codeplag settings show
   codeplag settings modify --reports_extension mongo
   codeplag settings modify --log-level debug // для отображения логов работы БД
   codeplag settings modify --mongo-port <mongo-port> --mongo-user <mongo-user> --mongo-pass <mongo-pass> --mongo-host <mongo-host> // при изменении стандартных настроек
   ```

6. Дальше можно протестировать работу на основе примеров из основной инструкции проекта.  
   При просмотре логов БД важно учитывать, что это логи непосредственно репозитория, поэтому даже при протухании данных
   будет успешное чтение из кэша, но после чтения протухшего кэша сразу последует лог его перезаписи.