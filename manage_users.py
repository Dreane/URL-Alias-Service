import argparse
from getpass import getpass
from app import create_app, db
from app.models import User

app = create_app()


def create_admin_user(username, password):
    """Создает нового пользователя или обновляет пароль существующего администратора."""
    with app.app_context(): 
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"Пользователь '{username}' уже существует. Обновление пароля...")
            user.set_password(password)
            action = "обновлен"
        else:
            print(f"Создание нового пользователя '{username}'...")
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            action = "создан"

        try:
            db.session.commit()
            print(f"Пользователь '{username}' успешно {action}.")
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при сохранении пользователя: {e}")


def main():
    '''
    Основная функция для управления пользователями сервиса URL Alias.
    '''
    parser = argparse.ArgumentParser(description="Скрипт для управления пользователями сервиса URL Alias.")
    parser.add_argument("command", choices=["createadmin"], help="Команда для выполнения (например, createadmin)")
    parser.add_argument("-u", "--username", help="Имя пользователя (по умолчанию 'admin')", default="admin")
    parser.add_argument("-p", "--password", help="Пароль пользователя (будет запрошен интерактивно, если не указан)")

    args = parser.parse_args()

    if args.command == "createadmin":
        password = args.password
        if not password: 
            password = getpass(f"Введите пароль для пользователя '{args.username}': ")
            password_confirm = getpass("Подтвердите пароль: ")
            if password != password_confirm:
                print("Пароли не совпадают. Операция отменена.")
                return

        if not password:
            print("Пароль не может быть пустым. Операция отменена.")
            return

        create_admin_user(args.username, password)


if __name__ == "__main__":
    main()
