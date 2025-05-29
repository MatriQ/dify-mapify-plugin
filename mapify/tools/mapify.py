import os
import re
import requests
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

MAPIFY_API_KEY = os.getenv('MAPIFY_API_KEY', '')
MAPIFY_API_URL = 'https://api.mapify.so/api/v1/mindmaps'

YOUTUBE_REGEX = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/')
WEB_URL_REGEX = re.compile(r'https?://')

class MapifyTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        query = tool_parameters.get('query', '').strip()
        language = tool_parameters.get('language', 'en')
        style = tool_parameters.get('style', 'default')
        if not query:
            yield self.create_json_message({
                'error': 'Query is required.'
            })
            return

        # Determine content type
        if YOUTUBE_REGEX.search(query):
            content_type = 'youtube'
        elif WEB_URL_REGEX.match(query):
            content_type = 'web'
        else:
            content_type = 'text'

        payload = {
            'content': query,
            'language': language,
            'style': style,
            'type': content_type
        }
        headers = {
            'Authorization': f'Bearer {MAPIFY_API_KEY}',
            'Content-Type': 'application/json'
        }
        try:
            resp = requests.post(MAPIFY_API_URL, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            # Expecting keys: image_url, edit_url, id, etc.
            result = {
                'image_url': data.get('image_url'),
                'edit_url': data.get('edit_url'),
                'id': data.get('id'),
                'meta': data.get('meta', {}),
                'raw': data
            }
            yield self.create_json_message(result)
        except Exception as e:
            yield self.create_json_message({
                'error': f'Failed to generate mind map: {str(e)}'
            })
