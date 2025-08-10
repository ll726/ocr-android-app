# -*- coding: utf-8 -*-
import re
import sys
import collections
from datetime import datetime

class SummaryHelper:
    """
    OCR結果文章要約ヘルパークラス
    オフラインで動作する軽量な文章要約機能
    """
    
    def __init__(self):
        # 重要度の高い単語（日本語）
        self.important_keywords = {
            # ビジネス関連
            '売上', '利益', '損失', '契約', '合意', '決定', '承認', '重要', '必須', '緊急',
            '問題', '課題', '解決', '改善', '成果', '結果', '効果', '影響', '変更', '更新',
            # 時間関連
            '今日', '明日', '昨日', '今週', '来週', '先週', '今月', '来月', '今年', '来年',
            '締切', '期限', '予定', '開始', '終了', '完了', '進捗', '遅延',
            # 人物・組織
            '社長', '部長', '課長', '担当', '責任者', '顧客', '取引先', '会社', '部署',
            # アクション
            '確認', '検討', '実施', '実行', '作成', '修正', '削除', '追加', '送信', '連絡'
        }
        
        # 不要な文字パターン
        self.noise_patterns = [
            r'[■□▲△◆◇●○★☆]+',  # 記号
            r'[ー─━]+',  # 罫線
            r'\s{3,}',   # 連続する空白
            r'[\(\)\[\]（）【】『』「」]+$',  # 行末の括弧のみ
        ]
    
    def clean_text(self, text):
        """テキストのクリーニング"""
        if not text or text.strip() == "":
            return ""
        
        # 改行を統一
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # ノイズパターンを除去
        for pattern in self.noise_patterns:
            text = re.sub(pattern, '', text)
        
        # 連続する改行を整理
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 前後の空白を除去
        text = text.strip()
        
        return text
    
    def split_sentences(self, text):
        """文章を文に分割"""
        # 日本語の文末記号で分割
        sentences = re.split(r'[。！？\n]+', text)
        
        # 空の文を除去し、短すぎる文をフィルタ
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 3]
        
        return sentences
    
    def calculate_sentence_score(self, sentence):
        """文の重要度スコアを計算"""
        score = 0
        
        # 文の長さによるスコア（適度な長さが良い）
        length = len(sentence)
        if 10 <= length <= 100:
            score += 2
        elif 5 <= length <= 150:
            score += 1
        
        # 重要キーワードによるスコア
        for keyword in self.important_keywords:
            if keyword in sentence:
                score += 3
        
        # 数字を含む文（データ、日付等）
        if re.search(r'\d+', sentence):
            score += 1
        
        # 疑問符・感嘆符（重要な表現）
        if re.search(r'[！？]', sentence):
            score += 1
        
        # 「です・ます調」（丁寧語は重要）
        if re.search(r'(です|ます|でした|ました)。?$', sentence):
            score += 1
        
        return score
    
    def extractive_summary(self, text, max_sentences=3):
        """抽出的要約（重要な文を選択）"""
        cleaned_text = self.clean_text(text)
        if not cleaned_text:
            return "要約できるテキストがありません。"
        
        sentences = self.split_sentences(cleaned_text)
        if len(sentences) <= max_sentences:
            return cleaned_text
        
        # 各文のスコアを計算
        sentence_scores = []
        for sentence in sentences:
            score = self.calculate_sentence_score(sentence)
            sentence_scores.append((sentence, score))
        
        # スコア順にソート
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 上位の文を選択
        top_sentences = sentence_scores[:max_sentences]
        
        # 元の順序で並び替え
        selected_sentences = []
        for sentence in sentences:
            for selected, _ in top_sentences:
                if sentence == selected:
                    selected_sentences.append(sentence)
                    break
        
        return '。'.join(selected_sentences) + '。'
    
    def keyword_summary(self, text):
        """キーワード抽出による要約"""
        cleaned_text = self.clean_text(text)
        if not cleaned_text:
            return "キーワードを抽出できません。"
        
        # 文字頻度分析
        words = re.findall(r'[ぁ-んァ-ン一-龯a-zA-Z0-9]+', cleaned_text)
        word_freq = collections.Counter(words)
        
        # 重要キーワードの検出
        found_keywords = []
        for keyword in self.important_keywords:
            if keyword in cleaned_text:
                found_keywords.append(keyword)
        
        # 頻出語上位
        common_words = [word for word, freq in word_freq.most_common(10) if len(word) > 1]
        
        # 数字・日付の抽出
        numbers = re.findall(r'\d+[年月日時分秒%円個台名様件]?', cleaned_text)
        
        summary_parts = []
        
        if found_keywords:
            summary_parts.append(f"重要キーワード: {', '.join(found_keywords[:5])}")
        
        if common_words:
            summary_parts.append(f"頻出語: {', '.join(common_words[:5])}")
        
        if numbers:
            summary_parts.append(f"数値情報: {', '.join(numbers[:5])}")
        
        return '\n'.join(summary_parts) if summary_parts else "特徴的なキーワードが見つかりませんでした。"
    
    def smart_summary(self, text, summary_type='auto'):
        """スマート要約（複数手法の組み合わせ）"""
        cleaned_text = self.clean_text(text)
        if not cleaned_text:
            return "要約できるテキストがありません。"
        
        text_length = len(cleaned_text)
        sentence_count = len(self.split_sentences(cleaned_text))
        
        # テキストの特性に応じて要約方法を選択
        if summary_type == 'auto':
            if text_length < 50:
                return f"【短文のため要約不要】\n{cleaned_text}"
            elif sentence_count <= 2:
                return f"【元テキスト】\n{cleaned_text}"
            elif text_length < 200:
                summary_type = 'keyword'
            else:
                summary_type = 'extractive'
        
        result = []
        
        if summary_type == 'extractive':
            max_sent = min(3, max(1, sentence_count // 3))
            extractive = self.extractive_summary(text, max_sent)
            result.append(f"【要約】\n{extractive}")
        
        if summary_type == 'keyword':
            keyword = self.keyword_summary(text)
            result.append(f"【キーワード分析】\n{keyword}")
        
        if summary_type == 'both':
            max_sent = min(2, max(1, sentence_count // 4))
            extractive = self.extractive_summary(text, max_sent)
            keyword = self.keyword_summary(text)
            result.append(f"【要約】\n{extractive}")
            result.append(f"【キーワード】\n{keyword}")
        
        return '\n\n'.join(result)

def format_summary_result(summary_result, original_length):
    """要約結果をフォーマット"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    formatted = f"""
{'='*50}
📄 文章要約結果 - {timestamp}
{'='*50}

📊 テキスト情報:
- 元テキスト長: {original_length}文字
- 要約後: {len(summary_result)}文字
- 圧縮率: {100*(1-len(summary_result)/max(original_length, 1)):.1f}%

💡 要約内容:
{summary_result}

{'='*50}
"""
    
    return formatted

def quick_summarize(text, summary_type='auto'):
    """クイック要約関数"""
    helper = SummaryHelper()
    return helper.smart_summary(text, summary_type)

# テスト用
if __name__ == "__main__":
    # テスト実行
    test_text = """
    会社の売上が前年度比15%増加しました。
    特に新商品の販売が好調で、目標を上回る結果となっています。
    来月の会議で詳細な分析結果を報告予定です。
    担当者は山田部長となります。
    締切は3月31日です。
    """
    
    helper = SummaryHelper()
    
    print("=== 要約テスト ===")
    print("元テキスト:")
    print(test_text)
    print("\n要約結果:")
    result = helper.smart_summary(test_text)
    print(result)