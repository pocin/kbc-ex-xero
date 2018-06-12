FROM python:3.6-alpine
RUN apk add --no-cache --update git gcc musl-dev python3-dev libffi-dev openssl-dev && pip3 install --no-cache-dir --upgrade \
      pytest \
      dateparser \
      flake8 \
      betamax \
      requests \
      pyxero \
      voluptuous \
      https://github.com/keboola/python-docker-application/tarball/master

WORKDIR /code

COPY . /code/

# Run the application
CMD python3 -u /code/main.py

