FROM alpine:3.7

WORKDIR /app

COPY . /app

RUN apk add --update\
	python \
	py-pip\
	&& pip install flask -U\
	&& rm -rf /var/cache/apk/* \
	&& pip install requests

EXPOSE 80

ENV TEAM_ID=CC_130_150_157_174

CMD ["python","acts.py"]
