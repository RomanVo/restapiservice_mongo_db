from flask import Flask, jsonify, url_for, redirect, request
# from flask_pymongo import PyMongo
# from flask_restful import Api, Resource
from config_class import Config
config = Config()

app = Flask(__name__)
app.config["MONGO_DBNAME"] = config.db['db_name']
mongo = PyMongo(app, config_prefix='MONGO')
APP_URL = '{app_url}:{app_port}'.format(app_url=config.db['app_url'], app_port=config.db['app_port'])


class Service(Resource):
    def get(self, component=None, branch=None, collections=None):
        data = []

        if collections:
            cursor = mongo.db.collection_names(include_system_collections=False)
            for result in cursor:
                result['url'] = APP_URL + url_for('results') + "/" + result.get('collections')
                data.append(result)

        else:
            cursor = mongo.db.test_results.find({}, {"_id": 0, "update_time": 0})

            for result in cursor:
                # for debugging
                #print result
                result['url'] = APP_URL + url_for('results') + "/" + result.get('component')
                data.append(result)

            return jsonify({"response": data})

    def post(self):
        data = request.get_json()
        # for debugging
        #print data
        if not data:
            data = {"response": "ERROR"}
            return jsonify(data)
        else:
            test_result = data.get('component')
            if test_result:
                mongo.db.test_results.insert(data)
            else:
                return {"response": "component missing"}

        return redirect(url_for("results"))


class Index(Resource):
    def get(self):
        return redirect(url_for("results"))


api = Api(app)
api.add_resource(Index, "/", endpoint="index")
api.add_resource(Service, "/api", endpoint="results")
api.add_resource(Service, "/api/collections", endpoint="component")
#api.add_resource(Service, "/api/component/<string:component>", endpoint="component")
#api.add_resource(Service, "/api/branch/<string:branch>", endpoint="branch")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(config.db['app_port']))
