import json
import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView  # 替换原来的 View，使用 DRF 的 APIView（支持序列化器和装饰器）
from rest_framework.permissions import AllowAny  # 允许所有用户访问（登录接口无需认证）
from drf_yasg.utils import swagger_auto_schema  # 文档装饰器
from .models import WechatUser
from .serializers import (
    WechatMiniLoginRequestSerializer,
    WechatMiniLoginResponseSerializer
)

class WechatMiniLoginView(APIView):
    """
    微信小程序登录接口
    功能：接收前端传递的 code，调用微信接口获取 openid，保存/更新用户信息，返回 Token 和用户信息
    适用场景：小程序用户首次登录、重新登录
    """
    permission_classes = [AllowAny]  # 登录接口无需认证（所有人可访问）

    # 关键：添加文档装饰器，指定请求/响应序列化器
    @swagger_auto_schema(
        request_body=WechatMiniLoginRequestSerializer,  # 请求参数格式
        responses={
            200: WechatMiniLoginResponseSerializer,  # 成功响应格式
            400: "请求参数错误（如缺少 code、JSON 格式错误）",
            500: "服务器错误（如微信接口调用失败、数据库异常）"
        },
        operation_summary="微信小程序用户登录",  # 接口标题（文档中显示）
        operation_description="""
        详细流程：
        1. 前端调用 wx.login() 获取 code，调用 wx.getUserProfile() 获取 userInfo（可选）
        2. 前端将 code 和 userInfo 以 JSON 格式 POST 到本接口
        3. 后端通过 code 调用微信 jscode2session 接口获取 openid 和 session_key
        4. 后端根据 openid 查找/创建用户，更新 userInfo（如昵称、头像）
        5. 后端生成 Token，返回 Token 和用户基础信息
        """,  # 接口详细描述
        tags=["微信登录相关"]  # 文档分类标签（便于归类）
    )
    def post(self, request):
        try:
            # 1. 使用序列化器验证请求参数（替代原来的 json.loads 手动解析）
            serializer = WechatMiniLoginRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return JsonResponse({
                    'code': 400,
                    'message': '请求参数错误',
                    'errors': serializer.errors  # 返回具体的错误信息（如 code 缺失）
                })
            # 从序列化器中获取验证后的参数
            code = serializer.validated_data['code']
            user_info = serializer.validated_data.get('userInfo', {})

            # 2. 调用微信 jscode2session 接口获取 openid
            login_url = 'https://api.weixin.qq.com/sns/jscode2session'
            params = {
                'appid': settings.WECHAT_MINI_APPID,
                'secret': settings.WECHAT_MINI_APPSECRET,
                'js_code': code,
                'grant_type': 'authorization_code'
            }
            response = requests.get(login_url, params=params)
            result = response.json()

            # 3. 处理微信接口错误
            if 'errcode' in result and result['errcode'] != 0:
                return JsonResponse({
                    'code': result['errcode'],
                    'message': f'微信接口调用失败：{result.get("errmsg", "未知错误")}'
                })

            # 4. 提取 openid、unionid
            openid = result.get('openid')
            unionid = result.get('unionid')
            if not openid:
                return JsonResponse({'code': 500, 'message': '获取 openid 失败'})

            # 5. 保存/更新用户信息
            user, created = WechatUser.objects.update_or_create(
                openid=openid,
                defaults={
                    'unionid': unionid,
                    'nickname': user_info.get('nickName'),
                    'avatar_url': user_info.get('avatarUrl'),
                }
            )

            # 6. 生成 Token（实际项目建议用 JWT，这里简化处理）
            login_token = f"{user.id}:{openid[:8]}"

            # 7. 返回成功响应（格式与序列化器一致）
            return JsonResponse({
                'code': 0,
                'message': '登录成功',
                'data': {
                    'token': login_token,
                    'userInfo': {
                        'id': user.id,
                        'nickname': user.nickname,
                        'avatarUrl': user.avatar_url,
                        'openid': openid
                    }
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({'code': 400, 'message': '请求数据格式错误，应为 JSON'})
        except Exception as e:
            return JsonResponse({'code': 500, 'message': f'服务器错误：{str(e)}'})