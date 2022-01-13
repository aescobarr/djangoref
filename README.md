# Ali-Bey

Ali-Bey is a web application for georeferencing site names, originally created for the Museu de Ciencies Naturals de Barcelona - [MCNB](https://museuciencies.cat/). It allows the storage, indexing and querying of georeferenced site names, including their geometry, and supports multiple versions of the site names. Ali-Bey is built using [Django Python web framework](https://www.djangoproject.com/).

Some functionality of the application is also exposed as an API which allows to query the underlying data. The API is a separate project and can be found [here](https://github.com/aescobarr/mcnb-alibey-api).

## Getting Started

These instructions will help you set up a basic working development environment on an Ubuntu 18.04 LTS system. It assumes [Git](https://git-scm.com/) is installed and running in the host machine. 

If you are a docker user, you can use the dockerized version from this [repository](https://github.com/aescobarr/mcnb-alibey-docker) which simplifies the installation process.

### Prerequisites

* Create a user which will own the project folder. Traditionally, the user is named djangoref but you can name it anything you want.
* Log on the machine as the djangoref user and clone this repo

```bash
git clone https://github.com/aescobarr/mcnb-alibey.git
```

#### General packages

First, install some basic general purpose packages:

```bash
sudo apt install libpq-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libffi-dev
sudo apt install gcc
sudo apt install g++
```

#### Database

Ali-Bey uses a [Postgresql 9+](https://www.postgresql.org) database with the [PostGIS](https://postgis.net) spatial database extension. You can install it like this:

```bash
sudo apt install postgresql-10
sudo apt install postgresql-10-postgis-2.4
sudo apt install postgresql-10-postgis-scripts
```

We recommend to create a separate PostgreSQL user which will own the Ali-Bey database and not use the postgres super user. To create the user and the application database we would follow these steps (we will create a user called georef_app):

Log in to the Postgresql console using the postgres (admin) user. Then:
```
-- Create the georef_app user
CREATE ROLE georef_app LOGIN PASSWORD 'mypassword' NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
```

With the user created, we now proceed to create the database which will host the application data. As the PostgreSQL system user, from the shell we can create the database and make it owned by the application user which we named georef_app in the last step (in this example we call the database georef):
```bash
# As postgresql user
createdb georef -O georef_app
```

Finally, we enable the PostGIS extensions in the database. We connect as the postgres user to the georef database and execute the commands:
```
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
```

Remember the name of the database, owner user and its password because we will have to put them in the database configuration file (adjusting config files section)

#### Python stuff

Python 3.6 should be installed in Ubuntu 18.04 by default. We also need pip for installing python packages:
```bash
sudo apt install python-pip
sudo apt install python3.6-dev
```

Ali-Bey relies heavily on [GDAL/OGR](https://live.osgeo.org/en/overview/gdal_overview.html) libraries for certain spatial calculations. These are installed like this:
```bash
sudo add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
sudo apt-get update
sudo apt install gdal-bin python-gdal python3-gdal
sudo apt-get install libgdal-dev
```

It is strongly recommended to install [Virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) to manage the app virtual environment:
```bash
pip install virtualenv
pip install virtualenvwrapper

# then, as the djangoref user or whatever you named it in prerequisites open ~/.bashrc with a text editor and add the line
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

#finally activate the virtualenvwrapper script
source ~/.bashrc
```

For additional info on virtualenvwrapper, go to the virtualenvwrapper [docs](https://virtualenvwrapper.readthedocs.io/en/latest/)

#### GeoServer

Ali-Bey uses a [GeoServer](http://geoserver.org/) instance to serve some layers via WMS services. This step could be considered optional in a development environment although it is mandatory in production deployment.

##### Geoserver dependencies

###### Java

We need a working [jdk](https://openjdk.java.net/). The basic install in Ubuntu 18.04 is as follows (for a Java 8 install):
```bash
sudo apt install openjdk-8-jdk
```

###### Tomcat

We recommend installing [Tomcat 8](https://tomcat.apache.org/download-80.cgi) and the manager add-on, which should be quite painless in Ubuntu 18.04:
```bash
sudo apt install tomcat8
sudo apt install tomcat8-admin
```

##### Geoserver install and basic setup

From the shell, do something like this:
```bash
# Go to temporary directory
cd /tmp
# Download 2.14.2 zip file
wget https://sourceforge.net/projects/geoserver/files/GeoServer/2.14.2/geoserver-2.14.2-bin.zip/download
# Rename the file
mv download geoserver-2.14.2-bin.zip
# Unzip package
unzip geoserver-2.14.2-bin.zip
# Move package folder outside of /tmp to its definitive location - in this example we put it in /opt/
mv geoserver-2.14.2 /opt/.
# Make tomcat8 user owner of the full folder
chown -R tomcat8:tomcat8 /opt/geoserver-2.14.2

```

Then we need to edit some config files. First, we create a tomcat8 context for the geoserver instance:
```bash
touch /var/lib/tomcat8/conf/Catalina/localhost/geoserver.xml
```

Then edit this file and add the following lines:
```
<Context        
        docBase="/opt/geoserver-2.14.2/webapps/geoserver"
        path="/geoserver"
        reloadable="true">
</Context>
```

Save the file and exit. This should have created an app wich should be visible in the tomcat manager. Stop the app for now and let's create a GeoServer Data Directory. This will create a working directory for GeoServer in which all the configuration data will be written, outside of the geoserver folder. This is a recommended practice, because it creates a separate folder for data which can be managed separately and makes easier the maintenance (backup and GeoServer upgrades).
```bash
# Create a folder for the data. In this example, we put it in /opt/
mkdir /opt/data_dir_gs_2.14.2
# Assign ownership to tomcat8 user
chown -R tomcat8:tomcat8 data_dir_gs_2.14.2/
```

Now we need to edit some files. Open the file
```
/opt/geoserver-2.14.2/webapps/geoserver/WEB-INF/web.xml
```
And change the key with a param-name that contains the string GEOSERVER_DATA_DIR so that it looks like so:
```
<context-param>
   <param-name>GEOSERVER_DATA_DIR</param-name>
    <param-value>/opt/data_dir_gs_2.14.2</param-value>
</context-param> 
```
This instructs GeoServer to use the /opt/data_dir_gs_2.14.2 instead of the default directory. It should take effect when restarting GeoServer from the tomcat manager.

Next, we should perform some administrative tasks in the GeoServer instance. This includes:

* Create a user which will perform the interactions between Ali-Bey and GeoServer
* Create a workspace to store the created layers
* Publish a few layers from the PostgreSQL database

### Installing


#### Virtual environment
We will need a python virtual environment to run the app. Execute these commands as the user that owns the project folder. We assume that the environment name is 'georef' but you can name it however you want:

```bash
#Create a virtual env named 'georef'
mkvirtualenv --python=/usr/bin/python3.6 georef
```

The --python parameter ensures that the python interpreter used will be 3.6. Once the environment is active, its name in parentheses will appear before the command line in shell. To activate, simply type:
```bash
#Activate the virtual env
workon georef
```
With the virtual environment active, let's load all the needed python packages into it. From the application folder, launch this command:
```bash
pip install -r requirements.txt
```
This will install all the packages listed in requirements.txt in the virtual environment.

#### Adjusting config files

The cloned repository has a [settings.py](https://github.com/aescobarr/nhc-georef/blob/master/djangoref/settings.py), the typical django config file. However, this file is not enough to run the app, as it points to a second settings_local.py file which must be created. Most parameters in settings.py are overwritten in the settings_local.py file, so it must be created and exist at the same level in the folder structure as settings.py.

The file settings_local.py contains the following (the comments give a brief description of each config key value):
```python
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Long, complicated string that django uses internally for things like identifying sessions
SECRET_KEY = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' 

# In development, this can be set to True to visualize additional debug info. In production, always set to False
DEBUG = False 

# If DEBUG = False, put here a comma separated list of the host name/s. For a single name -> ['www.example.com']/ for multiple names, ['www.example1.com','www.example2.com']. If DEBUG = True, leave as it is.
ALLOWED_HOSTS = []  

# Postgresql connection parameters
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', #We use the Postgis extension for spatial queries
        'NAME': 'DATABASE_NAME', # Put here your database name
        'USER': 'USER_NAME', # Put here the user that connects with the database. This user must be able to read/write the database
        'PASSWORD': 'PASSWORD', # The above user password
        'HOST': 'localhost', # The IP address of the machine hosting the database
        'PORT': '5432', # The port in which Postgresql listens for connections
    }
}

#Absolute path to static resources folder. In development, comment out this line
#STATIC_ROOT = '/home/djangoref/djangoref/static/'

# Media URL, relative to the app root address. For example if our app is running in www.example.com, media files should be accessible at www.example.com/media/
MEDIA_URL = "/media/" 
# Absolute Upload directory path, appended to BASE_DIR which points to the application root folder
UPLOAD_DIR = BASE_DIR + "/uploads" 
# The media path is the same as UPLOAD_DIR
MEDIA_ROOT = UPLOAD_DIR 
LOCAL_DATAFILE_ROOT_DIRECTORY = 'helpfile_uploads'

# Geoserver params
# The workspace and user should have been created in the previous step "Geoserver install and basic setup"
# Workspace in which the layers will be stored
GEOSERVER_WORKSPACE = 'SOME_WORKSPACE' 
# Geoserver user
GEOSERVER_USER = 'GEOSERVER_USER' 
# The password of the above user
GEOSERVER_PASSWORD = 'GEOSERVER_USER_PASSWORD' 
# Root url of the geoserver install address. The trailing slash is important
GEOSERVER_BASE_URL = 'https://www.example.com/' 
# Root url of the geoserver WMS services endpoint
GEOSERVER_WMS_URL_CLEAN = GEOSERVER_BASE_URL + 'geoserver/wms/' 
# Root url of the geoserver restful api endpoint
GEOSERVER_REST_URL = GEOSERVER_BASE_URL + 'geoserver/rest/' 
# URL to wms services endpoint of the previously defined GEOSERVER_WORKSPACE
GEOSERVER_WMS_URL = GEOSERVER_BASE_URL + 'geoserver/' + GEOSERVER_WORKSPACE + "/wms/?" 

# URL to google maps API key. Put your own key here
GOOGLE_MAPS_API_KEY='AIza..and something else'
GOOGLE_MAPS_KEY_URL='https://maps.googleapis.com/maps/api/js?key=' + GOOGLE_MAPS_API_KEY
```

#### Starting the app in dev mode

Before starting up the app, we need to perform a couple of additional setup steps to prepare the database. First, we create the base tables for the app. To do this, we execute a script in the "scripts" subfolder in the app folder:
```bash
# We connect as the app user and create some tables in the app database
# A brief breakdown of the parameters:
# -h is the address of the machine that hosts the database. We assume here that is running in localhost
# -d is the name of the database which we created in the Database section
# -U is the user name of the owner of the database
# -f is the path to the djangoref_db_tables.sql script
psql -h localhost -d georef -U georef_app -W -f [path_to_app_folder]/scripts/djangoref_db_tables.sql
```

This should create a few tables, which we need for the next step. From the command shell, we activate the virtual environment (this is important) and we run the migrations which will create the basic django management tables and a few model tables.
```bash
# We assume that we have named the virtual env georef. To activate, we do:
workon georef
# From the application folder, we run the command
./manage.py migrate
```

At this point, we need to run a second sql script which contains some foreign key definitions. This is very similar to the first step in this section:
```bash
# We connect as the app user and create some foreign keys in the app database
# A brief breakdown of the parameters:
# -h is the address of the machine that hosts the database. We assume here that is running in localhost
# -d is the name of the database which we created in the Database section
# -U is the user name of the owner of the database
# -f is the path to the djangoref_db_constraints.sql script
psql -h localhost -d georef -U georef_app -W -f [path_to_app_folder]/scripts/djangoref_db_constraints.sql
```

This leaves us with a fully prepared empty database. Now we can create a superuser:
```bash
./manage.py createsuperuser
```

With the virtual environment active, from inside the app folder we run the script
```bash
./manage.py runserver
```

This should start a development server at http://127.0.0.1:8000

## Deployment

### Apache

Our particular deployment setup uses [Apache](http://httpd.apache.org/) with mod_proxy to proxy a local [Gunicorn](https://gunicorn.org/) instance. The static resources will also be served by Apache. So we need to install a few additional pieces; Gunicorn should already be installed in your system as it is contained in the project requirements.txt file.

The Apache installation goes something like this:
```bash
# install apache2 package
apt install apache2
# enable proxy related mods
a2enmod proxy
a2enmod proxy_http
a2enmod headers
# restart service to wake up apache mods
systemctl restart apache2
```

### Static resources

Go to the app folder and activate the python virtual environment. In the present example we assume that the virtual environment is called georef:
```bash
workon georef
```

Build static resources folder using django manage command:
```bash
./manage.py collectstatic
```

This creates a folder named 'static' in the directory indicated in the config variable STATIC_ROOT (see [settings.py](https://github.com/aescobarr/nhc-georef/blob/master/djangoref/settings.py) and settings_local.py files). This folder will be served as a static folder by apache. As a previous step, we will create links to some folders in /var/www:
```bash
# create directory if doesn't exist
sudo mkdir /var/www/georef
# create symbolic link to static dir
sudo ln -s [path_to_app_folder]/static /var/www/georef/
# create symbolic link to uploads folder. In this case, the symbolic link will be called media (not uploads)
sudo ln -s [path_to_app_folder]/uploads /var/www/georef/media
```

### Apache virtual host

We create an apache virtual host file in /etc/apache2/sites-available/:
```
# we call the file georef.conf; other names are ok too
sudo touch /etc/apache2/sites-available/georef.conf
```
We edit the file, which will end up looking something like this:
```
<VirtualHost IP_ADDRESS:80>
            # The root where static resource folders are located
            DocumentRoot /var/www/djangoref

            # Server base address/name
            ServerName www.example.com

            ProxyPreserveHost On
            <Proxy *>
                Order deny,allow
                Allow from all
            </Proxy>

            # static served by apache
            ProxyPass /favicon.ico !
            ProxyPass /static/ !
            ProxyPass /media/ !
            
            # Transparent proxy to geoserver. Redirect all /geoserver* petitions
            # to http://localhost:8080/geoserver (this assumes that geoserver is running inside
            # a tomcat instance running in port 8080)
            ProxyPass /geoserver http://localhost:8080/geoserver
            ProxyPassReverse /geoserver http://localhost:8080/geoserver

            # Redirect to gunicorn processes the other. More on this later all /* petitions
            # will go to a gunicorn instance running in localhost:49155
            ProxyPass / http://localhost:49155/
            ProxyPassReverse / http://localhost:49155/

            <Directory "/var/www/djangoref">
                # Commented to avoid directory listing
                # Options Indexes FollowSymLinks MultiViews
                Header set Access-Control-Allow-Origin "*"
                Options FollowSymLinks MultiViews
                Allow from all
            </Directory>

            ErrorLog /var/log/apache2/georef.com.error.log
            LogLevel info

            CustomLog /var/log/apache2/georef.com.access.log combined
            ServerSignature On
</VirtualHost>

```
We save and exit. Now we must activate the virtual host:
```bash
# enable site
sudo a2ensite georef.conf
# reload apache service to apply changes
systemctl reload apache2
```

In the current state we should be able to access static resources, but the app is not running yet. Let's do that.

### Gunicorn

We need to setup the Gunicorn instance which will run the django app. To control Gunicorn we will use [supervisor](http://supervisord.org/index.html). We install it like this:
```bash
sudo apt install supervisor
```
We create a supervisor log file and give permissions to georef user (since the gunicorn process will be run as this user):
```bash
# create dir
sudo mkdir /var/log/gunicorn
# now it belongs to georef user
sudo chown georef /var/log/gunicorn
```
Next, we need to create a supervisor configuration file. This file will reside in /etc/supervisor/conf.d:
```bash
# we name the file gunicorn-georef.conf, but feel free to use any name you like
sudo touch /etc/supervisor/conf.d/gunicorn-georef.conf
```
Edit the file and put something like this inside:
```
# this is the program handle (gunicorn-georef). We will use to adress it from supervisor
[program:gunicorn-georef]
# this is the command that will launch the actual gunicorn instance. It uses the gunicorn binary inside the virtual env, the -c parameter
# points to a gunicorn_conf.py file which resides inside the app folder. Some parameters (number of workers, listening port, etc) are specified
# inside this file; feel free to change them at your convenience.
command=/home/georef/.virtualenvs/djangoref/bin/gunicorn -c /home/georef/djangoref/djangoref/gunicorn_conf.py djangoref.wsgi:application
# the root folder of the app
directory=/home/georef/djangoref
# the user which will own the gunicorn instance
user=georef
autostart=true
autorestart=true
priority=991
stopasgroup=true
stopsignal=KILL
# log stuff
stdout_logfile=/var/log/gunicorn/georef.log
stdout_logfile_maxbytes=1MB
stdout_logfile_backups=2
stderr_logfile=/var/log/gunicorn/georef.error.log
stderr_logfile_maxbytes=1MB
stderr_logfile_backups=2

```
We need to tell supervisor that we have created a new supervised process, we do it like this:
```bash
sudo supervisorctl reread
sudo supervisorctl update
```
The gunicorn process is registered. We can issue several commands to supervisor:
```bash
# list all registered processes
sudo supervisorctl status
# stop running process by handle (the name behind [program:] in the first line in /etc/supervisor/conf.d/gunicorn-georef.conf)
sudo supervisorctl stop gunicorn-georef
# start running process by handle
sudo supervisorctl start gunicorn-georef
```
We should now use the start command to start the gunicorn instance. The app is now running!

## Built With

* [Django](https://www.djangoproject.com/) 
* [django-bower](https://django-bower.readthedocs.io/en/latest/) - Javascript package manager
* [Leaflet](https://leafletjs.com/) - Maps 
* [Leaflet-draw](http://leaflet.github.io/Leaflet.draw/docs/leaflet-draw-latest.html) - Vector editing maps
* [Bootstrap](https://getbootstrap.com/) - HTML, CSS and JS Toolkit
* [Data Tables](https://datatables.net/) - JQuery plugin for HTML tables

## Authors

Developers: [Agustí Escobar](https://github.com/aescobarr) (current version), [Victor Garcia](https://github.com/vg-coder) (previous J2EE version)
Conceptual design: Arnald Marcer (CREAF), Francesc Uribe (Museu de Ciències Naturals de Barcelona)

## How to cite this software

Marcer A., Escobar A., Garcia V. and Uribe F. (2019) Ali-Bey. Github repository https://github.com/aescobarr/nhc-georef

## License

This software is licensed under [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html).

## Acknowledgments

Many thanks to Miguel Martínez( [Auupa](https://www.auupa.com/) ) for its help in integrating the software in the [MCNB](https://museuciencies.cat/espais/mcnb/) infrastructure.

