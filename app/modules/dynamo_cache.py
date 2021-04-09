#!/usr/bin/env python

from doglessdata import DataDogMetrics
import boto3

DYNAMODB = boto3.resource("dynamodb")
TABLE = DYNAMODB.Table("qi_user")

metrics = DataDogMetrics()
app = Chalice(app_name='qi-serverless')


def format_dynamo_record(raw_record):
    """
    Standard queue dict format
    """
    record = copy(raw_record)
    if isinstance(record, str):
        if record == "":
            record = "."
    elif isinstance(record, dict):
        for key, value in record.items():
            if isinstance(value, dict):
                value = format_dynamo_record(value)
            elif isinstance(value, list):
                value = [format_dynamo_record(item) for item in value]
            elif isinstance(value, float):
                value = Decimal(str(value))
            elif value == "":
                value = "."
            else:
                continue  # no transformation done
            record[key] = value
    else:
        raise ValueError(
            f"Invalid record, {record}, {type(record)} not suported"
        )
    return record

def get_current_user():
    request = app.current_request.to_dict()
    try:
        result = request["context"]
        result = result["authorizer"]
        result = result["claims"]
        result = result["cognito:username"]
    except KeyError:
        pass
    return str(result)


def is_dev():
    lambda_name = os.environ.get('AWS_LAMBDA_FUNCTION_NAME', "local-dev")
    if lambda_name.endswith("-dev"):
        return True
    elif "-testing" in lambda_name:
        return True
    else:
        return False


if is_dev():
    app.debug = True

    @app.route('/app', authorizer=AUTHORIZER)
    def get_app():
        """
        Debuging endpoint.
        Describe current app attributes.
        """
        return dir(app)

    @app.route('/app/{attr}', authorizer=AUTHORIZER)
    def get_app_attr(attr):
        """
        Debuging endpoint.
        Describe current app attribute.
        """
        return str(getattr(app, attr))

    @app.route('/request', authorizer=AUTHORIZER)
    def get_request():
        """
        Debuging endpoint.
        Describe current request context.
        """
        return app.current_request.to_dict()


@app.route("/")
@metrics.timeit
def get_root():
    """
    Self-documenting endpoint.
    Describes available endpoints.
    """
    endpoints = []
    for path in app.routes.values():
        for handler in path.values():
            url = "%s %s" % (handler.method, handler.uri_pattern)
            description = handler.view_function.__doc__
            doc_item = {"url": url, "description": description}
            endpoints.append(doc_item)
    return {"service": "Serverless QI", "endpoints": endpoints}


@metrics.timeit
@app.route('/instrument/{instrument_name}', authorizer=AUTHORIZER)
def get_instrument(instrument_name):
    """
    Get instrument and drivers info.
    """
    print("Instrument name: %s" % instrument_name)
    instrument_name = unquote(instrument_name)
    query_params = app.current_request.query_params or {}
#     print(query_params)
#     if "limit" in query_params:
#         print("'limit' is present")
    instruments = data.search_instrument(instrument_name)
    username = get_current_user()
    metrics.increment("billing", tags=["username:%s" % username,
                      "endpoint:instrument"])
    return {"username": username, "results": instruments}


@app.route('/dashboard', authorizer=AUTHORIZER)
@metrics.timeit
def get_dashboard():
    """
    Get default user's dashboard
    """
    username = get_current_user()
    response = TABLE.get_item(Key={"user_id": username})
    user = response.get("Item", {})
    dashboard = user.get("dashboard", {"instruments": ["msft"]})
    instruments = dashboard.get("instruments", [])
    instruments = dict((instrument, data.get_quotes(instrument))
                   for instrument in instruments)
    response = {
        "dashboard": {"instruments": instruments},
        "username": username
    }
    return response


@app.route('/dashboard', authorizer=AUTHORIZER, methods=["POST"])
@metrics.timeit
def set_dashboard():
    """
    Set default user's dashboard
    Receives as DATA:
    {
        "instruments": ["alph", "appl", "lynn"]
    }
    """
    username = get_current_user()
    dashboard = app.current_request.json_body
    if "instruments" not in dashboard:
        raise BadRequestError("a set of instruments must be specified, got: %s"
                              % dashboard)

    update_response = TABLE.update_item(
            Key={"user_id": username},
            UpdateExpression="SET dashboard = :dashboard",
            ExpressionAttributeValues={
                ":dashboard": dashboard
            }
    )
    response = {
        "dashboard": dashboard,
        "username": username,
#        "response": update_response,
    }
    return response


@app.route('/drivers/{instrument_name}', authorizer=AUTHORIZER)
@metrics.timeit
def get_drivers(instrument_name):
    """
    Get drivers for given instrument
    """
    instrument_name = unquote(instrument_name)
    drivers = data.get_drivers(instrument_name)

    username = get_current_user()
    metrics.increment("billing", tags=["username:%s" % username, "endpoint:drivers"])
    response = {
        "instrument": instrument_name,
        "username": username,
        "results": drivers
    }
    return response


@app.route('/sensitivities/{instrument}', authorizer=AUTHORIZER)
@metrics.timeit
def get_sensitivities(instrument):
    """
    Get sensitivities for drivers for given instrument
    """
#     results = qi_interface.run_generic().tolist()
    results = data.get_drivers_(instrument)
#     results = data.get_drivers(instrument)
    # results = qi_interface.learnparameters(data)

    username = get_current_user()
    metrics.increment("billing", tags=["username:%s" % username, "endpoint:drivers"])
    return {"username": username, "results": results}


