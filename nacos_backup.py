from urllib3 import PoolManager
import os.path
import json
from urllib.parse import urlencode

http = PoolManager()


class Api:

    def __init__(self, username: str, password: str, domain: str = 'nacos-headless.paas-middleware:8848'):
        self.domain = domain
        self.access_token = None
        token = self.login(username, password)
        if token:
            self.access_token = token

        if not self.access_token:
            exit()

    def login(self, username: str, password: str) -> str:
        """
        login
        :param username:
        :param password:
        :return:
        """
        r = http.request(
            'POST',
            url=f'http://{self.domain}/nacos/v1/auth/users/login',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body=urlencode({
                'username': username,
                'password': password
            })

        )
        resp_data = r.data.decode('utf-8')
        r_json = json.loads(resp_data)
        if r.status == 200 and 'accessToken' in r_json:
            return r_json['accessToken']
        print('login failed!')
        return ''

    def get_all_namespaces(self) -> list:
        r = http.request(
            'GET',
            url=f'http://{self.domain}/nacos/v1/console/namespaces?accessToken={self.access_token}',
        )
        resp_data = r.data.decode('utf-8')
        r_json = json.loads(resp_data)
        if r.status == 200 and 'code' in r_json and r_json['code'] == 200:
            return r_json['data']

        return []

    def get_config_item_by_namespace(self, namespace) -> list:
        params = {
            'dataId': '',
            'group': '',
            # 'appName': '',
            # 'config_tags': '',
            'pageNo': 1,
            'pageSize': 100,
            'tenant': f'{namespace}',
            'search': 'accurate',
            # 'username': 'nacos',
            'accessToken': self.access_token,
        }
        r = http.request(
            'GET',
            url=f'http://{self.domain}/nacos/v1/cs/configs?'+urlencode(params),
        )
        resp_data = r.data.decode('utf-8')
        r_json = json.loads(resp_data)
        if r.status == 200 and 'pageItems' in r_json:
            return r_json['pageItems']
        return []


def backup(sys_argv):
    NACOS_DOMAIN = sys_argv.host
    NACOS_USERNAME = sys_argv.username
    NACOS_PASSWORD = sys_argv.password
    BACKUP_PATH = sys_argv.directory

    api = Api(username=NACOS_USERNAME, password=NACOS_PASSWORD, domain=NACOS_DOMAIN)
    ns_list = api.get_all_namespaces()
    if not os.path.isdir(BACKUP_PATH):
        os.makedirs(BACKUP_PATH)
    fd = open(BACKUP_PATH + '/restore_cmd.txt', 'w+')
    for ns in ns_list:
        _namespace = ns['namespace']
        ns_show = ns['namespaceShowName']
        s = f'nacosctl ns create -n {ns_show}'
        if ns_show != _namespace and _namespace:
            s = s + f' --ns-id {_namespace}\n'
        else:
            s = s + '\n'
        fd.write(s)
        if not os.path.isdir(f'{BACKUP_PATH}/{ns_show}'):
            os.mkdir(f'{BACKUP_PATH}/{ns_show}')

        config_item_list = api.get_config_item_by_namespace(_namespace)

        for ci in config_item_list:
            _content = ci['content']
            _data_id = ci['dataId']
            _group = ci['group']
            if not os.path.isdir(f'{BACKUP_PATH}/{ns_show}/{_group}'):
                os.mkdir(f'{BACKUP_PATH}/{ns_show}/{_group}')

            with open(f'{BACKUP_PATH}/{ns_show}/{_group}/{_data_id}', 'w+') as fp:
                fp.write(_content)
                print(f'备份{ns_show}名称空间下{_data_id}成功，备份位置{BACKUP_PATH}/{ns_show}/{_group}/{_data_id}')
            fd.write(
                f'nacosctl cfg upload -n {_namespace if _namespace else ns_show} -g {_group} -f ./{ns_show}/{_group}/{_data_id}\n')

    fd.close()
