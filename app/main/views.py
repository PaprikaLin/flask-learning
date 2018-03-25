from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app, flash, abort

from .import main # 从同级目录导入，必须存在__init.py 文件
from .forms import NameForm # 同级目录的forms.py
from .. import db # 上级目录的__init__.py
from ..models import User #上级目录的 models.py
from ..email import send_email # 上级目录的email.py


@main.route('/', methods=['GET', 'POST']) # GET和POST的请求方式执行这个函数
def index():
    form = NameForm() # 创建表单类NameForm的实例
    if form.validate_on_submit(): # 如果submit按钮被点击
        # 在数据库的username列里面和表单数据一样的数据，如果有，取第一个值
        user = User.query.filter_by(username=form.name.data).first()
        if user is None: # 如果没有找到
            user = User(username=form.name.data) # 创建User类的实例，初始化username等于表单数据的值
            db.session.add(user) # 加入到用户会话，以便数据库提交
            session['known'] = False # 添加session字典 'known'键的值为False，表示是新用户
            if current_app.config['FLASKY_ADMIN']: # 如果收件人已经定义，则发送电子邮件
                # send_email的参数依次为：发件人，标题，模板的路径，用户名
                send_email(current_app.config['FLASKY_ADMIN'], 'New User',
                           'mail/new_user', user=user)
                flash('The mail has been sent out.')
        else:
            session['known'] = True # 老用户
        session['name'] = form.name.data #存储提交的数据
        form.name.data = "" # 清空表单
        return redirect(url_for('.index')) # 重定向到index页
    return render_template('index.html', current_time=datetime.utcnow(), form=form, name=session.get('name'),
                           known=session.get('known', False))


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)
