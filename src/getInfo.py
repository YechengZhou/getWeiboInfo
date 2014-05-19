# -*- coding: utf-8 -*-
# 上面这行不要删 否则所有的中文注释都会报错

import weibo  # http://michaelliao.github.com/sinaweibopy/  这个是一个sina api包 需要安装
import urllib
import urllib2
import sys
"""
import chilkat
import cookielib
from sgmllib import SGMLParser
import re
import cookielib
from lxml import html as HTML
"""
import WeiboMain



try:
    import logging
    import os
    logging.basicConfig(filename = os.path.join(os.getcwd(), 'log.txt'),level = logging.INFO, filemode = 'w', format = '%(asctime)s - %(levelname)s: %(message)s')
except ImportError,e:
    print "init logging module failed", e

# APP_KEY和APP_SECRET需要在从注册的微博应用中获取
APP_KEY = '529933965'
APP_SECRET = 'ceb77d069e01ec65572312539ea9c968'  #这个需要注册sina app才可以得到 你可以换成自己的 也可以一直用我的
CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html'
LOGIN_URL = 'https://api.weibo.com/oauth2/authorize'
USER_ID = '' # 用户名（登录邮箱）
USER_PASSWD = '' # 密码
COUNT = 200
USER_NAME = u'ZyC-eThaN' # 需要抓取那个用户的信息 需要和登录信息对应 新浪微博限制了api 只能得到当前登录用户的关注及粉丝信息

client = weibo.APIClient(
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    redirect_uri=CALLBACK_URL
)

# 用得到的url到新浪页面访问
url = client.get_authorize_url()
conn = urllib2.urlopen(url)
params = urllib.urlencode({
    'action': 'submit',
    'withOfficalFlag': '0',
    'ticket': '',
    'isLoginSina': '',
    'response_type': 'code',
    'regCallback': '',
    'redirect_uri': CALLBACK_URL,
    'client_id': APP_KEY,
    'state': '',
    'from': '',
    'userId': USER_ID,
    'passwd': USER_PASSWD
})

header = {
    'Referer': url,
    'Content-Type': 'application/x-www-form-urlencoded'
}

req = urllib2.Request(LOGIN_URL, params, header)
try:
    return_callback_url = urllib2.urlopen(req).geturl()
except urllib2.HTTPError, e:
    return_callback_url = e.geturl()

# 取到返回的code
code = return_callback_url.split('=')[1]
print code

# 新浪返回的token
req = client.request_access_token(code)
access_token = req.access_token
expires_in = req.expires_in

# 设置得到的access_token
client.set_access_token(access_token, expires_in)

##################################### 预备工作结束 ############################

##################################### 函数定义 ################################

# 得到所有的关注用户
def get_all_following():  # 调用API，获得朋友列表
    global client
    next_cursor = -1
    all_following = []
    # 由于每次获得的数据量有限制，需要分批次获取
    while next_cursor != 0:
        response = client.friendships.friends.get(
            screen_name=USER_NAME, count=COUNT, cursor=next_cursor)

        all_f = response.users
        if len(all_f) == 0: break
        all_following += all_f
        next_cursor = response.next_cursor
    return all_following

# 调用get_all_following并得到所有用户的个人主页url
def get_following_user_personal_page():
    global client
    # 生成各个用户的微博主页url
    following_users = get_all_following()
    page_urls = []
    for u in following_users[:10]:
        if u.domain == "":
            page_urls.append(u"http://weibo.com/u/" + str(u.id))
            postfix = str(u.id)
            this_url = u"http://weibo.com/u/" + str(u.id)
        else:
            page_urls.append(u"http://weibo.com/" + u.domain)
            postfix = str(u.domain)
            this_url = u"http://weibo.com/" + u.domain
        print postfix
        print this_url
    return page_urls, following_users

