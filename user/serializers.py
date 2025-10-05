from rest_framework import serializers
from .models import WechatUser

# 1. 微信登录请求参数序列化器（定义前端需要传什么参数）
class WechatMiniLoginRequestSerializer(serializers.Serializer):
    code = serializers.CharField(
        max_length=100,
        required=True,
        help_text="微信小程序通过 wx.login() 获取的临时登录凭证（有效期5分钟）"
    )
    # userInfo 是可选的嵌套参数，用 DictField 接收
    userInfo = serializers.DictField(
        required=False,
        help_text="微信用户基础信息（可选，包含 nickName、avatarUrl 等）",
        child=serializers.CharField()  # 子字段为字符串类型（适配 nickName、avatarUrl）
    )

# 2. 微信登录响应数据序列化器（定义后端返回什么格式的数据）
class WechatUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WechatUser
        fields = ['id', 'nickname', 'avatar_url', 'openid']  # 返回的用户信息字段
        extra_kwargs = {
            'avatar_url': {'source': 'avatar_url', 'label': '头像URL'},  # 字段别名（适配前端 camelCase 风格）
            'openid': {'read_only': True, 'help_text': '微信用户唯一标识（根据需求决定是否返回）'}
        }

# 3. 最终响应序列化器（包含 token 和 userInfo）
class WechatMiniLoginResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=0, help_text="状态码：0 成功，非0 失败")
    message = serializers.CharField(default="登录成功", help_text="提示信息")
    data = serializers.DictField(
        child=serializers.Field(),
        help_text="响应数据体",
        read_only=True
    )
    # 嵌套用户信息序列化器
    data.userInfo = WechatUserInfoSerializer(read_only=True)
    data.token = serializers.CharField(max_length=100, help_text="自定义登录态 Token（用于后续接口身份验证）")