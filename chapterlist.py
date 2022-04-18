'''
爬取漫画
'''
import re
import os
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup
import execjs

url = "http://www.mangabz.com/10917bz/"
# url = "http://www.mangabz.com/m130115/"
# http://www.mangabz.com/m130115/#ipg2

class Chapter:
    '''
    url:对应章节url
    path: 对应保存路径
    '''
    def __init__(self, url, comic_name):
        self.url = url
        self.path = comic_name
        self.root_path = 0
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
            'Referer': 'http://www.mangabz.com/10917bz/'
        }
    def get_chapter_list(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'lxml')
        alist = soup.select("#chapterlistload a")
        comic_name = soup.find(class_="detail-info-title").text.strip()
        self.path = r"D:/comic/{}".format(comic_name)
        self.root_path = "D:/comic/{}".format(comic_name)
        print(self.path)
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        # print(comic_name)
        # print(alist[0])
        # print(alist[0]['href'])
        # print(len(alist))
        suffix_list = []
        for i in range(len(alist)):
            suffix_list.append(alist[i]['href'])
        return suffix_list

    def get_js(self):
        try:
            response = requests.get(url=self.url, headers=self.headers,timeout=10)
            soup = BeautifulSoup(response.text, 'lxml')
        except:
            print("章节request错误")
        mangabz_cid = re.findall("MANGABZ_CID=(.*?);", response.text)[0]
        mangabz_mid = re.findall("MANGABZ_MID=(.*?);", response.text)[0]
        page_total = re.findall("MANGABZ_IMAGE_COUNT=(.*?);", response.text)[0]
        mangabz_viewsign_dt = re.findall("MANGABZ_VIEWSIGN_DT=\"(.*?)\";", response.text)[0]
        mangabz_viewsign = re.findall("MANGABZ_VIEWSIGN=\"(.*?)\";", response.text)[0]

        soup = BeautifulSoup(response.text, 'lxml').find(class_="top-title")

        chapter_name = str(soup.text).strip()
        return (mangabz_cid, mangabz_mid, mangabz_viewsign_dt, mangabz_viewsign, page_total,chapter_name)
    def get_js_url(self, mangabz_cid, page, mangabz_mid, mangabz_viewsign_dt, mangabz_viewsign):
        js_url = self.url+(
            "chapterimage.ashx?"+"cid={}&"+"page={}&"+"key=&"+"_cid={}&"+"_mid={}&"+"_dt={}&"+"_sign={}"
        ).format(mangabz_cid, page, mangabz_cid, mangabz_mid, urllib.parse.quote(mangabz_viewsign_dt),mangabz_viewsign)
        return js_url

    def get_image_url(self, js_url):
        try:
            res = requests.get(url=js_url, headers=self.headers, timeout=10)
            self.headers['Referer'] = res.url
            js_str = res.text
            imagelist = execjs.eval(js_str)
            return imagelist[0]
        except TimeoutError:
            print("Failed to get picture link")

    def down_image(self, image_url, page):
        try:
            if not os.path.isdir(self.path):
                os.makedirs(self.path)
        except:
            print("Failed to create file")
        ## judge if there ara the pictures
        try:
            if os.path.isfile(self.path+"/"+str(page).strip()+".png"):
                return 0
        except:
            print("failed to judge if there is the picture")

        try:
            res = requests.get(url=image_url, headers=self.headers, timeout=10)
            content = res.content
            with open(self.path+'/'+str(page)+".png", "wb") as f:
                f.write(content)
            print("dounload successful"+str(page)+"page")
            f.close()
        except:
            print("download error"+str(page)+"page")
            print(image_url)

        #time.sleep(0.2)


    def run(self):
        (mangabz_cid, mangabz_mid, mangabz_viewsign_dt, mangabz_viewsign, page_total,chapter_name) = self.get_js()
        self.path = self.path+'/'+str(chapter_name)
        # judge if this chapter has been downloaded, if so it will not been dounloaded
        if os.path.exists(self.path):
            files = os.listdir(self.path)
            print(self.path)
            num_png = len(files)
            # if the number of files is equal to the number of pages, that means that the download is finished
            if num_png == int(page_total):
                print(str(chapter_name)+"downloading")
                return

        print("downloading"+str(chapter_name)+"-----"+"total"+str(page_total)+"pages")
        for i in range(int(page_total)):
            js_url = self.get_js_url(mangabz_cid, i+1, mangabz_mid, mangabz_viewsign_dt, mangabz_viewsign)
            image_url = self.get_image_url(js_url)
            self.down_image(image_url, i+1)
        self.path = self.root_path
    def run_list(self):
        prefix = "http://www.mangabz.com"
        suffix_list = self.get_chapter_list()
        print(suffix_list)
        for i in suffix_list:
            self.url =  str(prefix+i)
            # print(url_chapter)
            self.run()






if __name__ == '__main__':
    chapter = Chapter(url,"")
    #chapter.run()
    chapter.run_list()