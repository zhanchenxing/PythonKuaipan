# coding=utf-8
import time
import math
import urllib
import hmac
import hashlib
import binascii
import json
import re
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2
from urlparse import urlparse
import cookielib

# 一些基础的接口的实现。

count = 0

def gen_oauth_nonce():
    '''
    生成oauth_nonce
    '''
    global count
    count += 1
    return str( time.time() + 1 ).replace(".", "")


def get_timestamp():
    '''
    生成oauth_timestamp
    '''
    return  int( math.ceil( time.time() ) )


def get_base_string(base_url, param_dic, method="GET"):
    '''
    生成产生signature需要的base_string
    @param base_url: base_url是不包括 "?" 号，不包括其右边的query参数，不包括端口号的url，例如：http://openapi.kuaipan.cn/1/fileops/create_folder
    @param param_dic: 所有的参数对应的key-value
    '''
    l = [urllib.quote_plus ( k ) + "=" +urllib.quote_plus ( v ) for k, v in param_dic.iteritems()]
    l.sort()
    return method + "&" + urllib.quote_plus(base_url) + "&" + urllib.quote_plus( "&".join(l) )


def get_signature( base_string, consumer_secret_and_oauth_token ):
    '''
    生成最终的signature
    @param base_string: 基础串
    @param secret_and_oauth_token: consumer_secret+"&"+oauth_token。如果还没有oauth_token,就用：consumer_secret+"&"
    '''
    binary_sig = hmac.new( consumer_secret_and_oauth_token, base_string, hashlib.sha1)
    return binascii.b2a_base64(binary_sig.digest())[:-1]


def build_base_param(consumer_key):
    '''
    生成一些基础的参数。这些参数基本上每次请求都需要用到。
    '''
    dic = {}
    dic["oauth_nonce"]=gen_oauth_nonce()
    dic["oauth_timestamp"] = str(get_timestamp())
    dic["oauth_consumer_key"] = consumer_key
    dic["oauth_signature_method"] = "HMAC-SHA1"
    dic["oauth_version"]="1.0"
    return dic


def remove_url_port(url):
    '''
    将 http://t1.dfs.kuaipan.cn:8080/cdlnode/ 变成 http://t1.dfs.kuaipan.cn/cdlnode/
    @param url:
    '''
    g = re.search(":\d+/", url)
    if g:
        start = g.start()
        end = g.end()-1
        
        return url[:start]+url[end:]
    else:
        return url


def build_request_url( consumer_key, consumer_secret, base_url, oauth_token="", oauth_token_secret = "", extra_params={}, method="GET" ):
    '''
    构造最终的url串
    @param consumer_key: 应用的consumer_key
    @param consumer_secret: 应用的consumer_secret
    @param base_url: base_url是不包括 "?" 号，不包括其右边的query参数，不包括端口号的url，例如：http://openapi.kuaipan.cn/1/fileops/create_folder
    @param oauth_token: 
    @param extra_params: 其它的需要传的参数
    '''
    dic = build_base_param(consumer_key)
    if len(oauth_token)!=0:
        dic["oauth_token"] = oauth_token
    dic.update( extra_params )
    signature = get_signature( get_base_string( remove_url_port(base_url),dic, method ), consumer_secret+"&"+oauth_token_secret )
    dic["oauth_signature"] = signature
    url = base_url +"?"+ urllib.urlencode(dic)
    return url


def request_token(consumer_key, consumer_secret):
    '''
    请求未授权的token和对应的secret
    @param consumer_key: 应用的consumer_key
    @param consumer_secret: 应用的consumer_secret
    
    @return 未授权的oauth_token和对应的oauth_token_secret
    '''
    url = build_request_url( consumer_key, consumer_secret, "https://openapi.kuaipan.cn/open/requestToken" )
    
    json_text = urllib.urlopen(url).read()
    j = json.loads(json_text)
    oauth_token = j["oauth_token"].encode("ascii")
    oauth_token_secret = j["oauth_token_secret"].encode("ascii")
    return (oauth_token, oauth_token_secret)
    
