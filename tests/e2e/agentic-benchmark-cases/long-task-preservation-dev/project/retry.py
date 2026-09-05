"""Retry policy lookups used by the job runner."""

from config import resolve_profile
from services import SERVICES


def attempts_for(service_name):
    return resolve_profile(SERVICES[service_name]["profile"])["attempts"]


def backoff_for(service_name):
    return resolve_profile(SERVICES[service_name]["profile"])["backoff_seconds"]
