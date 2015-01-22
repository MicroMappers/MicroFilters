============
MicroFilters
============

MicroFilters is a web application that generates data for MicroMappers from  AIDR Collection data. The collection data can be found via http://aidr.qcri.org

# Pre-Requisites

You only need two python packages installed:

Django:
`$ pip install django`

Celery: 
`$ pip install celery`

You also need to install a message broker for Celery, the recommended one is RabbitMQ.

`$ sudo apt-get install rabbitmq-server`

Celery and RabbitMQ are used to process files asyncrounously. This allows the user to leave the page or process multiple files at the same time. For the purposes of this program, file processing can take days, so this is very important. See http://docs.celeryproject.org/en/latest/index.html for more information on installing Celery and setting up task queues such as RabbitMQ.

# Setup

All the necessary configuration files for Django and Celery are included in this repo in the MicroFilters directory. No database is necessary. Beyond the normal django config settings, the following need to be added to settings.py:

`FILE_UPLOAD_HANDLERS = ('core.uploadhandler.UploadProgressCachedHandler', "django.core.files.uploadhandler.MemoryFileUploadHandler","django.core.files.uploadhandler.TemporaryFileUploadHandler",)`

For Celery:

    BROKER_URL = 'amqp://guest@localhost//'
    CELERY_RESULT_BACKEND = 'amqp'
    CELERY_ACCEPT_CONTENT = ['pickle']
    CELERY_TASK_SERIALIZER = 'pickle'
    CELERY_RESULT_SERIALIZER = 'pickle'

Disable CORS:

`ALLOWED_HOSTS = ['*']`


# Running Locally

Make sure a Celery worker is running. You can do this by running:

	$ celery -A MicroFilters worker

Then run MicroFilters:

	$ python manage.py runserver

# Deployment

Make sure a Celery worker is running, we reccomend supervisord. See the Celery docs and http://supervisord.org/ to set this up. The easiest way to deploy is using Nginx with Gunicorn. See http://gunicorn.org/ 

Default configuration files for all of these are included in the root directory of this repo for convenience.

# Logging

A log file named microfilters.log is created in the root directory of the project. It logs all processed files, whether successes or failures. It also logs whether AIDR was notified of the processed files (Sometimes it is not if AIDR is down at the time).

# Q & A



