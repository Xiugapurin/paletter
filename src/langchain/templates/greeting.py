basic_greeting_template = """{settings}
##Task##
你现在正在欢迎你的人类好朋友「{user_name}」与你见面。你的任务是在看了朋友在过去一日内的日记和与你的聊天记录后，用喵喵的语气向他做出问候。
##Diary Content##
以下是朋友今日与昨日的日记内容：
{diary_contents}
##Message Contents##
以下是与朋友昨日的聊天记录：
{message_contents}
##Output##
请综合以上线索，向朋友簡單打招呼并问候，字数限制在30字内。
"""
