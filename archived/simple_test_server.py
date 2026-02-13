"""
Simple test server to verify if there are any issues with the aiohttp setup
"""

from aiohttp import web
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def hello(request):
    return web.Response(text="Hub UI Test Server is Working!", content_type='text/plain')

async def index(request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CLAWDBOT HUB - Test Page</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #0f172a; color: white; }
            .container { max-width: 800px; margin: 0 auto; }
            .status { background: #1e293b; padding: 20px; border-radius: 8px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>CLAWDBOT HUB UI Test</h1>
            <div class="status">
                <h2>Server Status: Operational</h2>
                <p>The Hub UI server is running correctly.</p>
            </div>
            <p>If you see this page, the server is working but there may be an issue with the full UI files.</p>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')

app = web.Application()
app.router.add_get('/', index)
app.router.add_get('/test', hello)

if __name__ == '__main__':
    web.run_app(app, host='localhost', port=8083)