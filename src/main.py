from datetime import datetime, timedelta
import croniter
from zoneinfo import ZoneInfo
import dat_client
from dat_client.configuration import Configuration


def get_x_till_next_run(next_run_time, connection_time, x='minutes'):
    '''
    Get timedelta b/w next_run_time and connection_time
    Divide it by 60 to get minutes
    Args:
        next_run_time (datetime.datetime)
        connection_time (datetime.datetime) 
        x (str): time entity (minutes | hours | seconds)
    '''
    _divisor_map = {
        'hours': 60*60,
        'minutes': 60,
        'seconds': 1,
    }
    divisor = _divisor_map[x]
    n_days = (next_run_time - connection_time).days
    n_seconds = (n_days * 24 * 60 * 60) + \
        (next_run_time - connection_time).seconds
    return int(n_seconds / divisor)


def is_it_time(connection) -> bool:
    current_time_tz = datetime.now(ZoneInfo('UTC'))
    connection_tz = connection.schedule.cron.timezone
    connection_time = current_time_tz.astimezone(ZoneInfo(connection_tz))
    connection_time_1_min_ago = connection_time - timedelta(minutes=1)
    # connection_time_1_min_ago needs to be used instead of connection_time
    # because connection_time has already passed and next run will show next day
    # E.g. if a run is scheduled at 0823 and we check for the run at 0823
    # then next run for it will be shown next day
    cron_str = connection.schedule.cron.cron_expression
    next_run_time = croniter.croniter(
        cron_str, connection_time_1_min_ago).get_next(datetime)
    minutes_till_next_run = get_x_till_next_run(
        next_run_time, connection_time_1_min_ago, x='minutes')
    if minutes_till_next_run == 0:  # run scheduled for current minute
        return True
    return False


def main() -> None:
    with dat_client.ApiClient(
        Configuration(
            host="http://api:8000",
        )
    ) as api_client:
        connection_api_instance = dat_client.ConnectionsApi(
            api_client)
        connections = connection_api_instance.fetch_available_connections_connections_list_get()
        active_connections = [
            _c for _c in connections
            if _c.status.lower() == 'active']
        for a_c in active_connections:
            if not is_it_time(a_c):
                continue
            api_response = connection_api_instance.connection_trigger_run_connections_connection_id_run_post(
                connection_id=a_c.id)
            print(datetime.now(), api_response)


if __name__ == '__main__':
    main()
