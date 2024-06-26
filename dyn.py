import http.client
import json
import requests
import time
import datetime

# the following 4 are the actual values that pertain to your account and this specific metric
api_key = "ee150bc57fa5433782d96bf7c27dd0de"
page_id = "k5mqbzqf801p"
metric_id = "h8nxskkx5j1w"
api_base = "api.statuspage.io"


def fetch_dynatrace_metrics() -> tuple:
    base_url = "https://for07279.live.dynatrace.com/api/v2/metrics/query"
    params = {
        "metricSelector": "builtin:synthetic.http.availability.location.total:"
        "splitBy(dt.entity.http_check):fold:names",
        "from": "now-5m",
    }
    headers = {
        "Authorization": "Api-Token "
    }

    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        metric_data = response.json()["result"][0]["data"]
        for entry in metric_data:
            if "digital.firsthorizon.com" in entry["dimensionMap"].values():
                fhn_value, fhn_timestamps = entry["values"][0], entry["timestamps"][0]
                fhn_timestamps = fhn_timestamps / 1000
                return fhn_value, fhn_timestamps
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Dynatrace metrics: {e}")
        return None, None


# need 1 data point every 5 minutes
# submit random data for the whole day
def send_metrics_to_statuspage(fhn_value: float, fhn_timestamps: int) -> None:
    ts = int(time.time()) - (1 * 5 * 60)
    params = json.dumps({"data": {"timestamp": ts, "value": fhn_value}})
    headers = {
        "Content-Type": "application/json",
        "Authorization": "OAuth " + api_key,
    }
    conn = http.client.HTTPSConnection(api_base)
    conn.request(
        "POST",
        "/v1/pages/" + page_id + "/metrics/" + metric_id + "/data.json",
        params,
        headers,
    )
    response = conn.getresponse()

    if not (response.status >= 200 and response.status < 300):
        genericError = "Error encountered. Please ensure that your page code and authorization key are correct."
        print(genericError)
    else:
        print("Submitted point ")
        time.sleep(1)


def main() -> None:
    value, timestamp = fetch_dynatrace_metrics()
    if value is not None and timestamp is not None:
        send_metrics_to_statuspage(value, timestamp)


if __name__ == "__main__":
    main()
