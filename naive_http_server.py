import asyncio
import traceback
import datetime
import re
import uuid

STATUS_CODES = {
    200:"OK",
    303:"See Other",
    400:"Bad Request",
    403:"Forbidden",
    404:"Not Found",
    500:"Internal Server Error",
}

SESSION = { # セッションを管理するグローバル変数

}

class Article(object):
    def __init__(self, article_id, title, body, user):
        self.article_id = article_id
        self.title = title
        self.body = body
        self.date = datetime.datetime.now()
        self.user = user

class User(object):
    def __init__(self, name):
        self.name = name

class DBM(object):
    def __init__(self):
        self.articles = [
            Article(1, "あああ", "いいい", "sato"),
            Article(2, "ううう", "えええ", "takahashi")
        ]
        self.article_id_max = 2

        self.users = [
            User("sato"),
            User("takahashi")
        ]

    def add_article(self, title, body, user_name):
        self.article_id_max = self.article_id_max + 1
        article = Article(self.article_id_max, title, body, user_name)
        self.articles.append(article)
        return article

    def delete_article(self, article_id):
        target_idx = None
        for i, article in enumerate(self.articles):
            if article.article_id == article_id:
                target_idx = i
                break
        if target_idx is None:
            return False
        else:
            del self.articles[target_idx]
            return True

    def get_article(self, article_id):
        for article in self.articles:
            if article.article_id == article_id:
                return article
        return None

    def get_articles(self):
        return self.articles

    def get_user(self, user_name):
        for user in self.users:
            if user_name == user.name:
                return user
        return None

