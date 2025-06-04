from flask import request, jsonify, redirect, abort, Blueprint
from . import db, auth
from .models import Url, User
from datetime import datetime, timezone

main_bp = Blueprint('main', __name__)

@auth.verify_password
def verify_password(username, password):
    '''
    Проверка пароля пользователя.
    '''
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return username
    return None

@main_bp.route('/shorten', methods=['POST'])
@auth.login_required
def create_short_url():
    '''
    Создание короткой ссылки.
    '''
    data = request.get_json()
    if not data or 'url' not in data:
        abort(400, description="URL is required.")

    original_url = data['url']
    days_to_expire = data.get('days_to_expire', 1)

    if not isinstance(days_to_expire, int) or days_to_expire <= 0:
        abort(400, description="'days_to_expire' must be a positive integer.")

    new_url = Url(original_url=original_url, days_to_expire=days_to_expire)
    db.session.add(new_url)
    db.session.commit()

    short_url_full = request.host_url + new_url.short_code
    # Возврат JSON с информацией о новой короткой ссылке.
    return jsonify({
        'original_url': new_url.original_url,
        'short_code': new_url.short_code,
        'short_url': short_url_full,
        'created_at': new_url.created_at.isoformat(),
        'expires_at': new_url.expires_at.isoformat()
    }), 201

@main_bp.route('/<string:short_code>', methods=['GET'])
def redirect_to_original(short_code):
    '''
    Перенаправление на оригинальный URL.
    '''
    url_entry = Url.query.filter_by(short_code=short_code).first()

    if not url_entry:
        abort(404, description="Short URL not found.")

    if not url_entry.is_active:
        abort(410, description="URL deactivated.")

    if url_entry.expires_at < datetime.now():
        url_entry.is_active = False 
        db.session.commit()
        abort(410, description="Link expired.") 

    url_entry.clicks += 1
    db.session.commit()

    return redirect(url_entry.original_url)

@main_bp.route('/urls', methods=['GET'])
@auth.login_required
def get_all_urls():
    '''
    Получение всех URL.
    '''
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    filter_active = request.args.get('active', type=str)

    query = Url.query

    if filter_active is not None:
        if filter_active.lower() == 'true':
            query = query.filter_by(is_active=True)
        elif filter_active.lower() == 'false':
            query = query.filter_by(is_active=False)

    urls_pagination = query.order_by(Url.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    urls = urls_pagination.items

    output = []
    for url_entry in urls:
        output.append({
            'id': url_entry.id,
            'original_url': url_entry.original_url,
            'short_code': url_entry.short_code,
            'short_url': request.host_url + url_entry.short_code,
            'created_at': url_entry.created_at.isoformat(),
            'expires_at': url_entry.expires_at.isoformat(),
            'is_active': url_entry.is_active,
            'clicks': url_entry.clicks
        })

    return jsonify({
        'urls': output,
        'total_urls': urls_pagination.total,
        'current_page': urls_pagination.page,
        'total_pages': urls_pagination.pages
    })

@main_bp.route('/urls/<string:short_code>', methods=['DELETE'])
@auth.login_required
def deactivate_url(short_code):
    '''
    Деактивация URL.
    '''
    url_entry = Url.query.filter_by(short_code=short_code).first()

    if not url_entry:
        abort(404, description="Short URL not found.")

    if not url_entry.is_active:
        return jsonify({'message': 'URL already deactivated.'}), 200

    url_entry.is_active = False
    db.session.commit()
    return jsonify({'message': f'URL {short_code} was deactivated.'}), 200

@main_bp.route('/stats', methods=['GET'])
@auth.login_required
def get_stats():
    '''
    Получает статистику по URL.
    '''
    urls = Url.query.filter(Url.clicks > 0).order_by(Url.clicks.desc()).all()
    stats_output = [
        {
            'short_code': url.short_code,
            'original_url': url.original_url,
            'short_url': request.host_url + url.short_code,
            'clicks': url.clicks,
            'created_at': url.created_at.isoformat(),
            'expires_at': url.expires_at.isoformat(),
            'is_active': url.is_active
        }
        for url in urls
    ]
    return jsonify(stats_output)

@main_bp.app_errorhandler(400)
def bad_request(error):
    response = jsonify({'error': 'Bad Request', 'message': error.description})
    response.status_code = 400
    return response

@main_bp.app_errorhandler(401)
def unauthorized(error):
    response = jsonify({'error': 'Unauthorized', 'message': error.description if hasattr(error, 'description') else 'Authentication required.'})
    response.status_code = 401
    return response

@main_bp.app_errorhandler(404)
def not_found(error):
    response = jsonify({'error': 'Not Found', 'message': error.description})
    response.status_code = 404
    return response

@main_bp.app_errorhandler(410)
def gone(error):
    response = jsonify({'error': 'Gone', 'message': error.description})
    response.status_code = 410
    return response

@main_bp.app_errorhandler(500)
def internal_server_error(error):
    db.session.rollback() 
    response = jsonify({'error': 'Internal Server Error', 'message': 'Произошла внутренняя ошибка сервера.'})
    response.status_code = 500
    return response 