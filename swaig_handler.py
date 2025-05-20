from flask import request
import json
import io

def transform_swaig_request(request):
    """
    Transform incoming SWAIG requests to ensure proper argument structure for endpoint dispatch.
    """
    if request.method == 'POST' and request.path == '/swaig':
        try:
            if request.is_json:
                data = request.get_json(silent=True)
                if data and 'function' in data:
                    function_name = data['function']
                    # Normalize to always have an 'arguments' key
                    if 'arguments' in data:
                        args = dict(data['arguments'])
                    else:
                        args = {k: v for k, v in data.items() if k not in ('function', 'argument', 'meta_data', 'meta_data_token')}
                    new_data = {
                        'function': function_name,
                        'arguments': args
                    }
                    # Log the transformed payload
                    with open('swaig_debug_payload.json', 'a') as f:
                        f.write('NORMALIZED: ' + json.dumps(new_data) + '\n')
                    # Update the request
                    request._cached_json = {True: None, False: None}
                    json_data = json.dumps(new_data)
                    request.environ['wsgi.input'] = io.BytesIO(json_data.encode('utf-8'))
                    request.environ['CONTENT_LENGTH'] = str(len(json_data))
                    request.environ['CONTENT_TYPE'] = 'application/json'
                    request._cached_json[True] = new_data
                    request._cached_json[False] = new_data
                    return True
        except Exception as e:
            with open('swaig_debug_payload.json', 'a') as f:
                f.write(f'ERROR: {str(e)}\n')
    return False 