import json, time, hashlib, base64, requests, re
from urllib import parse
from bs4 import BeautifulSoup
from rich import print as rprint
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from alive_progress import alive_bar
import random, math

console = Console()

# 所有课程列表
courses_list = []
post_time = 1


def print_course():
    course_table = Table()
    course_table.add_column("序号", justify="center", style="cyan")
    course_table.add_column("名称", justify="center", no_wrap=True)
    course_table.add_column("状态", justify="center")
    for index, course in enumerate(courses_list):
        if (index < 10):
            index_str = "0" + str(index)
        else:
            index_str = str(index)
        course_table.add_row(index_str, course['course_name'], "未结课")
    return course_table


# 获取所有课程名称
def get_course_unit():
    console.rule("正在获取所有课程")
    course_heades = {
        "Content-Type": "application/x-www-form-urlencoded",
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
    }
    course_data = {
        "courseType": "1",
        "courseFolderId": "0",
        "baseEducation": "0",
        "courseFolderSize": "0"
    }
    course_url = "https://mooc1-1.chaoxing.com/visit/courselistdata"
    course_response = requests.post(url=course_url, headers=course_heades, cookies=cookies, data=parse.urlencode(course_data))
    soup = BeautifulSoup(course_response.content.decode("utf8"), 'html5lib')
    list = soup.find_all(attrs={"class", "color1"})
    for i in list:
        query = parse.parse_qs(parse.urlparse(i.get("href"))[4])
        courseid = query["courseid"][0]
        clazzid = query["clazzid"][0]
        cpi = query["cpi"][0]
        courses_list.append({"course_name": i.span.string, "courseId": courseid, "clazzid": clazzid, "cpi": cpi})
    # 准备打印课程
    course_table = print_course()
    console.print(course_table)
    console.rule("所有课程获取完成")


# 获取当前课程所有章节信息,以及当前章节总体完成状态
def get_chapterUnit(courseid, clazzid, cpi):
    # 所有任务章节情况
    classUrl = f"https://mooc2-ans.chaoxing.com/mycourse/studentcourse?courseid={courseid}&clazzid={clazzid}&cpi={cpi}&ut=s"
    missonResponse = requests.get(url=classUrl, headers=headers, cookies=cookies)
    soupMisson = BeautifulSoup(missonResponse.content.decode('utf8'), 'html5lib')
    # 所有章节
    chapter_unit = soupMisson.find_all("div", class_="chapter_unit")
    for chapter_index, chapter in enumerate(chapter_unit):
        chapter_title = chapter.find(attrs={"class", "chapter_item"}).find(attrs={"class", "catalog_name"}).span["title"]
        rprint(Panel(chapter_title, style="bright_blue"))
        try:
            chapter_child_unit = chapter.find(attrs={"class", "catalog_level"}).find_all("li")
            for chapter_child_index, chapter_child in enumerate(chapter_child_unit):
                chapter_child_title = chapter_child.find(attrs={"class", "chapter_item"})["title"]
                chapter_child_id = chapter_child.find(attrs={"class", "chapter_item"})["onclick"]
                str = chapter_child_id[7:]
                str = str[:-2]
                # 是否完成
                if (chapter_child.find(attrs={"class", "chapter_item"}).find(attrs={"class": "bntHoverTips"}).contents[0] == "已完成"):
                    print("{}.{}:{}:[章节ID:{}]".format(chapter_index + 1, chapter_child_index + 1, chapter_child_title, str.rsplit("', '")[1]))
                    console.print("[该章节已全部已完成]\n", style="green", )
                else:
                    print("{}.{}:{}:[章节ID:{}]".format(chapter_index + 1, chapter_child_index + 1, chapter_child_title, str.rsplit("', '")[1]))
                    get_missionData(courseid, clazzid, str.rsplit("', '")[1], cpi)
        except Exception as e:
            print("没有子章节")


