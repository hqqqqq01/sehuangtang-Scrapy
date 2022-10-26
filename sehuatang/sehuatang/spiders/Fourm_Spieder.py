import scrapy
from sehuatang.items import SehuatangItem
import bs4
import re
from lxml import etree

class ForumSpider(scrapy.Spider):
    name = 'Fourm_Spider'
    # allowed_domains = ['www.sehuatang.org']

    f_dic = {"103": "高清中文字幕", "104": "素人有码系列", "37": "亚洲有码原创",
             "36": "亚洲无码原创", "39": "动漫原创", "160": "vr", "151": "4k",
             "2": "国产原创", "38": "欧美无码", "107": "三级写真", "152": "韩国主播"}
    f_id = [103, 104, 37, 36, 39, 160, 151, 2, 38, 107, 152]  # 板块页id
    start_urls = [f'https://www.sehuatang.net/forum-{i}-1.html' for i in f_id]

    # 访问板块，发送所有页请求，并处理所有页请求
    def parse(self, response, **kwargs):
        if response.url in self.start_urls:
            f_id_pages = re.findall('span title="共 (\d+) 页"', response.text)[0]
            for page in range(2, 8):  # 这里设置截至页用来更新  原始：int(f_id_pages) + 1
                page_url = re.sub("\d+\.html", f"{page}.html", response.url)  # 所有页请求
                yield scrapy.Request(url=page_url, callback=self.parse)

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        page_all = soup.find_all(id=re.compile("^normalthread_"))  # 所有页的所有详情页
        for i in page_all:
            item = SehuatangItem()
            f_id = re.findall("forum-(\d+)-\d+\.html", response.url)[0]
            item["f_id"] = self.f_dic[f_id]
            item["f_id_page"] = re.findall("(\d+)\.html", response.url)[0]
            print("*" * 50, f"正在抓取 \033[0;31m{item['f_id']}\033[0m 板块的第 \033[0;35m{item['f_id_page']}\033[0m 页",
                  "*" * 50)

            title_list = i.find("a", class_="s xst").get_text().split(" ")
            number = title_list[0]
            title_list.pop(0)
            title = " ".join(title_list)
            date_td_em = i.find("td", class_="by").find("em")
            date_span = date_td_em.find(
                "span", attrs={"title": re.compile("^" + "20")}
            )
            if date_span is not None:
                date = date_span.attrs["title"]
            else:
                date = date_td_em.get_text()
            tid = i.find(class_="showcontent y").attrs["id"].split("_")[1]
            item["number"] = number
            item["title"] = title
            item["date"] = date
            item["tid"] = tid   # 详情页id
            detail_url = f"https://www.sehuatang.net/?mod=viewthread&tid={tid}"
            yield scrapy.Request(url=detail_url, callback=self.parse_detail, meta={"item": item})

    # 处理详情页
    def parse_detail(self, response, **kwargs):
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        # 获取帖子的标题
        title = soup.find("h1", class_="ts").find("span").get_text()
        # 存放图片的列表
        img_list = response.xpath("(//td[@class='t_f'])[1]//img/@file").extract()
        # 磁力链接
        div_blockcode = soup.find("div", class_="blockcode")
        magnet = div_blockcode.find("li").get_text() if div_blockcode is not None else None

        post_time_em = soup.find("img", class_="authicn vm").parent.find("em")
        post_time_span = post_time_em.find("span")
        if post_time_span is not None:
            post_time = post_time_span.attrs["title"]
        else:
            post_time = post_time_em.get_text()[4:]

        item = response.meta["item"]
        item["title"] = title
        item["post_time"] = post_time
        item["img"] = img_list
        item["magnet"] = magnet
        yield item
