# EnvoyReader
Runs python containers to read a local Envoy system into InfluxDB.
It also provides a web API that shows the current envoy data, using the paths:
* /power/production
* /power/inverter
* /power/stream

The data captured is:
* Every second - total production, consumption, net for the house and each power phase
* Every 15 minutes - inverter specific data

## Goal
- Easily capture local available Envoy data
- Allow visualisations in tools like Grafana

## References
* https://thecomputerperson.wordpress.com/2016/08/28/reverse-engineering-the-enphase-installer-toolkit/
* https://thecomputerperson.wordpress.com/2016/08/03/enphase-envoy-s-data-scraping/

## Requirements
- An enironment to run the containers
- InfluxDB to be up and running
- Redis to be up and running

## Install
1. Clone/download this repository
Assuming Raspberry PI or Debian
```sh
sudo apt-get install docker git
mkdir git
cd git
git clone https://github.com/jinxo13/EnvoyReader
```
2. Modify the docker-compose.yml for your environment
```yml
 - LOCAL_TZ= #Local timezone e.g. Australia/Brisbane
 - LOG_FILE=/var/log/envoy_reader.log
 - APP_PORT=5001 #Exposes current Envoy data
 - REDIS_HOST= #REDIS host e.g. redis.local
 - REDIS_PORT=6379
 - REDIS_PASSWORD=
 - INFLUXDB_HOST= #InluxDB host e.g. influx.local
 - INFLUXDB_PORT=8086
 - INFLUXDB_USER= #InluxDB user
 - INFLUXDB_PASSWORD=  #InluxDB password
 - INFLUXDB_DATABASE=envoy #InluxDB database name
 - INFLUXDB_METER_MEAS=power_meter #measurement used for meter data
 - INFLUXDB_INVERTER_MEAS=power_inverter #measurement used for inverter data
 - ENVOY_URL= #Envoy URL e.g. http://envoy.local
 - ENVOY_USERNAME=envoy
 - ENVOY_PASSWORD= #Envoy password - last 6 digits of your serial number - see https://enphase.com/en-au/support/how-do-i-update-password-my-home-wi-fi-network
 - ENVOY_INSTALLER_USER=installer
 - ENVOY_INSTALLER_PASS= #Installer password - see https://thecomputerperson.wordpress.com/2016/08/28/reverse-engineering-the-enphase-installer-toolkit/
```
3. Build the Docker image and start the containers
```sh
docker build . -t celery_app
docker-compose up -d
```
4. Troubleshooting
Logs are written to /var/log/envoy_reader.log in the envoyreader_worker_1 container.
