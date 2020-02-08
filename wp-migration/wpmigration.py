import abc
import calendar
import json
import optparse
import os
import time
import xml.etree.ElementTree as ET

# Namespaces used by ElementTree with parsing wp xml.
EXCERPT_NAMESPACE = "http://wordpress.org/export/1.2/excerpt/"
CONTENT_NAMESPACE = "http://purl.org/rss/1.0/modules/content/"
WFW_NAMESPACE = "http://wellformedweb.org/CommentAPI/"
DC_NAMESPACE = "http://purl.org/dc/elements/1.1/"
WP_NAMESPACE = "http://wordpress.org/export/1.2/"


class WpParser:
    def __init__(self, xml_file_path):
        self.xml_file_path = xml_file_path

    @abc.abstractmethod
    def parse(self):
        return

    def parse_item(self, item):
        title = item.find("./title").text
        pub_date = item.find("./pubDate").text
        creator = item.find("./{%s}creator" % DC_NAMESPACE).text
        content = item.find("./{%s}encoded" % CONTENT_NAMESPACE).text
        status = item.find("./{%s}status" % WP_NAMESPACE).text
        post_type = item.find("./{%s}post_type" % WP_NAMESPACE).text
        post_id = item.find("./{%s}post_id" % WP_NAMESPACE).text
        category_items = item.findall("./category")

        categories = []
        tags = []

        for category_item in category_items:
            if category_item.attrib["domain"] == "category":
                item_list = categories
            else:
                item_list = tags

            item_list.append(category_item.attrib["nicename"])

        return {
            "title": title,
            "categories": categories,
            "postedBy": creator,
            "date": pub_date,
            "content": content,
            "tags": tags,
            "id": post_id,
            "status": status,
            "postType": post_type
        }


class WpPostParser(WpParser):
    def __init__(self, xml_file_path):
        self.xml_file_path = xml_file_path

    def parse(self):
        doc = ET.parse(self.xml_file_path).getroot()
        channel = doc.find('./channel')
        posts = []
        items = channel.findall('item')
        for item in items:
            parsed_item = self.parse_item(item)
            posts.append(parsed_item)

        return posts


# TODO this is not completed
class DwqaQuestionParser(WpParser):
    def __init__(self, xml_file_path):
        self.xml_file_path = xml_file_path

    def parse(self):
        doc = ET.parse(self.xml_file_path).getroot()
        channel = doc.find('./channel')
        posts = []
        items = channel.findall('item')
        for item in items:
            post = self.parse_item(item)
            post_metas = item.find("./{%s}postmeta" % WP_NAMESPACE)
            for post_meta in post_metas:
                print post_meta


def parsePosts(channelElement):
    posts = []
    items = channelElement.findall('item')
    for item in items:

        title = item.find("./title").text
        pub_date = item.find("./pubDate").text
        creator = item.find("./{%s}creator" % DC_NAMESPACE).text
        content = item.find("./{%s}encoded" % CONTENT_NAMESPACE).text
        category_items = item.findall("./category")

        categories = []
        tags = []

        for category_item in category_items:
            if category_item.attrib["domain"] == "category":
                item_list = categories
            else:
                item_list = tags

            item_list.append(category_item.attrib["nicename"])

        posts.append({
            "title": title,
            "categories": categories,
            "postedBy": creator,
            "date": pub_date,
            "content": content,
            "tags": tags
        })

    return posts


def createFile(content, category, filename):
    categoryDir = "articles" + os.sep + category
    if not os.path.exists(categoryDir):
        os.makedirs(categoryDir)

    fullFilePath = categoryDir + os.sep + filename
    try:
        f = open(fullFilePath, "w")
        f.write(content.encode('utf-8'))
        f.close()
    except Exception as e:
        os.remove(fullFilePath)
        raise e


def createJsonEntry(articles):
    filename = "articles" + os.sep + "articles.json"
    with open(filename, "w") as outfile:
        jsonStr = json.dumps(articles, ensure_ascii=False).encode('utf8')
        f = open(filename, "w")
        f.write(jsonStr)
        f.close()


def getFileName(title, id):
    ts = calendar.timegm(time.gmtime())
    return title.replace(" ", "") + "_" + id + ".md"


def getOptionParser():
    parser = optparse.OptionParser()
    parser.add_option('-f', '--file', action="store", dest="file", help="File name fullpath")
    return parser


def main2():
    parser = getOptionParser()
    options, args = parser.parse_args()
    file = options.file
    post_parser = DwqaQuestionParser(file)
    post_parser.parse()


def main():
    parser = getOptionParser()
    options, args = parser.parse_args()
    file = options.file
    post_parser = WpPostParser(file)
    posts = post_parser.parse()
    articles = []
    answerForPosts = []
    for post in posts:
        try:
            if post["postType"] != "post":
                answerForPosts.append(post)
                continue

            if not post["content"] \
                    or len(post["content"]) < 200 \
                    or post["status"] != "publish":
                print "Content is empty"
                print post
                continue

            categories = post["categories"]
            if categories:
                category = categories[0]
            else:
                category = "genel"
            filename = getFileName(post["title"], post["id"])
            createFile(post["content"], category, filename)
            articles.append({
                "title": post["title"],
                "fileName": filename,
                "category": category,
                "postedBy": post["postedBy"],
                "date": post["date"],
                "tags": post["tags"]
            })
        except Exception as e:
            print "Exception"
            print e

    print articles
    createJsonEntry(articles)


if __name__ == "__main__":
    main()
