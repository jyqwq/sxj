# sjx_background

## 运行项目
`python manage.py runserver`

## 生成requirements.txt文件
`pip freeze > requirements.txt`
## 安装依赖
`pip install -r requriements.txt`

## 生成新应用
`python manage.py startapp appname`

## 更新数据库模型
### 生成迁移文件
`python manage.py makemigrations`
### 执行迁移文件
`python manage.py migrate`

## 生成Django管理员
`python manage.py createsuperuser`
