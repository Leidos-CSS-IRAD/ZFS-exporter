#!/usr/bin/python3


#### ZFS Exporter ####
#### (C) 2020 Leidos.  All rights reserved. 
#### Contact Information: Leidos_CSS_IRAD@leidos.com

from typing import Callable
from prometheus_client import start_http_server, Gauge
from zpool_parser import get_zpool_status, ZPoolState, DriveStatus, SubpoolType, SubpoolStatus, ZPoolStatus


POOL_HEALTH = Gauge("zfs_pool_health", "0=healthy, 1=degraded", ["pool"])
DRIVE_HEALTH = Gauge("zfs_drive_health", "0=healthy, 1=degraded, 2=unavail", ["pool", "name"])

RESILVER_STATUS = Gauge("zfs_resilver_status", "0=not resilvering, 1=resilvering", ["pool"])
RESILVER_TIME_REMAINING = Gauge("zfs_resilver_time_remaining", "time in seconds", ["pool"])
RESILVER_LAST_TIME = Gauge("zfs_resilver_last_time", "time since epoch", ["pool"])

SCRUB_STATUS = Gauge("zfs_scrub_status", "0=not scrubbing, 1=scrubbing", ["pool"])
SCRUB_TIME_REMAINING = Gauge("zfs_scrub_time_remaining", "time in seconds", ["pool"])
SCRUB_LAST_TIME = Gauge("zfs_scrub_last_time", "time since epoch", ["pool"])

def get_pool(pool_name: str) -> ZPoolStatus:
    for p in get_zpool_status():
        if p.name == pool_name:
            return p
    else:
        raise KeyError("{} not found in pool list".format(pool_name))

def get_pool_health(pool_name: str) -> Callable[[], float]:
    return lambda: get_pool(pool_name).state.value

def get_drive_health(pool_name: str, drive_name: str) -> Callable[[], float]:
    def f():
        for subpool in get_pool(pool_name).subpools:
            for drive in subpool.drives:
                if drive.name == drive_name:
                    return drive.state.value
        else:
            return 100
        
    return f

def get_resilver_status(pool_name: str) -> Callable[[], float]:
    return lambda: 1 if get_pool(pool_name).currently_resilvering else 0

def get_resilver_time(pool_name: str) -> Callable[[], float]:
    return lambda: get_pool(pool_name).resilver_time_remaining

def get_resilver_last_time(pool_name: str) -> Callable[[], float]:
    return lambda: get_pool(pool_name).last_resilver

def get_scrub_status(pool_name: str) -> Callable[[], float]:
    return lambda: 1 if get_pool(pool_name).currently_scrubbing else 0

def get_scrub_time(pool_name: str) -> Callable[[], float]:
    return lambda: get_pool(pool_name).scrub_time_remaining

def get_scrub_last_time(pool_name: str) -> Callable[[], float]:
    return lambda: get_pool(pool_name).last_scrub

def generate_gauges():
    pools = get_zpool_status()
    for pool in pools:
        # print(POOL_HEALTH.labels(""))
        POOL_HEALTH.labels(pool=pool.name).set_function(get_pool_health(pool.name))

        RESILVER_STATUS.labels(pool=pool.name).set_function(get_resilver_status(pool.name))
        RESILVER_TIME_REMAINING.labels(pool=pool.name).set_function(get_resilver_time(pool.name))
        RESILVER_LAST_TIME.labels(pool=pool.name).set_function(get_resilver_last_time(pool.name))

        SCRUB_STATUS.labels(pool=pool.name).set_function(get_scrub_status(pool.name))
        SCRUB_TIME_REMAINING.labels(pool=pool.name).set_function(get_scrub_time(pool.name))
        SCRUB_LAST_TIME.labels(pool=pool.name).set_function(get_scrub_last_time(pool.name))

        for subpool in pool.subpools:
            for drive in subpool.drives:
                DRIVE_HEALTH.labels(pool=pool.name, name=drive.name).set_function(get_drive_health(pool.name, drive.name))

    # POOL_HEALTH.


if __name__ == "__main__":
    generate_gauges()
    start_http_server(8080)
    while True:
        pass

