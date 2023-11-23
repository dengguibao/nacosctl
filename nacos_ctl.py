#!/usr/bin/python3
import json
import sys
import os
from urllib3 import PoolManager, encode_multipart_formdata
from configparser import ConfigParser
from urllib.parse import urlencode

# 获取用户目录
user_dir = os.path.expanduser('~')
filename = '.nacos/config.cfg'
cfg_file_path = os.path.join(user_dir, filename)
cp = ConfigParser()
OPTIONS = {}

# 检测文件是否存在
if os.path.isfile(cfg_file_path):
    cp.read(cfg_file_path, encoding='utf-8')
    if cp.has_section('nacos'):
        for op in cp.options('nacos'):
            if op in ['token', 'username', 'host']:
                OPTIONS[op] = cp.get('nacos', op)

# 创建一个连接池
http = PoolManager()


class NacosApi:

    def __init__(self):
        self.domain = OPTIONS['host'] if OPTIONS and 'host' in OPTIONS else None
        self.token = OPTIONS['token'] if OPTIONS and 'token' in OPTIONS else None
        self.username = OPTIONS['username'] if OPTIONS and 'username' in OPTIONS else None
        self.headers = {
            'json': {
                'Content-Type': 'application/json'
            },
            'urlencode': {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        }

    def verify_is_login(self):
        if not self.token:
            print('not login')
            sys.exit()

    @staticmethod
    def write_config_to_file(data: dict):
        if not os.path.isdir(user_dir + '/.nacos'):
            os.makedirs(user_dir + '/.nacos')
        fd = open(cfg_file_path, 'w+', encoding='utf-8')
        for s in data:
            if not cp.has_section(s):
                cp.add_section(s)
            for n in data[s]:
                cp.set(s, n, data[s][n])
        cp.write(fd)
        fd.close()

    @staticmethod
    def __init_kwargs__(sys_argv):
        data = vars(sys_argv)
        if 'namespace' in data:
            data['ns'] = data['namespace']
            del data['namespace']
        del data['func']
        # print(data)
        return data

    def login(self, sys_args):
        kwargs = self.__init_kwargs__(sys_args)
        self.__login(**kwargs)

    def create_ns(self, sys_args):
        kwargs = self.__init_kwargs__(sys_args)
        self.__create_ns(**kwargs)

    def list_ns(self, sys_args):
        self.__list_ns()

    def list_config_item(self, sys_args):
        kwargs = self.__init_kwargs__(sys_args)
        self.__list_config_item(**kwargs)

    def show_config_item(self, sys_args):
        kwargs = self.__init_kwargs__(sys_args)
        self.__show_config_content(**kwargs)

    def delete_config(self, sys_args):
        kwargs = self.__init_kwargs__(sys_args)
        self.__delete_config(**kwargs)

    def delete_ns(self, sys_args):
        kwargs = self.__init_kwargs__(sys_args)
        self.__delete_ns(**kwargs)

    def import_config_to_ns(self, sys_args):
        kwargs = self.__init_kwargs__(sys_args)
        self.__import_config_to_ns(**kwargs)

    def upload_config_to_ns(self, sys_args):
        kwargs = self.__init_kwargs__(sys_args)
        self.__upload_config_to_ns(**kwargs)

    def show_config_content(self, sys_args):
        kwargs = self.__init_kwargs__(sys_args)
        self.__show_config_content(**kwargs)

    def change_pwd(self, sys_args):
        kwargs = self.__init_kwargs__(sys_args)
        self.__change_pwd(**kwargs)

    @staticmethod
    def process_response(request):
        if request.status == 200:
            resp_data = request.data.decode('utf-8').strip()
            if 'text/plain' in request.headers.get('Content-Type'):
                print(resp_data)
                sys.exit(0)
            if resp_data.lower() in ['true', 'false']:
                if resp_data == 'true':
                    print('success')
                    sys.exit(0)
                else:
                    print('failed!')
                    sys.exit(1)
            if resp_data.startswith('{') and resp_data.endswith('}'):
                json_obj = json.loads(resp_data)
                # if json_obj['code'] != 200:
                #     print(json_obj)
                if 'message' in json_obj:
                    print(json_obj['message'])

                if 'data' in json_obj:
                    return json_obj['data']
                if 'pageItems' in json_obj:
                    return json_obj['pageItems']

        # print('request failed!')

    def __login(self, username, password, host):
        if host:
            self.domain = 'http://' + host if not host.startswith('http://') else host
        if not host and not self.domain:
            print('please specified host args')
            sys.exit(1)
        url = f'{self.domain}/nacos/v1/auth/users/login'
        data = {
            'host': self.domain,
            'username': username,
            'password': password
        }
        req = http.request('POST', url=url, body=urlencode(data), headers=self.headers['urlencode'])
        if req.status == 200:
            resp_json = json.loads(req.data.decode('utf-8'))
            if 'accessToken' in resp_json:
                print('login success')
                self.token = resp_json['accessToken']
                self.username = username
                cfg_data = {
                    'nacos': {
                        'username': username,
                        'token': self.token,
                        'host': self.domain
                    }
                }
                self.write_config_to_file(cfg_data)
            else:
                print('login failed')

    def __create_ns(self, ns, ns_id):
        """

        :param ns: the name of namespace
        :param ns_id: custom namespace id
        :return:
        """
        self.verify_is_login()
        url = f'{self.domain}/nacos/v1/console/namespaces?&accessToken={self.token}'
        data = {
            'customNamespaceId': ns_id if ns_id else ns,
            'namespaceName': ns,
            'namespaceDesc': ns
        }
        req = http.request('POST', url=url, body=urlencode(data), headers=self.headers['urlencode'])
        self.process_response(req)

    def __list_ns(self):
        self.verify_is_login()
        url = f'{self.domain}/nacos/v1/console/namespaces?&accessToken=${self.token}'
        req = http.request('GET', url=url)
        resp_data = self.process_response(req)
        print(f'{"namespace".center(32)}\t{"namespaceShowName".center(32)}')
        print(f'{"-" * 90}')
        for i in resp_data:
            print(f'namespace: {i["namespace"].ljust(32)}\tnamespaceShowName:{i["namespaceShowName"].ljust(32)}')

    def __list_config_item(self, ns: str):
        self.verify_is_login()
        url = f'{self.domain}/nacos/v1/cs/configs?'
        params = {
            'dataId': '',
            'appName': '',
            'config_tags': '',
            'group': '',
            'pageNo': 1,
            'pageSize': 100,
            'tenant': ns,
            'search': 'accurate',
            'accessToken': self.token,
            'username': self.username
        }
        # print(url+urlencode(params))
        req = http.request('GET', url=url + urlencode(params))
        resp_data = self.process_response(req)
        print(f'{"data-id".center(40)}\t{"group".center(20)}')
        print(f'{"-" * 90}')
        for i in resp_data:
            print(f'data-id: {i["dataId"].ljust(40)}\tgroup: {i["group"].ljust(20)}')

    def __show_config_content(self, ns: str, group: str, data_id: str):
        self.verify_is_login()
        url = f'{self.domain}/nacos/v1/cs/configs?'
        params = {
            'dataId': data_id,
            'group': group,
            'tenant': ns,
            'accessToken': self.token
        }
        req = http.request('GET', url + urlencode(params))
        self.process_response(req)

    def __delete_config(self, ns: str, group: str, data_id: str):
        self.verify_is_login()
        url = f'{self.domain}/nacos/v1/cs/configs?'
        params = {
            'dataId': data_id,
            'group': group,
            'tenant': ns,
            'accessToken': self.token
        }
        req = http.request('DELETE', url + urlencode(params))
        self.process_response(req)

    def __delete_ns(self, ns: str):
        self.verify_is_login()
        url = f'{self.domain}/nacos/v1/console/namespaces?namespaceId={ns}&accessToken={self.token}'
        req = http.request('DELETE', url)
        self.process_response(req)

    def __import_config_to_ns(self, ns: str, file_name: str):
        # self.verify_is_login()
        url = f'{self.domain}/nacos/v1/cs/configs?'
        params = {
            'username': self.username,
            'namespace': ns,
            'accessToken': self.token,
            # 'dataId': '',
            'import': 'true',
            # 'tenant': ns,
        }
        if not os.path.isfile(file_name):
            print('config file not found')
            sys.exit(404)
        if not os.access(file_name, os.R_OK):
            print('read compress package failed, permission denied')
            sys.exit(1)

        fd = open(file_name, 'rb')
        file_data = fd.read()
        fd.close()

        body, header = encode_multipart_formdata(
            fields={
                'file': (file_name.split('/')[-1], file_data)
            }
        )

        req = http.request(
            'POST',
            url=url + urlencode(params),
            headers={
                'Content-Type': header,
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': '*/*'
            },
            body=body
        )
        self.process_response(req)

    def __upload_config_to_ns(self, ns: str, group: str, file_name: str):
        self.verify_is_login()
        url = f'{self.domain}/nacos/v1/cs/configs'
        if not os.path.isfile(file_name):
            print('config file not found')
            sys.exit(1)
        if not os.access(file_name, os.R_OK):
            print('read config file failed, permission denied')
            sys.exit(1)

        fd = open(file_name, 'r')
        content = fd.read()
        fd.close()
        post_data = {
            'tenant': ns,
            'group': group,
            'dataId': file_name.split('/')[-1],
            'accessToken': self.token,
            'content': content
            # tenant =${ns} & accessToken =${token} & dataId =${data_id} & group =${group}
        }
        req = http.request('POST', url=url, body=urlencode(post_data), headers=self.headers['urlencode'])
        self.process_response(req)

    def __change_pwd(self, username, new_pwd):
        self.verify_is_login()
        url = f'{self.domain}/nacos/v1/auth/users?accessToken=${self.token}'
        post_data = {
            'username': username,
            'newPassword': new_pwd
        }
        req = http.request('PUT', url=url, body=urlencode(post_data), headers=self.headers['urlencode'])
        self.process_response(req)
