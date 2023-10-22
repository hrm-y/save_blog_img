import requests
import os
from bs4 import BeautifulSoup
import time

from settings import member_num

BASE_URL = "https://www.hinatazaka46.com"


def main(member_name, selected_save_path):
    BLOG_LIST_URL = (
        BASE_URL + "/s/official/diary/member/list?ct=" + member_num[member_name]
    )

    blog_url = get_latest_blog_url(BLOG_LIST_URL)
    last_date = ""

    No = 1
    # loop_cnt = 0

    next_exist = True
    while next_exist:
        imgs_url_list = get_image_url(blog_url)
        last_date, No = save_file(
            imgs_url_list, last_date, No, member_name, selected_save_path
        )
        blog_url, next_exist = get_next_blog_url(blog_url)
        """
        loop_cnt += 1
        if loop_cnt == 5:
            break
        """


def get_latest_blog_url(blog_list_url):
    res = requests.get(blog_list_url)
    soup = BeautifulSoup(res.text, "html.parser")

    latest_blog_url = BASE_URL + soup.find(
        "a", attrs={"class": "c-button-blog-detail"}
    ).get("href")

    return latest_blog_url


def get_image_url(blog_url):
    global blog_article

    print("【BlogURL】" + blog_url)

    res = requests.get(blog_url)
    soup = BeautifulSoup(res.text, "html.parser")
    blog_article = soup.find("div", attrs={"class": "p-blog-article"})

    imgs = blog_article.find_all("img")

    imgs_url_list = []
    for img in imgs:
        imgs_url_list.append(img.get("src"))

    return imgs_url_list


def save_file(imgs_url_list, last_date, No, member_name, selected_save_path):
    member_name = member_name.replace(" ", "")

    dir = os.path.join(selected_save_path, member_name)

    # 取得したメンバー名のフォルダが未作成であればフォルダを作成
    if not os.path.exists(dir):
        os.mkdir(dir)
        print("フォルダ作成")

    for img_url in imgs_url_list:
        filename, fg, last_date, No = make_filename(img_url, last_date, No)
        path = os.path.join(dir, filename)

        if not fg:
            print(fg)
        if not os.path.isfile(path) and fg:
            res = requests.get(img_url)
            time.sleep(1)
            if res.status_code == 200:
                with open(path, "wb") as f:
                    f.write(res.content)

                print("【FileName】" + filename, "【ImageURL】" + img_url, "保存完了")
            else:
                print("False", res.status_code, img_url)

    print()

    return last_date, No


def make_filename(img_url, last_date, No):
    blog_date = blog_article.find("div", attrs={"class": "c-blog-article__date"}).text
    blog_date = blog_date.strip().split(" ")[0].split(".")
    year = blog_date[0]
    month = blog_date[1]
    day = blog_date[2]
    date = year + month.zfill(2) + day.zfill(2)

    if last_date == date:
        No = No + 1
    else:
        No = 1

    label = date + "_" + str(No).zfill(2)

    last_date = date

    if img_url is None or img_url == "":
        img_url = "xxx"
        No = No - 1

    fg = True
    if ".jpeg" in img_url or ".jpg" in img_url:
        filename = label + ".jpg"
    elif ".png" in img_url:
        filename = label + ".png"
    else:
        filename = ""
        fg = False

    return filename, fg, last_date, No


def get_next_blog_url(blog_url):
    res = requests.get(blog_url)
    soup = BeautifulSoup(res.text, "html.parser")

    try:
        next_blog_url = BASE_URL + soup.find(
            "div",
            attrs={
                "class": "c-pager__item c-pager__item--prev c-pager__item--kiji c-pager__item--kiji__blog"
            },
        ).find("a").get("href")
        next_exist = True

    except AttributeError:
        next_blog_url = ""
        print("***************全てのブログを保存しました***************")
        next_exist = False

    return next_blog_url, next_exist
