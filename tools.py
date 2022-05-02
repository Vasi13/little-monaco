import json
import logging
import os
import shutil

import requests
# supress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

win_special_chars = '/\\:?"<>|.'
download_folder = './download'

def clean_file_name(file_name):
    for c in win_special_chars:
        file_name = file_name.replace(c, '')
    return file_name

def extract_env_name(url):
    tmp_url = url.split('.')
    if tmp_url[1] == 'sprint' or tmp_url[1] == 'live':
        env_name = tmp_url[0][8:]
    # managed ?
    else:
        _url = url.split('/')
        env_name = _url[4]
    return env_name

def create_download_folder(env_name, directory):
    # Parent Directory path
    parent_dir = os.path.join(download_folder, env_name)
    # Dashboard folder Path
    path = os.path.join(parent_dir, directory)

    # create ./download
    if not os.path.isdir(download_folder):
        try:
            os.mkdir(download_folder)
            logging.debug('Download folder created')
        except Exception as e:
            logging.error(f'Cannot create dir {download_folder}')
            exit()

    if not os.path.isdir(parent_dir):
        try:
            os.mkdir(parent_dir)
            logging.debug('Config Download folder created')
        except Exception as e:
            logging.error('Cannot create dir {}'.format(parent_dir))
            exit()
    else:
        if os.path.isdir(os.path.join(parent_dir, directory)):
            # Delete the exsiting Dashboard
            try:
                shutil.rmtree(path)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
                logging.error("Unable to delete folder " +
                              e.filename + ":" + e.strerror)

    # Create the directory
    # 'Dashboards' in
    #  the corresponding env download folder
    os.mkdir(path)
    return path

def store_entity(jsonEntity, path, fileName):
    # lock because of map file writting
    # self.lock.acquire()
    fileName = clean_file_name(fileName)
    fileName += '.json'
    completeName = os.path.join(path, fileName)
    jsonString = json.dumps(jsonEntity, sort_keys=True, indent=4)
    # self.write_hash(path, jsonString)
    try:
        jsonFile = open(completeName, "w")
    except Exception as e:
        logging.error('%s', e)
        logging.error('Invalid name %s', completeName)
        return
    jsonFile.write(jsonString)
    # jsonFile.close()
    logging.debug('Created %s', fileName)

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def replaceStrings(jsonString):
    # Rebranding
    jsonString = jsonString.replace('NWNA', "BTB")

    # Management zones
    jsonString = jsonString.replace('ACT', 'act')
    jsonString = jsonString.replace('-9093836084140912148', '9140897391800647078')
    jsonString = jsonString.replace('RTE', 'rte')
    jsonString = jsonString.replace('6582271140241290692', '3747111364203272220')
    jsonString = jsonString.replace('PREPROD', 'preprod')
    jsonString = jsonString.replace('-9080113026292230278', '-6731235818825171265')
    jsonString = jsonString.replace('PROD', 'prod')
    jsonString = jsonString.replace('8619667914839288924', '2196831306417849407')
    jsonString = jsonString.replace('VST', 'vst')
    jsonString = jsonString.replace('3951604299736995553', '6741562783482005349')
    jsonString = jsonString.replace('DR', 'dr')
    jsonString = jsonString.replace('-566573522810433853', '-1001755160764835678')

    # Ownership
    jsonString = jsonString.replace('cosmin.gherghel@nestle.com', "Sandeep.Rachuri@nestle.com")
    jsonString = jsonString.replace('cosmin.gherghel@dynatrace.com', "Sandeep.Rachuri@nestle.com")
    jsonString = jsonString.replace('vasile.gafton@nestle.com', "Sandeep.Rachuri@nestle.com")
    jsonString = jsonString.replace('vasile.gafton@dynatrace.com', "Sandeep.Rachuri@nestle.com")

    # Synthetic AG
    jsonString = jsonString.replace('SYNTHETIC_LOCATION-A6A2C5D1634C44A2', "SYNTHETIC_LOCATION-5E3B800757E86AFE")
    jsonString = jsonString.replace('SYNTHETIC_LOCATION-E8CAD583FEDCF984', "SYNTHETIC_LOCATION-5E3B800757E86AFE")

    return jsonString

def download(url, directory, entities):
    env_name = extract_env_name(url)
    path = create_download_folder(env_name, directory)
    logging.info("Downloading %s", directory)
    logging.debug(
        '%s folder created inside Config Download folder', directory)

    for entity in entities:
        if 'metadata' in entity:
            del entity['metadata']
        if 'id' in entity:
            del entity['id']
        if 'entityId' in entity:
            del entity['entityId']
        if 'automaticallyAssignedApps' in entity:
            del entity['automaticallyAssignedApps']
        if 'manuallyAssignedApps' in entity:
            del entity['manuallyAssignedApps']

        jsonString = json.dumps(entity)
        jsonString = replaceStrings(jsonString)
        entity = json.loads(jsonString)
        if jsonString.find('"name":') != -1:
            name = find_between(jsonString, '"name":', '",')
        elif jsonString.find('"displayName":') != -1:
            name = find_between(jsonString, '"displayName":', '",')

        store_entity(entity, path, name)

def upload(directory, srcURL, dstDt):
    env_name = extract_env_name(srcURL)
    parent_dir = os.path.join(download_folder, env_name)
    # Dashboard folder Path
    path = os.path.join(parent_dir, directory)
    for filename in os.listdir(path):
        with open(os.path.join(path, filename), 'r') as f:
            _json = json.load(f)
            if directory == "Dashboards":
                dstDt.pushDashboard(_json)
            elif directory == "Synthetic Monitors":
                dstDt.pushSyntheticMonitor(_json)
            elif directory == "Request Attributes":
                dstDt.pushRequestAttribute(_json)
            elif directory == "Calculated Metrics":
                dstDt.pushCalculatedMetric(_json)