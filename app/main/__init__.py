from flask import Blueprint

main = Blueprint('main', __name__) #创建蓝本


from . import views, errors
from ..models import Permission

@main.app_context_processor
def inject_permission():
    return dict(Permission=Permission)