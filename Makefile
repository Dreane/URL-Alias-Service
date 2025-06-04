.PHONY: help install run clean

help:
	@echo "Доступные команды:"
	@echo "  install    - Установка зависимостей из requirements.txt (в виртуальное окружение)"
	@echo "  run        - Запуск Flask development server"
	@echo "  clean      - Удаление артефактов сборки и виртуального окружения"

install: venv/touchfile
	@echo "Установка зависимостей..."
	@./venv/Scripts/pip install -r requirements.txt

venv/touchfile: requirements.txt
	@echo "Создание/обновление виртуального окружения..."
	python -m venv venv
	@./venv/Scripts/activate && ./venv/Scripts/pip install --upgrade pip
	@touch venv/touchfile

run: venv/touchfile
	@echo "Запуск Flask development server на http://127.0.0.1:5000/ ..."
	@echo "Для остановки нажмите CTRL+C"
	@./venv/Scripts/python run.py

clean:
	@echo "Очистка..."
	@if exist venv (rmdir /s /q venv)
	@if exist instance (rmdir /s /q instance)
	@echo "Готово."

# Для Unix-подобных систем (Linux/macOS) команды следующие:
# venv/touchfile:
# 	python3 -m venv venv
# 	./venv/bin/activate && ./venv/bin/pip install --upgrade pip
# 	touch venv/touchfile
# install:
# 	./venv/bin/pip install -r requirements.txt
# run:
# 	./venv/bin/python3 run.py
# clean:
# 	rm -rf venv
# 	rm -rf instance
# 	find . -name '*.pyc' -delete
# 	find . -name '__pycache__' -delete