# 获取当前章节当前任务块所有任务点信息
def get_missionData(courseid, clazzid, knowledgeid, cpi):
    # 块节点,不知道这个章节有多少个快,+1去请求,直到拿不到mArg,就返回
    # 当Num=0,mArg都取不到,说明该章节不存在任何任务点

    for missionParts_index in range(5):
        url = "https://mooc1-1.chaoxing.com/knowledge/cards?clazzid={}&courseid={}&knowledgeid={}&num={}&ut=s&cpi={}&v=20160407-1".format(clazzid, courseid, knowledgeid, missionParts_index, cpi)
        response = requests.get(url=url, headers=headers, cookies=cookies)
        soup = BeautifulSoup(response.content.decode("utf8"), "html5lib")
        # 节点任务的重要信息dict
        if (missionParts_index == 0):
            # setlog 需要的encode
            try:
                enc = re.search(r"var _from = '(.*?)';", response.content.decode("utf8"), flags=re.M).group(1).split("_")[3]
                url = f"https://mooc1.chaoxing.com/mycourse/studentstudy?chapterId={knowledgeid}&courseId={courseid}&clazzid={clazzid}&enc={enc}&mooc2=1&cpi={cpi}"
                res = BeautifulSoup(requests.get(url=url, headers=headers, cookies=cookies).content.decode('utf8'), 'html5lib')
                try:
                    headers1 = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE',
                        "Referer": url + "&openc=11628298bef5833a1b9464ec954f691d",
                        "Sec-Fetch-Dest": "script",
                        "Host": "fystat-ans.chaoxing.com",
                        "sec-ch-ua-mobile": "?0"
                    }
                    for src in res.find_all("script"):
                        if ("https://fystat-ans.chaoxing.com/log/setlog?" in src["src"]):
                            temp = src["src"] + f"&_={int(round(time.time() * 1000))}"
                            time.sleep(1)
                            res = requests.get(temp, headers=headers1, cookies=cookies)
                            print("[该章节完成学习打卡]")
                except:
                    pass
            except:
                console.log("setLog错误")
                pass
        try:
            missonData = json.loads(re.search(r'mArg =(.*?);(\s\S)catch', soup.body.find_all("script")[0].string, flags=re.M).group(1))

            # print("当前章节子节点{}有{}个任务点".format(missionParts_index, len(missonData["attachments"])))
            for missonDataItem_index, missonDataItem in enumerate(missonData["attachments"]):
                # 捕捉异常 有的没有类型,插入可能是图片 很恶心
                try:
                    if (missonDataItem["type"] == "video"):
                        def is_job():
                            try:
                                temp = missonDataItem["jobid"]
                                console.print("检测到任务:[yellow]Viedo[not b not uu red]\t[未完成]")
                                get_videoMission_data(missonDataItem, missonData["defaults"], missionParts_index, missonDataItem_index)
                            except:
                                console.print("检测到任务:[yellow]Viedo[not b not uu blue]\t[非任务]")

                        # 判断完成了没
                        try:
                            if (missonDataItem["isPassed"]):
                                console.print("检测到任务:[yellow]Viedo[not b not uu green]\t[已完成]")
                            else:
                                # 未完成
                                is_job()
                        except:
                            # 报错就是未完成
                            is_job()
                    elif ((missonDataItem["type"] == "document")):
                        # 加层判断 pdf不做处理 虽然有任务id 但是不作为任务点
                        if (missonDataItem["property"]['type'] != ".pdf"):
                            def is_job():
                                try:
                                    temp = missonDataItem["jobid"]
                                    console.print("检测到任务:[yellow]Document[not b not uu red]\t[未完成]")
                                    post_document(missonDataItem, missonData["defaults"], missionParts_index, missonDataItem_index)
                                except:
                                    console.print("检测到任务:[yellow]Document[not b not uu blue]\t[非任务]")

                            # 判断完成了没
                            try:
                                if (missonDataItem["isPassed"]):
                                    console.print("检测到任务:[yellow]Document[not b not uu green]\t[已完成]")
                                else:
                                    # 未完成
                                    is_job()
                            except:
                                # 报错就是未完成
                                is_job()
                    else:
                        # 题目类型workid
                        console.print("检测到任务:[yellow]Work[red]\t[已跳过]")
                except:
                    console.print("检测到任务:[yellow]混淆任务[red]\t[已过滤]")

        except Exception as e:
            # if (missionParts_index == 0):
            #     print("-当前章节所有任务点遍历完成-")
            # else:
            #     print("-当前章节所有任务点遍历完成-")
            continue
    console.print("[cyan][当前章节所有任务点遍历完成]\n")


# 获取video类型任务点信息
def get_videoMission_data(missonDataItem, missonData_defaults, missionParts_index, missonDataItem_index):
    # missionParts_index:当前章节任务块索引
    # missonDataItem_index:当前任务块视频任务索引
    headers = {
        "Referer": "https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2022-0406-1945",
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
    }
    url = "https://mooc1.chaoxing.com/ananas/status/{}".format(missonDataItem["objectId"])
    response = requests.get(url=url, cookies=cookies, headers=headers)
    video_data = json.loads(response.content.decode('utf8'))
    start_videoMission(missonDataItem, missonData_defaults, video_data, missionParts_index, missonDataItem_index)


