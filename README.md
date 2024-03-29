<p align="center">
    <a href="https://github.com/Hyrmm/chaoxingSpider" target="_blank" style="margin-right: 20px; font-style: normal; text-decoration: none;">
        <img src="https://img.shields.io/github/stars/Hyrmm/chaoxingSpider" alt="Github Stars" />
    </a>
    <a href="https://github.com/Hyrmm/chaoxingSpider" target="_blank" style="margin-right: 20px; font-style: normal; text-decoration: none;">
        <img src="https://img.shields.io/github/forks/Hyrmm/chaoxingSpider" alt="Github Forks" />
    </a>
    <a href="https://github.com/Hyrmm/chaoxingSpider" target="_blank" style="margin-right: 20px; font-style: normal; text-decoration: none;">
        <img src="https://img.shields.io/github/languages/code-size/Hyrmm/chaoxingSpider" alt="Code-size" />
    </a>
    <a href="https://github.com/Hyrmm/chaoxingSpider" target="_blank" style="margin-right: 20px; font-style: normal; text-decoration: none;">
        <img src="https://img.shields.io/github/v/release/Hyrmm/chaoxingSpider?display_name=tag&sort=semver" alt="version" />
    </a>
</p>


## :cl: 最近更新

- 2022.5.17 暴力跳过视频类型任务点的验证码检测
- 2022.5.26 修复无法登录失败问题(密码登录加密模式更新了)
  - 使用教程:
    1. [点我查看源码](https://github.com/Hyrmm/chaoxingSpider/blob/main/crypto.txt),也可在当前脚本目录下用记事本打开复制
    2. 复制`cypoto.txt`文件内的JavaScript源码
    3. 打开浏览器,按`F12`打开控制台(`CONSOLE`),粘贴源码,回车
    4. 在控制台输入`des("你的密码")`，注:双引号不要丢
    5. 举例:`des("123456")`
    6. 控制台会输出你的des密码，拿着这个密码去登录，可以保存下来，密码不更改，des密码也不会变动。
    7. 复制控制台的密码时，注意复制双引号内的内容
- 2022.5.28 一系列修复
   - 修复密码登录后,提交刷课问题
   - 添加自定义倍速



## :wrench: 功能介绍

### :one:智能自动化

- 自动跳过非任务点视频，ppt，word
- 自动根据历史进度完成视频播放(自己之前手动看过的进度)
- 自动完成当前任务继续完成下个任务,直至本课程全部完成

### :two:支持多类型任务点

- Document(ppt、word等)
- Video(视频类型)
- Work(没有题库，暂且不整)

### :three:可自定义视频类型任务点观看速率

- 倍速有风险,谨慎而为之

## :orange_book:使用教程

### :one:可执行文件运行(小白推荐,不稳定)

- 教程:待跟新

### :two:源码运行(更稳定)

1. 准备Python =3.6
2. git clone 项目至本地
3. pip install -r requirements.txt
4. python main.py 运行程序

## :warning: 免责声明  
- 本代码遵循 [GPL-3.0 License](https://github.com/Samueli924/chaoxing/blob/main/LICENSE)协议，允许**开源/免费使用和引用/修改/衍生代码的开源/免费使用**，不允许**修改和衍生的代码作为闭源的商业软件发布和销售**，禁止**使用本代码盈利**，以此代码为基础的程序**必须**同样遵守[GPL-3.0 License](https://github.com/Samueli924/chaoxing/blob/main/LICENSE)协议  
- 本代码仅用于**学习讨论**，禁止**用于盈利**  
- 他人或组织使用本代码进行的任何**违法行为**与本人无关  