def get_authorize_url(oauth_token):
    '''
    获取授权页面的url
    @param oauth_token: 未授权的oauth_token
    '''
    return "https://www.kuaipan.cn/api.php?ac=open&op=authorise&oauth_token=%s"%oauth_token


def request_access_token( consumer_key, consumer_secret, oauth_token, oauth_token_secret  ):
    '''
    获取授权的oauth_token_secret, oauth_token，
    之后就可以把返回的oauth_token_secret, oauth_token保存起来使用，直到过期
    @param consumer_key: 应用的consumer_key
    @param consumer_secret: 应用的consumer_secret
    @param oauth_token: 未授权的oauth_token
    @param oauth_token_secret: 对应未授权的oauth_token_secret
    @return: (oauth_token_secret, oauth_token, user_id, charged_dir )
    '''
    url = build_request_url( consumer_key, consumer_secret,
                             "https://openapi.kuaipan.cn/open/accessToken", oauth_token, oauth_token_secret )
    
    json_text = urllib.urlopen(url).read()
    j = json.loads(json_text)
    return ( j["oauth_token_secret"].encode("ascii"), j["oauth_token"].encode("ascii"), 
             j["user_id"], j["charged_dir"].encode("ascii") )


def get_account_info( consumer_key, consumer_secret, oauth_token, oauth_token_secret ):
    '''
    获取账户信息
    @param consumer_key:
    @param consumer_secret:
    @param oauth_token:
    @param oauth_token_secret:
    '''
    url = build_request_url( consumer_key, consumer_secret,
                             "http://openapi.kuaipan.cn/1/account_info", oauth_token, oauth_token_secret )    
    json_text = urllib.urlopen(url).read()
    return json_text


def get_metadata(consumer_key, consumer_secret, oauth_token, oauth_token_secret, root, path ):
    '''
    获取一个文件（夹）的信息
    @param consumer_key:
    @param consumer_secret:
    @param oauth_token:
    @param oauth_token_secret:
    @param root: kuaipan或者app_folder
    @param path: 文件（夹）路径
    '''
    
    # 去年首个/或者\
    if len(path)>0 and ( path[0]=='\\' or path[0]=='/' ) :
        path = path[1:]
    
    url = build_request_url( consumer_key, consumer_secret,
                             "http://openapi.kuaipan.cn/1/metadata/%s/%s"%(root, path ), oauth_token, oauth_token_secret )    
    json_text = urllib.urlopen(url).read()
    return json_text


def get_shares(consumer_key, consumer_secret, oauth_token, oauth_token_secret, root, path ):
    
    # 去掉首个/或者\
    if len(path)>0 and ( path[0]=='\\' or path[0]=='/' ) :
        path = path[1:]
    
    url = build_request_url( consumer_key, consumer_secret,
                             "http://openapi.kuaipan.cn/1/shares/%s/%s"%(root, path ), oauth_token, oauth_token_secret )    
    json_text = urllib.urlopen(url).read()
    return json_text


def create_folder(consumer_key, consumer_secret, oauth_token, oauth_token_secret, root, path ):
    
    # 去年首个/或者\
    extra_params={"root":root, "path":path}
    
    url = build_request_url( consumer_key, consumer_secret,
                             "http://openapi.kuaipan.cn/1/fileops/create_folder", oauth_token, oauth_token_secret, extra_params )    
    json_text = urllib.urlopen(url).read()
    return json_text


def delete_item(consumer_key, consumer_secret, oauth_token, oauth_token_secret, root, path, to_recycle=False ):
    
    # 去年首个/或者\
    to_recycle = str(bool(to_recycle))
        
    extra_params={"root":root, "path":path, "to_recycle":to_recycle }
    
    url = build_request_url( consumer_key, consumer_secret,
                             "http://openapi.kuaipan.cn/1/fileops/delete", oauth_token, oauth_token_secret, extra_params )    
    json_text = urllib.urlopen(url).read()
    return json_text