class NaiveHttpResponse(object):
    dbm = DBM()

    @classmethod
    def header_lines(cls, request, data=None):
        header = ['Content-Type: text/html']
        if request["cookie"] is None:
            now = datetime.datetime.now()
            now - datetime.timedelta(hours=9) + datetime.timedelta(minutes=1)
            cstr = 'Set-Cookie: SESSION_ID={}; expires={}; path=/;'.format(
                str(uuid.uuid4()), now.strftime("%a, %d-%h-%Y %H:%M:%S GMT"))
            header.append(cstr)
        if data:
            for k, v in data.items():
                header.append("{}: {}".format(k,v))
        return header

    @classmethod
    def status_line(cls, status_code):
        return "HTTP/1.1 {} {}".format(
            str(status_code), STATUS_CODES[status_code]
        )

    @classmethod
    def get_request_user(cls, request):
        user = None
        if request["cookie"]:
            session_id = request["cookie"]["key_values"].get("SESSION_ID")
            if session_id and SESSION.get(session_id):
                user = cls.dbm.get_user(SESSION[session_id])
        return user

    @classmethod
    def start_session(cls, request, user):
        if user and request["cookie"] and request["cookie"]["key_values"].get("SESSION_ID"):
            SESSION[request["cookie"]["key_values"]["SESSION_ID"]] = user.name
            return True
        return False

    @classmethod
    def delete_session(cls, request):
        if request["cookie"]:
            session_id = request["cookie"]["key_values"].get("SESSION_ID")
            if session_id and SESSION.get(session_id):
                del SESSION[session_id]
                return True
        return False

    @classmethod
    def http500(cls):
        result = '\r\n'.join([
            'HTTP/1.1 500 Internal Server Error',
            'Content-Type: text/html',
            '',
            '<!DOCTYPE HTML>',
            '<html lang="ja">',
            '<head></head>',
            '<body>Internal Server Error</body>',
            '</html>'
        ])
        return result

    @classmethod
    def http404(cls):
        result = '\r\n'.join([
            'HTTP/1.1 404 Not Found',
            '',
            '<!DOCTYPE HTML>',
            '<html lang="ja">',
            '<head>',
            '<meta charset="UTF-8">',
            '</head>',
            '<body>Not Found</body>',
            '</html>'
        ])
        return result

    @classmethod
    def http400(cls):
        result = '\r\n'.join([
            'HTTP/1.1 400 Bad Request',
            'Content-Type: text/html',
            '',
            '<!DOCTYPE HTML>',
            '<html lang="ja">',
            '<head>',
            '<meta charset="UTF-8">',
            '</head>',
            '<body>Bad Request</body>',
            '</html>'
        ])
        return result


    def create_response(self, request):
        if (request["path"] == []):
            return self.redirect_index(request)
        elif (request["method"] == "POST") and (request["path"] == ["login"]):
            return self.login(request)
        elif (request["method"] == "POST") and (request["path"] == ["logout"]):
            return self.logout(request)
        elif (request["method"] == "GET") and (request["path"] == ["articles"]):
            return self.index(request)
        elif (request["method"] == "GET") and (len(request["path"]) == 2) and (request["path"][0] == "users"):
            return self.user_page(request, request["path"][1])
        elif (request["method"] == "POST") and (request["path"] == ["articles"]):
            return self.post_articles(request)
        elif (request["method"] == "POST") and (request["path"] == ["articles", "delete"]):
            article_id = int(request["data"].get("article_id"))
            return self.delete_article(request, article_id)
        else:
            return self.http404()

    def login(self, request):
        if request["data"].get("user_name"):
            user = self.dbm.get_user(request["data"]["user_name"])
            if user:
                result = self.start_session(request, user)
                if result:
                    hdata = {'Location': 'http://localhost:8000/users/{}'.format(user.name)}
                    result = '\r\n'.join(
                        [self.status_line(303)] + self.header_lines(request, hdata) + ['']
                    )
                    return result
        return self.http400()

    def logout(self, request):
        self.delete_session(request)
        return self.redirect_index(request)

    def redirect_index(self, request):
        hdata = {'Location': 'http://localhost:8000/articles/'}
        result = '\r\n'.join(
            [self.status_line(303)] + self.header_lines(request, hdata) + ['']
        )
        return result

    def index(self, request):
        request_user = self.get_request_user(request)

        table = '''
        <table>
        <tr>
        <th>User</th>
        <th>Title</th>
        <th>Body</th>
        <th>Date</th>
        <th></th>
        </tr>
        '''
        for article in self.dbm.get_articles():
            table += '''
            <tr>
            <td><a href="http://localhost:8000/users/{}">{}</a></td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>
            <form method="POST" action="/articles/delete">
            <input type="hidden" name="article_id" value="{}" />
            <input type="submit" value="削除" />
            </form>
            </td>
            </tr>
            '''.format(article.user, article.user, article.title, article.body, str(article.date), article.article_id)
        table += '</table>'

        article_form = ''
        if request_user is not None:
            article_form = '''
            <form method="POST" action="/articles">
            <input type="text" name="title" />
            <input type="text" name="body" />
            <input type="submit" value="送信" />
            </form>
            '''

        mypage = ''
        if request_user is not None:
            mypage = '<a href="http://localhost:8000/users/{}">マイページ</a>'.format(
                request_user.name)

        logout_form = ''
        if request_user is not None:
            logout_form = '''
            <form method="POST" action="/logout">
            <input type="submit" value="ログアウト" />
            </form>
            '''

        login_form = ''
        if request_user is None:
            login_form = '''
            <form method="POST" action="/login">
            <input type="text" name="user_name" />
            <input type="submit" value="ログイン" />
            </form>
            '''

        content = [
            '<!DOCTYPE HTML>',
            '<html lang="ja">',
            '<head>',
            '<meta charset="UTF-8">',
            '</head>',
            '<body>',
            table,
            article_form,
            mypage,
            logout_form,
            login_form,
            '</body>',
            '</html>'
        ]

        result = '\r\n'.join(
            [self.status_line(200)] + self.header_lines(request) + [''] + content
        )
        return result

    def delete_article(self, request, article_id):
        user = self.get_request_user(request)
        article = self.dbm.get_article(article_id)

        if article is None:
            return self.http404()

        elif (user is not None) and (user.name == article.user):
            result = self.dbm.delete_article(article_id)
            return self.index(request)
        return self.http400()

    def post_articles(self, request):
        user = self.get_request_user(request)
        if request["data"].get("title") and request["data"].get("body") and user:
            article = self.dbm.add_article(
                request["data"]["title"], request["data"]["body"], user.name)
            return self.index(request)
        else:
            return self.http400()


    def user_page(self, request, target_user_name):
        target_user = self.dbm.get_user(target_user_name)
        if target_user is None:
            return self.http404()
        request_user = self.get_request_user(request)
        is_mypage = False
        if (request_user is not None) and (request_user.name == target_user.name):
            is_mypage = True

        table = '''
        <table>
        <tr>
        <th>User</th>
        <th>Title</th>
        <th>Body</th>
        <th>Date</th>
        <th></th>
        </tr>
        '''
        for article in self.dbm.get_articles():
            if article.user != target_user.name:
                continue
            delform = ''
            if is_mypage:
                delform = '''
                <form method="POST" action="/articles/delete">
                <input type="hidden" name="article_id" value="{}" />
                <input type="submit" value="削除" />
                </form>
                '''.format(article.article_id)
            table += '''
            <tr>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            </tr>
            '''.format(article.user, article.title, article.body, str(article.date), delform)
        table += '</table>'

        article_form = ''
        if is_mypage:
            article_form = '''
            <form method="POST" action="/articles">
            <input type="text" name="title" />
            <input type="text" name="body" />
            <input type="submit" value="送信" />
            </form>
            '''
        content = [
            '<!DOCTYPE HTML>',
            '<html lang="ja">',
            '<head>',
            '<meta charset="UTF-8">',
            '</head>',
            '<body>',
            table,
            article_form,
            '<div><a href="http://localhost:8000/">トップ</a></div>'
            '</body>',
            '</html>'
        ]

        result = '\r\n'.join(
            [self.status_line(200)] + self.header_lines(request) + [''] + content
        )
        return result

