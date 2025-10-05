# 导入Django的模型模块和时间工具
from django.db import models
from django.utils import timezone


# 用户表
class WechatUser(models.Model):
    """
    微信用户信息表
    用于存储通过微信一键登录的用户信息，与微信开放平台数据同步
    """

    # 微信开放平台唯一标识
    # openid是微信用户在当前应用中的唯一标识，不同应用间openid不同
    # max_length=100：根据微信文档，openid长度不超过100字符
    # unique=True：确保openid在数据库中唯一，避免重复用户
    # verbose_name：在Django Admin后台显示的字段名称
    openid = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="微信OpenID"
    )

    # 微信联合登录标识（多平台统一）
    # unionid是微信用户在同一开放平台下所有应用中的唯一标识
    # 用于实现同一用户在不同应用间的身份互通
    # blank=True, null=True：允许为空（部分用户可能没有unionid）
    # unique=True：确保unionid唯一（如果存在）
    unionid = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        verbose_name="微信UnionID"
    )

    # 用户基本信息
    # 微信昵称，可能包含特殊字符，长度限制为100
    nickname = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="昵称"
    )

    # 微信头像的URL地址，微信返回的头像链接有效期较长
    # 使用URLField自动验证URL格式合法性
    avatar_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="头像URL"
    )

    # 账号状态信息
    # 标记用户账号是否激活（可用），默认值为True
    # 用于实现账号禁用功能，比直接删除数据更安全
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否激活"
    )

    # 记录用户最后一次登录时间
    # auto_now=True：每次用户登录时自动更新为当前时间
    last_login = models.DateTimeField(
        auto_now=True,
        verbose_name="最后登录时间"
    )

    # 记录用户账号创建时间（首次登录时间）
    # default=timezone.now：默认值为记录创建时的时间
    # 注意这里不要加括号，否则会变成固定时间（服务器启动时间）
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name="创建时间"
    )

    # 模型元数据配置
    class Meta:
        # 在Admin后台显示的模型名称（单数）
        verbose_name = "微信用户"
        # 在Admin后台显示的模型名称（复数）
        verbose_name_plural = "微信用户"
        # 默认排序方式：按最后登录时间倒序（最新登录的用户排在前面）
        ordering = ['-last_login']

    # 定义模型实例的字符串表示
    def __str__(self):
        # 优先显示昵称，若昵称为空则显示openid
        return self.nickname or self.openid
