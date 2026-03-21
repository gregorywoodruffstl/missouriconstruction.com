"""
GPT-4o Vision utility for auto-tagging user-uploaded city images.
Called after an image is saved to Azure Blob Storage.
"""
import os
import re
from openai import OpenAI


def analyze_image(image_url: str) -> dict:
    """
    Pass a public image URL to GPT-4o Vision.
    Returns a dict with keys: description (str), tags (list), flagged (bool).
    On any failure returns safe defaults so the upload still succeeds.
    """
    api_key = os.getenv('OPENAI_API_KEY', '')
    if not api_key:
        return {'description': '', 'tags': [], 'flagged': False}

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[{
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': (
                            'Analyze this image. '
                            'First, write one sentence describing what you see. '
                            'Then list up to 10 comma-separated tags (landmarks, people, objects, activities, mood). '
                            'Finally, reply YES or NO: does this image contain nudity, violence, or inappropriate content? '
                            'Format exactly:\n'
                            'DESCRIPTION: <sentence>\n'
                            'TAGS: <tag1>, <tag2>, ...\n'
                            'FLAGGED: <YES or NO>'
                        ),
                    },
                    {
                        'type': 'image_url',
                        'image_url': {'url': image_url},
                    },
                ],
            }],
            max_tokens=300,
        )

        text = response.choices[0].message.content or ''

        description = ''
        tags = []
        flagged = False

        for line in text.splitlines():
            line = line.strip()
            if line.upper().startswith('DESCRIPTION:'):
                description = line.split(':', 1)[1].strip()
            elif line.upper().startswith('TAGS:'):
                raw_tags = line.split(':', 1)[1].strip()
                tags = [t.strip().lower() for t in raw_tags.split(',') if t.strip()]
            elif line.upper().startswith('FLAGGED:'):
                flagged = 'YES' in line.upper()

        return {'description': description, 'tags': tags, 'flagged': flagged}

    except Exception:
        return {'description': '', 'tags': [], 'flagged': False}
