import os
import re

# Read static/index.html as template baseline
with open('static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update font awesome CSS link to local css/all.min.css
html = html.replace('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css', 'css/all.min.css')

# 2. Add cordova.js in <head>
cordova_script = '<script src="cordova.js"></script>\n</head>'
html = html.replace('</head>', cordova_script)

# 3. Add Server Settings & Navigation in <header>
old_header_actions = '<div class="header-actions">'
new_header_actions = '''<div class="header-actions">
      <!-- Connectivity Status Button -->
      <button class="btn btn-outline" id="serverStatusBtn" onclick="openServerSettingsModal()" style="font-size: 12px; padding: 6px 12px; border-radius: 20px; border-color: #cbd5e1;">
        <span id="serverStatusDot" style="width: 8px; height: 8px; border-radius: 50%; background: #22c55e; display: inline-block; margin-right: 4px;"></span>
        <span id="serverStatusText">Online (AI Active)</span>
      </button>

      <!-- Classic Book View Link -->
      <a href="index.html?view=classic#home-list-1" class="btn btn-outline" style="border-color: #cbd5e1; font-size: 12px; padding: 6px 12px; text-decoration: none;">
        <i class="fa-solid fa-book-bookmark" style="color: #0369a1;"></i> Classic Book View
      </a>'''
html = html.replace(old_header_actions, new_header_actions)

# 4. Add Server Settings Modal HTML right before </body>
server_modal_html = '''
  <!-- Server / Connectivity Settings Modal -->
  <div id="serverSettingsModal" class="modal-overlay" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1100; align-items: center; justify-content: center;">
    <div style="background: white; border-radius: 12px; max-width: 500px; width: 90%; padding: 24px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.2);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px;">
        <h3 style="font-size: 16px; font-weight: 700; color: #0f172a;"><i class="fa-solid fa-network-wired" style="color: #2563eb; margin-right: 6px;"></i> Engine & Server Settings</h3>
        <button onclick="closeServerSettingsModal()" style="background: none; border: none; font-size: 18px; cursor: pointer; color: #64748b;">&times;</button>
      </div>
      <div style="font-size: 13px; color: #475569; margin-bottom: 16px; line-height: 1.5;">
        Configure whether the app connects to your local PC / Cloud server for Gemini AI symptom extraction, or runs offline using the mobile device's on-board Synthesis database.
      </div>
      <div style="margin-bottom: 14px;">
        <label style="display: block; font-size: 12px; font-weight: 700; margin-bottom: 6px; color: #334155;">Backend Server URL:</label>
        <input type="text" id="serverUrlInput" style="width: 100%; padding: 8px 12px; border-radius: 6px; border: 1px solid #cbd5e1; font-size: 13px; outline: none;" placeholder="http://192.168.7.178:5055">
        <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Default PC endpoint: <code>http://192.168.7.178:5055</code></div>
      </div>
      <div style="margin-bottom: 16px;">
        <label style="display: flex; align-items: center; gap: 8px; font-size: 13px; color: #1e293b; cursor: pointer;">
          <input type="checkbox" id="forceOfflineToggle">
          <span><strong>Force Offline Local Mode</strong> (Disables network; uses on-device SQLite)</span>
        </label>
      </div>
      <div id="serverTestStatus" style="font-size: 12px; margin-bottom: 14px; padding: 8px; border-radius: 6px; display: none;"></div>
      <div style="display: flex; justify-content: flex-end; gap: 10px;">
        <button class="btn btn-outline" onclick="testServerConnection()" style="font-size: 13px; padding: 8px 14px;"><i class="fa-solid fa-plug"></i> Test Connection</button>
        <button class="btn btn-primary" onclick="saveServerSettings()" style="font-size: 13px; padding: 8px 14px;"><i class="fa-solid fa-check"></i> Save & Apply</button>
      </div>
    </div>
  </div>
'''
html = html.replace('</body>', server_modal_html + '\n</body>')

# 5. Inject Dual-Engine API Client and Cordova Offline SQLite support in <script>
api_engine_js = '''
    // ==========================================
    // DUAL-ENGINE: ONLINE BACKEND & OFFLINE SQLITE
    // ==========================================
    let SERVER_BASE = localStorage.getItem('synthesis_server_url') || 'http://192.168.7.178:5055';
    let IS_FORCE_OFFLINE = localStorage.getItem('synthesis_force_offline') === 'true';
    let localDb = null;
    let isServerReachable = false;

    // Initialize Cordova on mobile
    document.addEventListener('deviceready', function() {
      console.log("[Synthesis Mobile] Cordova deviceready fired.");
      if (window.sqlitePlugin) {
        try {
          localDb = window.sqlitePlugin.openDatabase({ name: 'synthesis', location: 'default' });
          console.log("[Synthesis Mobile] Local SQLite database initialized.");
        } catch(e) {
          console.warn("[Synthesis Mobile] SQLite open error:", e);
        }
      }
      checkServerConnectivity();
    }, false);

    // Also check on standard page load (e.g. testing in browser)
    window.addEventListener('DOMContentLoaded', () => {
      const serverInput = document.getElementById('serverUrlInput');
      if (serverInput) serverInput.value = SERVER_BASE;
      const offlineToggle = document.getElementById('forceOfflineToggle');
      if (offlineToggle) offlineToggle.checked = IS_FORCE_OFFLINE;
      checkServerConnectivity();
    });

    async function checkServerConnectivity() {
      const dot = document.getElementById('serverStatusDot');
      const text = document.getElementById('serverStatusText');
      if (!dot || !text) return;
      if (IS_FORCE_OFFLINE) {
        dot.style.background = '#eab308';
        text.textContent = 'Offline (Local DB)';
        isServerReachable = false;
        return;
      }
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2000);
        const res = await fetch(`${SERVER_BASE}/api/autocomplete?q=mind&limit=1`, { signal: controller.signal });
        clearTimeout(timeoutId);
        if (res.ok) {
          dot.style.background = '#22c55e';
          text.textContent = 'Online (AI Active)';
          isServerReachable = true;
        } else {
          throw new Error("HTTP error " + res.status);
        }
      } catch(e) {
        dot.style.background = '#eab308';
        text.textContent = 'Offline (Local DB)';
        isServerReachable = false;
      }
    }

    function openServerSettingsModal() {
      document.getElementById('serverUrlInput').value = SERVER_BASE;
      document.getElementById('forceOfflineToggle').checked = IS_FORCE_OFFLINE;
      document.getElementById('serverTestStatus').style.display = 'none';
      document.getElementById('serverSettingsModal').style.display = 'flex';
    }

    function closeServerSettingsModal() {
      document.getElementById('serverSettingsModal').style.display = 'none';
    }

    async function testServerConnection() {
      const url = document.getElementById('serverUrlInput').value.trim().replace(/\\/$/, '');
      const statusDiv = document.getElementById('serverTestStatus');
      statusDiv.style.display = 'block';
      statusDiv.style.background = '#eff6ff';
      statusDiv.style.color = '#1e40af';
      statusDiv.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Testing connection to ' + url + '...';
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3500);
        const res = await fetch(`${url}/api/autocomplete?q=mind&limit=1`, { signal: controller.signal });
        clearTimeout(timeoutId);
        if (res.ok) {
          statusDiv.style.background = '#dcfce7';
          statusDiv.style.color = '#166534';
          statusDiv.innerHTML = '<i class="fa-solid fa-check-circle"></i> Connection successful! AI Engine & Gemini are reachable.';
        } else {
          throw new Error("Server responded with code " + res.status);
        }
      } catch(e) {
        statusDiv.style.background = '#fee2e2';
        statusDiv.style.color = '#991b1b';
        statusDiv.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Could not reach server. Verify PC is running Flask and phone is on same Wi-Fi.';
      }
    }

    function saveServerSettings() {
      const url = document.getElementById('serverUrlInput').value.trim().replace(/\\/$/, '');
      const forceOffline = document.getElementById('forceOfflineToggle').checked;
      SERVER_BASE = url || 'http://192.168.7.178:5055';
      IS_FORCE_OFFLINE = forceOffline;
      localStorage.setItem('synthesis_server_url', SERVER_BASE);
      localStorage.setItem('synthesis_force_offline', IS_FORCE_OFFLINE ? 'true' : 'false');
      closeServerSettingsModal();
      checkServerConnectivity();
    }

    // Unified API fetch helper with seamless offline fallback
    async function apiFetch(path, options = {}) {
      if (!IS_FORCE_OFFLINE) {
        try {
          const timeoutMs = path.includes('ai-extract-symptoms') ? 12000 : 3500;
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
          const fetchOptions = { ...options, signal: controller.signal };
          const res = await fetch(`${SERVER_BASE}${path}`, fetchOptions);
          clearTimeout(timeoutId);
          if (res.ok) {
            return await res.json();
          }
        } catch(e) {
          console.warn("[Synthesis Mobile] Remote fetch failed for " + path + ", falling back to local DB: ", e);
        }
      }
      return await localDbFallback(path, options);
    }

    // Local SQLite / Rule fallback for complete offline resilience
    async function localDbFallback(path, options = {}) {
      if (path.startsWith('/api/autocomplete')) {
        const urlParams = new URLSearchParams(path.split('?')[1]);
        const q = urlParams.get('q') || '';
        const limit = parseInt(urlParams.get('limit')) || 12;
        return await localAutocomplete(q, limit);
      } else if (path.startsWith('/api/rubric-children')) {
        const urlParams = new URLSearchParams(path.split('?')[1]);
        const parentId = parseInt(urlParams.get('parent_id'));
        return await localRubricChildren(parentId);
      } else if (path.startsWith('/api/rubric-book-view')) {
        const urlParams = new URLSearchParams(path.split('?')[1]);
        const symptomId = parseInt(urlParams.get('symptom_id'));
        return await localRubricBookView(symptomId);
      } else if (path.startsWith('/api/repertorise')) {
        const body = options.body ? JSON.parse(options.body) : {};
        return await localRepertorise(body.symptoms || [], body.weights || {}, body);
      } else if (path.startsWith('/api/ai-extract-symptoms')) {
        const body = options.body ? JSON.parse(options.body) : {};
        return localExtractSymptoms(body.transcript || '');
      }
      return null;
    }

    // Local SQLite Autocomplete
    function localAutocomplete(q, limit) {
      return new Promise((resolve) => {
        if (!localDb) {
          resolve([]);
          return;
        }
        let tokens = q.trim().toUpperCase().split(/\\s+/).filter(t => t.length > 0);
        let where = tokens.map(() => "(path LIKE ? OR search_path LIKE ?)").join(" AND ");
        let params = [];
        tokens.forEach(t => params.push(`%${t}%`, `%${t}%`));
        let sql = `SELECT id, path, remedies_count FROM syntree WHERE ${where} ORDER BY remedies_count DESC LIMIT ?`;
        params.push(limit);
        localDb.transaction((tx) => {
          tx.executeSql(sql, params, (tx, res) => {
            let out = [];
            for (let i = 0; i < res.rows.length; i++) {
              let r = res.rows.item(i);
              out.push({ id: r.id, path: r.path, remedies_count: r.remedies_count });
            }
            resolve(out);
          }, (err) => { resolve([]); });
        });
      });
    }

    // Local SQLite Rubric Children
    function localRubricChildren(parentId) {
      return new Promise((resolve) => {
        if (!localDb) { resolve([]); return; }
        localDb.transaction((tx) => {
          tx.executeSql("SELECT id, name, path, remedies_count FROM syntree WHERE id_father = ? ORDER BY name ASC", [parentId], (tx, res) => {
            let out = [];
            for (let i = 0; i < res.rows.length; i++) {
              out.push(res.rows.item(i));
            }
            resolve(out);
          }, (err) => { resolve([]); });
        });
      });
    }

    // Local SQLite Rubric Book View
    function localRubricBookView(symptomId) {
      return new Promise((resolve) => {
        if (!localDb) { resolve({}); return; }
        localDb.transaction((tx) => {
          tx.executeSql("SELECT id, name, path, id_father, remedies_count FROM syntree WHERE id = ?", [symptomId], (tx, rRubric) => {
            if (rRubric.rows.length === 0) { resolve({}); return; }
            let rubric = rRubric.rows.item(0);
            tx.executeSql(`
              SELECT sr.degree, r.abbreviation, r.fullname
              FROM symptom_remedies sr
              JOIN remedies r ON sr.remedy_id = r.id
              WHERE sr.symptom_id = ?
              ORDER BY sr.degree DESC, r.fullname ASC
            `, [symptomId], (tx, rRems) => {
              let remList = [];
              for (let i = 0; i < rRems.rows.length; i++) {
                let rem = rRems.rows.item(i);
                remList.push({
                  remedy: rem.fullname,
                  abbreviation: rem.abbreviation,
                  degree: rem.degree,
                  author_ids: []
                });
              }
              tx.executeSql("SELECT target_id, target_path FROM cross_references WHERE id = ?", [symptomId], (tx, rXref) => {
                let xrefs = [];
                for (let i = 0; i < rXref.rows.length; i++) {
                  xrefs.push(rXref.rows.item(i));
                }
                tx.executeSql("SELECT id, name, path, remedies_count FROM syntree WHERE id_father = ? ORDER BY name ASC", [symptomId], (tx, rSubs) => {
                  let subs = [];
                  for (let i = 0; i < rSubs.rows.length; i++) {
                    subs.push(rSubs.rows.item(i));
                  }
                  resolve({
                    id: rubric.id,
                    name: rubric.name,
                    path: rubric.path,
                    id_father: rubric.id_father,
                    ancestors: [],
                    remedies: remList,
                    remedies_count: remList.length,
                    cross_references: xrefs,
                    sub_rubrics: subs
                  });
                });
              });
            });
          });
        });
      });
    }

    // Local Zero-Hallucination Repertorisation Matrix
    function localRepertorise(symptomIds, weights, options) {
      return new Promise((resolve) => {
        if (!localDb || symptomIds.length === 0) {
          resolve({ matrix: {}, totals: {}, remedy_order: [] });
          return;
        }
        let placeholders = symptomIds.map(() => '?').join(',');
        let sql = `
          SELECT sr.symptom_id, sr.remedy_id, r.abbreviation, r.fullname, sr.degree
          FROM symptom_remedies sr
          JOIN remedies r ON sr.remedy_id = r.id
          WHERE sr.symptom_id IN (${placeholders})
        `;
        localDb.transaction((tx) => {
          tx.executeSql(sql, symptomIds, (tx, res) => {
            let scores = {};
            let matrix = {};
            for (let i = 0; i < res.rows.length; i++) {
              let row = res.rows.item(i);
              let sid = row.symptom_id;
              let rem = row.fullname;
              let deg = row.degree;
              let w = weights[sid] || 1;
              if (!matrix[sid]) matrix[sid] = {};
              matrix[sid][rem] = deg;
              if (!scores[rem]) {
                scores[rem] = { remedy: rem, abbreviation: row.abbreviation, total_score: 0, hits: 0 };
              }
              scores[rem].hits += 1;
              scores[rem].total_score += (deg * w);
            }
            let remedy_order = Object.values(scores)
              .sort((a, b) => b.total_score - a.total_score || b.hits - a.hits)
              .slice(0, 30)
              .map(s => s.remedy);
            let totals = {};
            remedy_order.forEach(r => {
              totals[r] = { score: scores[r].total_score, hits: scores[r].hits, abbreviation: scores[r].abbreviation };
            });
            resolve({ matrix, totals, remedy_order });
          }, (err) => { resolve({ matrix: {}, totals: {}, remedy_order: [] }); });
        });
      });
    }

    // Offline Clinical Symptom Matcher (Hindi + English)
    function localExtractSymptoms(text) {
      let t = text.toLowerCase();
      let extracted = {
        mind_and_emotion: [],
        generals_and_thermals: [],
        modalities: [],
        particulars: [],
        rubrics: [],
        model_used: "Offline Clinical Rule Engine"
      };
      if (t.includes('दर्द') || t.includes('मरोड़') || t.includes('cramp') || t.includes('griping')) {
        extracted.particulars.push({ symptom: "Abdominal cramps and griping pain (पेट में ऐंठन और मरोड़)", weight: 3 });
        extracted.rubrics.push({ rubric_name: "ABDOMEN - PAIN - cramping", relevance: 0.95 });
      }
      if (t.includes('दस्त') || t.includes('पतला मल') || t.includes('diarrhea') || t.includes('loose motion')) {
        extracted.particulars.push({ symptom: "Watery diarrhea, multiple times a day (बार-बार पतले दस्त)", weight: 3 });
        extracted.rubrics.push({ rubric_name: "RECTUM - DIARRHEA", relevance: 0.92 });
      }
      if (t.includes('उल्टी') || t.includes('जी मिचलाना') || t.includes('vomit') || t.includes('nausea')) {
        extracted.particulars.push({ symptom: "Nausea and vomiting (जी मिचलाना और उल्टी)", weight: 3 });
        extracted.rubrics.push({ rubric_name: "STOMACH - VOMITING - nausea - with", relevance: 0.90 });
      }
      if (t.includes('प्यास') || t.includes('मुंह सूख') || t.includes('thirst') || t.includes('dry mouth')) {
        extracted.generals_and_thermals.push({ symptom: "Extreme thirst and dry mouth (अधिक प्यास और मुंह सूखना)", weight: 3 });
        extracted.rubrics.push({ rubric_name: "STOMACH - THIRST", relevance: 0.88 });
      }
      if (t.includes('भूख') || t.includes('appetite') || t.includes('खाना खाने का मन नहीं')) {
        extracted.generals_and_thermals.push({ symptom: "Loss of appetite (भूख कम लगना)", weight: 2 });
        extracted.rubrics.push({ rubric_name: "STOMACH - APPETITE - wanting", relevance: 0.85 });
      }
      if (t.includes('कमजोरी') || t.includes('थकान') || t.includes('weakness') || t.includes('fatigue')) {
        extracted.generals_and_thermals.push({ symptom: "General weakness and fatigue (कमजोरी और थकान)", weight: 3 });
        extracted.rubrics.push({ rubric_name: "GENERALS - WEAKNESS", relevance: 0.92 });
      }
      if (t.includes('खाने के बाद') || t.includes('eating') || t.includes('after eating')) {
        extracted.modalities.push({ symptom: "Aggravation after eating (खाना खाने के बाद दर्द बढ़ना)", weight: 3 });
        extracted.rubrics.push({ rubric_name: "STOMACH - PAIN - eating - after - agg.", relevance: 0.94 });
      }
      if (t.includes('anxiety') || t.includes('घबराहट') || t.includes('fear') || t.includes('डर')) {
        extracted.mind_and_emotion.push({ symptom: "Anxiety and apprehension (घबराहट व बेचैनी)", weight: 2 });
        extracted.rubrics.push({ rubric_name: "MIND - ANXIETY", relevance: 0.89 });
      }
      return extracted;
    }
'''

# Safe replacements for fetch:
html = html.replace("fetch('/api/ai-extract-symptoms',", "apiFetch('/api/ai-extract-symptoms',")
html = html.replace("fetch(url);", "apiFetch(url);")
html = html.replace("fetch(`/api/rubric-children?parent_id=${parentId}`);", "apiFetch(`/api/rubric-children?parent_id=${parentId}`);")
html = html.replace("fetch(`/api/rubric-book-view?symptom_id=${symptomId}&remedy=${encodeURIComponent(highlightRemedy)}`);", "apiFetch(`/api/rubric-book-view?symptom_id=${symptomId}&remedy=${encodeURIComponent(highlightRemedy)}`);")
html = html.replace("fetch('/api/repertorise',", "apiFetch('/api/repertorise',")
html = html.replace("fetch('/api/chapters-directory');", "apiFetch('/api/chapters-directory');")
html = html.replace("fetch(`/api/remedy-citation?symptom_id=${symptomId}&remedy=${encodeURIComponent(remedy)}`);", "apiFetch(`/api/remedy-citation?symptom_id=${symptomId}&remedy=${encodeURIComponent(remedy)}`);")

# Inject api_engine_js at the start of <script>
script_pos = html.find('<script>') + len('<script>')
html = html[:script_pos] + '\n' + api_engine_js + '\n' + html[script_pos:]

# Save generated ai_repertory.html
with open('ai_repertory.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Generated ai_repertory.html, size:", len(html))
