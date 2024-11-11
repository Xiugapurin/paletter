# diary_emotion_template = """##Instruction##
# 以下是一段日記內容，你需要根據使用者的日記分析其文字中的情緒:
# {query}
# ##Restriction##
# 你需要挑選以下任一個情緒，以下是9種可挑選的情緒以及其對應的顏色:
# 1. 憤怒激動暴躁: Red
# 2. 興奮驚奇驚喜: Orange
# 3. 高興愉快喜悅: Yellow
# 4. 平靜輕鬆悠閒: Green
# 5. 疲憊無力嗜睡: Blue
# 6. 悲傷憂鬱沮喪: Indigo
# 7. 挫折煩躁苦惱: Purple
# 8. 緊張害怕驚恐: Pink
# 9. 當日記無法被分類為以上情緒時: White

# ##Format Instruction##
# {format_instructions}
# ##Output##
# 請回傳該日記情緒所對應的顏色字串，如:Yellow、White等
# """

# diary_title_template = """##Instruction##
# 你的任務是根據日記的內容以及時間戳來為該短篇日記命名一個標題，原則如下：
# 1. 若日記中包含地點或場合則優先包含在標題中
# 2. 若日記中包含情緒則可以將其包含在標題中
# 3. 若以上兩者皆不明確，則可以參考時間戳來命名
# ##Examples##
# 以下是一些的標題與內容之間的對應關係範例：
# 1. 校園生活的喜悅：當日記內容描述了在學校發生的開心的回憶，可以採用此類標題
# 2. 半夜的失落心情：當日記沒有明顯的描述地點，並且是在半夜時寫下的日記，可以採用此類標題
# 3. 生活中的小確幸：當日記沒有明顯的地點場合和時間，並且是驚喜愉悅的心情可以採用此類標題
# 4. 中午的心情小記：當日記內容雜亂無章或是沒有主旨，則可以考慮直接用時間+心情小記的命名法
# 注意：以上標題範例僅供參考，實際情況中的日記類型有數百種，請遵照命名原則自由命名即可。
# ##Restriction##
# 日記的標題命名請勿超過10字，過多的標題字數是違規的。
# ##Input##
# 以下是需要被命名的日記內容，該日記被寫下的時間為{timestamp}：
# """

diary_emotion_template = """##Instruction##
以下是一段日记内容，你需要根据使用者的日记分析其文字中的情绪:
{query}
##Restriction##
你需要挑选以下任一个情绪，以下是9种可挑选的情绪以及其对应的颜色:
1. 愤怒激动暴躁: Red
2. 兴奋惊奇惊喜: Orange
3. 高兴愉快喜悦: Yellow
4. 平静轻松悠闲: Green
5. 疲惫无力嗜睡: Blue
6. 悲伤忧鬱沮丧: Indigo
7. 挫折烦躁苦恼: Purple
8. 紧张害怕惊恐: Pink
9. 当日记无法被分类为以上情绪时: White

##Format Instruction##
{format_instructions}
##Output##
请回传该日记情绪所对应的颜色字串，如:Yellow、White等
"""

diary_title_template = """##Instruction##
你的任务是根据日记的内容以及时间戳来为该短篇日记命名一个标题，原则如下：
1. 若日记中包含地点或场合则优先包含在标题中
2. 若日记中包含情绪则可以将其包含在标题中
3. 若以上两者皆不明确，则可以参考时间戳来命名
##Examples##
以下是一些的标题与内容之间的对应关係范例：
1. 校园生活的喜悦：当日记内容描述了在学校发生的开心的回忆，可以採用此类标题
2. 半夜的失落心情：当日记没有明显的描述地点，并且是在半夜时写下的日记，可以採用此类标题
3. 生活中的小确幸：当日记没有明显的地点场合和时间，并且是惊喜愉悦的心情可以採用此类标题
4. 中午的心情小记：当日记内容杂乱无章或是没有主旨，则可以考虑直接用时间+心情小记的命名法
注意：以上标题范例仅供参考，实际情况中的日记类型有数百种，请遵照命名原则自由命名即可。
##Restriction##
日记的标题命名请勿超过10字，过多的标题字数是违规的。
##Input##
以下是需要被命名的日记内容，该日记被写下的时间为{timestamp}：
"""
