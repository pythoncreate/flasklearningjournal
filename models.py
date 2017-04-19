import datetime
from slugify import slugify
from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('jornl.db')


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    def get_posts(self):
        return Post.select().where(
            (Post.user == self)
        )

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")


class Post(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(
        rel_model=User,
        related_name='posts'
    )
    title = TextField()
    timespent = TextField()
    learned = TextField()
    resources = TextField()
    slug = TextField()

    def __init__(self, *args, **kwargs):
        if 'slug' not in kwargs:
            kwargs['slug'] = slugify(kwargs.get('title', ''))
        super().__init__(*args, **kwargs)

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)

def initialize():
    DATABASE.get_conn()
    DATABASE.create_tables([User, Post], safe=True)
    DATABASE.close()