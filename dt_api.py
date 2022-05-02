import logging
import requests
# supress SSL warnings
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Dynatrace():

    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.header = {
            "Authorization": "Api-TOKEN " + token,
            "Content-Type": "application/json"
        }

    '''TAGS'''
    def getAutoTags(self):
        logging.debug('Downloading all Tags from {}'.format(self.url))
        _url = self.url + '/api/config/v1/autoTags'
        res = self.make_request(_url, method='GET')
        res_json = json.loads(res.text)
        return res_json['values']

    def getSingleAutoTag(self, tagId):
        _url = self.url + '/api/config/v1/autoTags/' + tagId
        res = self.make_request(_url, method='GET')
        return json.loads(res.text)

    def deleteAutoTag(self, tagId):
        _url = self.url + '/api/config/v1/autoTags/' + tagId
        res = self.make_request(_url, method='DELETE')
        return res.status_code

    def pushAutoTag(self, tag):
        _url = self.url + '/api/config/v1/autoTags'
        logging.info('Uploading new Tag: {}'.format(tag['name']))
        _payload = json.dumps(tag)
        res = self.make_request(_url, method='POST', payload=_payload)
        return res.status_code

    '''Dasboards'''
    def getDashboards(self):
        logging.debug('Downloading all Dashboards from {}'.format(self.url))
        _url = self.url + '/api/config/v1/dashboards'
        res = self.make_request(_url, method='GET')
        res_json = json.loads(res.text)
        return res_json['dashboards']

    def getSingleDashboard(self, dashboardId):
        _url = self.url + '/api/config/v1/dashboards/' + dashboardId
        res = self.make_request(_url, method='GET')
        return json.loads(res.text)

    def pushDashboard(self, dashboard):
        _url = self.url + '/api/config/v1/dashboards'
        logging.info('Uploading new Dashboard: {}'.format(dashboard['dashboardMetadata']['name']))
        _payload = json.dumps(dashboard)
        res = self.make_request(_url, method='POST', payload=_payload)
        return res.status_code

    '''Synthetic Monitors'''

    def getSyntheticMonitors(self, parameters=None):
        logging.debug('Downloading all Synthetic Monitors from {}'.format(self.url))
        _url = self.url + '/api/v1/synthetic/monitors'
        res = self.make_request(_url, method='GET', parameters=parameters)
        res_json = json.loads(res.text)
        return res_json['monitors']

    def getSingleSyntheticMonitor(self, monitorId):
        _url = self.url + '/api/v1/synthetic/monitors/' + monitorId
        res = self.make_request(_url, method='GET')
        return json.loads(res.text)

    def pushSyntheticMonitor(self, monitor):
        _url = self.url + '/api/v1/synthetic/monitors'
        logging.info('Uploading new Synthetic Monitor: {}'.format(monitor['name']))
        _payload = json.dumps(monitor)
        res = self.make_request(_url, method='POST', payload=_payload)
        return res.status_code

    '''Request Attributes'''

    def getRequestAttributes(self):
        logging.debug('Downloading all Request Attributes from {}'.format(self.url))
        _url = self.url + '/api/config/v1/service/requestAttributes'
        res = self.make_request(_url, method='GET')
        res_json = json.loads(res.text)
        return res_json['values']

    def getSingleRequestAttribute(self, requestAttributeId):
        _url = self.url + '/api/config/v1/service/requestAttributes/' + requestAttributeId
        res = self.make_request(_url, method='GET')
        return json.loads(res.text)

    def pushRequestAttribute(self, requestAttribute):
        _url = self.url + '/api/config/v1/service/requestAttributes'
        logging.info('Uploading new Request Attribute: {}'.format(requestAttribute['name']))
        _payload = json.dumps(requestAttribute)
        res = self.make_request(_url, method='POST', payload=_payload)
        return res.status_code

    '''Calculated Metrics'''

    def getCalculatedMetrics(self):
        logging.debug('Downloading all Calculated Metrics from {}'.format(self.url))
        _url = self.url + '/api/config/v1/calculatedMetrics/service'
        res = self.make_request(_url, method='GET')
        res_json = json.loads(res.text)
        return res_json['values']

    def getSingleCalculatedMetric(self, calculatedMetricId):
        _url = self.url + '/api/config/v1/calculatedMetrics/service/' + calculatedMetricId
        res = self.make_request(_url, method='GET')
        return json.loads(res.text)

    def pushCalculatedMetric(self, calculatedMetric):
        _url = self.url + '/api/config/v1/calculatedMetrics/service'
        logging.info('Uploading new Calculated Metric: {}'.format(calculatedMetric['name']))
        _payload = json.dumps(calculatedMetric)
        res = self.make_request(_url, method='POST', payload=_payload)
        return res.status_code

    def make_request(self, url, parameters=None, method=None, payload=None):
        '''makes post or get request request'''
        try:
            if method == 'POST':
                res = requests.post(url, data=payload, headers=self.header,
                                    verify=False, params=parameters, timeout=10)
            elif method == 'GET':
                res = requests.get(url, headers=self.header,
                                   verify=False, params=parameters, timeout=10)
            elif method == 'PUT':
                res = requests.put(url, data=payload, headers=self.header,
                                   verify=False, params=parameters, timeout=10)
            elif method == 'DELETE':
                res = requests.delete(
                    url, headers=self.header, verify=False, timeout=10)
            else:
                print('Unkown Method')
                logging.error('Unkown Request Method')
                exit(-1)
        except requests.exceptions.RequestException as exception:
            logging.error(exception)
            raise SystemExit(exception)
        if res.status_code > 399:
            print(res.text)
            logging.error(res.text)
            #exit(-1)
        return res
