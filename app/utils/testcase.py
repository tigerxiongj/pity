from app.utils.swagger import Swagger

from app.schema.testcase_schema import TestCaseAssertsForm, PityTestCaseOutParametersForm, TestCaseForm, TestCaseInfo

def build_test_case_from_swagger(json_string):
    sw_parser = Swagger(json_string)
    api_data = sw_parser.parse()
    if not api_data:
        return None
    
    test_case_info_list = []
    test_case_dict = {
        'priority': 'P0',
        'url': '', #带参数的url
        'name': '', #名称
        'case_type': 0,
        'base_path':'ks_domain',
        'tag': '', #标签
        'body': None, #请求体
        'body_type': 0, #请求体类型，0表示请求体
        'request_headers': '{"Cookie": "token=${CC_TOKEN}"}',
        'request_method': '', #大写的请求方法
        'status': 3,
        'directory_id': 8,
        'request_type': 1,
    }

    for name, v in api_data.items():
        #构造用例主要信息
        tmp_test_case_dict = dict(test_case_dict)
        tmp_test_case_dict['name'] = name
        tmp_test_case_dict['request_method'] = v['sign'][1].upper()
        tmp_test_case_dict['tag'] = v['sign'][2]
        tmp_test_case_dict['url'] = v['detail']['url_with_params']
        body = v['detail']['body']
        simple_resp = v['detail']['simple_resp']
        if body:
            tmp_test_case_dict['body_type'] = 1 #写死json
            tmp_test_case_dict['body'] = body
        test_case_form = TestCaseForm(**tmp_test_case_dict)

        #构造断言
        test_assert_list = [
            {
                "name": 'code', 
                "assert_type": 'equal', 
                "expected": '200', 
                "actually": '${status_code}'
            },
            {
                "name": 'content', 
                "assert_type": 'json_match', 
                "expected": '{}' if isinstance(simple_resp, dict) else '[]', 
                "actually": '${response}'
            },
        ]
        test_asserts = [TestCaseAssertsForm(**a) for a in test_assert_list]

        #构造出参
        test_out_param_dict = {
            "name": 'status_code', 
            "source": 4,
        }
        test_out_params = [PityTestCaseOutParametersForm(**test_out_param_dict)]

        #构造完整用例数据
        test_case_info = TestCaseInfo(case=test_case_form, asserts=test_asserts, out_parameters=test_out_params)
        test_case_info_list.append(test_case_info)

    return test_case_info_list
    
    