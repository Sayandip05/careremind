"""
Worker module — Celery app and background task definitions.
All tasks live here so the worker container builds from the same
image as the API server (true modular monolith, no sys.path hacks).
"""
