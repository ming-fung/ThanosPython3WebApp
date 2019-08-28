# 用于部署到服务器时，修改数据库的host等信息，覆盖'config_default.py'中的配置
# 简单来说，就是生产环境的标准配置
configs = {
    'db' : {
        # 'host' : '172.16.128.75'
        'host':'127.0.0.1'
    }
}
