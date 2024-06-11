FROM ubuntu:18.04
WORKDIR /public_html/djangoref/
RUN apt-get update
RUN apt-get -y install dialog apt-utils
RUN apt-get -y install software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
RUN apt-get -y install python3.7
RUN apt-get -y install python3-pip
# RUN apt-get -y install openjdk-8-jdk
RUN apt-get -y install unzip
RUN apt-get -y install gdal-bin
RUN apt-get -y install libgdal-dev
RUN apt-get -y install libpq-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libffi-dev
RUN apt-get -y install nodejs-dev node-gyp libssl1.0-dev
RUN apt-get -y install npm
RUN apt-get -y install python3-venv
RUN apt-get -y install libpango1.0-0
RUN apt-get -y install libcairo2
# needed for entrypoint.sh
RUN apt-get -y install netcat
COPY . /public_html/djangoref/
RUN pip3 install -r /public_html/djangoref/requirements.txt
COPY conf/libgeos.py /usr/local/lib/python3.6/dist-packages/django/contrib/gis/geos/libgeos.py
COPY conf/createusers.py /public_html/djangoref/.

# collectstatic is now done in entrypoint
# RUN python3.6 manage.py collectstatic
# run entrypoint.sh
ENTRYPOINT ["/public_html/djangoref/entrypoint.sh"]
