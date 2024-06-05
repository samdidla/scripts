# mssql.py
import logging
import pymssql
import time
import datetime

logging.basicConfig(
    format="[ℹ] [%(asctime)s] [%(levelname)s]\t %(message)s", level=logging.INFO
)


def mssql_ready(conn, dbs):
    logging.info("mssql - wait")
    time.sleep(5)
    cur = conn.cursor()
    states = ["IN_PROGRESS", "CREATED", "CANCEL_REQUESTED"]
    while True:
        tasks = 0
        text = ""
        cur.execute("EXEC msdb.dbo.rds_task_status")
        for r in cur:
            if r[5] in states and r[2] in dbs:
                text = f"{text}{r[0]}-{r[2]}-{r[5]}-{r[3]}% "
                tasks = tasks + 1
        if tasks == 0:
            return True
        logging.info(f"mssql - {tasks} tasks {text}")
        time.sleep(5)


def mssql_backup(
    source_mssql_host, source_mssql_user, source_mssql_password, dbs, source_system_s3
):
    date_object = str(datetime.date.today())
    conn = pymssql.connect(  # type: ignore
        source_mssql_host, source_mssql_user, source_mssql_password
    )
    mssql_ready(conn, dbs)
    cur = conn.cursor()
    conn.autocommit(True)
    for d in dbs:
        cur.execute(
            f"exec msdb.dbo.rds_backup_database @source_db_name='{d}', @s3_arn_to_backup_to='arn:aws:s3:::{source_system_s3}-system/{d}_{date_object}.bak', @overwrite_S3_backup_file=1"
        )
    mssql_ready(conn, dbs)
    conn.close()


def mssql_restore(
    target_mssql_host, target_mssql_user, target_mssql_password, dbs, source_system_s3
):
    date_object = str(datetime.date.today())
    conn = pymssql.connect(  # type: ignore
        target_mssql_host, target_mssql_user, target_mssql_password
    )
    mssql_ready(conn, dbs)
    conn.autocommit(True)
    cur = conn.cursor()
    for d in dbs:
        try:
            cur.execute(f"EXEC msdb.dbo.rds_drop_database N'{d}'")
        except:
            pass
    mssql_ready(conn, dbs)
    for d in dbs:
        sql = f"EXEC msdb.dbo.rds_restore_database @restore_db_name='{d}', @s3_arn_to_restore_from='arn:aws:s3:::{source_system_s3}/{d}_{date_object}.bak'"
        cur.execute(
            f"EXEC msdb.dbo.rds_restore_database @restore_db_name='{d}', @s3_arn_to_restore_from='arn:aws:s3:::{source_system_s3}/{d}_{date_object}.bak'"
        )
    mssql_ready(conn, dbs)
    conn.close()


class Plugin:

    def process(self, source_vars, target_vars, dbs):
        logging.info("mssql backup")

        target_mssql_host = "sdaas"
        target_mssql_user = "sdaas"
        target_mssql_password = "sdaas"

        source_mssql_host = "sdaas"
        source_mssql_user = "sdaas"
        source_mssql_password = "sdaas"

        source_system_s3 = "sdaas"

        mssql_backup(
            source_mssql_host,
            source_mssql_user,
            source_mssql_password,
            dbs,
            source_system_s3,
        )
        mssql_restore(
            target_mssql_host,
            target_mssql_user,
            target_mssql_password,
            dbs,
            source_system_s3,
        )
