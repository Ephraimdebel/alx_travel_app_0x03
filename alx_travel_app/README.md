# Background Jobs with Celery and RabbitMQ — alx_travel_app_0x03

## ✅ Requirements
- RabbitMQ installed locally
- Celery installed
- Django Email backend configured

## ✅ Install Dependencies
```bash
pip install celery
pip install django
pip install django-celery-beat

sudo systemctl start rabbitmq-server

celery -A alx_travel_app worker -l info

celery -A alx_travel_app beat -l info
