import pika
import numpy as np
import json
import time
import os
from datetime import datetime
from sklearn.datasets import load_diabetes
 
# Создаём бесконечный цикл для отправки сообщений в очередь
while True:
    try:
        # Загружаем датасет о диабете
        X, y = load_diabetes(return_X_y=True)
        # Формируем случайный индекс строки
        random_row = np.random.randint(0, X.shape[0]-1)
 
        # Создаём подключение по адресу rabbitmq:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
 
        # Создаём очередь y_true
        channel.queue_declare(queue='y_true')
        # Создаём очередь features
        channel.queue_declare(queue='features')

        
        message_id = datetime.timestamp(datetime.now())
 
        # Публикуем сообщение в очередь y_true
        channel.basic_publish(exchange='',
                            routing_key='y_true',
                            body=json.dumps({
                                'id': message_id,
                                'y_true': y[random_row],
                            }))
        print('Сообщение с правильным ответом отправлено в очередь')
 
        # Публикуем сообщение в очередь features
        channel.basic_publish(exchange='',
                            routing_key='features',
                            body=json.dumps({
                                'id': message_id,
                                'features': list(X[random_row]),
                            }))
        print('Сообщение с вектором признаков отправлено в очередь')
 
        # Закрываем подключение
        connection.close()

        time.sleep(10)
    except:
        print('Не удалось подключиться к очереди')
        os.exit(1)