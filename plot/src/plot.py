import pika
import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
 
try:
    # Создаём подключение к серверу на локальном хосте
    connection = pika.BlockingConnection(pika.ConnectionParameters(os.getenv('RABBITMQ_HOST', 'localhost')))
    channel = connection.channel()
   
    # Объявляем очередь y_pred
    channel.queue_declare(queue='metric_added')

    x = list(pd.read_csv("logs/metric_log.csv")["absolute_error"])

    def redraw_error_distribution(message_id, absolute_error):
        x.append(absolute_error)

        fig, ax = plt.subplots( nrows=1, ncols=1 )
        # ax.plot([0,1,2], [10,20,3])

        counts, bins = np.histogram(x)
        ax.stairs(counts, bins)     

        fig.savefig('logs/error_distribution.png')   # save the figure to file
        plt.close(fig)    # close the figure window

        print(f"histogram обновлена id={message_id} absolute_error={absolute_error}")
 
    # Создаём функцию callback для обработки данных из очереди
    def callback(ch, method, properties, body):
        msg = json.loads(body)
        message_id = msg["id"]
        absolute_error = msg.get('absolute_error', 0.0)
        redraw_error_distribution(message_id, absolute_error)
 
    # Извлекаем сообщение из очереди y_true
    channel.basic_consume(
        queue='metric_added',
        on_message_callback=callback,
        auto_ack=True
    )
 
    # Запускаем режим ожидания прихода сообщений
    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()
except Exception as e:
    print('Ошибка обработки:', type(e), e)
    exit(1)