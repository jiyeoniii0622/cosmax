import streamlit as st

st.set_page_config(
    page_title="What's in my kitchen?",
    page_icon="🍳",
    layout="wide",
)

# ---------------------------------------------------------------------------
# 이 앱은 app.py 하나로 관리한다. (index.html / recipes.js 를 별도 파일로 두지
# 않고, 아래 문자열 하나에 UI(HTML/CSS/JS)와 레시피 데이터를 모두 담았다.)
# 렌더링은 st.iframe 을 사용한다. (구버전 st.components.v1.html 은 2026-06-01
# 이후 제거되어 대체함.)
# ---------------------------------------------------------------------------

APP_HTML = r"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>What's in my kitchen?</title>
  <style>
    :root{
      --bg:#fff7f0; --card:#ffffff; --ink:#2b2b2b; --muted:#8a8a8a;
      --accent:#ff7a45; --accent-soft:#ffe6d8; --line:#f0e6de; --ok:#31a24c;
      --shadow:0 6px 20px rgba(0,0,0,.06);
    }
    *{box-sizing:border-box}
    body{
      margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",
        "Malgun Gothic","Apple SD Gothic Neo",Roboto,sans-serif;
      background:var(--bg); color:var(--ink); line-height:1.5;
    }
    .wrap{max-width:920px; margin:0 auto; padding:24px 18px 60px}
    header{text-align:center; margin-bottom:20px}
    header h1{font-size:28px; margin:0 0 6px}
    header p{margin:0; color:var(--muted); font-size:15px}

    .panel{
      background:var(--card); border:1px solid var(--line); border-radius:16px;
      padding:18px; box-shadow:var(--shadow); margin-bottom:20px;
    }
    .panel h2{font-size:16px; margin:0 0 12px; display:flex; align-items:center; gap:8px}
    .search{
      width:100%; padding:11px 14px; font-size:15px; border:1px solid var(--line);
      border-radius:10px; outline:none; margin-bottom:14px; background:#fffdfb;
    }
    .search:focus{border-color:var(--accent)}

    .chips{display:flex; flex-wrap:wrap; gap:8px}
    .chip{
      border:1px solid var(--line); background:#fffdfb; color:var(--ink);
      padding:7px 12px; border-radius:999px; font-size:14px; cursor:pointer;
      transition:all .12s ease; user-select:none;
    }
    .chip:hover{border-color:var(--accent)}
    .chip.on{background:var(--accent); border-color:var(--accent); color:#fff; font-weight:600}

    .selected-bar{display:flex; flex-wrap:wrap; gap:8px; align-items:center; min-height:20px}
    .selected-bar .empty{color:var(--muted); font-size:14px}
    .tag{
      background:var(--accent-soft); color:#c94f1d; padding:6px 10px; border-radius:999px;
      font-size:13px; font-weight:600; display:inline-flex; align-items:center; gap:6px; cursor:pointer;
    }
    .tag span.x{font-weight:700}
    .clear-btn{
      margin-left:auto; background:none; border:none; color:var(--muted);
      font-size:13px; cursor:pointer; text-decoration:underline;
    }

    .results-head{display:flex; align-items:baseline; justify-content:space-between; margin-bottom:12px}
    .results-head h2{margin:0}
    .count{color:var(--muted); font-size:14px}

    .grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:14px}
    .recipe{
      background:var(--card); border:1px solid var(--line); border-radius:14px;
      padding:16px; box-shadow:var(--shadow); cursor:pointer; transition:transform .12s ease;
      display:flex; flex-direction:column;
    }
    .recipe:hover{transform:translateY(-3px)}
    .recipe .top{display:flex; align-items:center; gap:10px; margin-bottom:8px}
    .recipe .emoji{font-size:30px}
    .recipe .name{font-size:17px; font-weight:700}
    .recipe .meta{color:var(--muted); font-size:13px; margin-bottom:10px}
    .recipe .match{
      font-size:13px; margin-bottom:10px; font-weight:600;
    }
    .recipe.full .match{color:var(--ok)}
    .recipe .bar{height:6px; background:var(--line); border-radius:999px; overflow:hidden; margin-bottom:10px}
    .recipe .bar > i{display:block; height:100%; background:var(--accent)}
    .recipe.full .bar > i{background:var(--ok)}
    .ing-list{display:flex; flex-wrap:wrap; gap:6px}
    .ing{font-size:12px; padding:3px 8px; border-radius:6px; background:#f4f4f4; color:#666}
    .ing.have{background:var(--accent-soft); color:#c94f1d}
    .empty-state{text-align:center; color:var(--muted); padding:40px 10px}

    /* modal */
    .overlay{
      position:fixed; inset:0; background:rgba(0,0,0,.45); display:none;
      align-items:center; justify-content:center; padding:20px; z-index:10;
    }
    .overlay.on{display:flex}
    .modal{
      background:#fff; border-radius:18px; max-width:460px; width:100%;
      max-height:88vh; overflow:auto; padding:24px;
    }
    .modal .m-top{display:flex; align-items:center; gap:12px; margin-bottom:6px}
    .modal .m-emoji{font-size:38px}
    .modal h3{margin:0; font-size:22px}
    .modal .m-meta{color:var(--muted); font-size:14px; margin-bottom:16px}
    .modal h4{margin:18px 0 8px; font-size:14px; color:var(--accent)}
    .modal ol{margin:0; padding-left:20px}
    .modal ol li{margin-bottom:10px}
    .modal .close{
      margin-top:20px; width:100%; padding:12px; border:none; border-radius:10px;
      background:var(--accent); color:#fff; font-size:15px; font-weight:600; cursor:pointer;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>🍳 냉장고에 뭐 있지?</h1>
      <p>가지고 있는 재료를 골라보세요. 만들 수 있는 요리를 추천해 드려요!</p>
    </header>

    <div class="panel">
      <h2>🧺 재료 고르기</h2>
      <input id="ingSearch" class="search" type="text" placeholder="재료 검색 (예: 계란, 김치)…" />
      <div id="chips" class="chips"></div>
    </div>

    <div class="panel">
      <h2>✅ 선택한 재료</h2>
      <div class="selected-bar">
        <div id="selected" style="display:flex;flex-wrap:wrap;gap:8px"></div>
        <button id="clearBtn" class="clear-btn" style="display:none">모두 지우기</button>
      </div>
    </div>

    <div class="results-head">
      <h2>🍽️ 추천 요리</h2>
      <span id="count" class="count"></span>
    </div>
    <div id="results" class="grid"></div>
    <div id="emptyState" class="empty-state" style="display:none"></div>
  </div>

  <div id="overlay" class="overlay">
    <div class="modal" id="modal"></div>
  </div>

  <script>
  /* ===== 레시피 데이터베이스 ===== */
  window.RECIPES = [
    { name:'계란볶음밥', emoji:'🍳', time:'15분', diff:'쉬움', ing:['밥','계란','파','당근','간장'],
      steps:['팬에 기름을 두르고 잘게 썬 파와 당근을 볶아 향을 내요.','계란을 풀어 넣고 스크램블처럼 반쯤 익혀요.','밥을 넣고 재료와 고루 섞으며 볶아요.','간장 1큰술로 간을 하고 센 불에 30초 더 볶으면 완성!'] },
    { name:'토마토 계란볶음', emoji:'🍅', time:'10분', diff:'쉬움', ing:['토마토','계란','파','소금'],
      steps:['토마토는 큼직하게 썰고, 계란은 소금 약간 넣어 풀어요.','팬에 계란을 먼저 반쯤 익혀 따로 꺼내둬요.','같은 팬에 토마토를 볶아 즙이 배어나오게 해요.','계란을 다시 넣어 살짝 섞고 파를 올리면 완성!'] },
    { name:'감자채볶음', emoji:'🥔', time:'15분', diff:'쉬움', ing:['감자','양파','소금'],
      steps:['감자를 얇게 채 썰어 찬물에 5분 담가 전분을 빼요.','물기를 빼고 기름 두른 팬에 양파와 함께 볶아요.','감자가 투명해질 때까지 볶다가 소금으로 간해요.','아삭함이 남았을 때 불을 끄면 완성!'] },
    { name:'감자 수프', emoji:'🍲', time:'30분', diff:'보통', ing:['감자','양파','우유','버터'],
      steps:['감자와 양파를 깍둑 썰어 버터에 볶아요.','물을 자작하게 붓고 감자가 푹 익을 때까지 끓여요.','한 김 식힌 뒤 믹서에 곱게 갈아요.','다시 냄비에 붓고 우유를 넣어 데운 후 소금으로 간하면 완성!'] },
    { name:'토마토 파스타', emoji:'🍝', time:'25분', diff:'보통', ing:['토마토','마늘','양파','면','올리브유'],
      steps:['면을 소금 넣은 끓는 물에 8~9분 삶아요.','올리브유에 다진 마늘과 양파를 볶아 향을 내요.','토마토를 넣고 으깨가며 소스가 걸쭉해질 때까지 졸여요.','삶은 면을 넣어 버무리고 소금·후추로 간하면 완성!'] },
    { name:'치즈 오믈렛', emoji:'🍳', time:'10분', diff:'쉬움', ing:['계란','치즈','우유','버터'],
      steps:['계란에 우유 약간과 소금을 넣어 곱게 풀어요.','약불에 버터를 녹이고 계란물을 부어요.','가장자리가 익기 시작하면 치즈를 올려요.','반으로 접어 30초 더 익히면 완성!'] },
    { name:'야채 볶음', emoji:'🥘', time:'15분', diff:'쉬움', ing:['브로콜리','당근','양파','마늘'],
      steps:['브로콜리는 끓는 물에 30초 데쳐 건져요.','팬에 기름과 다진 마늘을 볶아 향을 내요.','당근·양파를 넣고 볶다가 브로콜리를 넣어요.','간장 1큰술로 간하고 센 불에 빠르게 볶으면 완성!'] },
    { name:'감자전', emoji:'🥔', time:'20분', diff:'보통', ing:['감자','양파','밀가루','소금'],
      steps:['감자를 강판에 갈고 양파는 곱게 다져요.','물기를 살짝 빼고 밀가루 2큰술과 소금을 넣어 반죽해요.','기름을 넉넉히 두른 팬에 반죽을 올려 얇게 펴요.','앞뒤로 노릇하게 부치면 완성!'] },
    { name:'팬케이크', emoji:'🥞', time:'20분', diff:'쉬움', ing:['밀가루','계란','우유','설탕'],
      steps:['밀가루·설탕·계란·우유를 덩어리 없이 섞어요.','약불 팬에 기름을 살짝 닦아내고 반죽을 동그랗게 부어요.','표면에 기포가 올라오면 뒤집어요.','노릇해지면 접시에 담고 시럽을 뿌리면 완성!'] },
    { name:'토마토 샐러드', emoji:'🥗', time:'10분', diff:'쉬움', ing:['토마토','양파','올리브유','소금'],
      steps:['토마토는 한입 크기로, 양파는 얇게 썰어요.','양파는 찬물에 5분 담가 매운맛을 빼요.','올리브유·소금·후추로 드레싱을 만들어요.','재료에 드레싱을 버무리면 상큼한 샐러드 완성!'] },
    { name:'치즈 토스트', emoji:'🧀', time:'10분', diff:'쉬움', ing:['빵','치즈','계란','버터'],
      steps:['팬에 버터를 녹여 빵을 노릇하게 구워요.','계란을 취향껏 프라이해요(반숙 추천!).','구운 빵에 치즈를 올리고 계란을 얹어요.','빵 한 장을 더 덮어 살짝 눌러 치즈를 녹이면 완성!'] },
    { name:'김치볶음밥', emoji:'🍚', time:'15분', diff:'쉬움', ing:['밥','김치','계란','대파','참기름'],
      steps:['팬에 김치를 볶아 신맛을 살짝 날려요.','밥을 넣어 김치와 고루 볶아요.','참기름을 둘러 향을 내고 접시에 담아요.','계란프라이를 얹으면 완성!'] },
    { name:'된장찌개', emoji:'🍲', time:'20분', diff:'쉬움', ing:['된장','두부','애호박','양파','대파'],
      steps:['물에 된장을 풀어 끓여요.','애호박과 양파를 넣고 끓여요.','두부와 대파를 넣어 5분 더 끓이면 완성!'] },
    { name:'계란말이', emoji:'🍳', time:'15분', diff:'보통', ing:['계란','당근','대파','소금'],
      steps:['계란을 풀고 다진 당근·대파와 소금을 섞어요.','약불 팬에 계란물을 얇게 부어요.','반쯤 익으면 한쪽으로 돌돌 말아요.','남은 계란물을 부어가며 여러 번 말면 도톰하게 완성!'] },
    { name:'어묵볶음', emoji:'🥘', time:'15분', diff:'쉬움', ing:['어묵','양파','간장','고춧가루','물엿'],
      steps:['어묵을 끓는 물에 살짝 데쳐 기름기를 빼요.','팬에 어묵과 양파를 볶아요.','간장·고춧가루·물엿 양념을 넣어요.','윤기 나게 조리면 완성!'] },
    { name:'콩나물국', emoji:'🍜', time:'15분', diff:'쉬움', ing:['콩나물','대파','마늘','소금'],
      steps:['콩나물을 물에 넣고 뚜껑을 덮어 끓여요.','다진 마늘을 넣어요.','소금으로 간하고 대파를 올리면 완성!'] },
    { name:'미역국', emoji:'🥣', time:'30분', diff:'보통', ing:['미역','소고기','국간장','참기름','마늘'],
      steps:['불린 미역과 소고기를 참기름에 볶아요.','물을 붓고 팔팔 끓여요.','국간장·마늘로 간해 20분 더 끓이면 완성!'] },
    { name:'참치김치찌개', emoji:'🥫', time:'20분', diff:'쉬움', ing:['김치','참치','양파','두부','대파'],
      steps:['김치를 볶다가 물을 부어 끓여요.','참치와 양파를 넣고 끓여요.','두부와 대파를 넣어 마무리하면 완성!'] },
    { name:'두부조림', emoji:'🍳', time:'20분', diff:'쉬움', ing:['두부','간장','고춧가루','대파','마늘'],
      steps:['두부를 도톰하게 썰어 노릇하게 구워요.','간장·고춧가루·마늘 양념을 부어요.','국물이 자작해질 때까지 조려요.','대파를 올리면 완성!'] },
    { name:'시금치나물', emoji:'🥗', time:'10분', diff:'쉬움', ing:['시금치','마늘','참기름','소금','깨'],
      steps:['시금치를 끓는 물에 살짝 데쳐요.','찬물에 헹궈 물기를 꼭 짜요.','마늘·참기름·소금·깨로 조물조물 무치면 완성!'] },
    { name:'애호박전', emoji:'🥔', time:'20분', diff:'보통', ing:['애호박','부침가루','계란','소금'],
      steps:['애호박을 동그랗게 썰어 소금을 살짝 뿌려요.','부침가루를 묻히고 계란물을 입혀요.','팬에 노릇하게 부치면 완성!'] },
    { name:'제육볶음', emoji:'🌶️', time:'25분', diff:'보통', ing:['돼지고기','고추장','고춧가루','양파','대파','마늘'],
      steps:['고추장·고춧가루·마늘로 양념장을 만들어요.','돼지고기를 양념에 버무려 재워요.','팬에 고기를 볶다 양파·대파를 넣어요.','고기가 익고 양념이 배면 완성!'] },
    { name:'불고기', emoji:'🥩', time:'30분', diff:'보통', ing:['소고기','간장','설탕','양파','당근','마늘'],
      steps:['간장·설탕·마늘로 양념을 만들어 고기를 재워요.','팬에 재운 고기를 볶아요.','양파·당근을 넣어 함께 볶으면 완성!'] },
    { name:'김치찌개', emoji:'🍲', time:'25분', diff:'쉬움', ing:['김치','돼지고기','두부','대파','고춧가루'],
      steps:['돼지고기와 김치를 볶아요.','물을 붓고 고춧가루를 넣어 끓여요.','두부·대파를 넣어 10분 더 끓이면 완성!'] },
    { name:'순두부찌개', emoji:'🍲', time:'20분', diff:'보통', ing:['순두부','계란','고춧가루','대파','마늘'],
      steps:['기름에 고춧가루·마늘을 볶아 고추기름을 내요.','물을 붓고 순두부를 넣어 끓여요.','계란과 대파를 넣어 마무리하면 완성!'] },
    { name:'잡채', emoji:'🍜', time:'40분', diff:'어려움', ing:['당면','시금치','당근','양파','간장','참기름'],
      steps:['당면을 삶아 간장·참기름으로 밑간해요.','시금치·당근·양파를 각각 볶아요.','모든 재료를 당면과 함께 버무리면 완성!'] },
    { name:'비빔밥', emoji:'🍚', time:'20분', diff:'쉬움', ing:['밥','나물','계란','고추장','참기름'],
      steps:['밥 위에 나물을 색색이 올려요.','계란프라이를 얹어요.','고추장·참기름을 넣고 쓱쓱 비비면 완성!'] },
    { name:'김밥', emoji:'🍙', time:'30분', diff:'보통', ing:['밥','김','단무지','당근','계란','시금치'],
      steps:['밥에 참기름·소금으로 간해요.','김 위에 밥을 펴고 속재료를 올려요.','돌돌 말아 한입 크기로 썰면 완성!'] },
    { name:'떡볶이', emoji:'🌶️', time:'20분', diff:'쉬움', ing:['떡','고추장','고춧가루','어묵','대파','설탕'],
      steps:['물에 고추장·고춧가루·설탕을 풀어 끓여요.','떡과 어묵을 넣어요.','국물이 걸쭉해질 때까지 졸이고 대파를 올리면 완성!'] },
    { name:'라볶이', emoji:'🍜', time:'20분', diff:'쉬움', ing:['라면','떡','고추장','어묵','대파'],
      steps:['물에 고추장 양념을 풀어 끓여요.','떡·어묵을 넣고 끓여요.','라면을 넣어 익히고 대파를 올리면 완성!'] },
    { name:'카레라이스', emoji:'🍛', time:'30분', diff:'쉬움', ing:['밥','카레가루','감자','당근','양파'],
      steps:['감자·당근·양파를 볶아요.','물을 붓고 채소가 익을 때까지 끓여요.','카레가루를 풀어 걸쭉하게 끓인 뒤 밥에 부으면 완성!'] },
    { name:'오므라이스', emoji:'🍳', time:'25분', diff:'보통', ing:['밥','계란','케첩','양파','당근'],
      steps:['양파·당근을 볶다 밥과 케첩을 넣어 볶아요.','볶음밥을 접시에 담아요.','부친 계란을 밥 위에 덮고 케첩을 뿌리면 완성!'] },
    { name:'볶음우동', emoji:'🍜', time:'15분', diff:'쉬움', ing:['우동면','양배추','당근','양파','간장'],
      steps:['양배추·당근·양파를 볶아요.','데친 우동면을 넣어요.','간장으로 간해 센 불에 볶으면 완성!'] },
    { name:'김치전', emoji:'🥘', time:'15분', diff:'쉬움', ing:['김치','부침가루','대파','물'],
      steps:['김치를 잘게 썰어 부침가루·물과 섞어요.','대파를 넣어 반죽해요.','팬에 얇게 펴 노릇하게 부치면 완성!'] },
    { name:'파전', emoji:'🥘', time:'20분', diff:'보통', ing:['쪽파','부침가루','계란','오징어','물'],
      steps:['부침가루를 물에 풀어 반죽을 만들어요.','팬에 쪽파를 깔고 반죽을 부어요.','오징어를 올리고 계란물을 둘러 앞뒤로 부치면 완성!'] },
    { name:'계란찜', emoji:'🍳', time:'15분', diff:'쉬움', ing:['계란','물','대파','소금'],
      steps:['계란을 풀어 물·소금과 섞어요.','뚝배기에 부어 저으며 약불로 끓여요.','부풀어 오르면 대파를 올려 완성!'] },
    { name:'소고기무국', emoji:'🥣', time:'30분', diff:'쉬움', ing:['소고기','무','대파','국간장','마늘'],
      steps:['소고기와 무를 참기름에 볶아요.','물을 붓고 끓여요.','국간장·마늘로 간하고 대파를 올리면 완성!'] },
    { name:'북엇국', emoji:'🥣', time:'25분', diff:'보통', ing:['북어','계란','두부','대파','참기름'],
      steps:['북어를 참기름에 볶아요.','물을 붓고 끓여요.','두부·계란·대파를 넣어 마무리하면 완성!'] },
    { name:'어묵탕', emoji:'🍢', time:'20분', diff:'쉬움', ing:['어묵','무','대파','국간장'],
      steps:['무를 넣고 물을 끓여 육수를 내요.','어묵을 꼬치에 끼워 넣어요.','국간장으로 간하고 대파를 올리면 완성!'] },
    { name:'감자조림', emoji:'🥔', time:'20분', diff:'쉬움', ing:['감자','간장','물엿','마늘'],
      steps:['감자를 깍둑 썰어 볶아요.','간장·물엿·마늘·물을 넣어요.','국물이 졸아들 때까지 조리면 완성!'] },
    { name:'멸치볶음', emoji:'🐟', time:'15분', diff:'쉬움', ing:['멸치','간장','물엿','견과류'],
      steps:['멸치를 마른 팬에 볶아 비린내를 날려요.','간장·물엿을 넣어 버무려요.','견과류를 넣고 살짝 더 볶으면 완성!'] },
    { name:'진미채볶음', emoji:'🦑', time:'15분', diff:'쉬움', ing:['진미채','고추장','물엿','마요네즈'],
      steps:['진미채를 부드럽게 손질해요.','고추장·물엿 양념에 버무려요.','마요네즈를 넣어 부드럽게 무치면 완성!'] },
    { name:'콩나물무침', emoji:'🥗', time:'10분', diff:'쉬움', ing:['콩나물','마늘','참기름','소금','고춧가루'],
      steps:['콩나물을 데쳐 찬물에 헹궈요.','물기를 빼요.','마늘·참기름·소금·고춧가루로 무치면 완성!'] },
    { name:'오이무침', emoji:'🥒', time:'10분', diff:'쉬움', ing:['오이','고춧가루','마늘','식초','설탕'],
      steps:['오이를 어슷하게 썰어요.','고춧가루·마늘·식초·설탕을 넣어요.','조물조물 무치면 완성!'] },
    { name:'무생채', emoji:'🥗', time:'15분', diff:'쉬움', ing:['무','고춧가루','마늘','식초','설탕'],
      steps:['무를 곱게 채 썰어요.','고춧가루로 색을 입혀요.','마늘·식초·설탕으로 새콤달콤하게 무치면 완성!'] },
    { name:'고등어구이', emoji:'🐟', time:'20분', diff:'쉬움', ing:['고등어','소금'],
      steps:['고등어에 소금을 뿌려 밑간해요.','물기를 닦고 팬이나 그릴에 올려요.','앞뒤로 노릇하게 구우면 완성!'] },
    { name:'삼겹살구이', emoji:'🥓', time:'15분', diff:'쉬움', ing:['삼겹살','마늘','쌈장','상추'],
      steps:['삼겹살을 팬에 노릇하게 구워요.','마늘을 함께 구워요.','상추에 고기·쌈장을 싸 먹으면 완성!'] },
    { name:'닭볶음탕', emoji:'🍗', time:'40분', diff:'보통', ing:['닭','감자','당근','고추장','양파'],
      steps:['닭을 데쳐 기름기를 빼요.','고추장 양념과 물을 넣고 끓여요.','감자·당근·양파를 넣어 자작하게 조리면 완성!'] },
    { name:'닭갈비', emoji:'🍗', time:'30분', diff:'보통', ing:['닭','양배추','고구마','고추장','떡'],
      steps:['닭을 고추장 양념에 재워요.','팬에 닭과 양배추·고구마를 볶아요.','떡을 넣어 익히면 완성!'] },
    { name:'육개장', emoji:'🍲', time:'50분', diff:'어려움', ing:['소고기','대파','고사리','숙주','고춧가루'],
      steps:['소고기를 삶아 결대로 찢어요.','고춧가루 고추기름에 고사리·숙주를 볶아요.','육수를 붓고 대파를 듬뿍 넣어 끓이면 완성!'] },
    { name:'콩국수', emoji:'🍜', time:'30분', diff:'보통', ing:['소면','콩','오이','소금'],
      steps:['불린 콩을 삶아 곱게 갈아 콩물을 만들어요.','소면을 삶아 찬물에 헹궈요.','면에 콩물을 붓고 오이·소금을 올리면 완성!'] },
    { name:'가든 샐러드', emoji:'🥗', time:'10분', diff:'쉬움', ing:['양상추','토마토','오이','올리브유','소금'],
      steps:['양상추를 한입 크기로 뜯어 찬물에 담갔다 빼요.','토마토·오이를 먹기 좋게 썰어요.','올리브유·소금(있으면 식초)으로 드레싱을 만들어요.','채소에 드레싱을 살살 버무리면 완성!'] },
    { name:'치즈 타코', emoji:'🌮', time:'20분', diff:'보통', ing:['토르티야','치즈','토마토','양파','다진 고기'],
      steps:['다진 고기와 양파를 볶아 소금·후추로 간해요.','토르티야를 팬에 살짝 데워요.','토르티야에 고기·토마토·치즈를 올려요.','반으로 접어 치즈가 녹을 때까지 살짝 구우면 완성!'] },
    { name:'홈메이드 피자', emoji:'🍕', time:'30분', diff:'보통', ing:['피자도우','토마토소스','치즈','양파','피망'],
      steps:['피자도우에 토마토소스를 고루 발라요.','치즈를 듬뿍 올려요.','양파·피망을 얇게 썰어 토핑해요.','200도 오븐(또는 팬 뚜껑)에서 치즈가 녹을 때까지 구우면 완성!'] }
  ];
  </script>

  <script>
    (function () {
      var RECIPES = (window.RECIPES || []);
      var selected = new Set();

      // 모든 재료를 빈도순으로 모으기
      var freq = {};
      RECIPES.forEach(function (r) {
        r.ing.forEach(function (i) { freq[i] = (freq[i] || 0) + 1; });
      });
      var allIngredients = Object.keys(freq).sort(function (a, b) {
        return freq[b] - freq[a] || a.localeCompare(b, 'ko');
      });

      var chipsEl = document.getElementById('chips');
      var searchEl = document.getElementById('ingSearch');
      var selectedEl = document.getElementById('selected');
      var clearBtn = document.getElementById('clearBtn');
      var resultsEl = document.getElementById('results');
      var countEl = document.getElementById('count');
      var emptyStateEl = document.getElementById('emptyState');
      var overlay = document.getElementById('overlay');
      var modal = document.getElementById('modal');

      function renderChips() {
        var q = searchEl.value.trim().toLowerCase();
        chipsEl.innerHTML = '';
        allIngredients
          .filter(function (i) { return !q || i.toLowerCase().indexOf(q) !== -1; })
          .forEach(function (ing) {
            var c = document.createElement('div');
            c.className = 'chip' + (selected.has(ing) ? ' on' : '');
            c.textContent = ing;
            c.onclick = function () { toggle(ing); };
            chipsEl.appendChild(c);
          });
      }

      function renderSelected() {
        selectedEl.innerHTML = '';
        if (selected.size === 0) {
          var e = document.createElement('div');
          e.className = 'empty';
          e.textContent = '아직 선택한 재료가 없어요.';
          selectedEl.appendChild(e);
          clearBtn.style.display = 'none';
          return;
        }
        clearBtn.style.display = 'inline';
        Array.from(selected).forEach(function (ing) {
          var t = document.createElement('span');
          t.className = 'tag';
          t.innerHTML = ing + ' <span class="x">×</span>';
          t.onclick = function () { toggle(ing); };
          selectedEl.appendChild(t);
        });
      }

      function toggle(ing) {
        if (selected.has(ing)) selected.delete(ing);
        else selected.add(ing);
        renderChips();
        renderSelected();
        renderResults();
      }

      function scored() {
        return RECIPES.map(function (r) {
          var have = r.ing.filter(function (i) { return selected.has(i); });
          return {
            recipe: r,
            have: have.length,
            total: r.ing.length,
            missing: r.ing.length - have.length,
            ratio: have.length / r.ing.length
          };
        });
      }

      function renderResults() {
        var list;
        if (selected.size === 0) {
          // 선택 전에는 전체 목록을 그냥 보여준다
          list = scored();
          countEl.textContent = '전체 ' + list.length + '개';
        } else {
          list = scored()
            .filter(function (s) { return s.have > 0; })
            .sort(function (a, b) {
              if (b.ratio !== a.ratio) return b.ratio - a.ratio;
              if (a.missing !== b.missing) return a.missing - b.missing;
              return b.have - a.have;
            });
          var makeable = list.filter(function (s) { return s.missing === 0; }).length;
          countEl.textContent = list.length + '개 추천' +
            (makeable ? ' · 바로 만들 수 있는 요리 ' + makeable + '개' : '');
        }

        resultsEl.innerHTML = '';
        if (list.length === 0) {
          emptyStateEl.style.display = 'block';
          emptyStateEl.textContent = '앗! 선택한 재료로 만들 수 있는 요리를 찾지 못했어요. 다른 재료를 골라보세요.';
          return;
        }
        emptyStateEl.style.display = 'none';

        list.forEach(function (s) {
          var r = s.recipe;
          var card = document.createElement('div');
          card.className = 'recipe' + (selected.size && s.missing === 0 ? ' full' : '');

          var ingHtml = r.ing.map(function (i) {
            return '<span class="ing' + (selected.has(i) ? ' have' : '') + '">' + i + '</span>';
          }).join('');

          var matchHtml = '';
          if (selected.size > 0) {
            var pct = Math.round(s.ratio * 100);
            matchHtml =
              '<div class="match">' +
                (s.missing === 0
                  ? '👍 바로 만들 수 있어요!'
                  : '재료 ' + s.have + '/' + s.total + ' · ' + s.missing + '개 부족') +
              '</div>' +
              '<div class="bar"><i style="width:' + pct + '%"></i></div>';
          }

          card.innerHTML =
            '<div class="top"><span class="emoji">' + r.emoji + '</span>' +
            '<span class="name">' + r.name + '</span></div>' +
            '<div class="meta">⏱ ' + r.time + ' · 난이도 ' + r.diff + '</div>' +
            matchHtml +
            '<div class="ing-list">' + ingHtml + '</div>';

          card.onclick = function () { openModal(r); };
          resultsEl.appendChild(card);
        });
      }

      function openModal(r) {
        var stepsHtml = r.steps.map(function (s) { return '<li>' + s + '</li>'; }).join('');
        var ingHtml = r.ing.map(function (i) {
          return '<span class="ing' + (selected.has(i) ? ' have' : '') + '">' + i + '</span>';
        }).join('');
        modal.innerHTML =
          '<div class="m-top"><span class="m-emoji">' + r.emoji + '</span>' +
          '<h3>' + r.name + '</h3></div>' +
          '<div class="m-meta">⏱ ' + r.time + ' · 난이도 ' + r.diff + '</div>' +
          '<h4>필요한 재료</h4>' +
          '<div class="ing-list">' + ingHtml + '</div>' +
          '<h4>만드는 법</h4>' +
          '<ol>' + stepsHtml + '</ol>' +
          '<button class="close" id="closeBtn">닫기</button>';
        overlay.classList.add('on');
        document.getElementById('closeBtn').onclick = closeModal;
      }

      function closeModal() { overlay.classList.remove('on'); }
      overlay.onclick = function (e) { if (e.target === overlay) closeModal(); };

      searchEl.addEventListener('input', renderChips);
      clearBtn.onclick = function () {
        selected.clear();
        renderChips(); renderSelected(); renderResults();
      };

      renderChips();
      renderSelected();
      renderResults();
    })();
  </script>
</body>
</html>
"""

# height는 필요에 맞게 조절 가능. 콘텐츠가 넘치면 iframe 내부에서 스크롤된다.
st.iframe(APP_HTML, height=1600)
