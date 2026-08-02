import json

# Load previous (8/2) data.json for reuse of unchanged cards
with open('/tmp/dib-2026-08-03/data.json') as f:
    prev = json.load(f)

prev_sections = {s['id']: s for s in prev['sections']}

def find_card(section_id, card_id):
    for c in prev_sections[section_id]['cards']:
        if c['id'] == card_id:
            return dict(c)
    raise KeyError(card_id)

# ---------- WORK ----------
chem_ppwr = find_card('work', 'chem-ppwr-pfas-2026')
chem_ppwr.pop('featured', None)
chem_ppwr['levelText'] = '残り9日'

chem_kashinho = find_card('work', 'chem-kashinho-lcpfca-shikou')

chem_svhc = {
    "id": "chem-svhc-2026jun",
    "cat": "化学物質管理",
    "levelClass": "know",
    "levelText": "知っておく",
    "title": "REACH SVHC候補リストに3物質追加、情報伝達義務は掲載日から即時発生",
    "body": "ECHAは2026年6月3日、REACH候補リスト(SVHC)に3物質を追加した。0.1wt%超で成形品を供給する場合、第33条の情報伝達義務は掲載日から即時、第7条(2)のECHA届出義務は2026年12月3日までに発生する。",
    "detail": "EU向け成形品の含有物質情報は、候補リスト収載と同時に取引先への伝達義務が発生するため対応の遅れが許されない。ECHAは2026年6月3日、候補リストに3物質を追加したと発表した。用途はフッ素系樹脂硬化剤1件・ナノスケールのカップリング剤2件（研磨材・塗料・先端材料向け）と報じられている。0.1wt%超で成形品を供給する場合、REACH第33条の情報伝達義務は掲載日から即時に、第7条(2)のECHA届出義務は掲載から6か月以内(2026年12月3日)に発生する。※物質名・CAS/EC番号はECHA一次情報で未確認のため、まずは自社のEU向け成形品供給先に該当物質の使用有無を照会し、含有率0.1wt%超の有無を確認しておきたい。",
    "source": "ECHA",
    "url": "https://www.echa.europa.eu/-/echa-adds-three-hazardous-chemicals-to-the-candidate-list",
    "tags": ["REACH", "SVHC", "化学物質管理"],
    "due": {"date": "2026-12-03", "label": "ECHA届出期限(第7条2項)"}
}

work_hokkaido = find_card('work', 'work-hokkaido-shinkansen-quality-2026')
work_hokkaido['featured'] = True

work_cards = [chem_ppwr, chem_kashinho, chem_svhc, work_hokkaido]

# ---------- TOOLS-AI ----------
eu_ai_act = {
    "id": "eu-ai-act-transparency-effective",
    "cat": "AI規制動向",
    "levelClass": "now",
    "levelText": "施行開始",
    "title": "EU AI法、生成AI・チャットボットの透明性表示義務が8月2日に適用開始",
    "body": "EU AI法第50条に基づく透明性義務が2026年8月2日に適用開始となった。チャットボット等の対話型AIはAIとのやり取りである旨の明示、AI生成・改変コンテンツには機械可読なラベル付けが求められる。",
    "detail": "EU域内でAI生成物を扱う企業には、利用者の誤認防止を目的とした透明性確保が新たに求められる。EU AI法(規則(EU)2024/1689)第50条は、チャットボット等の対話型AIシステムについて利用者がAIとやり取りしていることを明示する義務、AIで生成・改変された画像・動画・音声・テキストへの機械可読マーキング義務を課しており、2026年8月2日に予定通り適用開始となった。高リスクAIシステムの適合性評価義務は2027年12月2日まで延期されたが、第50条の透明性義務はこの延期の対象外で予定通り施行されている。既存の生成AIシステムについては機械可読マーキング要件のみ2026年12月2日まで猶予される。EU向け製品・サービスでAI生成コンテンツ(広告・資料等)を使っている場合、海外展開部門は表示義務への対応状況を確認しておきたい。",
    "source": "AI Factory Austria(AI:AT)",
    "url": "https://ai-at.eu/en/news/article-50-of-the-eu-ai-act-transparency-obligations-become-applicable-on-2-august-2026/",
    "tags": ["EU AI法", "AI規制", "コンプライアンス"],
    "featured": True
}

kintone_update = {
    "id": "kintone-update-aug9-2026",
    "cat": "社内ITツール活用",
    "levelClass": "know",
    "levelText": "知っておく",
    "title": "kintone、8月9日にアップデート予定",
    "body": "サイボウズは2026年7月23日、kintoneの次回アップデートを8月9日に実施すると告知した。",
    "detail": "kintoneは主要アップデート情報を公式ヘルプページで随時公開しており、業務での利用部門は事前に変更内容を確認しておくと移行がスムーズになる。公式アップデート情報ページによれば、2026年7月23日付で8月9日のアップデート実施が告知されている(詳細な機能内容は公式ページで順次公開予定)。直近ではkintone AIとして検索AIチャットボット・レコード一覧分析AI・スレッド要約AI・アプリ作成AIなどが提供されている。自社でkintoneを利用している部門は、8月9日のアップデート内容を公式ヘルプで確認し、業務アプリへの影響有無を点検しておきたい。",
    "source": "サイボウズ(kintoneヘルプ)",
    "url": "https://jp.kintone.help/k/ja/update/main",
    "tags": ["kintone", "アップデート", "社内ITツール"]
}

