from faker import Faker
from confluent_kafka import Producer
import json
import time
import random

faker = Faker()
producer = Producer(
    {'bootstrap.servers': 'kafka:9092'}
)

actions = ['view_product', 'view_product', 'view_product' ,'add_to_cart', 'checkout']
status_codes = [200, 200, 500, 404, 404]
products = [f'prod-{i:04d}' for i in range(1, 51)]

def generate_user_session(user_id,ip, session_start):
    session_logs = []
    num_actions = random.randint(1,5)
    current_time = session_start
    for _ in range(num_actions):
        action = random.choice(actions)
        if action == 'checkout' and 'add_to_cart' not in [log['action'] for log in session_logs]:
            action = 'add_to_cart'  
        
        log = {
            'timestamp': current_time.isoformat(), # ISO format for Kafka
            'user_id': user_id,
            'ip_address': ip,
            'action': action,
            'product_id': random.choice(products),
            'user_agent': faker.user_agent() if random.random() > 0.05 else None,
            'response_time': round(random.uniform(0.1, 2.0) if random.random() > 0.05 else random.uniform(5.0, 10.0), 3),
            'status_code': random.choice(status_codes)
            }
        session_logs.append(log)
        current_time = faker.date_time_between(start_date=current_time, end_date='+5m')
    return session_logs

def generate_bot_logs(bot_ip='192.168.1.100', num_logs=50):
    bot_logs = []
    for _ in range(num_logs):
        log = {
            'timestamp': faker.date_time_this_month().isoformat(),
            'user_id': faker.uuid4(),
            'ip_address': bot_ip,
            'action': 'view_product',  # Bot chủ yếu xem sản phẩm
            'product_id': random.choice(products),
            'user_agent': 'Bot-Agent/1.0',  # User agent cố định cho bot
            'response_time': round(random.uniform(0.05, 0.2), 3),  # Response time nhanh bất thường
            'status_code': 200
        }
        bot_logs.append(log)
    return bot_logs

def produce_logs(num_sessions = 50, bot_percentage = 0.2):
    topic = 'web_logs'
    bot_sessions = int(num_sessions * bot_percentage)
    normal_sessions = num_sessions - bot_sessions
    for _ in range(normal_sessions):
        user_id = faker.uuid4()
        ip = faker.ipv4()
        session_start = faker.date_time_this_month()
        logs = generate_user_session(user_id, ip, session_start)
        for log in logs:
            producer.produce(topic, value=json.dumps(log).encode('utf-8'))
            print(f"Produced log: {log}")
            time.sleep(random.uniform(0.05, 0.2))
        
    bot_logs = generate_bot_logs(num_logs=bot_sessions * 10)
    for log in bot_logs:
        producer.produce(topic, value=json.dumps(log).encode('utf-8'))
        print(f"Produced bot log: {log}")
        time.sleep(0.01)
        
    producer.flush()

if __name__ == "__main__":
    produce_logs(num_sessions=100, bot_percentage=0.3)
    print("Log production completed.")

