# 表演脚本参考（Fish Audio S2 / Drama 3）

目录
1. 语法
2. 情绪标签（49）
3. 语气标签（6）
4. 音效标签（11）
5. 特殊效果（5）
6. 强度调节
7. 常用组合
8. 摆放规则与禁忌
9. 四个场景模板
10. Drama 3 导演语法
11. 音素控制

---

## 1. 语法

情绪用方括号写在句首：`[happy] What a beautiful day!`

**方括号内可写自由自然语言**，不限于固定标签：

```text
What a [warm and happy] wonderful day!
```

---

## 2. 情绪标签（49）

### 基础（24）

| 标签 | 含义 | 典型场景 |
|---|---|---|
| `[happy]` | 愉快上扬 | 好消息、问候 |
| `[sad]` | 低沉 | 安慰、坏消息 |
| `[angry]` | 愤怒 | 投诉、警告 |
| `[excited]` | 兴奋 | 宣布、庆祝 |
| `[calm]` | 平静 | 说明、冥想 |
| `[nervous]` | 紧张不安 | 免责声明、道歉 |
| `[confident]` | 自信笃定 | 演讲、销售 |
| `[surprised]` | 惊讶 | 反应、发现 |
| `[satisfied]` | 满意 | 确认、评价 |
| `[delighted]` | 非常高兴 | 庆祝、赞美 |
| `[scared]` | 害怕 | 警告、恐怖故事 |
| `[worried]` | 担忧 | 疑虑、提问 |
| `[upset]` | 心烦 | 抱怨、出问题 |
| `[frustrated]` | 沮丧烦躁 | 技术故障、拖延 |
| `[depressed]` | 非常低落 | 严肃话题 |
| `[empathetic]` | 共情 | 客服安抚、咨询 |
| `[embarrassed]` | 尴尬 | 道歉、失误 |
| `[disgusted]` | 厌恶 | 差评 |
| `[moved]` | 被打动 | 感人时刻 |
| `[proud]` | 自豪 | 成就、表扬 |
| `[relaxed]` | 放松随意 | 闲聊 |
| `[grateful]` | 感激 | 道谢 |
| `[curious]` | 好奇 | 提问、探索 |
| `[sarcastic]` | 讽刺 | 幽默、吐槽 |

### 进阶（25）

`[disdainful]` 轻蔑 · `[unhappy]` 不悦 · `[anxious]` 焦虑 · `[hysterical]` 情绪失控 · `[indifferent]` 冷漠 · `[uncertain]` 不确定 · `[doubtful]` 怀疑 · `[confused]` 困惑 · `[disappointed]` 失望 · `[regretful]` 后悔 · `[guilty]` 愧疚 · `[ashamed]` 羞愧 · `[jealous]` 嫉妒 · `[envious]` 羡慕 · `[hopeful]` 抱有希望 · `[optimistic]` 乐观 · `[pessimistic]` 悲观 · `[nostalgic]` 怀旧 · `[lonely]` 孤独 · `[bored]` 无聊 · `[contemptuous]` 鄙视 · `[sympathetic]` 同情 · `[compassionate]` 关怀 · `[determined]` 坚定 · `[resigned]` 认命

---

## 3. 语气标签（6）

| 标签 | 效果 |
|---|---|
| `[in a hurry tone]` | 匆忙催促 |
| `[shouting]` | 大声喊 |
| `[screaming]` | 尖叫（紧急/恐惧） |
| `[whispering]` | 耳语 |
| `[soft tone]` | 轻柔（安慰、摇篮曲） |
| `[emphasis]` | 重读**紧随其后**的词 |

```text
This is [emphasis] really important.
```

---

## 4. 音效标签（11）

| 标签 | 建议同时写的文字 |
|---|---|
| `[laughing]` | Ha, ha, ha |
| `[chuckling]` | Heh, heh |
| `[sobbing]` | — |
| `[crying loudly]` | — |
| `[sighing]` | sigh |
| `[groaning]` | ugh |
| `[panting]` | huff, puff |
| `[gasping]` | gasp |
| `[yawning]` | yawn |
| `[snoring]` | zzz |
| `[clear throat]` | ahem |

**音效后补文字能显著提高命中率。** 也可以完全不用标签，直接写 `Ha, ha, ha`。

---

## 5. 特殊效果（5）

`[audience laughing]` 观众笑 · `[background laughter]` 背景笑 · `[crowd laughing]` 人群笑 · `[break]` 短停 · `[long-break]` 长停

---

## 6. 强度调节

用修饰词微调，不必换标签：

```text
[slightly sad] I'm a bit disappointed.
[very excited] This is absolutely amazing!
[extremely angry] This is unacceptable!
```

| 情绪 | 轻 | 中 | 强 |
|---|---|---|---|
| 高兴 | satisfied | happy | delighted |
| 难过 | disappointed | sad | depressed |
| 生气 | frustrated | angry | furious |
| 害怕 | nervous | scared | terrified |
| 兴奋 | interested | excited | ecstatic |

---

## 7. 常用组合

| 场景 | 组合 | 示例 |
|---|---|---|
| 说悄悄话 | `[mysterious][whispering]` | "I have something to tell you..." |
| 怒吼 | `[angry][shouting]` | "Stop right there!" |
| 叹气 | `[sad][sighing]` | "I wish things were different. Sigh." |
| 笑出声 | `[excited][laughing]` | "We did it! Ha ha!" |
| 迟疑发问 | `[nervous][uncertain]` | "Are you sure about this?" |

