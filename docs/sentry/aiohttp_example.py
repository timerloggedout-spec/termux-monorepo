#!/usr/bin/env python3
"""Minimal aiohttp + Sentry verify app (project 4511844256055296)."""
from aiohttp import web
import sentry_sdk

sentry_sdk.init(
    dsn="https://c7fb0bb5cf4210fae90119131c12b320@o4511844213522432.ingest.us.sentry.io/4511844256055296",
    send_default_pii=True,
    enable_logs=True,
    traces_sample_rate=1.0,
    profile_session_sample_rate=1.0,
    profile_lifecycle="trace",
)


async def hello(request):
    1 / 0  # intentional — appears in Sentry linked to the transaction
    return web.Response(text="Hello, world")


app = web.Application()
app.add_routes([web.get("/", hello)])

if __name__ == "__main__":
    web.run_app(app)
