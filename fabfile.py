# fabfile.py
# 实现自动化部署
# http://www.fabfile.org/

import os, re
from datetime import datetime

######## fabric v2 实现 ########
#使用教程 https://my.oschina.net/yves175/blog/1919714
#https://blog.csdn.net/th_num/article/details/84143473

from fabric import Connection, task, Config

host = '47.107.133.95' # 默认测试服
port = 22
user = 'mingfung'
password = '1014'
key_filename = "/Users/milknero/.ssh/id_rsa.key"

#### 远端拉Git ####

app_path = '/srv/thanos'

def update_config(connect):
    run_host = connect.host if connect.host.split('.').__len__() == 4 else host
    conf = {
        'host': run_host,
        'user': user,
        'port': port,
        'connect_kwargs': {'password':password, "key_filename":key_filename}
    }
    for k, v in conf.items():
        if hasattr(connect, k):
            setattr(connect, k, v)


# 同步采取拉取Git仓库的代码，非从本地直接推给服务器
@task
def pull_git_code(connect):
    with update_config(connect) as c:
        with c.cd(os.path.join(app_path, 'generator')): # 拉取到放源码的路径
            c.run('git pull', warn=True, pty=False)

# 重启服务(器)
@task
def restart_generator_svr(connect):
    with update_config(connect) as c:
        with c.cd(os.path.join(app_path, 'deploy')): # 到放编译好的库或发布版的代码的路径
            c.run('./supervisor_ctl.sh restart generator', warn=True, pty=False)
            ret = c.run('./supervisor_ctl.sh status |grep generator', warn=True, pty=False)
            stdout=ret.stdout
            status=stdout.split()
            if status[1] == 'RUNNING':
                print(u'%s重启成功' % status[0])

# 重启所有服务
@task
def restart_all_svr(connect):
    with update_config(connect) as c:
        with c.cd(os.path.join(app_path, 'deploy')):
            c.run('git pull', warn=True, pty=False)
            c.run('./supervisor_ctl.sh restart all', warn=True, pty=False)
            ret = c.run('./supervisor_ctl.sh status', warn=True, pty=False)
            stdout = ret.stdout
            status_list = stdout.split('\n')
            for ca in status_list:
                status = ca.split()
                if not status:
                    continue
                if status[1] == 'RUNNING':
                    print(u'%重启成功' % status[0])
                else:
                    print(u'%s重启失败' % status[0])
                    break

@task
def rsync_db(connect):
    with update_config(connect) as c:
        with c.cd(os.path.join(app_path, 'generator')):
            c.run('workon developgenerator && python manage.py migrate', warn=True, pty=False)

#if __name__ == '__main__':
#    server = Connection(host=host)
#    pull_svr_code(server)
#    restart_generator_svr(server)

# 或 fab -H xxx.xxx.xxx.xxx pull-svr-code restart-generator-svr

#### 本地推远端 ####

# 一切的远程shell命令的执行都是基于Connection来实现的。实现的原理，也就是SSH
# config = Config(overrides={'sudo': {'password': 'Gg992018'}})
c = Connection(host, port=port, user='root', connect_kwargs={'password':'Gg992018'})

result = c.run('uname -s') # 输出系统名

_TAR_FILE = 'dist-thanos.tar.gz'

# 打包源码
@task
def build(ctx):
    includes = ['static', 'templates', 'transwarp', 'favicon.ico', '*.py', 'requirements.txt']
    excludes = ['test', '.*', '*.pyc', '*.pyo']
    # local() 由 fabric所提供来运行本地命令，run()是执行远程的命令
    c.local('rm -f dist/%s' % _TAR_FILE)
    # 更改当前目录
    os.chdir(os.path.join(os.path.abspath('.'), 'www'))
    cmd = ['tar', '--dereference', '-czvf', '../dist/%s' % _TAR_FILE]
    cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
    cmd.extend(includes)
    c.local(' '.join(cmd))

# 使用方式：$ fab build ，在项目目录下（www平级）调用

_REMOTE_TMP_TAR = '/tmp/%s' % _TAR_FILE
_REMOTE_BASE_DIR = '/srv/thanos'

