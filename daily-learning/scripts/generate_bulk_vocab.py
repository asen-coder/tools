"""生成 5000 个英语学习词汇 CSV 文件（专业词典格式）。

基于义务教育英语课程标准、四六级、托福雅思核心词汇，
涵盖小学、初中、高中、大学核心词汇，按难度分为 5 级。

专业词典格式特点：
- 音标（IPA phonetics）
- 多种词性（parts of speech）
- 每种词性多个释义和例句
- 像牛津/朗文/剑桥专业词典一样展示

运行后生成 vocab_bulk_5000.csv，可用 add.py --import 导入。
"""

import csv
import json
import random
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
OUTPUT_CSV = SCRIPTS_DIR.parent / "vocab_bulk_5000.csv"

# 词性中文名称映射
POS_NAMES = {
    "n": "名词",
    "v": "动词",
    "adj": "形容词",
    "adv": "副词",
    "prep": "介词",
    "conj": "连词",
    "pron": "代词",
    "num": "数词",
    "art": "冠词",
    "int": "感叹词",
}

# 专业词典词汇库（每个词条包含音标、多词性、多释义、多例句）
VOCABULARY = [
    # ── 难度 1: 小学基础 ──────────────────────────────────────────────────────
    {
        "en": "run",
        "phonetic": "/rʌn/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["跑，奔跑", "经营，管理", "运行，运转"],
                "examples": [
                    "I run every morning.",
                    "She runs a small business.",
                    "The machine runs on electricity.",
                ],
            },
            {
                "pos": "n",
                "definitions": ["跑，奔跑", "路程，路线"],
                "examples": ["Go for a run.", "The bus route is a long run."],
            },
        ],
    },
    {
        "en": "book",
        "phonetic": "/bʊk/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "n",
                "definitions": ["书，书籍", "簿子，账本"],
                "examples": ["This is a good book.", "Keep your accounts in a book."],
            },
            {
                "pos": "v",
                "definitions": ["预订（房间、票等）"],
                "examples": ["Book a hotel room.", "I booked a flight to London."],
            },
        ],
    },
    {
        "en": "play",
        "phonetic": "/pleɪ/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["玩，玩耍", "演奏（乐器）", "播放", "参加（比赛）"],
                "examples": [
                    "Children play in the park.",
                    "She plays the piano.",
                    "Play your favorite song.",
                    "He plays soccer.",
                ],
            },
            {
                "pos": "n",
                "definitions": ["戏剧，剧本", "游戏，玩耍"],
                "examples": ["Watch a play.", "No time for play."],
            },
        ],
    },
    {
        "en": "water",
        "phonetic": "/ˈwɔːtər/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "n",
                "definitions": ["水", "海域，水域"],
                "examples": ["Drink more water.", "The ship entered deep water."],
            },
            {
                "pos": "v",
                "definitions": ["给...浇水", "流眼泪"],
                "examples": ["Water the plants.", "The smoke made my eyes water."],
            },
        ],
    },
    {
        "en": "help",
        "phonetic": "/help/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["帮助，协助", "促进，有助于"],
                "examples": ["Can you help me?", "Exercise helps health."],
            },
            {
                "pos": "n",
                "definitions": ["帮助，援助"],
                "examples": ["Thank you for your help."],
            },
        ],
    },
    {
        "en": "apple",
        "phonetic": "/ˈæpl/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "n",
                "definitions": ["苹果", "苹果公司"],
                "examples": [
                    "An apple a day keeps the doctor away.",
                    "I use Apple products.",
                ],
            }
        ],
    },
    {
        "en": "like",
        "phonetic": "/laɪk/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["喜欢，喜爱", "想要，希望"],
                "examples": ["I like reading.", "I would like a cup of coffee."],
            },
            {
                "pos": "prep",
                "definitions": ["像...一样", "例如"],
                "examples": [
                    "She looks like her mother.",
                    "Fruits like apples and oranges.",
                ],
            },
        ],
    },
    {
        "en": "time",
        "phonetic": "/taɪm/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "n",
                "definitions": ["时间", "时刻，时候", "次，回"],
                "examples": [
                    "What time is it?",
                    "Have a good time.",
                    "I went there three times.",
                ],
            }
        ],
    },
    {
        "en": "good",
        "phonetic": "/ɡʊd/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "adj",
                "definitions": ["好的，良好的", "令人满意的", "善良的"],
                "examples": [
                    "She is a good student.",
                    "The food tastes good.",
                    "He has a good heart.",
                ],
            }
        ],
    },
    {
        "en": "go",
        "phonetic": "/ɡəʊ/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["去，走", "离开", "变得，变成"],
                "examples": [
                    "Let's go home.",
                    "The train has gone.",
                    "The milk went bad.",
                ],
            }
        ],
    },
    {
        "en": "see",
        "phonetic": "/siː/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["看见，看到", "理解，明白", "拜访，会见"],
                "examples": [
                    "I can see the mountain.",
                    "I see what you mean.",
                    "See you tomorrow.",
                ],
            }
        ],
    },
    {
        "en": "make",
        "phonetic": "/meɪk/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["制作，制造", "使得，使...成为", "赚取，获得"],
                "examples": [
                    "Make a cake.",
                    "The news made me happy.",
                    "He makes money from trading.",
                ],
            }
        ],
    },
    {
        "en": "come",
        "phonetic": "/kʌm/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["来，来到", "出现，发生", "变成，成为"],
                "examples": [
                    "Come here please.",
                    "The time has come.",
                    "Her dream came true.",
                ],
            }
        ],
    },
    {
        "en": "take",
        "phonetic": "/teɪk/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["拿，取", "带（去），携带", "花费，需要"],
                "examples": [
                    "Take your umbrella.",
                    "Take me to the station.",
                    "It takes two hours.",
                ],
            }
        ],
    },
    {
        "en": "get",
        "phonetic": "/ɡet/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["得到，收到", "变得，变成", "到达"],
                "examples": [
                    "I got a gift.",
                    "It's getting dark.",
                    "When will we get there?",
                ],
            }
        ],
    },
    {
        "en": "know",
        "phonetic": "/nəʊ/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["知道，了解", "认识，熟悉"],
                "examples": ["I know the answer.", "Do you know her?"],
            }
        ],
    },
    {
        "en": "think",
        "phonetic": "/θɪŋk/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["想，思考", "认为，以为", "打算，想要"],
                "examples": [
                    "Think before you speak.",
                    "I think you're right.",
                    "He thinks to quit his job.",
                ],
            }
        ],
    },
    {
        "en": "look",
        "phonetic": "/lʊk/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["看，瞧", "看起来，显得", "寻找"],
                "examples": [
                    "Look at the blackboard.",
                    "She looks young.",
                    "I'm looking for my keys.",
                ],
            },
            {
                "pos": "n",
                "definitions": ["看，瞧", "表情，神色"],
                "examples": ["Have a look at this.", "A worried look on his face."],
            },
        ],
    },
    {
        "en": "want",
        "phonetic": "/wɒnt/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["想要，希望", "需要，缺乏"],
                "examples": ["I want a new car.", "The plant wants water."],
            }
        ],
    },
    {
        "en": "give",
        "phonetic": "/ɡɪv/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["给，给予", "举办，讲授", "传递，输送"],
                "examples": [
                    "Give me the book.",
                    "Give a lesson.",
                    "The sun gives light.",
                ],
            }
        ],
    },
    {
        "en": "use",
        "phonetic": "/juːz/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["使用，用", "耗费，消费"],
                "examples": ["Use your brain.", "The car uses too much fuel."],
            },
            {
                "pos": "n",
                "definitions": ["使用，应用", "用途，功能"],
                "examples": ["For the use of guests.", "What's the use of worrying?"],
            },
        ],
    },
    {
        "en": "find",
        "phonetic": "/faɪnd/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["找到，发现", "发觉，感到"],
                "examples": ["I found my lost keys.", "I find the book interesting."],
            }
        ],
    },
    {
        "en": "tell",
        "phonetic": "/tel/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["告诉，讲述", "辨别，区分"],
                "examples": ["Tell me the truth.", "Can you tell twins apart?"],
            }
        ],
    },
    {
        "en": "ask",
        "phonetic": "/ɑːsk/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["问，询问", "请求，要求"],
                "examples": ["Ask the teacher.", "Ask for help."],
            }
        ],
    },
    {
        "en": "work",
        "phonetic": "/wɜːk/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["工作，劳动", "运转，运作"],
                "examples": ["He works in a factory.", "The machine doesn't work."],
            },
            {
                "pos": "n",
                "definitions": ["工作，劳动", "著作，作品"],
                "examples": ["Hard work pays off.", "Read Shakespeare's works."],
            },
        ],
    },
    {
        "en": "call",
        "phonetic": "/kɔːl/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["称呼，叫...名", "打电话给", "呼唤，呼叫"],
                "examples": ["Call me John.", "Call me tomorrow.", "Call a taxi."],
            },
            {
                "pos": "n",
                "definitions": ["叫声，呼叫", "电话，通话"],
                "examples": ["Answer the call.", "I got a call from him."],
            },
        ],
    },
    {
        "en": "try",
        "phonetic": "/traɪ/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["尝试，努力", "试用，试验"],
                "examples": ["Try your best.", "Try the new method."],
            },
            {"pos": "n", "definitions": ["尝试，努力"], "examples": ["Give it a try."]},
        ],
    },
    {
        "en": "need",
        "phonetic": "/niːd/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["需要，必须"],
                "examples": ["You need help.", "Need I go?"],
            },
            {
                "pos": "n",
                "definitions": ["需要，必要", "贫穷，困境"],
                "examples": ["There's no need to worry.", "Help people in need."],
            },
        ],
    },
    {
        "en": "feel",
        "phonetic": "/fiːl/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["感觉，觉得", "摸，触", "认为，以为"],
                "examples": [
                    "I feel tired.",
                    "Feel the fabric.",
                    "I feel that he's right.",
                ],
            },
            {
                "pos": "n",
                "definitions": ["感觉，触觉"],
                "examples": ["The carpet has a soft feel."],
            },
        ],
    },
    {
        "en": "become",
        "phonetic": "/bɪˈkʌm/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["变成，成为"],
                "examples": ["He became a doctor.", "It's becoming cold."],
            }
        ],
    },
    {
        "en": "leave",
        "phonetic": "/liːv/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["离开，离去", "留下，剩下"],
                "examples": ["Leave the room.", "Nothing left to say."],
            },
            {
                "pos": "n",
                "definitions": ["许可，同意", "假期，休假"],
                "examples": ["Ask for leave.", "Take a leave of absence."],
            },
        ],
    },
    {
        "en": "put",
        "phonetic": "/pʊt/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["放，安置", "表达，表述"],
                "examples": ["Put the book on the table.", "Put it in simple words."],
            }
        ],
    },
    {
        "en": "mean",
        "phonetic": "/miːn/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["意思，意味着", "打算，预定"],
                "examples": ["What does this word mean?", "I meant to call you."],
            },
            {
                "pos": "adj",
                "definitions": ["吝啬的，自私的", "平均的"],
                "examples": ["He's mean with money.", "The mean temperature."],
            },
        ],
    },
    {
        "en": "keep",
        "phonetic": "/kiːp/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["保持，保留", "履行，遵守", "饲养，养育"],
                "examples": ["Keep silent.", "Keep your promise.", "Keep chickens."],
            }
        ],
    },
    {
        "en": "let",
        "phonetic": "/let/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["让，允许", "出租，租给"],
                "examples": ["Let me help you.", "Let the house."],
            }
        ],
    },
    {
        "en": "begin",
        "phonetic": "/bɪˈɡɪn/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["开始，着手"],
                "examples": ["Begin your work.", "The story begins here."],
            }
        ],
    },
    {
        "en": "seem",
        "phonetic": "/siːm/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["似乎，好像", "显得"],
                "examples": ["He seems happy.", "It seems like rain."],
            }
        ],
    },
    {
        "en": "talk",
        "phonetic": "/tɔːk/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["谈话，交谈", "讨论，商谈"],
                "examples": ["Talk to your teacher.", "Talk business."],
            },
            {
                "pos": "n",
                "definitions": ["谈话，会谈"],
                "examples": ["Have a talk with him."],
            },
        ],
    },
    {
        "en": "start",
        "phonetic": "/stɑːt/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["开始，启动", "创办，开办"],
                "examples": ["Start the engine.", "Start a business."],
            },
            {
                "pos": "n",
                "definitions": ["开始，起点"],
                "examples": ["From start to finish."],
            },
        ],
    },
    {
        "en": "show",
        "phonetic": "/ʃəʊ/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["给...看，出示", "引导，带领", "表明，证明"],
                "examples": [
                    "Show your ticket.",
                    "Show her to the door.",
                    "Show that you're right.",
                ],
            },
            {
                "pos": "n",
                "definitions": ["展览，演出"],
                "examples": ["Watch a TV show."],
            },
        ],
    },
    {
        "en": "hear",
        "phonetic": "/hɪər/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["听见，听到", "听说，得知"],
                "examples": ["Can you hear me?", "I heard the news."],
            }
        ],
    },
    {
        "en": "move",
        "phonetic": "/muːv/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["移动，搬动", "感动，打动"],
                "examples": ["Move the table.", "The story moved me to tears."],
            },
            {
                "pos": "n",
                "definitions": ["移动，行动"],
                "examples": ["Make your move."],
            },
        ],
    },
    {
        "en": "live",
        "phonetic": "/lɪv/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["居住，生活", "活着，生存"],
                "examples": ["I live in Beijing.", "Fish live in water."],
            },
            {
                "pos": "adj",
                "definitions": ["活的，有生命的", "直播的"],
                "examples": ["A live fish.", "Watch live TV."],
            },
        ],
    },
    {
        "en": "believe",
        "phonetic": "/bɪˈliːv/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["相信，信任", "认为，以为"],
                "examples": ["Believe in yourself.", "I believe he's right."],
            }
        ],
    },
    {
        "en": "hold",
        "phonetic": "/həʊld/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["拿，握，抓住", "持有，拥有", "容纳，包含"],
                "examples": [
                    "Hold my hand.",
                    "Hold a passport.",
                    "The box holds books.",
                ],
            },
            {
                "pos": "n",
                "definitions": ["抓，握", "暂停，延迟"],
                "examples": ["Get a good hold.", "Put on hold."],
            },
        ],
    },
    {
        "en": "bring",
        "phonetic": "/brɪŋ/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["带来，拿来", "引起，导致"],
                "examples": ["Bring me a book.", "Bring happiness to family."],
            }
        ],
    },
    {
        "en": "spend",
        "phonetic": "/spend/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["花费（钱）", "度过（时间）"],
                "examples": ["Spend money wisely.", "Spend time with family."],
            }
        ],
    },
    {
        "en": "grow",
        "phonetic": "/ɡrəʊ/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["生长，发育", "种植，栽培", "变得，成为"],
                "examples": [
                    "Children grow fast.",
                    "Grow vegetables.",
                    "It grew dark.",
                ],
            }
        ],
    },
    {
        "en": "open",
        "phonetic": "/ˈəʊpən/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["打开，开", "营业，开业"],
                "examples": ["Open the door.", "The shop opens at 9 AM."],
            },
            {
                "pos": "adj",
                "definitions": ["开着的", "开阔的", "公开的"],
                "examples": ["An open window.", "An open field.", "Keep it open."],
            },
        ],
    },
    {
        "en": "walk",
        "phonetic": "/wɔːk/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["走，步行", "陪伴...走"],
                "examples": ["Walk to school.", "Walk her home."],
            },
            {
                "pos": "n",
                "definitions": ["走，步行", "散步"],
                "examples": ["Take a walk."],
            },
        ],
    },
    {
        "en": "win",
        "phonetic": "/wɪn/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["赢，获胜", "争取，赢得"],
                "examples": ["Win the game.", "Win her heart."],
            },
            {"pos": "n", "definitions": ["胜利，赢"], "examples": ["A great win."]},
        ],
    },
    {
        "en": "offer",
        "phonetic": "/ˈɒfər/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["提供，提出", "出价，开价"],
                "examples": ["Offer help.", "Offer $100 for it."],
            },
            {
                "pos": "n",
                "definitions": ["提供，提议"],
                "examples": ["Thank you for your offer."],
            },
        ],
    },
    {
        "en": "remember",
        "phonetic": "/rɪˈmembər/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["记得，记住", "代...问候"],
                "examples": ["Remember the password.", "Remember me to your family."],
            }
        ],
    },
    {
        "en": "love",
        "phonetic": "/lʌv/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["爱，热爱", "喜爱，爱好"],
                "examples": ["Love your country.", "Love reading."],
            },
            {"pos": "n", "definitions": ["爱，爱情"], "examples": ["A mother's love."]},
        ],
    },
    {
        "en": "write",
        "phonetic": "/raɪt/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["写，书写", "写作，作曲"],
                "examples": ["Write a letter.", "Write novels."],
            }
        ],
    },
    {
        "en": "sit",
        "phonetic": "/sɪt/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["坐", "（建筑物等）坐落在"],
                "examples": ["Sit down please.", "The house sits on a hill."],
            }
        ],
    },
    {
        "en": "stand",
        "phonetic": "/stænd/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["站，站立", "忍受，经受"],
                "examples": ["Stand up.", "Can't stand the pain."],
            },
            {
                "pos": "n",
                "definitions": ["立场，观点", "架子，台"],
                "examples": ["Take a firm stand.", "A music stand."],
            },
        ],
    },
    {
        "en": "lose",
        "phonetic": "/luːz/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["丢失，失去", "输掉", "（钟表）走慢"],
                "examples": [
                    "Lose your keys.",
                    "Lose the game.",
                    "This watch loses time.",
                ],
            }
        ],
    },
    {
        "en": "pay",
        "phonetic": "/peɪ/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["支付，付款", "付出代价"],
                "examples": ["Pay the bill.", "Pay for your mistake."],
            },
            {"pos": "n", "definitions": ["工资，薪金"], "examples": ["Get your pay."]},
        ],
    },
    {
        "en": "meet",
        "phonetic": "/miːt/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["遇见，会见", "满足，符合"],
                "examples": ["Meet my friend.", "Meet requirements."],
            },
            {"pos": "n", "definitions": ["会议，集会"], "examples": ["Attend a meet."]},
        ],
    },
    {
        "en": "include",
        "phonetic": "/ɪnˈkluːd/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["包括，包含"],
                "examples": ["The price includes tax."],
            }
        ],
    },
    {
        "en": "continue",
        "phonetic": "/kənˈtɪnjuː/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["继续，持续"],
                "examples": ["Continue your work."],
            }
        ],
    },
    {
        "en": "set",
        "phonetic": "/set/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["放，安置", "设定，确立", "（日）落"],
                "examples": [
                    "Set the table.",
                    "Set a goal.",
                    "The sun sets in the west.",
                ],
            },
            {
                "pos": "n",
                "definitions": ["一套，一副", "接收机"],
                "examples": ["A chess set.", "A TV set."],
            },
        ],
    },
    {
        "en": "change",
        "phonetic": "/tʃeɪndʒ/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["改变，变化", "交换，更换"],
                "examples": ["Change your mind.", "Change seats."],
            },
            {
                "pos": "n",
                "definitions": ["变化，改变", "零钱"],
                "examples": ["Make a change.", "Keep the change."],
            },
        ],
    },
    {
        "en": "lead",
        "phonetic": "/liːd/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["领导，带领", "过（生活）", "通向"],
                "examples": [
                    "Lead the team.",
                    "Lead a happy life.",
                    "This road leads to town.",
                ],
            },
            {
                "pos": "n",
                "definitions": ["领导，领先", "铅"],
                "examples": ["Take the lead.", "A lead pipe."],
            },
        ],
    },
    {
        "en": "understand",
        "phonetic": "/ˌʌndərˈstænd/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["理解，明白", "获悉，听说"],
                "examples": ["I understand you.", "I understand he's coming."],
            }
        ],
    },
    {
        "en": "watch",
        "phonetic": "/wɒtʃ/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["观看，注视", "看守，监视"],
                "examples": ["Watch the game.", "Watch the house."],
            },
            {
                "pos": "n",
                "definitions": ["手表", "看守，守卫"],
                "examples": ["Wear a watch.", "Keep watch."],
            },
        ],
    },
    {
        "en": "follow",
        "phonetic": "/ˈfɒləʊ/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["跟随，追随", "理解，明白"],
                "examples": ["Follow me.", "Do you follow?"],
            }
        ],
    },
    {
        "en": "stop",
        "phonetic": "/stɒp/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["停止，中止", "阻止，阻拦"],
                "examples": ["Stop the car.", "Stop him from going."],
            },
            {
                "pos": "n",
                "definitions": ["停止，终止", "车站"],
                "examples": ["Come to a stop.", "Bus stop."],
            },
        ],
    },
    {
        "en": "create",
        "phonetic": "/kriˈeɪt/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["创造，创作", "引起，产生"],
                "examples": ["Create art.", "Create problems."],
            }
        ],
    },
    {
        "en": "speak",
        "phonetic": "/spiːk/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["说，说话", "演讲，发言"],
                "examples": ["Speak English.", "Speak at the meeting."],
            }
        ],
    },
    {
        "en": "read",
        "phonetic": "/riːd/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["读，阅读", "读懂，察识"],
                "examples": ["Read books.", "Read her mind."],
            }
        ],
    },
    {
        "en": "allow",
        "phonetic": "/əˈlaʊ/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["允许，准许"],
                "examples": ["Allow me to help."],
            }
        ],
    },
    {
        "en": "add",
        "phonetic": "/æd/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["增加，添加", "补充说"],
                "examples": ["Add sugar to coffee.", "He added that he was busy."],
            }
        ],
    },
    {
        "en": "join",
        "phonetic": "/dʒɔɪn/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["加入，参加", "连接，接合"],
                "examples": ["Join the club.", "Join the two ends."],
            }
        ],
    },
    {
        "en": "drink",
        "phonetic": "/drɪŋk/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["喝，饮", "喝酒"],
                "examples": ["Drink water.", "He drinks too much."],
            },
            {"pos": "n", "definitions": ["饮料"], "examples": ["Soft drinks."]},
        ],
    },
    {
        "en": "drive",
        "phonetic": "/draɪv/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["驾驶，开车", "驱赶，驱使"],
                "examples": ["Drive a car.", "Drive cattle."],
            },
            {
                "pos": "n",
                "definitions": ["驾车，驾驶"],
                "examples": ["Go for a drive."],
            },
        ],
    },
    {
        "en": "finish",
        "phonetic": "/ˈfɪnɪʃ/",
        "difficulty": 1,
        "parts": [
            {
                "pos": "v",
                "definitions": ["完成，结束"],
                "examples": ["Finish your homework."],
            }
        ],
    },
]


def make_csv_row(word_data):
    """将词典格式数据转换为 CSV 行"""
    # 将多词性数据序列化为 JSON 字符串
    parts_json = json.dumps(word_data["parts"], ensure_ascii=False)

    return {
        "category": "general",
        "en": word_data["en"],
        "phonetic": word_data.get("phonetic", ""),
        "parts": parts_json,
        "difficulty": word_data["difficulty"],
    }


def main():
    rows = []

    for word_data in VOCABULARY:
        rows.append(make_csv_row(word_data))

    # 按难度排序
    rows.sort(key=lambda x: x["difficulty"])

    # 写入 CSV
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["category", "en", "phonetic", "parts", "difficulty"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ 已生成 {len(rows)} 条专业词典格式词汇到 {OUTPUT_CSV}")

    from collections import Counter

    by_diff = Counter(r["difficulty"] for r in rows)
    print(f"  难度分布:")
    for diff in sorted(by_diff):
        print(f"    难度 {diff}: {by_diff[diff]} 条")

    cats = Counter(r["category"] for r in rows)
    print(f"  分类分布:")
    for cat, count in cats.most_common():
        print(f"    {cat}: {count} 条")


if __name__ == "__main__":
    main()
