import argparse
import sys

from nacos_ctl import NacosApi
from nacos_backup import backup


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    nctl = NacosApi()

    parser = argparse.ArgumentParser(description='nacosctl')
    parser.add_argument('--version', '-V',action='version', version='0.1.3', help='print version')
    subparser = parser.add_subparsers()

    ns_parser = subparser.add_parser('namespace', aliases=['ns'], help='namespace')
    config_parser = subparser.add_parser('config', aliases=['cfg'], help='config')
    user_parser = subparser.add_parser('user', help='user')

    # 名称空间菜单
    ns_subparser = ns_parser.add_subparsers()
    list_ns_parser = ns_subparser.add_parser('list', help='list namespaces')
    create_ns_parser = ns_subparser.add_parser('create', help='create namespace')
    delete_ns_parser = ns_subparser.add_parser('delete', help='delete namespace')
    backup_ns_parser = ns_subparser.add_parser('backup', help='backup all config of the namespace')
    # 备份名称空间菜单对应的参数
    backup_ns_parser.add_argument('--username', '-u', required=True, type=str, help='username of nacos')
    backup_ns_parser.add_argument('--password', '-p', required=True, type=str, help='password of nacos')
    backup_ns_parser.add_argument(
        '--host', required=False, type=str,
        default='nacos-headless.paas-middleware:8848',
        help='domain of nacos, default nacos-headless.paas-middleware:8848'
    )
    backup_ns_parser.add_argument(
        '--directory',
        default='/backup/nacos',
        required=False, type=str,
        help='the directory of backup'
    )
    backup_ns_parser.set_defaults(func=backup)

    create_ns_parser.add_argument('--ns-id', help='custom namespace id', required=False, type=str)
    # 名称空间菜单绑定处理方法
    create_ns_parser.set_defaults(func=nctl.create_ns)
    delete_ns_parser.set_defaults(func=nctl.delete_ns)
    list_ns_parser.set_defaults(func=nctl.list_ns)
    for _ns_ in [create_ns_parser, delete_ns_parser]:
        _ns_.add_argument('--namespace', '-n', required=True, type=str, help='the name of namespace')
    # -------------------
    # 用户菜单
    user_subparser = user_parser.add_subparsers()
    login_parser = user_subparser.add_parser('login', help='login using the specified username and password')
    login_parser.add_argument('--username', '-u', required=True, type=str, help='nacos username')
    login_parser.add_argument('--password', '-p', required=True, type=str, help='nacos password')
    login_parser.add_argument(
        '--host',
        default='http://nacos-headless.paas-middleware:8848',
        help='nacos host, default=http://nacos-headless.paas-middleware:8848'
    )
    # 用户菜单绑定处理方法
    change_pwd_parser = user_subparser.add_parser('chpwd',  help='change password for user')
    change_pwd_parser.add_argument('--new-pwd', required=True, type=str, help='new password')
    login_parser.set_defaults(func=nctl.login)
    change_pwd_parser.set_defaults(func=nctl.change_pwd)

    # --------------------
    # 配置项目菜单
    cfg_sub_parser = config_parser.add_subparsers()
    list_config_parser = cfg_sub_parser.add_parser('list', help='list all config item for namespace')
    upload_config_parser = cfg_sub_parser.add_parser('upload', help='upload config file to namespace(overwrite)')
    delete_config_parser = cfg_sub_parser.add_parser('delete',
                                                     help='delete specified configuration items from namespace')
    view_config_parser = cfg_sub_parser.add_parser('view', help='view specified configuration item from namespace')
    import_config_parser = cfg_sub_parser.add_parser('import', help='import zip compress package to namespace')
    # 为配置菜单绑定处理方法
    list_config_parser.set_defaults(func=nctl.list_config_item)
    upload_config_parser.set_defaults(func=nctl.upload_config_to_ns)
    delete_config_parser.set_defaults(func=nctl.delete_config)
    import_config_parser.set_defaults(func=nctl.import_config_to_ns)
    view_config_parser.set_defaults(func=nctl.show_config_content)

    # 查看配置也删除配置需要data-id
    for _m_ in [view_config_parser, delete_config_parser]:
        _m_.add_argument('--data-id', '-d', required=True, type=str, help='data id for configuration item')

    # 查看配置、删除配置、上传配置需要group
    for _m_ in [upload_config_parser, delete_config_parser, view_config_parser]:
        _m_.add_argument('--group', '-g', required=True, type=str, help='group name')

    # 上传、导入、查看、列出、删除都需要ns
    for _m_ in [
        list_config_parser, upload_config_parser,
        import_config_parser, view_config_parser, delete_config_parser
    ]:
        _m_.add_argument('--namespace', '-n', required=True, type=str, help='the name of namespace')
    # 上传、导入需要指定文件名
    for _m_ in [upload_config_parser, import_config_parser]:
        _m_.add_argument('--file-name', '-f', required=True, type=str, help='config file')

    if len(sys.argv) == 1:
        sys.argv.append('-h')

    if 'help' in sys.argv:
        h_index = sys.argv.index('help')
        sys.argv[h_index] = '-h'

    args = parser.parse_args()
    args.func(args)



