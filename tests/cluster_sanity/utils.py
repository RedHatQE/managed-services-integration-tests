import logging

TIMEOUT_3MIN = 3*60

LOGGER = logging.getLogger(__name__)

def verify_no_listed_alerts_on_cluster(prometheus, alerts_list):
    """
    It gets a list of alerts and verifies that none of them are firing on a cluster.
    """
    fired_alerts = {}
    for alert in alerts_list:
        
        alert_state = prometheus.get_alert(alert=alert)
        
        if alert_state and alert_state[0]["metric"]["alertstate"] == "firing":
            fired_alerts[alert] = alert_state
    assert (
        not fired_alerts
    ), f"Alerts should not be fired on healthy cluster.\n {fired_alerts}"

def verify_prometheus_connection(prometheus,query):
    response = prometheus.query(query=query)
    LOGGER.info(f'\n query response: \t {(response["data"]["result"])}')
    assert response["status"] == "success"
