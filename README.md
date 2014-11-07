============
MicroFilters
============

MicroFilters is a web application that generates data for MicroMappers from  AIDR Collection data.

# Setup

Whether you’re using a virtual environment or not, you only need two python packages installed:

Django:
`$ pip install django`

Celery: 
`$ pip install celery`

You also need to install a message broker for Celery, the recommended one is RabbitMQ.

`$ sudo apt-get install rabbitmq-server`


# Running Locally

Make sure a Celery worker is running. You can do this by running:

	$ celery -A MicroFilters worker

Then run MicroFilters:

	$ python manage.py runserver

# Deployment

Make sure a Celery worker is running, you can use supervisord for that.

Deploy using Nginx with Gunicorm.



