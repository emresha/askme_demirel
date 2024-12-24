def test(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'text/plain; charset=utf-8')]
    start_response(status, headers)

    def url_decode(s):
        result = {}
        pairs = s.split('&') if s else []
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                key = pair_split_decode(key)
                value = pair_split_decode(value)
                if key in result:
                    result[key].append(value)
                else:
                    result[key] = [value]
            else:
                key = pair_split_decode(pair)
                if key in result:
                    result[key].append('')
                else:
                    result[key] = ['']
        return result

    def pair_split_decode(s):
        result = ''
        i = 0
        while i < len(s):
            if s[i] == '+':
                result += ' '
            elif s[i] == '%' and i + 2 < len(s):
                hex_value = s[i+1:i+3]
                try:
                    result += chr(int(hex_value, 16))
                    i += 2
                except ValueError:
                    result += '%'
            else:
                result += s[i]
            i += 1
        return result

    query_string = environ.get('QUERY_STRING', '')
    get_params = url_decode(query_string)

    post_params = {}
    try:
        content_length = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError, TypeError):
        content_length = 0

    if environ.get('REQUEST_METHOD', '').upper() == 'POST' and content_length > 0:
        try:
            body = environ['wsgi.input'].read(content_length).decode('utf-8')
            post_params = url_decode(body)
        except Exception:
            post_params = {}

    print("Новый запрос.")
    print("Метод:", environ.get('REQUEST_METHOD', ''))
    print("GET параметры:")
    if get_params:
        for key, values in get_params.items():
            for value in values:
                print(f"  {key}: {value}")
    else:
        print("  Нет GET параметров.")

    print("POST параметры:")
    if post_params:
        for key, values in post_params.items():
            for value in values:
                print(f"  {key}: {value}")
    else:
        print("  Нет POST параметров.")
    print("------------------------\n")

    response_body = "Параметры получены"
    return [response_body.encode('utf-8')]

application = test