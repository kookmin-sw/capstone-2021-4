FROM tiangolo/uwsgi-nginx-flask:python3.7
COPY requirements.txt /tmp
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt && \
	rm /tmp/requirements.txt    
RUN pwd && ls -al
COPY . /app
WORKDIR /app
ENV UWSGI_INI /app/uwsgi.ini
# custom static folder
ENV STATIC_PATH /app/app/static 
ENV UWSGI_BUFFER_SIZE=32768