# 发布
@task
def deploy(ctx):

    newdir = 'www-%s' % datetime.now().strftime('%y-%m-%d_%H.%M.%S')

    # 删除已有的tar文件
    c.run('rm -f %s' % _REMOTE_TMP_TAR)
    # 上传新的tar文件
    c.put('dist/%s' % _TAR_FILE, _REMOTE_TMP_TAR)

    # 创建新目录
    with c.cd(_REMOTE_BASE_DIR): # with结构内继承cd的状态，远程路径切换
        c.run("mkdir %s" % newdir)  # 异步执行远端创建文件夹

    # 解压到新目录
    with c.cd("%s/%s" % (_REMOTE_BASE_DIR, newdir)):
        c.run('tar -xzvf %s' % _REMOTE_TMP_TAR)
    # 重置软链接
    with c.cd(_REMOTE_BASE_DIR):
        c.run('rm -f www')
        c.run('ln -s %s www' % newdir)  # 创建替身
        c.run('chown mingfung:mingfung www')  # 指定 www 文件夹（替身）归属mingfung用户及mingfung用户组
        c.run('chown -R mingfung:mingfung %s' % newdir)  # 指文件夹及其子文件的归属用户及用户组
        # 重启Python服务和nginx服务
        c.run('supervisorctl stop thanos')
        c.run('supervisorctl start thanos')
        c.run('/etc/init.d/nginx reload')


######## fabric v1 实现 ########
# 使用教程 https://www.jianshu.com/p/379824a4a35b

# 导入Fabric API
#from fabric.api import *

# 服务器登录用户名
#env.user = 'mingfung'
# sudo用户为root:
#env.sudo_user = 'root'
# 服务器地址，可以有多个，依次部署：
#env.hosts = [']

# 服务器MySQL用户名和口令：
#db_user='mingfung'
#db_password='1014'

#_TAR_FILE = 'dist-awesome.tar.gz'

'''
def build():
    includes = ['static', 'templates', 'transwarp', 'favicon.ico', '*.py']
    excludes = ['test', '.*', '*.pyc', '*.pyo']
    # local() 由 fabric所提供来运行本地命令，run()是执行远程的命令
    local('rm -f dist/%s' % _TAR_FILE)
    # with lcd() 可把当前命令的目录切换到 lcd 指定的目录，cd()是切换远程的目录
    with lcd(os.path.join(os.path.abspath('.'), 'www')):
        cmd = ['tar', '--dereference', '-czvf', '../dist/%s' % _TAR_FILE]
        cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
        cmd.extend(includes)
        local(' '.join(cmd))
'''

#$ fab build ，在项目目录下（www平级）运行来调用
#$ fab --list ， 可查看可执行的函数名

#_REMOTE_TMP_TAR = '/tmp/%s' % _TAR_FILE
#_REMOTE_BASE_DIR = '/srv/awesome'

'''
def deploy():
    newdir = 'www-%s' % datetime.now().strftime('%y-%m-%d_%H.%M.%S')
    # 删除已有的tar文件:
    run('rm -f %s' % _REMOTE_TMP_TAR)
    # 上传新的tar文件:
    put('dist/%s' % _TAR_FILE, _REMOTE_TMP_TAR)
    # 创建新目录:
    with cd(_REMOTE_BASE_DIR):
        sudo('mkdir %s' % newdir)
    # 解压到新目录:
    with cd('%s/%s' % (_REMOTE_BASE_DIR, newdir)):
        sudo('tar -xzvf %s' % _REMOTE_TMP_TAR)
    # 重置软链接:
    with cd(_REMOTE_BASE_DIR):
        sudo('rm -f www')
        sudo('ln -s %s www' % newdir)
        sudo('chown www-data:www-data www')
        sudo('chown -R www-data:www-data %s' % newdir)
    # 重启Python服务和nginx服务器:
    with settings(warn_only=True):
    # 执行Supervisor重启前，需要先在远端配置好Supervisor
    # Supervisor 是一个管理进程工具，可以随系统启动而启动服务，还能时刻监控服务进程，如果服务进程意外退出，Supervisor可自动重启服务。
        sudo('supervisorctl stop awesome')
        sudo('supervisorctl start awesome')
        sudo('/etc/init.d/nginx reload')
'''

