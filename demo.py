# coding=utf-8

import webbrowser
import kp_base_api
import re

# 已经授权的信息保存到这个文件里
token_saved_to = "./authorized.data"

class kp_demo():
    consumer_key = "xcrXHUiEHAUTXZSs"
    consumer_secret = "2Pm61rweLUTkfs5S"
    root = "app_folder"
    
    def __init__(self):
        self.oauth_token=""
        self.oauth_token_secret=""
        self.load_authorized_token()
    
    def load_authorized_token(self):
        try:
            lines = open(token_saved_to).readlines()
            for line in lines:
                g = re.match( "oauth_token\s*=\s*(\w+)", line)
                if g:
                    self.oauth_token = g.group(1)
                else:
                    g = re.match( "oauth_token_secret\s*=\s*(\w+)", line)
                    if g:
                        self.oauth_token_secret = g.group(1)
            
            if len(self.oauth_token)>0 and len(self.oauth_token_secret)>0:
                return True
            else:
                return False
        except:
            return False
    
    def save_authorized_token(self, oauth_token_secret, oauth_token):
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        open(token_saved_to, "w").write("oauth_token=%s\noauth_token_secret=%s" %( oauth_token, oauth_token_secret ) )
        
    def is_authorized(self):
        return len(self.oauth_token)>0 and len( self.oauth_token_secret )>0
    
    def authorize(self):
        try:
            # 1. 获取未授权的token和secret
            oauth_token, oauth_token_secret = kp_base_api.request_token(kp_demo.consumer_key, kp_demo.consumer_secret)
            
            # 2. 打开授权页面
            authorize_url = "https://www.kuaipan.cn/api.php?ac=open&op=authorise&oauth_token=%s"%oauth_token
            webbrowser.open(authorize_url)
            
            inputed = raw_input("请在打开的页面里面，给此程序授权。\n已经授权了吗？(Y/N 默认为Y)")
            if inputed == "" or inputed == "Y":
                # 3. 换取授权的，并且保存下来
                authorized_oauth_token_secret, authorized_oauth_token, user_id, charged_dir = kp_base_api.request_access_token( kp_demo.consumer_key, kp_demo.consumer_secret, oauth_token, oauth_token_secret)
                self.save_authorized_token(authorized_oauth_token_secret, authorized_oauth_token)
                print "授权成功"
            else:
                print "授权失败"
        except:
            print "授权失败"
            raise
            
    def get_metadata(self, path):
        return kp_base_api.get_metadata(kp_demo.consumer_key, kp_demo.consumer_secret, self.oauth_token, self.oauth_token_secret, kp_demo.root, path)
        
    def get_account_info(self):
        return kp_base_api.get_account_info(kp_demo.consumer_key, kp_demo.consumer_secret, self.oauth_token, self.oauth_token_secret)

    def get_shares(self, path):
        return kp_base_api.get_shares(kp_demo.consumer_key, kp_demo.consumer_secret, self.oauth_token, self.oauth_token_secret, kp_demo.root, path )
    
    def create_folder(self, path):
        return kp_base_api.create_folder(kp_demo.consumer_key, kp_demo.consumer_secret, self.oauth_token, self.oauth_token_secret, kp_demo.root, path )
    
    def delete_item(self, path, to_recycle=False):
        return kp_base_api.delete_item(kp_demo.consumer_key, kp_demo.consumer_secret, self.oauth_token, self.oauth_token_secret, kp_demo.root, path, to_recycle )
    
    def move_item(self, from_path, to_path ):
        return kp_base_api.move_item(kp_demo.consumer_key, kp_demo.consumer_secret, self.oauth_token, self.oauth_token_secret, kp_demo.root, from_path, to_path )

    def copy_item(self, from_path, to_path ):
        return kp_base_api.copy_item(kp_demo.consumer_key, kp_demo.consumer_secret, self.oauth_token, self.oauth_token_secret, kp_demo.root, from_path, to_path )
        
    def upload_file(self, path, local_file_path, overwrite=False):
        return kp_base_api.upload_file(kp_demo.consumer_key, kp_demo.consumer_secret, self.oauth_token, self.oauth_token_secret, kp_demo.root, path, local_file_path, overwrite )

    def download_file(self, path, local_file_path):
        return kp_base_api.download_file(kp_demo.consumer_key, kp_demo.consumer_secret, self.oauth_token, self.oauth_token_secret, kp_demo.root, path, local_file_path )


demo = kp_demo()
if demo.is_authorized():
    print demo.oauth_token
    print demo.oauth_token_secret
    print "已经授权"
    
else:
    print "尚未授权"
    demo.authorize()

print "get_metadata:"
print demo.get_metadata("/")

print "get_account_info:"
print demo.get_account_info()

print demo.get_shares("/new_path.png")
print demo.create_folder("/folder_created")
print demo.move_item("/folder_created", "/folder_created_moved")
print demo.delete_item("/folder_created_moved")

print demo.create_folder("/source_folder")
print demo.copy_item("/source_folder", "/dest_folder")
print demo.upload_file("/uploaded.png", "../boost2.png", True)
print demo.download_file("/uploaded.png", "../downloaded_uploaded.png")
# 下载文件暂时还有问题
