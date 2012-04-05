# coding=gbk

import kp_base_api

consumer_key = "xcrXHUiEHAUTXZSs"
consumer_secret = "2Pm61rweLUTkfs5S"

oauth_token = "00928d1573a8f7176fdebc1b"
oauth_token_secret = "c0f2bc7609ea4f4d8608ea88d6ada3dd"

print kp_base_api.get_account_info( consumer_key, consumer_secret, oauth_token, oauth_token_secret )
print kp_base_api.get_metadata( consumer_key, consumer_secret, oauth_token, oauth_token_secret, "app_folder", "" )
print kp_base_api.get_shares( consumer_key, consumer_secret, oauth_token, oauth_token_secret, "app_folder", "/boost222.png" )
print kp_base_api.create_folder( consumer_key, consumer_secret, oauth_token, oauth_token_secret, "app_folder", "/china.png.exe" )
print kp_base_api.delete_item( consumer_key, consumer_secret, oauth_token, oauth_token_secret, "app_folder", "/china.png" )
print kp_base_api.move_item( consumer_key, consumer_secret, oauth_token, oauth_token_secret, "app_folder", "boost222.png", "new_path.png" )
print kp_base_api.copy_item( consumer_key, consumer_secret, oauth_token, oauth_token_secret, "app_folder", "boost222.png", "new_path.png" )
print kp_base_api.get_upload_url( consumer_key, consumer_secret, oauth_token, oauth_token_secret)
print kp_base_api.remove_url_port("http://t1.dfs.kuaipan.cn:8080/cdlnode/")
print kp_base_api.remove_url_port("http://t1.dfs.kuaipan.cn/cdlnode/")
print kp_base_api.remove_url_port("http://api-content.dfs.kuaipan.cn/1/fileops/download_file")=="http://api-content.dfs.kuaipan.cn/1/fileops/download_file"
print kp_base_api.upload_file( consumer_key, consumer_secret, oauth_token, oauth_token_secret, "app_folder", "/china2.png", False )
print kp_base_api.upload_file( consumer_key, consumer_secret, oauth_token, oauth_token_secret, "app_folder", "/china5.txt", "./jason.txt" )
url = kp_base_api.download_file( consumer_key, consumer_secret, oauth_token, oauth_token_secret, "app_folder", "/china5.txt", "../readed.png" )
print url

exit(0)