class NaiveHttpParser(object):
    @classmethod
    def unquote(cls, inputstr):
        s = bytes()
        i = 0
        while i < len(inputstr):
            if inputstr[i] == "%":
                s += int(inputstr[i+1:i+3], base=16).to_bytes(1, "little")
                i += 3
            else:
                s += inputstr[i].encode("ascii")
                i += 1
        return s.decode("utf-8")

    @classmethod
    def parse_path(cls, path_str):
        return [unit for unit in path_str.split("/") if bool(unit)]

    @classmethod
    def parse_query(cls, query):
        result = {}
        for kv_str in query.split("&"):
            kv = kv_str.split("=")
            if len(kv) != 2:
                raise cls.ParseError()
            result[cls.unquote(kv[0])] = cls.unquote(kv[1])
        return result

    @classmethod
    def _set_header_data(cls, result, key, value):
        if key == "Cookie":
            result["cookie"] = cls.parse_cookie(value)

    @classmethod
    def parse_cookie(cls, cookie_str):
        key_values = {}
        metadata = {"expires": None, "domain": None, "path":None, "secure":None}

        for cookie_content in cookie_str.split("; "):
            if cookie_content == "secure":
                metadata["secure"] = True
            else:
                ckv = cookie_content.split("=")
                if len(ckv) != 2:
                    raise cls.ParseError()
                elif ckv[0] in metadata:
                    metadata[ckv[0]] = ckv[1]
                else:
                    key_values[ckv[0]] = ckv[1]
        if not key_values:
            raise cls.ParseError()
        return {"key_values": key_values, "metadata": metadata}

    @classmethod
    def add_dict(cls, d_target, d_source):
        for k,v in d_source.items():
            d_target[k] = v

    @classmethod
    def parse_request(cls, message):
        result = {
            "method": None,
            "path": [],
            "query": {},
            "data": {},
            "cookie": None,
            "header": {},
        }

        lines = list(message.splitlines())
        req = lines[0].split(" ")
        try:
            if len(req) != 3:
                raise cls.ParseError()

            if req[0] not in ["get", "post", "GET", "POST"]:
                raise cls.ParseError()
            result["method"] = req[0].upper()

            url = req[1].split("?")
            if len(url) == 1:
                result["path"] = cls.parse_path(url[0])
            elif len(url) == 2:
                result["path"] = cls.parse_path(url[0])
                result["query"] = cls.parse_query(url[1])
            else:
                raise cls.ParseError()

            is_header = True
            for line in lines[1:]:
                if not line:
                    is_header = False
                elif is_header:
                    match = re.match("[^:]+:", line)
                    if match:
                        hkey = line[:match.end()-1]
                        vstart = match.end()
                        while line[vstart] == " ":
                            vstart += 1
                        hvalue = line[vstart:]
                        result["header"][hkey] = hvalue
                        cls._set_header_data(result, hkey, hvalue)
                else:
                    cls.add_dict(result["data"], cls.parse_query(line))

        except (cls.ParseError, ValueError):
            return None
        return result
    class ParseError(Exception):
        pass

class NaiveHttpServerProtocol(asyncio.Protocol):
    nhr = NaiveHttpResponse()
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        try:
            message = data.decode()
            request = NaiveHttpParser.parse_request(message)
            if request is None:
                response = self.nhr.http500()
            else:
                response = self.nhr.create_response(request)
        except Exception as e:
            print(traceback.format_exc())
            response = self.nhr.http500()
        else:
            print('RECEIVE--------------------------')
            for mline in message.splitlines():
                print(mline)
                print('---------------------------------')
            print('RESPONSE-------------------------')
            for line in response.splitlines():
                if not line:
                    break
                print(line)
            print('---------------------------------')

        self.transport.write(response.encode("utf-8"))
        self.transport.close()

loop = asyncio.get_event_loop()
# Each client connection will create a new protocol instance
#coro = loop.create_server(EchoServerClientProtocol, '127.0.0.1', 8000)
coro = loop.create_server(NaiveHttpServerProtocol, '0.0.0.0', 8000)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
