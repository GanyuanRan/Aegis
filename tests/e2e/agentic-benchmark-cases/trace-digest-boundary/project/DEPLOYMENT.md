# Deployment observations

The build registry reports digest `8f21`. The orchestrator recorded rollout ID
204, but only four of five regions appear in its summary. The provider audit
API was unavailable, and the local account cannot query the missing region.
