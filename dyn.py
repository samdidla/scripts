import requests
import json
from datetime import datetime, timedelta

API_URL = "https://for07279.live.dynatrace.com/api/v2/metrics/query"
STATUSPAGE_API_URL = (
    "https://api.statuspage.io/v1/pages/k5mqbzqf801p/metrics/h8nxskkx5j1w/data"
)
API_KEY = "ee150bc57fa5433782d96bf7c27dd0de"


def fetch_dynatrace_metrics():
    headers = {
        "Authorization": "Api-Token dt0c01.MNVY3YS2DQDMZKNFNHEBNEIU.GGCFRYXJL5VP5JYRAHWTKPZP3575PZBDXTDMQRE7ZGA7DW3RPJ2K2XBCDOMLGGLS",
        "Content-Type": "application/json",
    }
    now = datetime.now()
    start_time = (now - timedelta(minutes=5)).isoformat()
    request_body = {
        "timeseriesId": "com.dynatrace.builtin:host.cpu.usage",
        "aggregationType": "AVG",
        "startTimestamp": start_time,
        "endTimestamp": now.isoformat(),
        "resolution": "INF",
    }
    response = requests.post(API_URL, headers=headers, json=request_body)
    response.raise_for_status()
    return response.json()


def send_metrics_to_statuspage(metrics):
    headers = {
        "Authorization": f"OAuth {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "data": [
            {
                "timestamp": metrics["result"][0]["from"],
                "value": metrics["result"][0]["dataPoints"][0]["value"],
            }
        ]
    }
    response = requests.post(STATUSPAGE_API_URL, headers=headers, json=payload)
    response.raise_for_status()


def main():
    metrics = fetch_dynatrace_metrics()
    send_metrics_to_statuspage(metrics)


if __name__ == "__main__":
    main()
