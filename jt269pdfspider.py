# -*- coding: UTF-8 -*-
from concurrent.futures.thread import ThreadPoolExecutor

import requests
from lxml import etree
import urllib.request
import urllib.parse
import os

_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9," +
              "image/avif,image/webp,image/apng,*/*;q=0.8,application/sig" +
              "ned-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Host": "www.jt269.com",
    "Pragma": "no-cache",
    "Proxy-Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

_pool = ThreadPoolExecutor(max_workers=100)


def _download(p, viewid):
    path = "./data/" + viewid + "/" + p.replace("@", "/").rsplit("/", 1)[0]
    filename = p.rsplit("@")[-1] + ".pdf"
    url = "http://www.jt269.com/" + urllib.parse.quote(p) + ".pdf-" + viewid
    filepath = f"{path}/{filename}"
    os.makedirs(path, exist_ok=True)
    if os.path.exists(path + "/" + filename):
        print(f"already download {filepath}")
        return

    def _action():
        print(f"download {filepath} from {url}")
        urllib.request.urlretrieve(url, filename=path + "/" + filename)

    _pool.submit(_action)


def _concat_path(path, name):
    _new_path = path
    if path != "":
        _new_path += "@"
    _new_path += name
    return _new_path


def _crawling_tree(node, path, viewid):
    # print(f"path={path}  node:tag={node.tag},text={node.text},getchildren={node.getchildren()}")
    if node.tag == "ul":
        for child in node.getchildren():
            _crawling_tree(child, path, viewid)
    elif node.tag == "li":
        children = node.getchildren()
        name = None
        for c in children:
            if c.tag == "span":
                name = c.text
        if name is None:
            raise Exception("not found dir name!")
        new_path = _concat_path(path, name)
        find_ul = False
        for c in children:
            if c.tag == "ul":
                find_ul = True
                _crawling_tree(c, new_path, viewid)
        if not find_ul:
            attr = node.attrib
            if attr["exetn"] == ".pdf":
                _download(new_path, viewid)


def crawling(viewid):
    html_resp = requests.get("http://www.jt269.com/view-" + viewid + ".html", headers=_headers)
    xml_tree_list = etree.HTML(html_resp.text).xpath("/html/body/div[4]/div[2]/div[2]/ul")
    if len(xml_tree_list) != 0:
        _crawling_tree(xml_tree_list[0], "", viewid)


if __name__ == '__main__':
    crawling("118")
    crawling("1523")
    crawling("962")
