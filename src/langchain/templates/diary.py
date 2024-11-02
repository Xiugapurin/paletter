diary_emotion_template = """##Instruction##
以下是一段日記內容，你需要根據使用者的日記分析其文字中的情緒:
{query}
##Restriction##
你需要挑選以下任一個情緒，以下是9種可挑選的情緒以及其對應的顏色:
1. 憤怒激動暴躁: Red
2. 興奮驚奇驚喜: Orange
3. 高興愉快喜悅: Yellow
4. 平靜輕鬆悠閒: Green
5. 疲憊無力嗜睡: Blue
6. 悲傷憂鬱沮喪: Indigo
7. 挫折煩躁苦惱: Purple
8. 緊張害怕驚恐: Pink
9. 當日記無法被分類為以上情緒時: White

##Format Instruction##
{format_instructions}
##Output##
請回傳該日記情緒所對應的顏色字串，如:Yellow、White等
"""
