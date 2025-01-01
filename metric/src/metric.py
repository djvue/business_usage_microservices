import pika
import json
import os
 
try:
    # Создаём подключение к серверу на локальном хосте
    connection = pika.BlockingConnection(pika.ConnectionParameters(os.getenv('RABBITMQ_HOST', 'localhost')))
    channel = connection.channel()
   
    # Объявляем очередь y_true
    channel.queue_declare(queue='y_true')
    # Объявляем очередь y_pred
    channel.queue_declare(queue='y_pred')
    # Объявляем очередь y_pred
    channel.queue_declare(queue='metric_added')

    y_true_processing = {}
    y_pred_processing = {}

    if not os.path.isfile('logs/metric_log.csv'):
        with open('logs/metric_log.csv', "w") as f:
            f.write(f"id,y_true,y_pred,absolute_error\n")

    def write_metric(message_id, y_pred, y_true):
        absolute_error = abs(y_true - y_pred)

        with open('logs/metric_log.csv', "a") as f:
            f.write(f"{message_id},{y_true},{y_pred},{absolute_error}\n")

        print("записана метрика", {
                            'id': message_id,
                            'y_pred': y_pred,
                            'y_true': y_true,
                            'absolute_error': absolute_error,
                        })
        channel.basic_publish(exchange='',
                        routing_key='metric_added',
                        body=json.dumps({
                            'id': message_id,
                            'y_pred': y_pred,
                            'y_true': y_true,
                            'absolute_error': absolute_error,
                        }))
 
    # Создаём функцию callback для обработки данных из очереди
    def callback(ch, method, properties, body):
        msg = json.loads(body)
        message_id = msg["id"]

        if method.routing_key == 'y_true':
            y_true = msg['y_true']

            if message_id in y_pred_processing:
                write_metric(message_id, y_pred_processing[message_id], y_true)
                del y_pred_processing[message_id]
                return

            y_true_processing[message_id] = y_true
        elif method.routing_key == 'y_pred':
            y_pred = msg['y_pred']

            if message_id in y_true_processing:
                write_metric(message_id, y_pred, y_true_processing[message_id])
                del y_true_processing[message_id]
                return

            y_pred_processing[message_id] = y_pred
        else:
            raise Exception(f"unsupported routing_key {method.routing_key}")
 
    # Извлекаем сообщение из очереди y_true
    channel.basic_consume(
        queue='y_true',
        on_message_callback=callback,
        auto_ack=True
    )
    # Извлекаем сообщение из очереди y_pred
    channel.basic_consume(
        queue='y_pred',
        on_message_callback=callback,
        auto_ack=True
    )
 
    # Запускаем режим ожидания прихода сообщений
    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()
except Exception as e:
    print('Ошибка обработки:', type(e), e)
    exit(1)