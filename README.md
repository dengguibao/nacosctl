# nacosctl  

## usage:  

nacosctl user login -u nacos -p  'Nacos!@#123'
使用指定的用户名密码登陆nacos， 有效时间3小时
默认域名http://nacos-headless.paas-middleware:8848如果有变化可以通过--host参数自定义

nacosctl ns create -n abcd
创建名称空间abcd

nacosctl ns create -n abcd --ns-id     aaaa-bbbb-cccc-ddd-eeee
创建名称空间abcd，且自定义名称空间id为 aaaa-bbbb-cccc-ddd-eeee

nacosctl ns list
列出所有名称空间

nacosctl ns delete -n abcd
删除名称空间abcd

nacosctl ns backup -u nacos -p 'Nacos!@#123'
备份所有名称空间及配置
参数--host默认为        nacos-headless.paas-middleware:8443
参数--directory默认为   /backup/nacos（目录不存在会自动创建目录，但是需要有相应的权限）
如果需要自定义，可以通过参数自定义

nacosctl  cfg list -n paas-ms
查看paas-ms名称空间下面所有配置

nacosctl cfg view -n paas-portal -g paas-portal -d portal-config
查看paas-portal名称空间下group为paas-portal data-id为portal-config的配置文件

nacosctl cfg delete -n paas-portal -g paas-portal -d portal-config
删除paas-portal名称空间下group为paas-portal data-id为portal-config的配置文件


nacosctl cfg upload -n paas-portal -g paas-portal -f ./portal-config
上传当前目录下portal-config配置，至paas-portal名称空间下，group为paas-portal

nacosctl cfg import -n paas-portal -f ./xxxx.zip
上传xxxx.zip至paas-portal名称空间下