@app.route('/authenticate', methods=['POST'])
def post_authenticate():
    """
    Authenticate endpoint
    """
    headers = app.current_request.headers
    authorization = headers.get("authorization", "")
    if not authorization.startswith("Basic "):
        raise ForbiddenError()
    encoded = authorization.split()[1]
    decoded = b64decode(encoded).decode()
    user, password = decoded.split(":", 1)
    idp_client = boto3.client('cognito-idp')
    user = idp_client.admin_initiate_auth(UserPoolId=USER_POOL_ID,
                                          AuthFlow='ADMIN_NO_SRP_AUTH', ClientId=CLIENT_ID,
                                          AuthParameters={'USERNAME': user, "PASSWORD": password})
    return user["AuthenticationResult"]


@app.route('/learn', methods=['POST'], authorizer=AUTHORIZER)
@metrics.timeit
def post_learn():
    """
    Receives url as DATA:
    {
        "samples": [[int]],
        "model_parameters": {
            "normalization_window": float,
            "regression_window": float
        }
    }

    <samples>: is a bi-dimensional array MxN (list of M list of N numbers), e.g.:
        [
         [1, 2, 3],
         [4, 5, 6]
        ]
    <model_parameters>: is optional, defaults to:
        {
            "normalization_window": 60,
            "regression_window": 60
        }

    """
    data = app.current_request.json_body
    model_parameters = data.get("model_parameters", None)
    if not model_parameters:
        model_parameters = {
            "normalization_window": 60,
            "regression_window": 60
        }
    result = data.get_drivers("msft")
    result["model_parameters"] = model_parameters
    return result

@metrics.timeit
def post_to_dynamo(event_type, description, body, priority=5):
    item = {
        "Body": body,
        "Datetime": Decimal(time.time()),
        "Description": description,
        "Type": event_type,
        "Sender": "Sensitivities runner",
        "Priority": int(priority),
        "Status": "New",
    }
    if DUMMY:
        print("Dummy alert event:")
        pprint(item)
    else:
        return EVENTS.put_item(Item=item)



'''
Simple Python interface to Amazon DynamoDB,
adding some dict-like sugar to boto.dynamodb.layer2.

Usage:

    pip install dynamo_db_dict
    from dynamo_db_dict import dynamo_db

    db = dynamo_db(aws_access_key_id='YOUR KEY HERE', aws_secret_access_key='YOUR SECRET KEY HERE') # or via: os.environ, ~/.boto, /etc/boto.cfg
    # Set table_name_prefix='YOUR_PROJECT_NAME_' if you use the same DynamoDB account for several projects.

    # Either create table "user" with hash_key "email" via AWS concole, or via inherited db.create_table(...).
    db.user['john@example.com'] = dict(first_name='John', last_name='Johnson') # Put. No need to repeat "email" in dict(...).
    john = db.user['john@example.com'] # Get.
    assert john == dict(email='john@example.com', first_name='John', last_name='Johnson') # Complete item, with "email".
    assert john['first_name'] == 'John' # Key access.
    assert john.first_name == 'John' # Attr access.
    del db.user['john@example.com'] # Delete.

See also:
* http://aws.amazon.com/dynamodb/
* http://boto.cloudhackers.com/en/latest/ref/dynamodb.html#module-boto.dynamodb.layer2

dynamo_db_dict version 0.2.4
Copyright (C) 2012 by Denis Ryzhkov <denis@ryzhkov.org>
MIT License, see http://opensource.org/licenses/MIT
'''

#### requirements

from adict import adict
from boto.dynamodb.layer2 import Layer2
from boto.dynamodb.table import Table

#### dynamo_db

class dynamo_db(Layer2):

    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, table_name_prefix='', **kwargs):
        '''
        Configures boto Layer2 connection to DynamoDB, creates cache for repeated access to tables:
            db = dynamo_db(aws_access_key_id='YOUR KEY HERE', aws_secret_access_key='YOUR SECRET KEY HERE') # or via: os.environ, ~/.boto, /etc/boto.cfg
        '''
        self.tables = {}
        self.table_name_prefix = table_name_prefix
        super(dynamo_db, self).__init__(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, **kwargs)

    def __getattr__(self, table_name):
        '''
        Simple access to a table:
            db.user

        For table names conflicting with Layer2 attributes, e.g. db.scan(), use:
            db.get_table('scan')
        '''
        table_name = self.table_name_prefix + table_name
        table = self.tables.get(table_name)
        if not table:
            table = self.tables[table_name] = dynamo_table(layer2=self, response=self.describe_table(table_name))
        return table

    get_table = __getattr__ # See __getattr__ docstring.

#### dynamo_table

class dynamo_table(Table):

    def __setitem__(self, hash_key, attrs):
        '''
        Puts item to db:
            db.user[email] = dict(first_name='...', ...)

        TODO: range_key support:
            db.message[topic][date] = dict(text='...', ...)
        '''
        self.layer2.put_item(item=self.new_item(hash_key=hash_key, attrs=attrs))

    def __getitem__(self, hash_key):
        '''
        Gets item from db:
            user = db.user[email]

        TODO: range_key support:
            message = db.message[topic][date]

        TODO: Option to control consistent_read.
        '''
        return adict(self.get_item(hash_key=hash_key, consistent_read=True))

    def __delitem__(self, hash_key):
        '''
        Deletes item from db:
            del db.user[email]

        TODO: range_key support:
            del db.message[topic][date]
        '''
        self.layer2.delete_item(item=adict(table=self, hash_key=hash_key, range_key=None))
        # NOTE: Do not change `adict` to `dict` here. It emulates Item object with attr access.

#### test

def test():
    print('Please copy the Usage above and test it with your own AWS keys and existing tables. TODO: Use `ddbmock` package.')

if __name__ == '__main__':
    test()
