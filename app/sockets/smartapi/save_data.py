from kafka import KafkaConsumer
from app.database.sqlite.sqlite_db_connection import get_session
from app.database.sqlite.models.websocket_models import SocketStockPriceInfo
import json

consumer = KafkaConsumer('muni', bootstrap_servers='localhost:9094')


def save_data(data,session):
    decoded_data = data.decode('utf-8')
    decoded_data = json.loads(decoded_data)
    socket_stock_price_info = SocketStockPriceInfo(
       last_traded_timestamp=decoded_data['last_traded_timestamp'],
        token=decoded_data['token'],
        retrival_timestamp=decoded_data['retrived_timestamp'],
        socket_name=decoded_data['socket_name'],
        exchange_timestamp=decoded_data['exchange_timestamp'],
        name=decoded_data['name'],
        last_traded_price=decoded_data['last_traded_price'],
        open_price_of_the_day=decoded_data['open_price_of_the_day'],
        high_price_of_the_day=  decoded_data['high_price_of_the_day'],
        low_price_of_the_day= decoded_data['low_price_of_the_day'],
        closed_price=decoded_data.get('closed_price'),
        last_traded_quantity=decoded_data.get('last_traded_quantity'),
        average_traded_price=decoded_data.get('average_traded_price'),
        volume_trade_for_the_day=decoded_data.get('volume_trade_for_the_day'),
        total_buy_quantity=decoded_data.get('total_buy_quantity'),
        total_sell_quantity=decoded_data.get('total_sell_quantity'),
        open_interest=decoded_data.get('open_interest'),
        open_interest_change_percentage=decoded_data.get('open_interest_change_percentage')
        
    )
    session.add(socket_stock_price_info)
    session.commit()

def main():
    session = next(get_session())
    for message in consumer:
        save_data(message.value,session)
        
if __name__ == "__main__":
    main()
    