# 开始刷课
def start_videoMission(missonDataItem, missonData_defaults, video_data, missionParts_index, missonDataItem_index):
    # missionParts_index:当前章节任务块索引
    # missonDataItem_index:当前任务块视频任务索引
    response_json = {"isPassed": "false"}

    def get_test(courseid, clazzid, knowledgeid, cpi):
        url = "https://mooc1-1.chaoxing.com/knowledge/cards?clazzid={}&courseid={}&knowledgeid={}&num={}&ut=s&cpi={}&v=20160407-1".format(clazzid, courseid, knowledgeid, missionParts_index, cpi)
        response = requests.get(url=url, headers=headers, cookies=cookies)
        soup = BeautifulSoup(response.content.decode("utf8"), "html5lib")
        missonData = json.loads(re.search(r'mArg =(.*?);(\s\S)catch', soup.body.find_all("script")[0].string, flags=re.M).group(1))
        current_missonDataItem = missonData["attachments"][missonDataItem_index]
        # 加个判断,第一次看视频,检测服务器保存的进度为空
        # try:
        #     console.print(f'[完成提交进度]{current_missonDataItem["playTime"]}ms', justify="center")
        # except:
        #     console.print(f'[完成提交进度]{0}ms', justify="center")

    def post(isdrag):
        # [clazzId][userid][jobid][objectid][playingTime*1000][d_yHJ!$pdA~5][duration*1000][0_duration] md5
        encStr = '[{}][{}][{}][{}][{}][{}][{}][{}]'
        encStr = encStr.format(missonData_defaults["clazzId"], missonData_defaults["userid"], missonDataItem['jobid'], missonDataItem["objectId"], playTime, "d_yHJ!$pdA~5",
                               int(video_data['duration']) * 1000, "0_" + str(video_data['duration']))
        md5 = hashlib.md5(encStr.encode("utf8"))
        enc = md5.hexdigest()
        try:
            rt = missonDataItem["property"]['rt']
        except:
            rt = "0.9"
        data = {
            "clazzId": missonData_defaults["clazzId"],  # 获取到
            "playingTime": int(int(playTime) / 1000),  # 当前播放到的时间 秒
            "duration": video_data['duration'],  # 视频总时长	秒
            "clipTime": "0_" + str(video_data['duration']),  # 视频总时长	秒
            "objectId": missonDataItem["objectId"],  # 获取到
            "otherInfo": missonDataItem["otherInfo"],  # 获取到
            "jobid": missonDataItem['jobid'],  # 获取到
            "userid": missonData_defaults["userid"],  # 获取到
            "isdrag": isdrag,  # 固定 3首次开始播放 2暂停 0播放自己提交
            "view": "pc",  # 固定
            "enc": enc,  # md5加密
            "rt": rt,  # 固定
            "dtype": "Video",  # 固定
            "_t": int(round(time.time() * 1000))  # 时间戳 固定
        }
        lt = []
        for k, v in data.items():
            lt.append(k + '=' + str(v))
        query_string = '&'.join(lt)
        url = "https://mooc1.chaoxing.com/multimedia/log/a/{}/{}?{}".format(missonData_defaults['cpi'], video_data["dtoken"], query_string)
        response = requests.get(url=url, cookies=cookies, headers=headers)
        try:
            # 加个判断 防止提交进度出问题，好定位bug
            rjson = json.loads(response.content.decode('utf8'))
            if (rjson["isPassed"]):
                # 已经通过了
                return True
            else:
                return False
        except:
            # t =math.floor(2147483647*random.random())
            # verify_soup = BeautifulSoup(response.content.decode('utf8'), "html5lib")
            # print(verify_soup.find("img"))
            # img_headers = {
            #     "Accept": "image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            #     "Accept-Encoding": "gzip, deflate, br",
            #     "Cache-Control": "no-cache",
            #     "Connection": "keep-alive",
            #     "Host": "mooc1-2.chaoxing.com",
            #     "Pragma": "no-cache",
            #     "sec-ch-ua-mobile": "?0",
            #     "sec-ch-ua-platform": "\"Windows\"",
            #     "Sec-Fetch-Dest": "image",
            #     "Sec-Fetch-Mode": "no-cors",
            #     "Sec-Fetch-Site": "same-origin",
            #     "Referer": "https://mooc1-2.chaoxing.com/antispiderShowVerify.ac",
            #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47"
            # }
            # imgUrl = f"https://mooc1-2.chaoxing.com/processVerifyPng.ac?t={math.floor(random.random() * 2147483647)}"
            # res = requests.get(imgUrl, cookies=cookies, headers=img_headers)
            # print(res.content)
            # with open("./code.png", "wb") as f:
            #     r = requests.get(imgUrl)
            #     f.write(r.content)
            #     f.close()

            # 暴力破解过验证码
            console.print("[red][系统拦截]:拦截到验证码检测,已经跳过验证码检测...")
            # get_url = f"https://mooc1-2.chaoxing.com/html/processVerify.ac?app=0&ucode={verify_code}"
            # print(requests.get(get_url, cookies=cookies, headers=headers).content.decode("utf8"))
            return False

    headers = {
        "Referer": "https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2022-0406-1945",
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
    }
    try:
        playTime = int(missonDataItem["playTime"])
    except:
        playTime = 0

    try:
        isPassed = missonDataItem["isPassed"]
    except:
        isPassed = False

    if (not isPassed):
        global post_time

        console.rule("[bold green]开 始 刷 课")
        console.print(f"{playTime}ms/{int(video_data['duration']) * 1000}ms", style="green", justify="center")
        console.print(f"{video_data['filename']}", style="green", justify="center")
        isPassed_count = 0
        with alive_bar(int(video_data['duration']) * 1000, manual=True) as bar:
            while True:
                # 60秒提交一次 模拟自动提交 isdrag=0
                # 睡之前判断下还剩多少时长,小于60之内直接睡剩下的时间
                if (int(video_data["duration"] * 1000) - int(playTime) < 1000):
                    time.sleep(int(int(video_data["duration"] * 1000) - int(playTime)))
                    playTime += int(video_data["duration"] * 1000) - int(playTime)
                else:
                    time.sleep(post_time)
                    playTime += 1000 * post_time
                isPassed_bool = post("0")
                # console.print("[已提交进度]{}ms/{}ms".format(playTime, int(video_data["duration"] * 1000)), justify="center")
                if (isPassed_bool):
                    # 说明已经返回isPassed为True了,为了防止数据不准,当5次返回都true时,说明完成了,记录一下测试,只有有一次false就清理
                    isPassed_count += 1
                    post_time = 1
                    if (isPassed_count == 10):
                        break
                    else:
                        console.print(f"当前视频已经完成,正在进行{isPassed_count}次检测[red](需要完成10测检测即完成当前任务点)", style="blue")
                else:
                    isPassed_count = 0
                bar(playTime / int(video_data["duration"] * 1000))
        console.rule("[bold red]学 习 完 成")


