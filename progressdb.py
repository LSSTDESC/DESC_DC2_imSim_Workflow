import logging
import sqlite3
import parsl

logger = logging.getLogger(__name__)

class ProgressDB:
    def __init__(self):
        logger.info("progress db init")

    def put_visit(self, catalog_name: str):
        logger.info("put visit: {}".format(catalog_name))

    def put_sensor_visit(self, catalog_name: str, sensor_number: int, complete: bool, pathname: str):
        logger.info("put sensor visit: {} {}".format(catalog_name, sensor_number))

    def update_visit_status(self, catalog_name: str):
        logger.info("update visit status for visit {}".format(catalog_name))

if __name__ == '__main__':

    parsl.set_stream_logger(name = __name__)

    logger.info("progressdb: start")
    db = ProgressDB()

    # before you can put visit sensor info, you have to put the visit.
    # call it as many times for the same visit as needed - it doesn't
    # hurt to call it many times.
    db.put_visit("abc-1111")

    # call these as many times as necessary - it won't hurt to call
    # it many times for the same sensor, although don't report a
    # sensor as completed if it is not.

    # put sensor 3, completed...
    db.put_sensor_visit("abc-1111", 3, True, "/DC2/path.to.gz")

    # put sensor 5, not completed...
    db.put_sensor_visit("abc-1111", 5, False, None)

    # call this to update visit status - only call this after you have
    # reported all of the sensor_visits (especially the incomplete ones)
    # otherwise the DB might think the visit is complete when it is not.
    db.update_visit_status("abc-1111")

    logger.info("progressdb test: end")
