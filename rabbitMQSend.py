import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel2 = connection.channel()
channel2.queue_declare(queue='blob')



def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

channel2.basic_consume(queue='blob', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel2.start_consuming()