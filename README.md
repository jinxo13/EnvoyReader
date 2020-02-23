# EnvoyReader
Runs python containers to read a local Envoy system into InfluxDB.

The data captured is:
* Every second - total production, consumption, net for the house and each power phase
* Every 15 minutes - inverter specific data

See the [wiki](https://github.com/jinxo13/EnvoyReader/wiki) for more detail

## Goal
- Easily capture local available Envoy data
- Allow visualisations in tools like Grafana

## References
* https://thecomputerperson.wordpress.com/2016/08/28/reverse-engineering-the-enphase-installer-toolkit/
* https://thecomputerperson.wordpress.com/2016/08/03/enphase-envoy-s-data-scraping/

## Requirements
- An enironment to run the containers
- InfluxDB
- Redis

Refer [here](https://github.com/jinxo13/EnvoyReader/wiki/Setup-InfluxDb-and-Redis-containers) for setting up Redis and InfluxDb

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
cd EnvoyReader
docker build . -t envoy_reader
docker-compose up -d
```
## Troubleshooting
* The containers keeps restarting

Run in interactive mode to see the error
```sh
docker-compose up
```

* The container is running but not writing

Check the application log file for any errors.
```sh
docker exec -it envoyreader_worker_1 bash
cat /var/log/envoy_reader.log
```
