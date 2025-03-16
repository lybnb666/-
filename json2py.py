#抛出异常提示错误信息
def err(msg):
    raise Exception(msg)

#创建token
def mark_token(tag, val=None):
    return [tag, val]

#获取token的标签
def token_tag(token):
    return token[0]

#获取token的值
def token_val(token):
    return token[1]

#逐个字符读取输入字符串
def make_str_reader(s):
    pos = -1
    cur = None

    def peek():
        return cur

    def next():
        nonlocal cur, pos

        old = cur

        pos = pos + 1
        if pos >= len(s):
            cur = 'eof'
        else:
            cur = s[pos]

        return old

    def match(c):
        if c != peek():
            err(f'期望{c},实际为{peek()}')

        return next()

    next()

    return peek, match, next

#词法分析器 将输入字符串转换为token列表 跳过空白字符 识别字符串、数字、关键字（true/false/null）、符号
def lexer(prog):
    peek, match, next = make_str_reader(prog)

    def skip_ws():
        while peek() in [' ', '\t', '\r', '\n']:
            next()

    def json_tokens():
        # 由很多token组成 直到碰到eof

        r = []

        while True:
            skip_ws()

            if peek() == 'eof':
                break

            t = token()
            r.append(t)

        return r

    #处理符号
    def token():

        c = peek()

        if c == '"':
            return string()

        if isdigit(c) or c == '-':
            return num()

        if c in ['[', ']', ',', '{', '}', ':']:
            next()
            return mark_token(c)

        # c是true，false和null的情况
        if c in ['t', 'f', 'n']:
            return keywords()

        err(f'非法字符{c}')

    #处理关键字
    def keywords():

        c = next()

        if c == 't':
            match('r')
            match('u')
            match('e')
            return mark_token('true')

        if c == 'f':
            match('a')
            match('l')
            match('s')
            match('e')
            return mark_token('false')

        if c == 'n':
            match('u')
            match('l')
            match('l')
            return mark_token('null')

        err(f'非法字符{c}')

    def isdigit(c):
        return c >= '0' and c <= '9'

    #处理数字 修改后 按照词法标准
    def num():
        num_str = []

        # 处理负号
        if peek() == '-':
            num_str.append(next())

        # 处理整数部分
        if peek() == '0':
            num_str.append(next())
            # 前导零后不能接数字
            if isdigit(peek()):
                err("前导零后不能有其他数字")
        else:
            # 必须有至少一个数字
            if not isdigit(peek()):
                err("无效的数字格式")
            while isdigit(peek()):
                num_str.append(next())

        # 处理小数部分
        if peek() == '.':
            num_str.append(next())
            # 必须接至少一个数字
            if not isdigit(peek()):
                err("小数部分缺少数字")
            while isdigit(peek()):
                num_str.append(next())

        # 处理指数部分
        if peek().lower() == 'e':
            num_str.append(next())
            # 处理指数符号
            if peek() in ['+', '-']:
                num_str.append(next())
            # 必须接至少一个数字
            if not isdigit(peek()):
                err("指数部分缺少数字")
            while isdigit(peek()):
                num_str.append(next())

        # 转换为数字
        try:
            return mark_token('num', float(''.join(num_str)))
        except ValueError:
            err(f"无效的数字格式: {''.join(num_str)}")

    #处理字符串
    def string():

        r = ''

        match('"')

        while peek() != '"' and peek() != 'eof':
            r = r + next()

        match('"')

        return mark_token('string', r)

    return json_tokens()

EOF = mark_token('EOF')


def make_token_reader(tokens):
    pos = -1
    cur = None

    def peek():
        return token_tag(cur)

    def next():
        nonlocal pos, cur
        old = cur
        pos = pos + 1
        if pos >= len(tokens):
            cur = EOF
        else:
            cur = tokens[pos]

        return old

    def match(t):
        if t != peek():
            err(f'期望{t}, 实际是{cur}')

        return next()

    next()
    return peek, next, match

#语法分析器 将token列表解析成Python的数据结构
def parser(tokens):
    peek, next, match = make_token_reader(tokens)

    def json():
        t = peek()

        if t == 'num':
            return token_val(next())

        if t == 'string':
            return token_val(next())

        if t == 'true':
            next()
            return True

        if t == 'false':
            next()
            return False

        if t == 'null':
            next()
            return None

        if t == '[':
            return array()

        if t == '{':
            return object()

        err(f'非法token{t}')

    def array():

        match('[')

        if peek() == ']':
            r = []
        else:
            r = elements()

        match(']')

        return r

    def elements():
        r = []
        r.append(json())

        while peek() == ',':
            match(',')
            r.append(json())

        return r

    def object():
        match('{')

        if peek() == '}':
            r = {}
        else:
            r = pairs()

        match('}')

        return r

    def pair():
        k = token_val(match('string'))
        match(':')
        v = json()

        return (k, v)

    def add_pair(p, r):
        k, v = p
        r[k] = v

    def pairs():
        r = {}

        add_pair(pair(), r)

        while peek() == ',':
            match(',')
            add_pair(pair(), r)

        return r

    return json()

j1 = '[ , ] [true]'
print(lexer(j1))
print(lexer('"hello world"'))

j2 = '1'
j3 = '1.'
j4 = '1.234'
j5 = '[1,2.0,["hello","world"]]'
j6 = '{"name":"张三","age":20,"scores":[null,1,false,true]}'
print(lexer(j6))


# def test(f, cases):
#     total = len(cases)
#     passed = 0
#     failed = 0
#
#     for c in cases:
#         i, o = c
#         if f(i) == o:
#             passed = passed + 1
#         else:
#             failed = failed + 1
#
#     print(f'总共{total}: 通过{passed}, 失败{failed}')
#
# cases = [
#     ('1',[['num', 1.0]]),
#     ('[]',[['[', None], [',',None]]),
# ]
#
# print(test(lexer, cases))

def json2py(s):
    tokens = lexer(s)
    v = parser(tokens)
    return v

print(json2py(j5))