def post_document(missonDataItem, missonData_defaults, missionParts_index, missonDataItem_index):
    console.rule("开始文档类型提交")
    console.print(f'文档名称:{missonDataItem["property"]["name"]}', justify="center")
    # document类型提交
    headers = {
        "Referer": "https://mooc1.chaoxing.com/ananas/modules/pdf/index.html?v=2022-0218-1135",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54"
    }
    data = {
        "jobid": missonDataItem["jobid"],
        "knowledgeid": missonData_defaults["knowledgeid"],
        "courseid": missonData_defaults["courseid"],
        "clazzid": missonData_defaults["clazzId"],
        "jtoken": missonDataItem["jtoken"],
        "_dc": int(round(time.time() * 1000))
    }
    url = f"https://mooc1.chaoxing.com/ananas/job/document?jobid={data['jobid']}&knowledgeid={data['knowledgeid']}&courseid={data['courseid']}&clazzid={data['clazzid']}&jtoken={data['jtoken']}&_dc={data['_dc']}"

    # 检查文档类型学习提交是否通过
    while True:

        try:
            res = requests.get(url=url, cookies=cookies, headers=headers)
            if (json.loads(res.content.decode("utf8"))["status"]):
                console.print(f'[blue][{time.strftime("%H:%M", time.localtime())}][green]任务点提交成功!')
                console.rule("完成文档类型提交")
                break
        except:
            print("提交异常,即将重新尝试提交")


def login(uname, passward):
    login = requests.get("http://passport2.chaoxing.com/login?", headers=headers)
    global cookies
    cookies = login.cookies
    login_heades = {
        "Content-Type": "application/x-www-form-urlencoded",
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
    }
    login_url = "http://passport2.chaoxing.com/fanyalogin"
    login_data = {
        "fid": "-1",
        "uname": uname,
        "password": base64.b64encode(passward.encode("utf8")),
        "refer": "http://i.chaoxing.com",
        "t": "true",
        "forbidotherlogin": "0",
        "validate": ""
    }
    login_response = requests.post(url=login_url, headers=login_heades, cookies=cookies, data=parse.urlencode(login_data), )
    cookies.update(login_response.cookies)

    get_course_unit()
    try:
        return login_response.json()["status"]
    except:
        return False


# 登录
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}
cookies = ""

while True:
    uname = input("请输入账号(手机号):")
    passward = input("请输入密码:")
    if (login(uname, passward)):
        break
    else:
        console.print("[red][登录失败,请尝试重新登录]")

while True:
    command = input("输入需要刷课的课程序号:")
    try:
        get_chapterUnit(courses_list[int(command)]["courseId"], courses_list[int(command)]["clazzid"], courses_list[int(command)]["cpi"])
        console.print(print_course())
    except:
        print("指令出错")
