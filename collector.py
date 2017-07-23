from googlefinance import getQuotes
from pymongo import MongoClient
from time import sleep
import json
from config_class import Config
from logger import FileLogger, ConsoleLogger
config = Config()


# get index list from yaml file
index_list = config.stocks['index_list']
# get period from yaml file
period = config.system['collection_period']
# get db name from yaml file
db_name = config.db['db_name']

file_logger = FileLogger()
console_logger = ConsoleLogger()


class DbHandler:
    def __init__(self, db_name, index_list):
        self.index_list = index_list
        self.db_name = db_name
        self.client = MongoClient()
        self.db = self.client[self.db_name]
        file_logger.log('info', 'Starting DbHandler')
        console_logger.log('info', 'Starting DbHandler')
        file_logger.log('info', 'db_name = {db_name}'.format(db_name=self.db))
        file_logger.log('info', 'index_list = {index_list}'.format(index_list=self.index_list))

    def get_db_collections(self):
        """
        Get list of db collections
        :return: list of db collections
        """
        return self.db.collection_names(include_system_collections=False)

    def get_collection_data(self, collection_name):
        """
        Get all collaction data by collection name
        :param collection_name:
        :return: collection data
        """
        data = []
        cursor = self.db[collection_name.lower()].find()

        for doc in cursor:
            doc.pop('_id')
            data.append(doc)
        return data

    def get_last_inserted_document(self, collection_name):
        """
        Get last inserted document from collection
        :param collection_name: collection name
        :return: last inserted document
        """
        data = []
        cursor = self.db[collection_name.lower()].find().sort('$natural', -1).limit(1)
        for doc in cursor:
            doc.pop('_id')
            data.append(doc)
        return data

    def align_db_collections(self):
        """
        Verify collections exist for all indices
        :return:
        """
        collections = self.get_db_collections()
        console_logger.log('info', 'db collections = {collections}'.format(collections=collections))
        file_logger.log('info', 'db collections = {collections}'.format(collections=collections))

        for index in self.index_list:
            if index.lower() not in collections:
                self.db.create_collection(index.lower())
                console_logger.log('info', 'create collection - {index}'.format(index=index.lower()))
                file_logger.log('info', 'create collection - {index}'.format(index=index.lower()))


class Collector:
    def __init__(self, index_list, period=10):
        self.index_list = index_list
        self.period = period
        self.client = MongoClient()
        self.db = self.client[db_name]
        console_logger.log('info', 'Starting Collector')
        file_logger.log('info', 'Starting Collector')
        file_logger.log('info', 'db_name = {db_name}'.format(db_name=self.db))
        file_logger.log('info', 'index_list = {index_list}'.format(index_list=self.index_list))
        file_logger.log('info', 'period = {period}'.format(period=self.period))

    def collect_data(self, index):
        """
        Collect index data
        :param index: index name string
        :return: data dict
        """
        try:
            data = json.dumps(getQuotes(index), indent=2)
            file_logger.log('info', 'received data for {index}: {data}'.format(index=index, data=str(data)))
            return data

        except:
            file_logger.log('error', 'error getting data for {index}'.format(index=index))
            return None

    def insert_to_db(self, data):
        """
        Insert data to db
        :param data: data
        :return: result of operation
        """
        j_data = json.loads(data)
        index_name = j_data[0]['StockSymbol']
        try:
            file_logger.log('info', 'data is: ' + str(j_data))
            result = self.db[index_name.lower()].insert(j_data)
            file_logger.log('info', 'data inserted to db for {index}'.format(index=index_name))
            file_logger.log('info', result)
            return result

        except Exception, e:
            file_logger.log('error', 'data insertion failed for {index}'.format(index=index_name))
            file_logger.log('error', str(e))

    def operate(self):
        """
        Main operating method
        # iterate through the list on indices
        # collect data
        # insert to db
        # idle
        """
        polling_count = 1

        while True:
            file_logger.log('info', 'starting polling cycle {count}'.format(count=polling_count))
            for index in self.index_list:
                # log iteration number
                data = self.collect_data(index)
                if data:
                    self.insert_to_db(data)
            sleep(self.period)
            file_logger.log('info', 'finished polling cycle {count}'.format(count=polling_count))
            polling_count += 1


if __name__ == '__main__':
    db_handler = DbHandler(db_name=db_name, index_list=index_list)
    db_handler.align_db_collections()
    collector = Collector(index_list=index_list, period=period)
    collector.operate()
