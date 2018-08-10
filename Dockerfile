FROM python:3.6.6-jessie

RUN apt-get update && apt-get install -y git \
      && pip3 install --no-cache-dir --upgrade \
      pytest \
      dateparser \
      requests \
      git+git://github.com/freakboy3742/pyxero.git@a602f51de2c407bb3ae0fc8634681cd71b6ce9ff \
      voluptuous \
       https://github.com/keboola/python-docker-application/tarball/master

# pyxero from git because maintainer is sleeping and pypi version uses JWT1.4 which is deprecated

WORKDIR /code

COPY . /code/

# Run the application
CMD python3 -u /code/main.py

