FROM tiangolo/uwsgi-nginx-flask:python3.7
COPY requirements.txt /tmp
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt && \
	rm /tmp/requirements.txt    

# custom static folder
ENV STATIC_PATH /app/project/static 

COPY ./app /app 