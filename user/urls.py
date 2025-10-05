from django.urls import path
from .views import WechatMiniLoginView

urlpatterns = [
    # 微信小程序登录接口
    path('wechat/mini/login/', WechatMiniLoginView.as_view(), name='wechat_mini_login'),
]
