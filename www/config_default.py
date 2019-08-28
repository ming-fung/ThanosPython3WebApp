# 由于Python本身语法简单，完全可以直接用Python源代码来实现配置，而不需要再解析一个单独的.properties或者.yaml等配置文件
# 简单来说，这就是开发环境的标准配置
configs = {
    'db' : {
        'host' : '127.0.0.1',
        'port' : 3306,
        'user' : 'mingfung',
        'password' : '1014',
        'database' : 'thanos'
    },
    'session' : {
        'secret' : 'AwEsOmE'
    }
}
