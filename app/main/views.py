from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app, flash, abort, request

from .import main # 从同级目录导入，必须存在__init.py 文件
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm # 同级目录的forms.py
from .. import db # 上级目录的__init__.py
from ..models import User, Role, Permission, Post #上级目录的 models.py
from ..email import send_email # 上级目录的email.py
from flask_login import login_required, current_user
from ..decorators import admin_required


# @main.route('/', methods=['GET', 'POST']) # GET和POST的请求方式执行这个函数
# def index():
#     form = NameForm() # 创建表单类NameForm的实例
#     if form.validate_on_submit(): # 如果submit按钮被点击
#         # 在数据库的username列里面和表单数据一样的数据，如果有，取第一个值
#         user = User.query.filter_by(username=form.name.data).first()
#         if user is None: # 如果没有找到
#             user = User(username=form.name.data) # 创建User类的实例，初始化username等于表单数据的值
#             db.session.add(user) # 加入到用户会话，以便数据库提交
#             session['known'] = False # 添加session字典 'known'键的值为False，表示是新用户
#             if current_app.config['FLASKY_ADMIN']: # 如果收件人已经定义，则发送电子邮件
#                 # send_email的参数依次为：发件人，标题，模板的路径，用户名
#                 send_email(current_app.config['FLASKY_ADMIN'], 'New User',
#                            'mail/new_user', user=user)
#                 flash('The mail has been sent out.')
#         else:
#             session['known'] = True # 老用户
#         session['name'] = form.name.data #存储提交的数据
#         form.name.data = "" # 清空表单
#         return redirect(url_for('.index')) # 重定向到index页
#     return render_template('index.html', current_time=datetime.utcnow(), form=form, name=session.get('name'),
#                            known=session.get('known', False))
@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object()) # 11章「博客文章」有说明，获取真正的用户对象
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/edit-profile', methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash("Your profile has been updated.")
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


