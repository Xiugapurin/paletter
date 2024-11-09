import uuid
import math
from collections import defaultdict
from datetime import datetime
from calendar import monthrange
from flask import g
from flask_restful import Resource
from sqlalchemy import extract
from src.models import Diary, DiaryEntry
from src.constants.paletter_table import paletter_name_table, emotion_value_table


def get_emotion_stats_list(diaries, emotion_stats_list):
    entries_by_day_list = []
    for diary in diaries:
        diary_entries = DiaryEntry.query.filter(
            DiaryEntry.diary_id == diary.diary_id
        ).all()

        total_word_count = sum(len(entry.content) for entry in diary_entries)
        entries = []
        for entry in diary_entries:
            word_count = len(entry.content)
            if word_count > 0:
                proportion = (
                    word_count / total_word_count if total_word_count > 0 else 0
                )
                entries.append({"emotion": entry.emotion, "proportion": proportion})

        entries_by_day_list.append(
            {
                "diary_id": diary.diary_id,
                "date": diary.date.strftime("%Y-%m-%d"),
                "entries": entries,
            }
        )

    for day_entry in entries_by_day_list:
        date = datetime.strptime(day_entry["date"], "%Y-%m-%d")
        day_index = date.day - 1

        if 0 <= day_index < len(emotion_stats_list):
            arousal_value = 0
            valence_value = 0
            unique_emotions = set()

            if day_entry["entries"]:
                for entry in day_entry["entries"]:
                    emotion = entry["emotion"]
                    unique_emotions.add(emotion)
                    proportion = entry["proportion"]

                    arousal_value += (
                        emotion_value_table[emotion]["arousal"] * proportion
                    )
                    valence_value += (
                        emotion_value_table[emotion]["valence"] * proportion
                    )

                arousal_value = min(int(math.floor(arousal_value / 0.2)) + 1, 5)
                valence_value = min(int(math.floor(valence_value / 0.2)) + 1, 5)

            emotion_stats_list[day_index].update(
                {
                    "diary_id": day_entry["diary_id"],
                    "date": day_entry["date"],
                    "emotion_list": list(unique_emotions),
                    "arousal_value": arousal_value,
                    "valence_value": valence_value,
                }
            )

    return emotion_stats_list


def get_emotion_percentage_by_count(emotion_counts):
    total_count = sum(count for count in emotion_counts.values() if count > 0)
    emotion_percentage_list = [
        {
            "uid": str(uuid.uuid4()),
            "emotion": emotion,
            "percentage": (
                round((count / total_count) * 100, 2) if total_count > 0 else 0
            ),
        }
        for emotion, count in emotion_counts.items()
        if count > 0
    ]

    emotion_percentage_list.sort(key=lambda x: x["percentage"], reverse=True)

    return emotion_percentage_list


def get_emotion_percentage_by_words(diaries):
    emotion_word_counts = {
        "Red": 0,
        "Orange": 0,
        "Yellow": 0,
        "Green": 0,
        "Blue": 0,
        "Indigo": 0,
        "Purple": 0,
        "Pink": 0,
        "White": 0,
    }

    for diary in diaries:
        diary_entries = DiaryEntry.query.filter(
            DiaryEntry.diary_id == diary.diary_id
        ).all()

        for entry in diary_entries:
            if entry.emotion:
                word_count = len(entry.content)
                emotion_word_counts[entry.emotion] += word_count

    total_words = sum(count for count in emotion_word_counts.values() if count > 0)

    emotion_percentage_by_words_list = [
        {
            "uid": str(uuid.uuid4()),
            "emotion": emotion,
            "percentage": (
                round((count / total_words) * 100, 2) if total_words > 0 else 0
            ),
        }
        for emotion, count in emotion_word_counts.items()
        if count > 0
    ]

    emotion_percentage_by_words_list.sort(key=lambda x: x["percentage"], reverse=True)
    return emotion_percentage_by_words_list


def get_paletter_rank_list(diary_list):
    paletter_counts = {}
    for entry in diary_list:
        if entry["paletter_code"] != "" and entry["diary_id"] != -1:
            paletter_code = entry["paletter_code"]
            paletter_counts[paletter_code] = paletter_counts.get(paletter_code, 0) + 1

    paletter_rank_list = [
        {
            "paletter_code": code,
            "paletter_name": paletter_name_table[code],
            "count": count,
        }
        for code, count in paletter_counts.items()
    ]

    paletter_rank_list.sort(key=lambda x: x["count"], reverse=True)

    return paletter_rank_list


class EmotionListResource(Resource):
    def get(self, year, month):
        user_id = g.user_id

        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return {"error": "Invalid year or month format."}, 400

        if month < 1 or month > 12:
            return {"error": "Invalid month."}, 400

        if year < 1900 or year > datetime.now().year + 1:
            return {"error": "Invalid year."}, 400

        days_in_month = monthrange(year, month)[1]
        current_date = datetime.now().date()

        diary_list = [
            {
                "diary_id": -1,
                "date": f"{year}-{month:02d}-{str(day).zfill(2)}",
                "emotion": "",
                "paletter_code": "",
            }
            for day in range(1, days_in_month + 1)
        ]

        init_emotion_stats_list = [
            {
                "diary_id": -1,
                "date": f"{year}-{month:02d}-{str(day).zfill(2)}",
                "emotion_list": [],
                "arousal_value": 0,
                "valence_value": 0,
            }
            for day in range(1, days_in_month + 1)
        ]

        emotion_counts = {
            "Red": 0,
            "Orange": 0,
            "Yellow": 0,
            "Green": 0,
            "Blue": 0,
            "Indigo": 0,
            "Purple": 0,
            "Pink": 0,
            "White": 0,
        }

        diaries = Diary.query.filter(
            Diary.user_id == user_id,
            extract("year", Diary.date) == year,
            extract("month", Diary.date) == month,
            (
                Diary.date <= current_date
                if year == current_date.year and month == current_date.month
                else True
            ),
        ).all()

        for diary in diaries:
            day = diary.date.day - 1
            diary_dict = diary.to_emotion_dict()
            diary_list[day] = diary_dict
            diary_emotion = diary_dict.get("emotion", "")
            if diary_emotion != "":
                emotion_counts[diary_emotion] += 1

        emotion_stats_list = get_emotion_stats_list(diaries, init_emotion_stats_list)
        emotion_percentage_by_count = get_emotion_percentage_by_count(emotion_counts)
        emotion_percentage_by_words = get_emotion_percentage_by_words(diaries)
        paletter_rank_list = get_paletter_rank_list(diary_list)

        return {
            "diary_list": diary_list,
            "emotion_stats_list": emotion_stats_list,
            "emotion_percentage_by_count": emotion_percentage_by_count,
            "emotion_percentage_by_words": emotion_percentage_by_words,
            "paletter_rank_list": paletter_rank_list,
        }, 200
