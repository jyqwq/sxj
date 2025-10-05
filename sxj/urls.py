from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# 1. 初始化文档视图
schema_view = get_schema_view(
    # 文档元信息：标题、版本、描述
    openapi.Info(
        title="拾像集接口文档",  # 文档标题
        default_version='v1',          # 接口版本
        description="拾像集的详细文档，包含请求参数、响应格式、错误码说明等",  # 接口描述
    ),
    public=True,  # 是否公开文档（True 表示无需登录即可访问）
    permission_classes=(permissions.AllowAny,),  # 访问权限（允许所有用户）
)

# 2. 配置路由
urlpatterns = [
    path('admin/', admin.site.urls),
    # 3. 添加文档路由（两种风格：Swagger UI 和 ReDoc）
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger 风格
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),          # ReDoc 风格（更简洁）
    path('user/', include('user.urls')),
]