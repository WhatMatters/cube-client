import requests
import json
from datetime import datetime

API_VERSION = "1.0"

class Cube:
  def __init__(self, hostname="localhost", **kwargs):
    self.collector_url = "http://%s:%s/%s/" % (hostname, \
                          kwargs.get("collector_port", 1080), API_VERSION)
    self.evaluator_url = "http://%s:%s/%s/" % (hostname, \
                          kwargs.get("evaluator_port", 1081), API_VERSION)

  @classmethod
  def build_event(cls, event_type, event_data={}, **kwargs):
    """
    Build an event hash ready for putting
    """
    event = dict(type=event_type, data=event_data)

    event["time"] = kwargs.get("time", datetime.utcnow().isoformat())

    if kwargs.get("id"):
        event["id"] = kwargs.get("id")

    return event

  def puts(self, events):
    """
    Create/update events
    """
    ready_events = []
    for e in events:
      if type(e) != dict:
        event_type = e[0]
        event_data = {}
        event_kwargs = {}

        if len(e) > 1:
          event_data = e[1]
        if len(e) > 2:
          event_kwargs = e[2]

        ready_events.append(self.build_event(event_type, event_data, **event_kwargs))
      else:
        ready_events.append(e)

    data = json.dumps(ready_events)
    r = requests.post(self.collector_url + "event/put", data=data,
                      headers={'content-type': 'application/json'})
    r.raise_for_status()

    return ready_events

  def put(self, event_type, event_data={}, **kwargs):
    """
    Create/update an event.
    """
    event = dict(type=event_type, data=event_data)

    event["time"] = kwargs.get("time", datetime.utcnow().isoformat())

    if kwargs.get("id"):
      event["id"] = kwargs.get("id")

    data = json.dumps([event])

    r = requests.post(self.collector_url + "event/put", data=data,
                      headers={'content-type': 'application/json'})
    r.raise_for_status()

    return [event]

  def make_query(self, query_type, expression, **kwargs):
    data = dict(expression=expression,
          stop=kwargs.get("stop", datetime.utcnow().isoformat()))

    if kwargs.get("start"):
      data["start"] = kwargs.get("start")

    if kwargs.get("limit"):
      data["limit"] = kwargs.get("limit")

    if query_type == "metric" and kwargs.get("step"):
      data["step"] = kwargs.get("step")

    r = requests.get(self.evaluator_url + query_type, params=data)
    r.raise_for_status()

    return r.json

  def event(self, expression, **kwargs):
    """
    Query with an event expression
    """
    return self.make_query("event", expression, **kwargs)

  def metric(self, expression, **kwargs):
    """
    Query with a metric expression
    """
    return self.make_query("metric", expression, **kwargs)

  def types(self):
    """
    List of the known event types
    """
    r = requests.get(self.evaluator_url + "types")
    r.raise_for_status()
    return r.json
