import random, math
from datetime import date, datetime
from collections import defaultdict
from flask import g
from flask_restful import Resource, reqparse
from src import db
from src.models import User, Paletter, Diary, DiaryEntry, Knowledge
from src.langchain.responses import get_diary_reply
from src.langchain.utils import get_embedding
from src.constants.paletter_table import paletter_code_table

parser = reqparse.RequestParser()


def combine_entries_to_chunks(diary_entries):
    chunks = []
    current_chunk = []
    current_length = 0

    i = 0
    while i < len(diary_entries):
        entry = diary_entries[i]
        timestamp = f"{entry.created_time.strftime('20%y/%m/%d %H:%M')}"
        entry_text = f"{timestamp} - {entry.content}"
        entry_length = len(entry.content)  # 只計算content的長度，不含timestamp

        # 如果單一entry字數大於200，直接加入chunks
        if entry_length > 200:
            chunks.append(entry_text)
            i += 1
            continue

        # 如果entry字數小於200，嘗試與後續entries合併
        current_chunk = [entry_text]
        current_length = entry_length
        next_idx = i + 1
        can_combine = True

        while next_idx < len(diary_entries) and current_length < 200 and can_combine:
            next_entry = diary_entries[next_idx]
            next_length = len(next_entry.content)  # 只計算content的長度，不含timestamp

            # 檢查合併後是否會超過300
            if current_length + next_length > 300:
                can_combine = False
                break

            next_timestamp = f"{next_entry.created_time.strftime('20%y/%m/%d %H:%M')}"
            next_text = f"{next_timestamp} - {next_entry.content}"
            current_chunk.append(next_text)
            current_length += next_length
            next_idx += 1

        # 將當前chunk加入chunks列表
        chunks.append("\n\n".join(current_chunk))
        i = next_idx if can_combine else i + 1

    return chunks


class DiaryResource(Resource):
    def get(self, diary_id):
        user_id = g.user_id

        # Today's diary
        if diary_id == 0:
            today = datetime.now().date()

            diary = Diary.query.filter_by(user_id=user_id, date=today).first()

            if not diary:
                diary = Diary(user_id=user_id)
                db.session.add(diary)
                db.session.commit()

                return {
                    "diary_info": diary.to_dict(),
                    "diary_entries": [],
                }, 200

            diary_id = diary.diary_id
        else:
            diary = Diary.query.filter_by(
                user_id=user_id, diary_id=diary_id
            ).first_or_404()

        diary_entries = DiaryEntry.query.filter_by(diary_id=diary_id).all()

        return {
            "diary_info": diary.to_dict(),
            "diary_entries": [entry.to_dict() for entry in diary_entries],
        }, 200

    def put(self, diary_id):
        user_id = g.user_id

        user = User.query.get_or_404(user_id)
        diary = Diary.query.filter_by(user_id=user_id, diary_id=diary_id).first_or_404()
        diary_entries = DiaryEntry.query.filter_by(diary_id=diary_id).all()

        if not diary_entries:
            return {"message": "Diary is empty."}, 404

        emotion_stats = defaultdict(lambda: {"chars": 0, "latest_time": datetime.min})

        for entry in diary_entries:
            emotion = entry.emotion
            char_count = len(entry.content)

            emotion_stats[emotion]["chars"] += char_count
            if entry.created_time > emotion_stats[emotion]["latest_time"]:
                emotion_stats[emotion]["latest_time"] = entry.created_time

        max_chars = max(stat["chars"] for stat in emotion_stats.values())
        dominant_emotions = [
            emotion
            for emotion, stat in emotion_stats.items()
            if stat["chars"] == max_chars
        ]

        if len(dominant_emotions) > 1:
            dominant_emotion = max(
                dominant_emotions, key=lambda e: emotion_stats[e]["latest_time"]
            )
        else:
            dominant_emotion = dominant_emotions[0]

        available_paletters = paletter_code_table[dominant_emotion]
        selected_paletter = random.choice(available_paletters)
        paletter_code = f"{dominant_emotion}-{selected_paletter['number']}"
        paletter_name = selected_paletter["name"]

        # TODO: Add paletter when paletter not exist
        paletter = Paletter.query.filter_by(
            user_id=user_id, paletter_code=paletter_code
        ).first_or_404()

        today = date.today()
        days_diff = str((today - paletter.created_time.date()).days + 1)
        intimacy_level = str(math.floor(paletter.intimacy_level / 20))

        diary_content = "\n\n".join(
            [
                f"{entry.created_time.strftime('%H:%M')} - {entry.content}"
                for entry in diary_entries
            ]
        )

        reply_content = get_diary_reply(
            user.name,
            paletter_code,
            paletter_name,
            days_diff,
            intimacy_level,
            diary_content,
        )

        diary.reply_paletter_code = paletter_code
        diary.reply_content = reply_content

        diary_chunks = combine_entries_to_chunks(diary_entries)

        for chunk_content in diary_chunks:
            embedding = get_embedding(chunk_content)

            knowledge = Knowledge(
                user_id=user_id,
                paletter_id=paletter.paletter_id,
                date=today,
                content=chunk_content,
                embedding=embedding,
                activate_count=0,
                is_activate=True,
            )

            db.session.add(knowledge)

        db.session.add(diary)
        db.session.commit()

        return diary.to_dict(), 200

    def delete(self, diary_id):
        user_id = g.user_id
        diary = Diary.query.filter_by(user_id=user_id, diary_id=diary_id).first_or_404()

        db.session.delete(diary)
        db.session.commit()

        return "", 200


class DiaryListResource(Resource):
    def get(self, page):
        user_id = g.user_id

        try:
            page = int(page)
        except ValueError:
            return {"error": "Invalid page format."}, 400

        if page < 1:
            return {"error": "Page number must be greater than or equal to 1."}, 400

        pagination = (
            Diary.query.filter_by(user_id=user_id)
            .order_by(Diary.date.desc())
            .paginate(page=page, per_page=30, error_out=False)
        )

        diary_list = [diary.to_limited_dict() for diary in pagination.items]
        next_page = pagination.page + 1 if pagination.has_next else -1

        return {
            "diary_list": diary_list,
            "next_page": next_page,
            "total_pages": pagination.pages,
        }, 200