powerplatform_update = {
    "id": "powerplatform-update-2026-07",
    "cat": "社内ITツール活用",
    "levelClass": "know",
    "levelText": "知っておく",
    "title": "Power Platform、7月アップデートで「Power Appを実行」アクション等が追加",
    "body": "Power Automateデスクトップフローから直接Power Appを起動できる「Power Appを実行」アクション(プレビュー)など、2026年7月のPower Platformアップデートがまとまった。",
    "detail": "業務自動化と業務アプリの連携が強化され、より柔軟な自動化フローが組みやすくなる方向の更新である。まとめ記事によれば、2026年7月のアップデートではPower Automateデスクトップフローから直接Power Appを開き、入力・出力の受け渡しやイベント駆動の自動化を行える「Power Appを実行」アクション(プレビュー)が追加された。あわせてDataverseとAIコーディングエージェント(Claude・Cursor・GitHub Copilot等)との連携強化、Power Pages向けの新しい認可の仕組み(パブリックプレビュー)、Advanced Connector Policiesの一般提供開始も行われている。社内でPower Automate・Power Appsを使った業務自動化を担当する部門は、新アクションの活用余地を確認しておきたい。",
    "source": "ギークフジワラ",
    "url": "https://www.geekfujiwara.com/tech/powerplatform/8437/",
    "tags": ["PowerPlatform", "PowerAutomate", "業務自動化"]
}

tools_carry_1 = find_card('tools-ai', 'tools-anthropic-cognizant-2026')
tools_carry_2 = find_card('tools-ai', 'tools-kddi-buffmee-2026')
tools_carry_3 = find_card('tools-ai', 'tools-copilotstudio-trigger-ga-2026')

tools_cards = [eu_ai_act, tools_carry_1, tools_carry_2, tools_carry_3, kintone_update, powerplatform_update]

# ---------- SUBSIDY (mostly unchanged; update shoryokuka card) ----------
subsidy_shoryokuka = find_card('subsidy', 'subsidy-shoryokuka-ippan-8th-2026')
subsidy_shoryokuka['body'] = "第7回公募(締切2026年7月31日17:00)は終了。第8回は2026年8月中旬(予定)開始〜10月中旬(予定)締切の見通しと報じられているが、正式日程は事務局サイトで未公表(2026年8月3日時点)。"
subsidy_shoryokuka['detail'] = "省力化投資補助金は公募回ごとに需要が高く、次回スケジュールの早期把握が現場の投資計画に直結する。第7回公募要領は6月5日に公開され、受付は7月上旬から開始、締切は7月31日17:00、採択発表は11月中旬の予定とされていた。第8回公募は2026年8月中旬(予定)開始〜10月中旬(予定)締切で実施される見通しと報じられているが、正式な受付期間・締切日は中小企業庁・事務局サイト(shoryokuka.smrj.go.jp)ともに2026年8月3日時点で未公表のままとなっている。まずは次回公募の即応に備え、GビズIDプライムの取得・更新状況を今のうちに確認しておきたい。",

subsidy_cards = [
    subsidy_shoryokuka,
    find_card('subsidy', 'subsidy-shinjigyo-monodukuri-1st-2026'),
    find_card('subsidy', 'subsidy-digital-ai-4th-2026'),
    find_card('subsidy', 'subsidy-sii-energy-3rd-2026'),
    find_card('subsidy', 'subsidy-jinzai-kaihatsu-2026'),
    find_card('subsidy', 'subsidy-chemical-regulation-2026'),
]

# ---------- EVENTS (unchanged) ----------
events_cards = [find_card('events', cid) for cid in [
    'events-chemican-seminar-2026',
    'events-kyotocci-eigyo-training-2026',
    'events-juse-kikakoukousa-2026',
    'events-material-week-tokyo-2026',
    'events-smartfactory-expo-autumn-2026',
    'events-manufacturingworld-osaka-2026',
]]

# ---------- SOCIETY ----------
society_fx = find_card('society', 'society-jpus-fx-intervention-0801-2026')

