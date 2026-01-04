# app.py
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 启用CORS
    CORS(app)

    @app.route('/')
    def index():
        return jsonify({
            'project': '智慧林草系统',
            'status': '运行中',
            'version': '1.0.0',
            'endpoints': {
                '健康检查': '/health',
                '小组信息': '/about'
            }
        })

    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'timestamp': '2024'})

    @app.route('/about')
    def about():
        return jsonify({
            'course': '数据库系统课程设计',
            'instructor': '崔晓晖',
            'team_size': 5,
            'modules': [
                '环境监测',
                '灾害预警',
                '资源管理',
                '设备管理',
                '统计分析'
            ]
        })

    return app


if __name__ == '__main__':
    app = create_app()
    print("🌲 智慧林草系统启动中...")
    print("📡 访问 http://localhost:5000")
    print("🔧 按 Ctrl+C 停止")
    app.run(debug=True, host='0.0.0.0', port=5000)