**每句最多 3 个**（官方建议）。情绪标记不计 token、不增加延迟。

---

## 8. 摆放规则与禁忌

**位置**
- 句子级情绪 → 放**句首**
- 语气控制 → 任意位置
- 音效 → 任意位置
- `[emphasis]` → **紧贴**目标词之前

**该做**
- 每句一个主情绪
- 音效后补文字
- 情绪变化拉开间隔
- 优先用自然表达（`Ha, ha, ha`）

**别做**
- 短文本堆标签
- 同一句混冲突情绪
- 方括号里写小作文（>40 字符就打断可读性）
- 忘写方括号
- 情绪离它控制的句子太远

**情绪递进（最像人的写法）**

```text
[happy] I got the promotion!
[uncertain] But... it means relocating.
[sad] I'll miss everyone here.
[hopeful] Though it's a great opportunity.
[determined] I'm going to make it work!
```

---

## 9. 四个场景模板

**客服**

```text
[friendly] Hello! How can I help you today?
[empathetic] I understand your frustration.
[confident] I'll resolve this for you right away.
[grateful] Thank you for your patience!
```

**叙事**

```text
[narrator] Once upon a time...
[mysterious][whispering] The old house stood silent.
[scared] "Is anyone there?" she called out.
[relieved][sighing] No one answered. Phew.
```

**教学**

```text
[enthusiastic] Welcome to today's lesson!
[curious] Have you ever wondered why?
[encouraging] That's a great question!
[proud] Excellent work!
```

**营销**

```text
[excited] Introducing our newest product!
[confident] You won't find better quality anywhere.
[urgent] Limited time offer!
[satisfied] Join thousands of happy customers!
```

---

## 10. Drama 3 导演语法

只改 `model` 头为 `drama-3`，其余请求不变。**头拼错会静默回落 `s2.1-pro`。**

### 自然语言导演

方括号里按"给配音演员交代戏"的写法来：情绪、意图、节奏、在对谁说话。

```text
[barely holding it together, forcing a smile] I'm fine. Really. Go on without me.
```

### 就地加声音与停顿

```text
I'm fine. [shaky breath] Really. [small laugh] Go on without me.
```

### 导演指令可以用中文

指令语言不必与脚本一致：

```text
[像是在强忍着眼泪，却努力笑着] I'm fine. Really. Go on without me.
```

### 行内切语言（实验性）

`<french>` `<spanish>` `<german>` `<japanese>` `<chinese>` `<korean>` `<italian>`

```text
She looked at the menu and said <french>Je voudrais une table pour deux.</french> The waiter smiled.
```

要点：用**双语流利**的音色；只包住切换的那几个词；准确率随语言和音色波动，不保证所有语言组合。

### 多说话人

`reference_id` 传数组 + 每段开头 `<|speaker:N|>`（N 从 0 开始）：

```text
<|speaker:0|>[calm, measured storyteller voice] The ship had been silent for three days.
<|speaker:1|>[low, gravelly, tired but in control] Status report.
<|speaker:2|>[fast, nervous, stumbling over words] Uh, sir, the reactor is not great.
<|speaker:1|>[slow, dangerously quiet] Define "not great."
<|speaker:2|>[voice breaking, close to panic] It is going to [emphasis] blow.
```

对应 `reference_id: ["id0", "id1", "id2"]`，本 skill 里就是 `--voice "旁白|船长|工程师"`。

---

## 11. 音素控制

把要锁定的读音包在 `<|phoneme_start|>` 与 `<|phoneme_end|>` 之间。

| 语言 | 音素体系 | 例子 |
|---|---|---|
| 英文 | CMU Arpabet | `I am an <\|phoneme_start\|>EH1 N JH AH0 N IH1 R<\|phoneme_end\|>.` |
| 中文 | 带声调数字拼音 | `我是一个<\|phoneme_start\|>gong1<\|phoneme_end\|><\|phoneme_start\|>cheng2<\|phoneme_end\|><\|phoneme_start\|>shi1<\|phoneme_end\|>。` |
| 日文 | OpenJTalk 罗马字 + 音调数字 | `<\|phoneme_start\|>ha0shi1ga0<\|phoneme_end\|>見えます。` |
| IPA（仅 drama-3） | 国际音标 | `kuːbərˈnɛtiːz` |

**英文**：元音上的数字是重音，`1` 主重音、`0` 非重读。
`EH1 N JH AH0 N IH1 R`（en-GI-neer）与 `EH0 N JH AH0 N IH1 R` 重音落点不同。

**中文**：声调 `1` 高平 / `2` 升 / `3` 降升 / `4` 降 / `5` 轻声。**一个汉字一个标签**，标点放标签外。

多音字必须手选：

| 词 | 拼音 |
|---|---|
| 重庆 | `chong2` `qing4` |
| 重要 | `zhong4` `yao4` |
| 银行 | `yin2` `hang2` |
| 行走 | `xing2` `zou3` |
| 音乐 | `yin1` `yue4` |
| 快乐 | `kuai4` `le4` |

可以只标歧义字：`请把这个字读作<|phoneme_start|>hang2<|phoneme_end|>。`

**音素标签不会被文本规范化破坏**，可以保留 `normalize` 默认开启。
批量场景（品牌名、缩写反复出现）改用**发音词典**，别逐条塞标签。
