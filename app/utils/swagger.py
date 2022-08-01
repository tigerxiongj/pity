
import json

from swagger_parser import SwaggerParser
from urllib.parse import urlencode, urlparse, parse_qs

class Swagger(object):
    PARAM_TYPES = set(['integer', 'string', 'boolean'])
    PARAM_TYPE_DEFAULT = {'integer': 1, 'string': '', 'boolean': 'true'}
    PARAM_IN_PATH_DEFAULT = {'name': 'host'}
    PARAM_IN_ALL = set(['query', 'path', 'body'])
    PARAM_IN_URL = set(['query', 'path'])

    def __init__(self, json_string) -> None:
        self.parser = SwaggerParser(swagger_dict=json.loads(json_string), use_example=False)
    
    @staticmethod
    def merge_url_query_params(url: str, additional_params: dict) -> str:
        url_components = urlparse(url)
        original_params = parse_qs(url_components.query)
        # Before Python 3.5 you could update original_params with 
        # additional_params, but here all the variables are immutable.
        merged_params = {**original_params, **additional_params}
        updated_query = urlencode(merged_params, doseq=True)
        # _replace() is how you can create a new NamedTuple with a changed field
        return url_components._replace(query=updated_query).geturl()

    def get_paramters_example(self, path, action, paramters_def):
        paramters = {}
        body = None
        for _, param_info in paramters_def.items():
            p_in = param_info['in']
            p_name = param_info['name']

            if p_in not in self.PARAM_IN_ALL:
                print('not supported in {0}'.format(p_in))
                continue
            #body参数
            if p_in not in self.PARAM_IN_URL:
                body = self.parser.get_send_request_correct_body(path, action)
                continue

            p_type = param_info['type']
            if p_type not in self.PARAM_TYPES:
                print('not supported type {0}'.format(p_type))
                continue 
            paramters[p_name] = self.PARAM_TYPE_DEFAULT[p_type]

            #将路径参数中的名称替换
            if p_in == 'path' and p_name in self.PARAM_IN_PATH_DEFAULT:
                paramters[p_name] = self.PARAM_IN_PATH_DEFAULT[p_name]

        return (paramters, body)

    def get_api_data(self, oper, sign):
        api_data = {}
        path = sign[0]
        action = sign[1]

        api_data[oper] = {'sign': sign}
        api_detail = {}
        api_data[oper]['detail'] = api_detail

        paramters_def = self.parser.paths[path][action]['parameters']
        (paramters, body) = self.get_paramters_example(path, action, paramters_def)
        if paramters:
            api_detail['url_with_params'] = Swagger.merge_url_query_params(path, paramters)
        else:
            api_detail['url_with_params'] = path
        
        api_detail['simple_resp'] = None
        resp_data = self.parser.get_request_data(path, action)
        if 200 in resp_data:
            r = resp_data[200]
            if isinstance(r, dict):
                api_detail['simple_resp'] = {}
            elif isinstance(r, list):
                api_detail['simple_resp'] = []

        api_detail['body'] = body
        return api_data

    def parse(self):
        api_data = {}
        for oper, sign in self.parser.operation.items():
            api_data.update(self.get_api_data(oper, sign))
        return api_data