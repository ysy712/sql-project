# main.py - 主应用入口文件
from flask import Flask, jsonify, render_template, request, redirect, url_for
from config import Config
from models import db
from api import init_api
import os
from datetime import datetime


def create_app():
    """创建Flask应用"""
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')

    # 加载配置
    app.config.from_object(Config)
    Config.init_app(app)

    # 初始化数据库
    db.init_app(app)

    # 初始化API
    init_api(app)

    # 创建必要的目录
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('templates', exist_ok=True)

    # 登录页面
    @app.route('/')
    def index():
        return render_template('login.html')

    # 首页
    @app.route('/home')
    def home():
        return render_template('index.html')

    # 仪表板
    @app.route('/dashboard')
    def dashboard():
        return render_template('monitoring_system.html')

    # 区域管理
    @app.route('/areas')
    def areas():
        return render_template('monitoring_system.html')

    # 环境监测系统
    @app.route('/monitoring')
    def monitoring():
        return render_template('monitoring_system.html')

    # 传感器管理（重定向到监测系统）
    @app.route('/sensors')
    def sensors():
        return redirect('/monitoring')

    # 监测数据（重定向到监测系统）
    @app.route('/monitors')
    def monitors():
        return redirect('/monitoring')

    # 用户管理
    @app.route('/user-management')
    def user_management():
        return render_template('user_management.html')

    # 灾害预警
    @app.route('/disaster-warning')
    def disaster_warning():
        return render_template('disaster_warning.html')

    # 资源管理
    @app.route('/resource-management')
    def resource_management():
        return render_template('resource_management.html')

    # 设备管理
    @app.route('/device-management')
    def device_management():
        return render_template('device_management.html')

    # 统计分析
    @app.route('/statistical-analysis')
    def statistical_analysis():
        return render_template('statistical_analysis.html')

    # 健康检查
    @app.route('/health')
    def health():
        try:
            with app.app_context():
                db.session.execute('SELECT 1')
            db_status = 'connected'
        except:
            db_status = 'disconnected'

        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })

    # 测试页面
    @app.route('/test')
    def test_page():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>API测试</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <h1>API测试页面</h1>
                <div class="list-group mt-4">
                    <a href="/api/environment/areas" class="list-group-item list-group-item-action" target="_blank">
                        区域API测试
                    </a>
                    <a href="/api/environment/sensors" class="list-group-item list-group-item-action" target="_blank">
                        传感器API测试
                    </a>
                    <a href="/api" class="list-group-item list-group-item-action" target="_blank">
                        API首页
                    </a>
                    <a href="/health" class="list-group-item list-group-item-action" target="_blank">
                        健康检查
                    </a>
                </div>
            </div>
        </body>
        </html>
        '''

    # API文档页面
    @app.route('/api-docs')
    def api_docs():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>API文档</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <h1>智慧林草系统 API 文档</h1>
                <div class="card mt-4">
                    <div class="card-header">
                        <h5>认证API</h5>
                    </div>
                    <div class="card-body">
                        <ul>
                            <li><strong>POST /api/auth/login</strong> - 用户登录</li>
                            <li><strong>POST /api/auth/logout</strong> - 用户登出</li>
                            <li><strong>GET /api/auth/verify</strong> - 验证令牌</li>
                            <li><strong>POST /api/auth/change-password</strong> - 修改密码</li>
                            <li><strong>POST /api/auth/register</strong> - 用户注册</li>
                        </ul>
                    </div>
                </div>
                
                <div class="card mt-4">
                    <div class="card-header">
                        <h5>用户管理API</h5>
                    </div>
                    <div class="card-body">
                        <ul>
                            <li><strong>GET /api/users</strong> - 获取用户列表</li>
                            <li><strong>POST /api/users</strong> - 创建用户</li>
                            <li><strong>GET /api/users/{id}</strong> - 获取用户详情</li>
                            <li><strong>PUT /api/users/{id}</strong> - 更新用户</li>
                            <li><strong>DELETE /api/users/{id}</strong> - 删除用户</li>
                        </ul>
                    </div>
                </div>
                
                <div class="card mt-4">
                    <div class="card-header">
                        <h5>环境监测API</h5>
                    </div>
                    <div class="card-body">
                        <h6>区域管理</h6>
                        <ul>
                            <li><strong>GET /api/environment/areas</strong> - 获取区域列表</li>
                            <li><strong>POST /api/environment/areas</strong> - 创建区域</li>
                            <li><strong>GET /api/environment/areas/{id}</strong> - 获取区域详情</li>
                            <li><strong>PUT /api/environment/areas/{id}</strong> - 更新区域</li>
                            <li><strong>DELETE /api/environment/areas/{id}</strong> - 删除区域</li>
                        </ul>
                        <h6 class="mt-3">传感器管理</h6>
                        <ul>
                            <li><strong>GET /api/environment/sensors</strong> - 获取传感器列表</li>
                            <li><strong>POST /api/environment/sensors</strong> - 创建传感器</li>
                            <li><strong>GET /api/environment/sensors/{id}</strong> - 获取传感器详情</li>
                            <li><strong>DELETE /api/environment/sensors/{id}</strong> - 删除传感器</li>
                        </ul>
                        <h6 class="mt-3">监测数据</h6>
                        <ul>
                            <li><strong>POST /api/environment/monitors</strong> - 创建监测数据</li>
                            <li><strong>POST /api/environment/monitors/batch</strong> - 批量创建监测数据</li>
                            <li><strong>GET /api/environment/sensors/{id}/monitors</strong> - 获取传感器监测数据</li>
                        </ul>
                    </div>
                </div>
                
                <div class="mt-4">
                    <a href="/test" class="btn btn-primary">API测试页面</a>
                    <a href="/" class="btn btn-secondary">返回登录页</a>
                </div>
            </div>
        </body>
        </html>
        '''

    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'code': 404,
                'message': f'API端点 {request.path} 不存在',
                'data': None
            }), 404
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'code': 500,
            'message': '服务器内部错误',
            'data': str(error) if app.debug else None
        }), 500

    return app


if __name__ == '__main__':
    app = create_app()

    print("=" * 60)
    print("智慧林草环境监测系统")
    print("=" * 60)
    print(f"数据库: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("\n🚀 系统已启动!")
    print("\n📱 访问地址:")
    print("• 登录页面: http://localhost:5000")
    print("• 系统首页: http://localhost:5000/home")
    print("• 环境监测: http://localhost:5000/monitoring")
    print("• 区域管理: http://localhost:5000/areas")
    print("• 用户管理: http://localhost:5000/user-management")
    print("• API测试: http://localhost:5000/test")
    print("• API文档: http://localhost:5000/api-docs")
    print("• 健康检查: http://localhost:5000/health")
    print("\n🔗 主要API端点:")
    print("• 区域管理: GET /api/environment/areas")
    print("• 传感器管理: GET /api/environment/sensors")
    print("• 用户登录: POST /api/auth/login")
    print("• 用户管理: GET /api/users")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)