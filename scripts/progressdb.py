import logging
import sqlite3
#import parsl

logger = logging.getLogger(__name__)


class ProgressDB:
    def __init__(self):
        logger.info("progress db init, with sqlite3 version {}".format(
                    sqlite3.sqlite_version))
        self.conn = sqlite3.connect('/global/homes/d/descim/ALCF_1.2i/progress_run2.1i.db')

        c = self.conn.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS visit "
            "(visit_id INTEGER NOT NULL PRIMARY KEY, "
            "complete BOOLEAN NOT NULL)")
        c.execute(
            "CREATE TABLE IF NOT EXISTS sensor_visit "
            "(visit_id INTEGER NOT NULL, "
            "sensor_name TEXT NOT NULL, "
            "complete BOOLEAN NOT NULL, "
            "path TEXT, "
            "PRIMARY KEY (visit_id, sensor_name))")
        c.close()
        self.conn.commit()

    def check_visit(self, visit_id: int):
        logger.info("check visit: {}".format(visit_id))
        c = self.conn.cursor()
        c.execute("SELECT count(*) FROM visit WHERE visit_id = ?", (visit_id,))
        test = (c.fetchone())[0]
        if test == 0:
            return False
        else:
            return True

    def put_visit(self, visit_id: int):
        logger.info("put visit: {}".format(visit_id))
        c = self.conn.cursor()
        c.execute("INSERT OR IGNORE INTO visit (visit_id, complete) "
                  "VALUES(?, 'false')", [visit_id])
        c.close()
        self.conn.commit()

    ## this will safely add sensor_visits without risking overwriting a complete flag.
    def init_sensor_visit(self, visit_id: int,  sensor_name: str,
                          complete: bool):
        logger.info("init sensor visit: {} {}".format( visit_id, sensor_name))
        c = self.conn.cursor()
        c.execute("INSERT OR IGNORE INTO sensor_visit "
                  "(visit_id, sensor_name, complete) "
                  "VALUES (?,?,?)",
                  [visit_id, sensor_name, complete])
        c.close()
        self.conn.commit()   

    def put_sensor_visit(self, visit_id: int, sensor_name: str,
                         complete: bool, pathname: str):
        logger.info("put sensor visit: {} {}".format(
                                                visit_id, sensor_name))

        c = self.conn.cursor()
        c.execute("INSERT OR REPLACE INTO sensor_visit "
                  "(visit_id, sensor_name, complete, path) "
                  "VALUES (?,?,?,?)",
                  [visit_id, sensor_name, complete, pathname])
        c.close()
        self.conn.commit()

    # this should: toggle the complete flag from false to true if there are no
    # incomplete sensor_visits for this particular catalog.
    def update_visit_status(self, visit_id: int):
        logger.info("update visit status for visit {}".format(visit_id))

        c = self.conn.cursor()

        c.execute("SELECT COUNT(*) FROM sensor_visit "
                  "WHERE visit_id=? AND NOT complete", [visit_id])
        (count,) = c.fetchone()
        logger.info("update_visit_state: {} known incomplete sensor-visits"
                    .format(count))

        if count == 0:
            logger.info("Marking visit as complete")
            c.execute("UPDATE visit SET complete = 1")

        c.close()
        self.conn.commit()


if __name__ == '__main__':

    #parsl.set_stream_logger(name=__name__)

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
    db.put_sensor_visit("abc-1111", 6, False, None)
    db.put_sensor_visit("abc-1111", 56, False, None)

    # call this to update visit status - only call this after you have
    # reported all of the sensor_visits (especially the incomplete ones)
    # otherwise the DB might think the visit is complete when it is not.
    db.update_visit_status("abc-1111")

    db.put_sensor_visit("abc-1111", 6, True, None)
    db.update_visit_status("abc-1111")

    db.put_sensor_visit("abc-1111", 3, True, None)
    db.put_sensor_visit("abc-1111", 56, True, None)
    db.put_sensor_visit("abc-1111", 5, True, None)
    db.update_visit_status("abc-1111")

    logger.info("progressdb test: end")
