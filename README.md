# ZFS-exporter

Uses [zpool parser](https://github.com/Leidos-CSS-IRAD/zfs-textfile-collector) and [Prometheus Python client](https://github.com/prometheus/client_python) to provide live metrics on ZFS status (pool + drive health, resilver + scrub status and time) to Prometheus.

## Usage

Grab [zpool_parser.py](https://github.com/Leidos-CSS-IRAD/zfs-textfile-collector/blob/master/zpool_parser.py) from the ZFS textfile collector repository and put it in this directory (ideally, clone the repository separately and symlink the zpool_parser.py file into this directory). Then, if you want to run it once manually, enter `python3 zfs_exporter.py` into the command line. This will start an HTTP server on port 8080, which, when accessed, will provide live metrics.

Alternatively, to run the exporter as a service, place the `zfs-exporter.service` file into `/etc/systemd/system/zfs-exporter.service` or wherever your system places service files. Then, run `systemctl daemon-reload` and `systemctl enable zfs-exporter`. The exporter will now start on startup. You can check the current status of the service with `systemctl status zfs-exporter`.

## How it Works

The zpool parser parses the output of the `zpool status` command. Then, the ZFS exporter uses the Prometheus client to serve live metrics through an HTTP server.

The Prometheus client library allows for the creation of `Gauge`s, which can be provided labels, documentation, and values. In order to get live updating values, we can provide a gauge with a function rather than a value. For the ZFS exporter, we create gauges for each metric we want to collect, then provide each of those gauges with a function to call when the metric is requested. These functions use the zpool parser to get the current status of whatever metric they correspond to.
