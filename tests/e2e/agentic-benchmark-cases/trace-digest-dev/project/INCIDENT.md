# Invoice retry incident

The first delivery returned HTTP 503. A retry was queued, but no provider
receipt was captured. The local queue entry is now marked sent. Provider-side
delivery remains unverified.
