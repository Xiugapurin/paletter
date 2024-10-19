diary_emotion_template = """##Instruction##
以下是一段日記內容，你需要根據使用者的日記分析其文字中的情緒：
{query}

限制：你需要挑選以下任一個情緒，以下是9種可挑選的情緒以及其對應的顏色:

1. 憤怒暴躁：Red
2. 快樂喜悅：Yellow
3. 悲傷難過：Blue
4. 恐懼害怕：Purple
5. 焦慮煩惱：Orange
6. 厭惡煩躁：Green
7. 平靜祥和：Indigo
8. 無助委屈：Gray
9. 當日記無法被分類為以上情緒時: White

請回傳該日記情緒所對應的顏色字串，如：Yellow、White等
"""
