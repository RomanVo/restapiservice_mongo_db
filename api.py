from flask import Flask, jsonify, abort
from config_class import Config
from logger import FileLogger, ConsoleLogger
from collector import DbHandler
config = Config()

# get db name from yaml file
db_name = config.db['db_name']

file_logger = FileLogger()
console_logger = ConsoleLogger()
db_handler = DbHandler(db_name=db_name, index_list='')

app = Flask(__name__)


# get_collections
@app.route('/api/indices', methods=['GET'])
def get_collections():
    return jsonify({'collections': db_handler.get_db_collections()})


# get_by_collection_name
@app.route('/api/index/<index>', methods=['GET'])
def get_collection_data(index):
    is_index_exist(index)
    return jsonify({'results': db_handler.get_collection_data(index)})


# get_last_entry_from_collection
@app.route('/api/index/<index>/last', methods=['GET'])
def get_last_inserted_document(index):
    is_index_exist(index)
    return jsonify({'results': db_handler.get_last_inserted_document(index)})


def is_index_exist(index):
    if index not in db_handler.get_db_collections():
        abort(404)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(config.db['app_port']))