society_outlook = {
    "id": "society-nikkei-outlook-0803-2026",
    "cat": "株式・為替",
    "levelClass": "know",
    "levelText": "知っておく",
    "title": "日経平均、為替介入後は「底堅い」見通し—AI・半導体株の売りは一巡",
    "body": "日本経済新聞は2026年8月2日、8月3〜7日の週の日経平均株価についてAI・半導体関連株への売りが一巡し底堅い展開になるとの見通しを伝えた。円相場は政府・日銀の介入で円高方向に振れ、なお流動的な展開が続くとみられる。",
    "detail": "6月下旬以降、AI・半導体関連株を中心とした利益確定売りが続いていたが、直近ではその流れが一巡しつつあるとの見方が出ている。日本経済新聞によれば、8月3〜7日の週はキオクシア・アドバンテスト・東京エレクトロン・ソフトバンクグループなど指数インパクトの大きいAI・半導体株のリバウンド継続が焦点となる。為替は8月1日の政府・日銀の協調介入以降、円高・ドル安方向に振れており、介入効果の見極めや追加介入の思惑、日米両政府の是正方針表明が今週の焦点とされる。中東情勢の緊迫化で原油価格も下がりにくいとの見方が優勢という。資金調達や設備投資計画を持つ部門は、当面の株式・為替・原油価格のボラティリティを踏まえた計画の柔軟性確保が引き続き望ましい。",
    "source": "日本経済新聞",
    "url": "https://www.nikkei.com/article/DGXZQODL020KD0S6A800C2000000/",
    "tags": ["株式市場", "為替", "市場見通し"]
}

society_kumamoto = {
    "id": "society-pm-kumamoto-visit-0803-2026",
    "cat": "政治・災害対応",
    "levelClass": "know",
    "levelText": "知っておく",
    "title": "高市首相、8月3日に熊本地震の被災地を初視察",
    "body": "高市早苗首相は2026年8月3日、令和8年熊本地震の被災地を発災後初めて視察する。避難所訪問やヘリコプターでの被害状況確認、自治体関係者との意見交換を予定し、被災自治体には普通交付税616億円の繰り上げ交付も決定した。",
    "detail": "政府として災害復旧・復興への本気度を示す動きが今週相次いでいる。首相官邸は8月2日、高市首相が3日に熊本地震の被災地を視察すると発表した。避難所訪問に加えヘリコプターでの上空からの被害状況確認、自治体関係者との意見交換も調整されており、政府は「災害関連死」対策も急ぐ方針という。あわせて被災自治体への支援として、普通交付税616億円の繰り上げ交付も決定された。復旧・復興関連の公共工事・資材需要が今後具体化する可能性があり、九州エリアに取引先・拠点がある場合は自治体発注情報のアンテナを高めておきたい。",
    "source": "時事通信",
    "url": "https://www.jiji.com/jc/article?k=2026073100773&g=pol",
    "tags": ["政治", "災害対応", "熊本地震"]
}

society_cards = [society_fx, society_outlook, society_kumamoto]

# ---------- ASSEMBLE ----------
sections = [
    {"id": "work", "emoji": "🏭", "title": "仕事（専門）", "barColor": "#2f8f63",
     "tag": "不織布・品質・生産技術・化学物質", "desc": "不織布・品質管理/品質保証・生産技術・化学物質管理の最新動向",
     "cards": work_cards},
    {"id": "tools-ai", "emoji": "🧰", "title": "ITツール & AI", "barColor": "#3f8f86",
     "tag": "生成AI最新動向・Copilot・Kintone・SharePoint・Power Platform", "desc": "生成AIの最新動向と社内ITツールの活用Tips",
     "cards": tools_cards},
    {"id": "subsidy", "emoji": "💴", "title": "補助金・助成金", "barColor": "#a6772f",
     "tag": "ものづくり・省力化・省エネ・IT/DX・人材", "desc": "申請・締切が動く補助金・助成金の最新情報",
     "cards": subsidy_cards},
    {"id": "events", "emoji": "📅", "title": "展示会・セミナー", "barColor": "#b0518f",
     "tag": "不織布・素材・品質・DX・化学・営業", "desc": "出張・参加の検討に役立つ展示会・セミナー情報",
     "cards": events_cards},
    {"id": "society", "emoji": "🌐", "title": "社会情勢（一般ニュース）", "barColor": "#d98e3d",
     "tag": "政治・経済・世界", "desc": "直近の政治・経済・世界情勢のトピック",
     "cards": society_cards},
]

quickTips = [
    {"text": "EU包装規則(PPWR)の食品接触包装PFAS制限、8月12日適用開始まで残り9日。食品接触用途の品番洗い出しと全フッ素(TF)測定の見積を進めたい。", "target": "chem-ppwr-pfas-2026"},
    {"text": "EU AI法の透明性表示義務が8月2日に適用開始。EU向け資料・広告等でAI生成コンテンツを使っている場合は表示ルールを確認したい。", "target": "eu-ai-act-transparency-effective"},
    {"text": "デジタル化・AI導入補助金2026、1〜4次締切分は8月25日締切(あと22日)。検討中のデジタル化ツールがあれば今月中に事務局へ相談を。", "target": "subsidy-digital-ai-4th-2026"},
]

data = {
    "date": "2026年8月3日（月）",
    "updated": "⟳ 毎朝 7:00 自動更新",
    "quickTips": quickTips,
    "sections": sections,
}

with open('/tmp/dib-2026-08-03/data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("WROTE data.json")
