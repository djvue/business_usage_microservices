import pika
import numpy as np
import json
import time
import os
from datetime import datetime
from sklearn.datasets import load_diabetes

# Загружаем датасет о диабете
X, y = load_diabetes(return_X_y=True)
 
# Создаём бесконечный цикл для отправки сообщений в очередь
while True:
    try:
        # Формируем случайный индекс строки
        random_row = np.random.randint(0, X.shape[0]-1)
 
        # Создаём подключение по адресу rabbitmq:
        connection = pika.BlockingConnection(pika.ConnectionParameters(os.getenv('RABBITMQ_HOST', 'localhost')))
        channel = connection.channel()
 
        # Создаём очередь y_true
        channel.queue_declare(queue='y_true')
        # Создаём очередь features
        channel.queue_declare(queue='features')

        
        message_id = datetime.timestamp(datetime.now())

        print(f"Отправка сообщения с id {message_id} в очередь")
 
        # Публикуем сообщение в очередь y_true
        channel.basic_publish(exchange='',
                            routing_key='y_true',
                            body=json.dumps({
                                'id': message_id,
                                'y_true': y[random_row],
                            }))
        print(f"Сообщение с правильным ответом id {message_id} отправлено в очередь")
 
        # Публикуем сообщение в очередь features
        channel.basic_publish(exchange='',
                            routing_key='features',
                            body=json.dumps({
                                'id': message_id,
                                'features': list(X[random_row]),
                            }))
        print(f"Сообщение с вектором признаков id {message_id} отправлено в очередь")
 
        # Закрываем подключение
        connection.close()

        print(f"Ожидание 10 секунд")
        time.sleep(10)
    except Exception as e:
        print('Ошибка обработки:', type(e), e)
        exit(1)