# -*- coding: utf-8 -*-
import sys
import re
import json
from datetime import datetime
import collections

class AISummaryHelper:
    """
    高度なAI要約ヘルパークラス
    オフラインで動作する高度な文章要約機能
    """
    
    def __init__(self):
        # 文章構造の重要度パラメータ
        self.structure_weights = {
            'title': 5.0,      # タイトル・見出し
            'first_sentence': 3.0,  # 最初の文
            'last_sentence': 2.5,   # 最後の文
            'question': 3.0,    # 疑問文
            'conclusion': 4.0,  # 結論を示す表現
            'emphasis': 2.5,    # 強調表現
            'data': 3.5,        # 数値・データ
            'action': 3.0,      # アクション動詞
        }
        
        # 高度なキーワード分類
        self.keyword_categories = {
            'business': ['売上', '利益', '損失', '契約', '取引', '会社', '企業', '事業', '営業', '販売', '顧客', '市場', '競合', '戦略', '計画', '予算', '投資', '資金'],
            'time': ['今日', '明日', '昨日', '今週', '来週', '今月', '来年', '締切', '期限', '予定', '開始', '終了', '完了', '遅延', '急ぎ', '至急'],
            'people': ['社長', '部長', '課長', '主任', '担当', '責任者', '管理者', 'リーダー', 'チーム', 'スタッフ', '従業員', '職員', '専門家', '顧客', '取引先'],
            'action': ['実施', '実行', '実現', '達成', '完成', '作成', '制作', '開発', '改善', '改良', '修正', '変更', '追加', '削除', '更新', '確認', '検討', '検証', '分析'],
            'status': ['成功', '失敗', '完了', '未完了', '進行中', '延期', '中止', '承認', '否決', '保留', '検討中', '確定', '決定', '変更'],
            'importance': ['重要', '必須', '必要', '不要', '緊急', '優先', '重大', '深刻', 'critical', 'important', 'urgent', '注意', '警告'],
            'emotion': ['満足', '不満', '安心', '心配', '期待', '不安', '喜び', '悲しみ', '驚き', '困惑', '興味', '関心']
        }
        
        # 文章パターンの分析
        self.sentence_patterns = {
            'conclusion': [r'したがって', r'そのため', r'結論として', r'まとめると', r'つまり', r'要するに', r'このように'],
            'cause_effect': [r'なぜなら', r'理由は', r'原因は', r'結果として', r'その結果', r'影響で'],
            'contrast': [r'しかし', r'ところが', r'一方', r'反対に', r'それに対して', r'逆に'],
            'addition': [r'また', r'さらに', r'加えて', r'その上', r'同時に'],
            'example': [r'例えば', r'具体的には', r'たとえば', r'実際に'],
            'emphasis': [r'特に', r'とりわけ', r'何より', r'最も', r'非常に', r'極めて']
        }
    
    def analyze_text_structure(self, text):
        """テキストの構造を分析"""
        sentences = re.split(r'[。！？\n]+', text.strip())
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 3]
        
        if not sentences:
            return {}
        
        structure_info = {
            'total_sentences': len(sentences),
            'avg_sentence_length': sum(len(s) for s in sentences) / len(sentences),
            'sentences': []
        }
        
        for i, sentence in enumerate(sentences):
            sentence_info = {
                'text': sentence,
                'position': i,
                'length': len(sentence),
                'is_first': i == 0,
                'is_last': i == len(sentences) - 1,
                'has_numbers': bool(re.search(r'\d+', sentence)),
                'is_question': sentence.endswith('？') or sentence.endswith('?'),
                'keywords': [],
                'patterns': [],
                'importance_score': 0
            }
            
            # キーワード分析
            for category, keywords in self.keyword_categories.items():
                found = [kw for kw in keywords if kw in sentence]
                if found:
                    sentence_info['keywords'].extend([(kw, category) for kw in found])
            
            # パターン分析
            for pattern_type, patterns in self.sentence_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, sentence):
                        sentence_info['patterns'].append(pattern_type)
            
            structure_info['sentences'].append(sentence_info)
        
        return structure_info
    
    def calculate_advanced_scores(self, structure_info):
        """高度なスコア計算"""
        for sentence_info in structure_info['sentences']:
            score = 0
            
            # 位置による重み
            if sentence_info['is_first']:
                score += self.structure_weights['first_sentence']
            if sentence_info['is_last']:
                score += self.structure_weights['last_sentence']
            
            # 疑問文の重み
            if sentence_info['is_question']:
                score += self.structure_weights['question']
            
            # キーワードによる重み
            keyword_score = 0
            for keyword, category in sentence_info['keywords']:
                if category == 'importance':
                    keyword_score += 3.0
                elif category == 'business':
                    keyword_score += 2.5
                elif category == 'action':
                    keyword_score += 2.0
                elif category in ['time', 'people']:
                    keyword_score += 1.5
                else:
                    keyword_score += 1.0
            
            score += min(keyword_score, 10.0)  # 最大10点まで
            
            # パターンによる重み
            for pattern in sentence_info['patterns']:
                if pattern == 'conclusion':
                    score += self.structure_weights['conclusion']
                elif pattern == 'emphasis':
                    score += self.structure_weights['emphasis']
                elif pattern in ['cause_effect', 'contrast']:
                    score += 2.0
                else:
                    score += 1.0
            
            # 数値データの重み
            if sentence_info['has_numbers']:
                score += self.structure_weights['data']
            
            # 文の長さによる調整（適度な長さが望ましい）
            length = sentence_info['length']
            if 20 <= length <= 80:
                score += 2.0
            elif 10 <= length <= 120:
                score += 1.0
            elif length < 10:
                score -= 1.0
            
            sentence_info['importance_score'] = score
        
        return structure_info
    
    def extractive_ai_summary(self, text, max_sentences=3, diversity_factor=0.3):
        """高度な抽出的要約"""
        structure_info = self.analyze_text_structure(text)
        if not structure_info['sentences']:
            return "要約できるテキストがありません。"
        
        structure_info = self.calculate_advanced_scores(structure_info)
        
        # スコア順にソート
        sentences_by_score = sorted(structure_info['sentences'], 
                                  key=lambda x: x['importance_score'], reverse=True)
        
        # 多様性を考慮した選択
        selected_sentences = []
        used_keywords = set()
        
        for sentence_info in sentences_by_score:
            if len(selected_sentences) >= max_sentences:
                break
            
            # 多様性チェック
            sentence_keywords = set(kw for kw, cat in sentence_info['keywords'])
            
            if not selected_sentences:  # 最初の文は必ず選択
                selected_sentences.append(sentence_info)
                used_keywords.update(sentence_keywords)
            else:
                # 既存の選択文との類似度をチェック
                overlap = len(sentence_keywords & used_keywords)
                diversity_score = 1 - (overlap / max(len(sentence_keywords), 1))
                
                if diversity_score >= diversity_factor:
                    selected_sentences.append(sentence_info)
                    used_keywords.update(sentence_keywords)
        
        # 元の順序で並び替え
        selected_sentences.sort(key=lambda x: x['position'])
        
        # 要約文を構築
        summary_parts = []
        for sentence_info in selected_sentences:
            summary_parts.append(sentence_info['text'])
        
        return '。'.join(summary_parts) + '。'
    
    def abstractive_ai_summary(self, text):
        """抽象的要約（テンプレートベース）"""
        structure_info = self.analyze_text_structure(text)
        if not structure_info['sentences']:
            return "要約できるテキストがありません。"
        
        # 要約テンプレートの生成
        key_info = {
            'main_topics': [],
            'actions': [],
            'people': [],
            'timeline': [],
            'numbers': [],
            'conclusions': []
        }
        
        for sentence_info in structure_info['sentences']:
            # 主要なトピック抽出
            if sentence_info['importance_score'] > 5.0:
                key_info['main_topics'].append(sentence_info['text'])
            
            # アクション抽出
            action_keywords = [kw for kw, cat in sentence_info['keywords'] if cat == 'action']
            if action_keywords and 'action' in sentence_info['patterns']:
                key_info['actions'].append(sentence_info['text'])
            
            # 人物抽出
            people_keywords = [kw for kw, cat in sentence_info['keywords'] if cat == 'people']
            if people_keywords:
                key_info['people'].extend(people_keywords)
            
            # タイムライン抽出
            time_keywords = [kw for kw, cat in sentence_info['keywords'] if cat == 'time']
            if time_keywords:
                key_info['timeline'].extend(time_keywords)
            
            # 数値抽出
            if sentence_info['has_numbers']:
                numbers = re.findall(r'\d+[%円年月日時分個台名様件]?', sentence_info['text'])
                key_info['numbers'].extend(numbers)
            
            # 結論抽出
            if 'conclusion' in sentence_info['patterns']:
                key_info['conclusions'].append(sentence_info['text'])
        
        # 要約文の生成
        summary_parts = []
        
        if key_info['main_topics']:
            summary_parts.append("【主要内容】" + key_info['main_topics'][0][:100] + "...")
        
        if key_info['actions']:
            summary_parts.append("【実施事項】" + "、".join(set([kw for kw, cat in 
                                [item for sublist in [[kw for kw, cat in s_info['keywords'] if cat == 'action'] 
                                 for s_info in structure_info['sentences']] for item in sublist]]))[:50])
        
        if key_info['people']:
            unique_people = list(set(key_info['people']))[:3]
            summary_parts.append("【関係者】" + "、".join(unique_people))
        
        if key_info['numbers']:
            unique_numbers = list(set(key_info['numbers']))[:3]
            summary_parts.append("【重要数値】" + "、".join(unique_numbers))
        
        if key_info['conclusions']:
            summary_parts.append("【結論】" + key_info['conclusions'][0][:80] + "...")
        
        return '\n'.join(summary_parts) if summary_parts else "構造化要約を生成できませんでした。"
    
    def ai_smart_summary(self, text, mode='hybrid'):
        """AI駆動スマート要約"""
        if not text or len(text.strip()) < 20:
            return "テキストが短すぎるため、AI要約は不要です。"
        
        structure_info = self.analyze_text_structure(text)
        text_complexity = self.analyze_complexity(structure_info)
        
        result_parts = []
        
        if mode in ['hybrid', 'extractive']:
            # 抽出的要約
            max_sentences = min(3, max(1, structure_info['total_sentences'] // 3))
            extractive = self.extractive_ai_summary(text, max_sentences, diversity_factor=0.4)
            result_parts.append(f"【AI抽出要約】\n{extractive}")
        
        if mode in ['hybrid', 'abstractive']:
            # 抽象的要約
            abstractive = self.abstractive_ai_summary(text)
            if abstractive != "構造化要約を生成できませんでした。":
                result_parts.append(f"【AI構造化要約】\n{abstractive}")
        
        # 複雑度分析
        complexity_info = f"【文章分析】複雑度: {text_complexity['level']}, 重要文: {text_complexity['key_sentences']}文, キーワード密度: {text_complexity['keyword_density']:.1%}"
        result_parts.append(complexity_info)
        
        return '\n\n'.join(result_parts)
    
    def analyze_complexity(self, structure_info):
        """テキストの複雑度分析"""
        if not structure_info['sentences']:
            return {'level': '低', 'key_sentences': 0, 'keyword_density': 0.0}
        
        total_sentences = structure_info['total_sentences']
        high_score_sentences = sum(1 for s in structure_info['sentences'] if s['importance_score'] > 5.0)
        total_keywords = sum(len(s['keywords']) for s in structure_info['sentences'])
        avg_length = structure_info['avg_sentence_length']
        
        # 複雑度の判定
        complexity_score = 0
        
        if total_sentences > 10:
            complexity_score += 2
        elif total_sentences > 5:
            complexity_score += 1
        
        if avg_length > 50:
            complexity_score += 2
        elif avg_length > 30:
            complexity_score += 1
        
        if total_keywords > total_sentences * 2:
            complexity_score += 1
        
        if high_score_sentences > total_sentences * 0.3:
            complexity_score += 1
        
        if complexity_score >= 5:
            level = '高'
        elif complexity_score >= 3:
            level = '中'
        else:
            level = '低'
        
        keyword_density = total_keywords / max(sum(len(s['text']) for s in structure_info['sentences']), 1)
        
        return {
            'level': level,
            'key_sentences': high_score_sentences,
            'keyword_density': keyword_density
        }

def format_ai_summary_result(summary_result, original_length):
    """AI要約結果をフォーマット"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    formatted = f"""
{'='*50}
🤖 AI文章要約結果 - {timestamp}
{'='*50}

📊 分析情報:
- 元テキスト長: {original_length}文字
- AI要約後: {len(summary_result)}文字
- 圧縮率: {100*(1-len(summary_result)/max(original_length, 1)):.1f}%
- 処理タイプ: 高度AI要約

🧠 AI要約内容:
{summary_result}

{'='*50}
"""
    
    return formatted

def quick_ai_summarize(text, mode='hybrid'):
    """クイックAI要約関数"""
    helper = AISummaryHelper()
    return helper.ai_smart_summary(text, mode)

# テスト用
if __name__ == "__main__":
    test_text = """
    当社の第3四半期の業績について報告いたします。
    売上高は前年同期比で18%増加し、過去最高を記録しました。
    特に新商品Aの売上が好調で、目標を大きく上回っています。
    一方で、原材料費の高騰により利益率は若干低下しました。
    今後の戦略として、コスト削減と新市場開拓に注力します。
    プロジェクトリーダーは田中部長が担当し、来月から開始予定です。
    詳細は来週の会議で議論することが決定されました。
    """
    
    helper = AISummaryHelper()
    
    print("=== AI要約テスト ===")
    print("元テキスト:")
    print(test_text)
    print("\nAI要約結果:")
    result = helper.ai_smart_summary(test_text)
    print(result)