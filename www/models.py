
import time, uuid
from orm import Model
from orm import StringField, IntegerField, BooleanField, FloatField, TextField
# import orm
# mysql -u root -p < schema.sql 执行SQL脚本创建表

def next_id():
	return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
	__table__ = 'users'

	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	email = StringField(ddl='varchar(50)')
	passwd = StringField(ddl='varchar(50)')
	admin = BooleanField()
	name = StringField(ddl='varchar(50)')
	image = StringField(ddl='varchar(500)')
	created_at = FloatField(default=time.time)

class Blog(Model):
	__table__ = 'blogs'

	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	user_id = StringField(ddl='varchar(50)')
	user_name = StringField(ddl='varchar(50)')
	user_image = StringField(ddl='varchar(500)')
	name = StringField(ddl='varchar(50)')
	summary = StringField(ddl='varchar(200)')
	content = TextField()
	created_at = FloatField(default=time.time)

class Comment(Model):
	__table__ = 'comments'

	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	blog_id = StringField(ddl='varchar(50)')
	user_id = StringField(ddl='varchar(50)')
	user_name = StringField(ddl='varchar(50)')
	user_image = StringField(ddl='varchar(500)')
	content = TextField()
	created_at = FloatField(default=time.time)

# 以上为类属性，对象属性需要在__init__()中指定和初始化

async def test():
	await orm.create_pool(user='mingfung', password='1014', database='thanos')

	u = User(name='Test', email='test@example.com', passwd='1234567890', image='about:blank')

	await u.save()

if __name__ == '__main__':
	# 创建实例:
	user = User(id=123, name='Michael')
	# 存入数据库:
	user.insert()
	# 查询所有User对象:
	users = User.findAll()

	user['id']
	user.id
	# user = yield from User.find('123')
	# user = User(id=123, name='Michael')
	# yield from user.save()

	for x in test():
		pass





