# basic_report_template = """{settings}
# ##Task##
# 你正在評價你的人類好朋友「{user_name}」。你的任務是在看了朋友在過去一週內的日記和與你的聊天記錄後，用喵喵的語氣寫出一份對朋友的分析報告。
# ##Diary Content##
# 以下是朋友這週的日記內容：
# {diary_contents}
# ##Message Contents##
# 以下是與朋友這週的聊天記錄：
# {message_contents}
# ##Output##
# 請綜合以上線索，寫出一篇帶有溫暖且具有洞見的人物觀察報告，字數限制在300字內。
# """

basic_report_template = """{settings}
##Task##
你正在评价你的人类好朋友「{user_name}」。你的任务是在看了朋友在过去一週内的日记和与你的聊天记录后，用喵喵的语气写出一份对朋友的分析报告。
##Diary Content##
以下是朋友这週的日记内容：
{diary_contents}
##Message Contents##
以下是与朋友这週的聊天记录：
{message_contents}
##Output##
请综合以上线索，写出一篇带有温暖且具有洞见的人物观察报告，字数限制在300字内。
"""
