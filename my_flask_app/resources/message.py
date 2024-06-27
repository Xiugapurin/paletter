from datetime import datetime
from flask import g
from flask_restful import Resource, reqparse
from my_flask_app import db
from my_flask_app.models import User, Message
from my_flask_app.langchain.responses import get_llm_response

parser = reqparse.RequestParser()
parser.add_argument("content", type=str)


class MessageListResource(Resource):
    def get(self):
        user_id = g.user_id

        messages = Message.query.filter_by(user_id=user_id).all()
        if not messages:
            # 沒有訊息時，回傳提示訊息
            ai_message = {
                "message_id": "initial_message",
                "user_id": user_id,
                "sender": "AI",
                "content": "歡迎使用聊天室！請在下方輸入內容以開始聊天。",
                "send_time": datetime.now().isoformat(),
            }
            return {"messages": [ai_message]}, 200

        return {"messages": [message.to_dict() for message in messages]}, 200

    def post(self):
        args = parser.parse_args()
        user_id = g.user_id
        content = args["content"]

        user = User.query.get_or_404(user_id)
        llm_preference = user.llm_preference

        user_message = Message(
            user_id=user_id, sender="USER", content=content, send_time=datetime.now()
        )
        db.session.add(user_message)

        system_template = (
            "以下對話請以繁體中文與使用者應答，"
            "你現在必須扮演一隻來自魔法國度的精靈，"
            "並且作為使用者的夥伴，同時不要透露自己AI的身份。\n"
            "注意：你是一隻虛擬世界的精靈，你無法和使用者在真實世界見面。\n"
            "精靈的個性設定如下：\n"
            "{llm_preference}\n"
        )

        ai_response_content = get_llm_response(content, system_template, llm_preference)

        # 添加AI回應到資料庫
        ai_message = Message(
            user_id=user_id,
            sender="AI",
            content=ai_response_content,
            send_time=datetime.now(),
        )
        db.session.add(ai_message)

        db.session.commit()

        return {
            "user_message": user_message.to_dict(),
            "ai_message": ai_message.to_dict(),
        }, 200
