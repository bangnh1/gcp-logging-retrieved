import os
import sys
from google.cloud.logging import Client
import time
from itertools import islice
from dateutil.rrule import MINUTELY, rrule
import dateutil.parser
import logging as pythonLog
import concurrent.futures
import argparse
import log
import yaml
from cerberus import Validator
from pathlib import Path
import json

# Logging configuration
logger = pythonLog.getLogger(__name__)

# Instantiates a client
if os.path.isfile('keyfile.json'):
    logging_client = Client.from_service_account_json('keyfile.json')
else:
    logging_client = Client()


class LogBlock:
    def __init__(self, start, end, field, queryStatement):
        self.start = start
        self.end = end
        self.name = start
        self.field = field
        self.queryStatement = queryStatement + ' AND timestamp>=' + \
            '\"' + start + '\"' + ' AND timestamp<=' + \
            '\"' + end + '\"'


def divideTime(startTime, endTime, interval):
    startTime = dateutil.parser.parse(startTime)
    endTime = dateutil.parser.parse(endTime)
    interval = tuple(islice(rrule(freq=MINUTELY, dtstart=startTime,
                                  until=endTime), None, None, interval))
    return interval


def createQueue(interval, field, queryStatement):
    task_queue = []
    for count, stop in enumerate(interval):
        if count < len(interval) - 1:
            start = interval[count].isoformat()
            end = interval[count+1].isoformat()
            task_queue.append(LogBlock(start, end, field, queryStatement))
    return tuple(task_queue)


def fixkey(key):
    return key.replace("-", "_").replace("/", "_").replace(".", "_")


def normalize(data):
    if isinstance(data, dict):
        data = {fixkey(key): normalize(value) for key, value in data.items()}
    elif isinstance(data, list):
        data = [normalize(item) for item in data]
    return data


def getEntries(task_queue):

    getEntries = logging_client.list_entries(
        filter_=task_queue.queryStatement, page_size=1000)
    result = map(lambda x: normalize(x.to_api_repr()), getEntries)
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    Path(application_path + "/results").mkdir(parents=True, exist_ok=True)
    with open(application_path + "/results/" + task_queue.name + ".log", "w") as f:
        data = tuple(result)
        field = task_queue.field
        if field != '':
            result = map(lambda x: x.get(field), data)
            for line in result:
                f.write(line)
        else:
            f.write(json.dumps(data))


def readConfiguration(confPath):

    def load_yaml():

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        with open(application_path + '/' + confPath, 'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exception:
                raise exception
    if hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)
    schema = eval(open('schema.yaml', 'r').read())
    validationResults = Validator(schema)
    configurationData = load_yaml()
    if validationResults.validate(configurationData, schema) == False:
        raise ValueError(validationResults.errors)
    logger.debug(validationResults.validate(configurationData, schema))
    logger.debug(validationResults.errors)
    return configurationData


def queryStatementTransform(statement):
    return " ".join(statement.split()).replace('=', ':').replace(' ', ' AND ')


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf-name',
                        default="config.yaml", help="configuration file")

    log.__add_options(parser)
    args = parser.parse_args()
    log.__process_options(parser, args)
    logger.debug(f"Argument: {args}")

    configurationPath = args.conf_name
    configurationData = readConfiguration(configurationPath)
    logger.debug(configurationData)
    startTime = configurationData.get('startTime')
    endTime = configurationData.get('endTime')
    interval = configurationData.get('interval', 30)
    maxWorkers = configurationData.get('maxWorkers', os.cpu_count())
    field = configurationData.get('field', '')
    queryStatement = queryStatementTransform(configurationData.get(
        'queryStatement'))

    queueInterval = divideTime(startTime, endTime, interval)
    task_queue = createQueue(queueInterval, field, queryStatement)
    start = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=maxWorkers) as executor:
        executor.map(getEntries, task_queue)
    end = time.time()
    print(f'\nTime to complete: {end - start:.2f}s\n')


if __name__ == "__main__":
    main()
