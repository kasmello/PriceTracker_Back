import os
import datetime

from tqdm import tqdm
from dotenv import load_dotenv
from fuelwatch import FuelWatch
from neo4j import GraphDatabase, RoutingControl
from constants import PRODUCT, REGION, BRAND, SUBURB

load_dotenv()
URI = os.getenv('URI')
USR = os.getenv('USR')
PASSWORD = os.getenv('PASSWORD')
AUTH = (USR,PASSWORD)
fuel_watch_obj = FuelWatch()


def insert_data_into_db(xml,query_date,product,driver):
    
    for item in tqdm(xml):
        query_str = ''
        # query brand, location(suburb) and place. if not there, add
        query_str += f'MERGE (b:Brand {{brand: "{item["brand"]}"}})\n'
        query_str += f'MERGE (l:Location {{location: "{item["location"].title()}"}})\n'
        query_str += f'MERGE (p:Place {{address: "{item["address"]}"}})\n'\
            +f'ON CREATE SET p.phone= "{item["phone"]}",\
                p.latitude= {item["latitude"]}, p.longitude= {item["longitude"]}, \
                p.description= "{item["site-features"].strip().lstrip(", ").rstrip(",")}"\n\
                MERGE (b)-[:OWNS]->(p)\nMERGE (l)-[:CONTAINS]->(p)\n'

        query_str += f'MERGE (d:DATE_{PRODUCT[product]} {{date: "{query_date}"}})\n\
            MERGE (d)-[path:PRICED_AT]->(p)\nON CREATE SET path.price={item["price"]}'
        driver.execute_query(query_str)

def loop_historical_data(days, driver):
    #days is how many days you want to go back
    for product in tqdm([1,6,10]):
        for delta in tqdm(range(-1,days+1)):
            d = datetime.date.today()-datetime.timedelta(days=delta)
            date_str=f'{d.day}/{d.month}/{d.year}'
            query_date = f'{d.year}-{d.month}-{d.day}'
            fuel_watch_obj.query(day=date_str,product=product)
            xml = fuel_watch_obj.get_xml
            insert_data_into_db(xml,query_date,product,driver)

    

if __name__ == '__main__':
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        print(driver.verify_connectivity())
        # loop_historical_data(7,driver)
        loop_historical_data(-1,driver)