def move_item(consumer_key, consumer_secret, oauth_token, oauth_token_secret, root, from_path, to_path ):
    '''
    移动文件或者文件夹
    @param consumer_key:
    @param consumer_secret:
    @param oauth_token:
    @param oauth_token_secret:
    @param root: kuaipan或者app_folder
    @param from_path: 源路径
    @param to_path: 目标路径
    '''
    
    # 去掉首个/或者\
    extra_params={"root":root, "from_path":from_path, "to_path":to_path }
    
    url = build_request_url( consumer_key, consumer_secret,
                             "http://openapi.kuaipan.cn/1/fileops/move", oauth_token, oauth_token_secret, extra_params )    
    json_text = urllib.urlopen(url).read()
    return json_text


def copy_item(consumer_key, consumer_secret, oauth_token, oauth_token_secret, root, from_path, to_path ):
    
    # 去年首个/或者\
    extra_params={"root":root, "from_path":from_path, "to_path":to_path }
    
    url = build_request_url( consumer_key, consumer_secret,
                             "http://openapi.kuaipan.cn/1/fileops/copy/", oauth_token, oauth_token_secret, extra_params )    
    json_text = urllib.urlopen(url).read()
    return json_text


def get_upload_url(consumer_key, consumer_secret, oauth_token, oauth_token_secret):
    '''
    获取上传文件的url
    @param consumer_key:
    @param consumer_secret:
    @param oauth_token:
    @param oauth_token_secret:
    @return: 上传文件的url
    '''
    url = build_request_url( consumer_key, consumer_secret,
                             "http://api-content.dfs.kuaipan.cn/1/fileops/upload_locate", oauth_token, oauth_token_secret )
    json_text = urllib.urlopen(url).read()
    j = json.loads( json_text )
    return j["url"].encode("ascii")


def upload_file(consumer_key, consumer_secret, oauth_token, oauth_token_secret, root, path, local_file_path, overwrite=False ):
    '''
    上传一个文件到指定的位置
    @param consumer_key:
    @param consumer_secret:
    @param oauth_token:
    @param oauth_token_secret:
    @param root: 
    @param path: 上传到哪里
    @param local_file_path: 本地文件的路径
    @param overwrite: 如果文件已经存在是否覆盖
    '''
    
    # 获取上传的URL，如 http://t1.dfs.kuaipan.cn:8080/cdlnode/
    upload_url = get_upload_url(consumer_key, consumer_secret, oauth_token, oauth_token_secret)
    
    overwrite = str(bool(overwrite))
    
    extra_params = {
           "path":path,
           "root":root,
           "overwrite":overwrite,
           }
    
    full_url = upload_url + "1/fileops/upload_file"
    
    request_url = build_request_url( consumer_key, consumer_secret,
                             full_url, oauth_token, oauth_token_secret, extra_params, "POST" )
    
    datagen, headers = multipart_encode({"file": open(local_file_path, "rb")})
    headers["Accept-Encoding"]="identity"
    o=urlparse(full_url)
    headers["host"]=o.hostname
    headers["connection"]="close"
    headers["User-Agent"]="klive"
    register_openers()
    
    # Create the Request object
    request = urllib2.Request( request_url, datagen, headers)
    
    # Actually do the request, and get the response
    json_text = urllib2.urlopen(request).read()    
    return json_text


def download_file(consumer_key, consumer_secret, oauth_token, oauth_token_secret, root, path, local_file_path ):
    '''
    下载一个文件到某个 位置
    @param consumer_key:
    @param consumer_secret:
    @param oauth_token:
    @param oauth_token_secret:
    @param root: 根目录（root或者是app_path）
    @param path: 要下载的文件的路径
    @param local_file_path: 要下载到的位置
    '''
    
    extra_params = {
           "root":root,
           "path":path,
           }
    
    request_url = build_request_url( consumer_key, consumer_secret,
                             "http://api-content.dfs.kuaipan.cn/1/fileops/download_file", oauth_token, oauth_token_secret, extra_params )
    
    cookie=cookielib.CookieJar()
    opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    req = opener.open( request_url )
    write_to = open(local_file_path, "w")
    while True:
        readed = req.read(1024)
        if len(readed)==0:
            write_to.close()
            break
        else:
            write_to.write(readed)