"""
# 得到微博指定用户微博页url前缀， 传入个人主页url
def get_weibo_url_prefix(main_page_url):
    weiboLogin = WeiboMain.WeiboLogin(USER_ID,USER_PASSWD )
    if weiboLogin.Login():
        print "Login successfaully"
    else:
        sys.exit()
    content = urllib2.urlopen(main_page_url).read()
    p_index = content.find('\/p\/')
    p_num = content[p_index + 5:p_index + 5 + 16]
    yuanchuang_url = "http://weibo.com/p/" + p_num + "/weibo?is_search=0&visible=0&is_ori=1&is_tag=0&profile_ftype=1&page="
    print "original:", yuanchuang_url
    return yuanchuang_url
    #p = re.compile(r'\d{16}\\/weibo')
    #p.findall(str(content))
    #temp_str = p.findall(str(content))
    #print main_page_url
    #weibo_page_id =temp_str[0][:16]
    #weibo_url_prefix = "http://weibo.com/p/" + str(weibo_page_id) + "/weibo?is_search=0&visible=0&is_ori=1&is_tag=0&profile_ftype=1&page="
    #weibo_url_prefix = main_page_url + "/weibo?is_search=0&visible=0&is_ori=1&is_tag=0&profile_ftype=1&page="
    #return weibo_url_prefix


# 在抓取类
class WeiboParser(SGMLParser):

    def reset(self):
        self.weibos = []
        self.div_flag = False
        SGMLParser.reset(self)

    def start_div(self, attrs):
        for k,v in attrs:
            if k == 'class' and v == 'WB_text':
                print "nimabia"
                self.div_flag = True
                return

    def end_div(self):
        self.div_flag = False

    def handle_data(self, text):
        if self.div_flag == True:
            print "*"*10 , text
            #b = re.findall(r'.*',text) # return list, list contain only 1 build num
            #b = b[0]
            self.weibos.append(text)

    def printer(self):
        print self.weibos

    def getWeibo(self):
        return self.weibos


# 根据每个prefix生成5个mht
def generate_mht_for_5_pages(prefix, screen_name): #
    print prefix, screen_name
    weiboLogin = WeiboMain.WeiboLogin(USER_ID,USER_PASSWD )
    if weiboLogin.Login():
        print "Login successfaully"
    else:
        sys.exit()
    for i in range(5):
        this_url = prefix + str(i+1)
        print "*****URL: ", this_url
        content = urllib2.urlopen(this_url).read()
        weibo_parser = WeiboParser()
        weibo_parser.feed(content)
        all_weibos = weibo_parser.getWeibo()
        print all_weibos

        mht = chilkat.CkMht()
        success = mht.UnlockComponent("Anything for 30-day trial")
        if not success:
            print mht.lastErrorText()
            sys.exit()
        file_name = "%s.mht" % (str(screen_name) + str(i+1))
        success = mht.GetAndSaveMHT(this_url, file_name)
        if not success:
            print mht.lastErrorText()
            sys.exit()
        else:
            print("MHT Created!")

    print "Generated 5 mht pages for 1 user"

class WB_text_finder():  # unused
    def __init__(self, content):
        self.msg_list = []
        self.content = content
        self.begin_index = 0

    def get_wb_text(self):
        while True:
            WB_index = self.content.find('WB_text',self.begin_index)
            if WB_index == -1:
                print "No weibos "
                break
            temp_str = self.content[self.content.find('>',WB_index)+1:content.find('<',WB_index) ]
            temp_str = temp_str[temp_str.find(r"\n") + len(r"\n"):].strip()
            self.msg_list.append(temp_str)
            self.begin_index = self.content.find(temp_str) + len(temp_str)
            print self.begin_index

    def get_all_wb_text(self):
        return self.msg_list

def generate_html(screen_name, wb_text_list):  # unused
    temp_str = ""
    for i in wb_text_list:
        temp_str += "<div>" + i + "</div>"

    html_str = "<html><head><title>" + screen_name + "</title></head>" + temp_str + "</html>"
    ff = open(str(screen_name) + r".html", "w")
    ff.write(html_str)
    ff.close()

"""

def get_yuanchuang_link_prefix(content):  # 得到原创微博url前缀
    p_index = content.find('\/p\/')
    p_num = content[p_index + 5:p_index + 5 + 16]
    yuanchuang_url = "http://weibo.com/p/" + p_num + "/weibo?is_search=0&visible=0&is_ori=1&is_tag=0&profile_ftype=1&page="
    return yuanchuang_url



