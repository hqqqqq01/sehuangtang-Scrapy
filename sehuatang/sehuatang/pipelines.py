# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql

class SehuatangPipeline:

    def open_spider(self, spider):
        self.conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="root", db="sehuatang")
        self.cursor = self.conn.cursor()
        self.inserted_num = 0


    def process_item(self, item, spider):
        sql = "select tid from sht_data"
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        tid_list = [str(i[0]) for i in res]
        if item["tid"] in tid_list:
            print("*"*10, f' {item["tid"]} 之前已被抓取 ', "*"*10)
            return item
        try:
            sql = "insert into " + 'sht_data' + "(magnet, number, title, post_time, date, tid, f_id, f_id_page) values " \
                                                "(%s, %s, %s, %s, %s, %s, %s, %s) "
            self.cursor.execute(sql, (item["magnet"], item["number"], item["title"],
                                      item["post_time"], item['date'], item["tid"], item["f_id"], item["f_id_page"]))
            id_ = self.cursor.lastrowid
            # 图片数据关联写入sht_images表
            sql = "insert into " + 'sht_images' + " (sht_data_id, image_url) values (%s, %s)"
            for image_url in item["img"]:
                self.cursor.execute(sql, (id_, image_url))
            self.conn.commit()
            self.inserted_num += 1
            print("*" * 10,
                  f"\033[0;31m{item['f_id']}\033[0m 板块的第 \033[0;35m{item['f_id_page']}\033[0m 页中的 \033[0;34m{item['tid']}\033[0m 抓取完成",
                  "*" * 10)
            print("*"*10, f"\033[0;36m{item['title']}\033[0m 存入数据库成功！当前已存入 \033[0;36m{self.inserted_num}\033[0m 条数据", "*"*30)
        except Exception as e:
            print("*"*50, f"\033[0;36m{item['title']}\033[0m 写入失败：%s " % e, "*"*10)
            self.conn.rollback()
        return item



    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()