# Бизнес использование машинного обучения, задание 1

## Описание

В соответствии с заданием доработаны сервисы metric (логика в `metric/src/metric.py`) и plot (логика в `plot/src/plot.py`).

Первый подписан на rabbitmq очереди `y_true` и `y_pred`, сохраняет метрики в конец файла `logs/metric_logs.csv` и публикует событие `metric_added`.

В событии присутствует поле `absolute_error` для построения гистограммы.

Сервис plot подписан на rabbitmq очередь `metric_added`, при получении события добавляет `absolute_error` в датасет и перерисовывает гистограмму `logs/error_distribution.png`. При запуске он считывает `logs/metric_logs.csv` для добавления в датасет ранее записанных метрик.

## Запуск сервисов в docker-compose

```bash
# Очистка файла логов для дебага, необязательно. Файлы автоматически создадутся при отсутствии
# Если файл лога при перезапуске существует, то продолжится запись в конец файла.
rm -f logs/error_distribution.png logs/metric_log.csv

docker-compose up -d
```

В Dockerfile `CMD` добавлен флаг `-u` для немедленной записи stdout логов в логи docker контейнера.
Также секция установки зависимостей перенесена выше копирования файлов сервиса,
чтобы при изменениях файлов не устанавливать заново зависимости, что может занимать до 15 мин,
а использовать кэшированный слой docker.

При запуске docker-compose единоразово запускается сервис `learn_model` для обучения модели.
При успешном выполнении с кодом ответа 0 контейнер не запускается заново из-за конфигурации `restart: on-failure`.

Обученная модель, метрики-логи и картинка-гистограмма шарится между контейнерами и хостовой системой через volumes.

## Локальный запуск (в docker только rabbitmq)

Удобно использовать для дебага и разработки

```bash
docker-compose down
docker-compose up -d rabbitmq

# Очистка файла логов для дебага
rm -f logs/error_distribution.png logs/metric_log.csv

# venv
python -m venv .venv
pip install -r model/requirements.txt
pip install -r plot/requirements.txt
pip install -r metric/requirements.txt
pip install -r features/requirements.txt

# console 1, features
.venv/bin/python features/src/features.py
# console 2, model
.venv/bin/python model/src/model.py
# console 3, metric
.venv/bin/python metric/src/metric.py
# console 4, plot
.venv/bin/python plot/src/plot.py
```