# 去掉 导航栏 话题 热门微博 构造参数 ：文件操作对象
class useless_remover():
    def __init__(self,f):
        self.start_index = 0
        self.nav_str = "WB_global_nav"
        self.topic_str = "PRF_modwrap S_line1 clearfix"
        self.hot_weibo_str = "PRF_modwrap S_line1 clearfix"
        self.script_start = 0
        self.script_end = 0
        self.content = ""
        self.file_handler = f
        self.remove_list = [self.nav_str, self.topic_str, self.hot_weibo_str]

    def do_remove(self):
        self.content = self.file_handler.read()
        # 移出导航栏
        for i in self.remove_list:
            while True:
                self.script_start = self.content.find("<script>", self.script_start)
                if self.script_start == -1:
                    return "Finished"
                self.script_end = self.content.find("</script>", self.script_start)
                if self.content.find(i,self.script_start,self.script_end):
                    # 移出这部分script
                    self.content = self.content[0:self.script_start] + self.content[self.script_end:len(self.content)]
                    self.script_start = 0
                    self.script_end = 0
                    break
                else:
                    self.script_start = self.script_end + 1
        self.file_handler.write(self.content)
        # 取出导航

"""
class Fetcher(object):
    def __init__(self, username=None, pwd=None, cookie_filename=None):
        self.cj = cookielib.LWPCookieJar()
        if cookie_filename is not None:
            self.cj.load(cookie_filename)
        self.cookie_processor = urllib2.HTTPCookieProcessor(self.cj)
        self.opener = urllib2.build_opener(self.cookie_processor, urllib2.HTTPHandler)
        urllib2.install_opener(self.opener)

        self.username = username
        self.pwd = pwd
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/14.0.1',
                        'Referer':'','Content-Type':'application/x-www-form-urlencoded'}
    def get_rand(self, url):
        headers = {'User-Agent':'Mozilla/5.0 (Windows;U;Windows NT 5.1;zh-CN;rv:1.9.2.9)Gecko/20100824 Firefox/3.6.9','Referer':''}
        req = urllib2.Request(url ,urllib.urlencode({}), headers)
        resp = urllib2.urlopen(req)
        login_page = resp.read()
        rand = HTML.fromstring(login_page).xpath("//form/@action")[0]
        passwd = HTML.fromstring(login_page).xpath("//input[@type='password']/@name")[0]
        vk = HTML.fromstring(login_page).xpath("//input[@name='vk']/@value")[0]
        return rand, passwd, vk

    def login(self, username=None, pwd=None, cookie_filename=None):
        if self.username is None or self.pwd is None:
            self.username = username
            self.pwd = pwd
        assert self.username is not None and self.pwd is not None

        url = 'http://3g.sina.com.cn/prog/wapsite/sso/login.php?ns=1&revalid=2&backURL=http%3A%2F%2Fweibo.cn%2F&backTitle=%D0%C2%C0%CB%CE%A2%B2%A9&vt='
        rand, passwd, vk = self.get_rand(url)
        data = urllib.urlencode({'mobile': self.username,
            passwd: self.pwd,
                    'remember': 'on',
                    'backURL': 'http://weibo.cn/',
                    'backTitle': '新浪微博',
                    'vk': vk,
                    'submit': '登录',
                    'encoding': 'utf-8'})
        url = 'http://3g.sina.com.cn/prog/wapsite/sso/' + rand
        req = urllib2.Request(url, data, self.headers)
        resp = urllib2.urlopen(req)
        page = resp.read()
        link = HTML.fromstring(page).xpath("//a/@href")[0]
        if not link.startswith('http://'): link = 'http://weibo.cn/%s' % link
        req = urllib2.Request(link, headers=self.headers)
        urllib2.urlopen(req)
        if cookie_filename is not None:
            self.cj.save(filename=cookie_filename)
        elif self.cj.filename is not None:
            self.cj.save()
        print 'login success!'

    def fetch(self, url):
        print 'fetch url: ', url
        req = urllib2.Request(url, headers=self.headers)
        return urllib2.urlopen(req).read()

"""


if __name__ == "__main__":
    main_page_urls, all_following_users = get_following_user_personal_page() ## 得到关注用户主页url和用户信息类表 from API

    weiboLogin = WeiboMain.WeiboLogin(USER_ID, USER_PASSWD )
    if weiboLogin.Login():
        print "Login successfaully"
    else:
        sys.exit()

    for j in range(len(all_following_users)): # 便利列表 为每个用户生成html文件
        for i in range(1, 6):
            yuanchuang_link_prefix = get_yuanchuang_link_prefix(urllib2.urlopen(main_page_urls[j]).read())
            ff = open(str(all_following_users[j].id) + str(i) +'.html',"w").write(urllib2.urlopen(yuanchuang_link_prefix + str(i)).read()) # html 文件根据
            remove_useless = useless_remover(ff)
            remove_useless.do_remove()
            ff.close()

    print "finished whole process"
