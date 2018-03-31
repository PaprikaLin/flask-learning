from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from datetime import datetime
from flask import request
import hashlib
from markdown import markdown
import bleach

class Permission:
    FOLLOW = 1               # 0b00000001 关注
    COMMENT = 2              # 0b00000010 评论
    WRITE = 4       # 0b00000100 发文章
    MODERATE = 8    # 0b00001000 修改评论
    ADMINISTER = 16          # 0b10000000 管理员


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMINISTER],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    #
    member_since = db.Column(db.DateTime(), default=datetime.now)
    last_seen = db.Column(db.DateTime(), default=datetime.now)

    avatar_hash = db.Column(db.String(32))

    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # 生成确认修改密码的token，传入实例--也就是用户的主键，用于加密
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    # 重置密码，传入Token之后，
    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        # 尝试解密，不存在则返回False
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        # 解密后Get得用户主键--ID，如果用户不存在则返回False，存在则更新密码
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    # 检测用户是否有指定的权限
    def can(self, permissions):
        #return self.role is not None and (self.role.permissions & permissions) == permissions
        return self.role is not None and self.role.has_permission(permissions)

    def is_admin(self):
        return self.can(Permission.ADMINISTER)

    # 每次收到用户请求时都要调用ping方法
    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)

    def __repr__(self):
        return '<User %r>' % self.username

    # 生成头像
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'https://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


    # 生成虚拟用户和博客文章
    # @staticmethod
    # def generate_fake(count=100):
    #     from sqlalchemy.exc import IntegrityError
    #     from random import seed
    #     import forgery_py
    #
    #     seed()
    #     for i in range(count):
    #         u = User(email=forgery_py.internet.email_address(),
    #                  username=forgery_py.internet.user_name(True),
    #                  password=forgery_py.lorem_ipsum.word(),
    #                  confirmed=True,
    #                  name=forgery_py.name.full_name(),
    #                  location=forgery_py.address.city(),
    #                  about_me=forgery_py.lorem_ipsum.sentence(),
    #                  member_since=forgery_py.date.date(True)
    #                  )
    #     db.session.add(u)
    #     try:
    #         db.session.commit()
    #     except IntegrityError:
    #         db.session.rollback()

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']

        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

# set 事件监听
db.event.listen(Post.body, 'set', Post.on_changed_body)

    # # 生成虚拟文章
    # @staticmethod
    # def generate_fake(count=100):
    #     from random import seed, randint
    #     import forgery_py
    #
    #     seed()
    #     user_count = User.query.count()
    #     for i in range(count):
    #         u = User.query.offset(randint(0, user_count - 1)).first()
    #         p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
    #                  timestamp=forgery_py.date.date(True),
    #                  author=u)
    #     db.session.add(p)
    #     db.session.commit()


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_admin(self):
        return False

login_manager.anonymous_user = AnonymousUser



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