'''
def backup():
    # Dump entire database on server and backup to local.
    dt = _now()
    f = 'backup-awesome-%s.sql' % dt
    with cd('/tmp'):
        run('mysqldump --user=%s --password=%s --skip-opt --add-drop-table --default-character-set=utf8 --quick thanos > %s' % (db_user, db_password, f))
        run('tar -czvf %s.tar.gz %s' % (f, f))
        get('%s.tar.gz' % f, '%s/backup/' % _current_path())
        run('rm -f %s' % f)
        run('rm -f %s.tar.gz' % f)
'''

def _current_path():
    return os.path.abspath('.')

def _now():
    return datetime.now().strftime('%y-%m-%d_%H.%M.%S')


'''
RE_FILES = re.compile('\r?\n')

def rollback():
    # rollback to previous version
    with cd(_REMOTE_BASE_DIR):
        r = run('ls -p -1')
        files = [s[:-1] for s in RE_FILES.split(r) if s.startswith('www-') and s.endswith('/')]
        files.sort(cmp=lambda s1, s2: 1 if s1 < s2 else -1)
        r = run('ls -l www')
        ss = r.split(' -> ')
        if len(ss) != 2:
            print ('ERROR: \'www\' is not a symbol link.')
            return
        current = ss[1]
        print ('Found current symbol link points to: %s\n' % current)
        try:
            index = files.index(current)
        except ValueError, e:
            print ('ERROR: symbol link is invalid.')
            return
        if len(files) == index + 1:
            print ('ERROR: already the oldest version.')
        old = files[index + 1]
        print ('==================================================')
        for f in files:
            if f == current:
                print ('      Current ---> %s' % current)
            elif f == old:
                print ('  Rollback to ---> %s' % old)
            else:
                print ('                   %s' % f)
        print ('==================================================')
        print ('')
        yn = raw_input ('continue? y/N ')
        if yn != 'y' and yn != 'Y':
            print ('Rollback cancelled.')
            return
        print ('Start rollback...')
        sudo('rm -f www')
        sudo('ln -s %s www' % old)
        sudo('chown www-data:www-data www')
        with settings(warn_only=True):
            sudo('supervisorctl stop awesome')
            sudo('supervisorctl start awesome')
            sudo('/etc/init.d/nginx reload')
        print ('ROLLBACKED OK.')

def restore2local():
    # Restore db to local
    
    backup_dir = os.path.join(_current_path(), 'backup')
    fs = os.listdir(backup_dir)
    files = [f for f in fs if f.startswith('backup-') and f.endswith('.sql.tar.gz')]
    files.sort(cmp=lambda s1, s2: 1 if s1 < s2 else -1)
    if len(files)==0:
        print 'No backup files found.'
        return
    print ('Found %s backup files:' % len(files))
    print ('==================================================')
    n = 0
    for f in files:
        print ('%s: %s' % (n, f))
        n = n + 1
    print ('==================================================')
    print ('')
    try:
        num = int(raw_input ('Restore file: '))
    except ValueError:
        print ('Invalid file number.')
        return
    restore_file = files[num]
    yn = raw_input('Restore file %s: %s? y/N ' % (num, restore_file))
    if yn != 'y' and yn != 'Y':
        print ('Restore cancelled.')
        return
    print ('Start restore to local database...')
    p = raw_input('Input mysql root password: ')
    sqls = [
        'drop database if exists awesome;',
        'create database awesome;',
        'grant select, insert, update, delete on awesome.* to \'%s\'@\'localhost\' identified by \'%s\';' % (db_user, db_password)
    ]
    for sql in sqls:
        local(r'mysql -uroot -p%s -e "%s"' % (p, sql))
    with lcd(backup_dir):
        local('tar zxvf %s' % restore_file)
    local(r'mysql -uroot -p%s awesome < backup/%s' % (p, restore_file[:-7]))
    with lcd(backup_dir):
        local('rm -f %s' %
'''
