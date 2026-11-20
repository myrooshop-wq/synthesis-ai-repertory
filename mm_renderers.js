// mm_renderers.js - Enhanced with robust formatMMText, intelligent paragraph segmentation, Read More collapsible controls, and clean Allen parsing

function formatMMText(raw) {
  if (!raw) return '';
  // 1. First normalize HTML entities and non-ascii artifacts
  let s = raw
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&amp;/g, '&')
    .replace(/&#9472;/g, '—')
    .replace(/&ndash;/g, '–')
    .replace(/&mdash;/g, '—')
    .replace(/&nbsp;/g, ' ')
    .replace(/[\u008c\u0152]/g, 'Oe')
    .replace(/[\u009c\u0153]/g, 'oe')
    .replace(/[\u0092\u2019]/g, "'")
    .replace(/[\u0093\u0094\u201c\u201d]/g, '"')
    .replace(/[\u0096\u2013]/g, '–')
    .replace(/[\u0097\u2014]/g, '—')
    .replace(/æ/g, 'ae')
    .replace(/Æ/g, 'Ae');

  // 2. Escape HTML characters safely
  s = s
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');

  // 3. Highlight Aggravation '<' and Amelioration '>' with unique placeholders
  s = s.replace(/<\s*([a-zA-Z0-9])/g, function(match, nextChar) {
    return '___AGG_BADGE___ ' + nextChar;
  });

  s = s.replace(/>\s*([a-zA-Z0-9])/g, function(match, nextChar) {
    return '___AMEL_BADGE___ ' + nextChar;
  });

  // 4. Any remaining bare < or > safe escape
  s = s.replace(/</g, '&lt;').replace(/>/g, '&gt;');

  // 5. Expand placeholders into styled HTML badges
  s = s.replace(/___AGG_BADGE___/g, '<span class="mm-agg-badge"><i class="fa-solid fa-arrow-up-right-dots"></i> Agg. (&lt;)</span>');
  s = s.replace(/___AMEL_BADGE___/g, '<span class="mm-amel-badge"><i class="fa-solid fa-arrow-down-right-dots"></i> Amel. (&gt;)</span>');

  return s;
}

// Split continuous dense prose into readable paragraphs (~300-350 chars each)
function splitIntoParagraphs(text, targetLength = 320) {
  if (!text) return [];
  if (text.includes('\n\n')) {
    return text.split(/\n\s*\n/).map(p => p.trim()).filter(Boolean);
  }
  const sentences = text.split(/(?<=[.!?])\s+(?=[A-Z])/);
  const paras = [];
  let current = [];
  let currentLen = 0;

  for (let s of sentences) {
    let trimmed = s.trim();
    if (!trimmed) continue;
    current.push(trimmed);
    currentLen += trimmed.length;

    if (currentLen >= targetLength) {
      paras.push(current.join(' '));
      current = [];
      currentLen = 0;
    }
  }

  if (current.length > 0) {
    paras.push(current.join(' '));
  }
  return paras;
}

// Helper to render collapsible paragraphs with "Read More" button
function renderCollapsibleParas(paras, initialCount = 2) {
  if (!paras || paras.length === 0) return '';
  const initialParas = paras.slice(0, initialCount);
  const remainingParas = paras.slice(initialCount);

  let out = initialParas.map(p => `<p class="mm-prose-p">${formatMMText(p)}</p>`).join('');

  if (remainingParas.length > 0) {
    const uniqueId = 'kent_more_' + Math.random().toString(36).substring(2, 9);
    out += `
      <div id="${uniqueId}" class="mm-collapsible-content" style="display: none;">
        ${remainingParas.map(p => `<p class="mm-prose-p">${formatMMText(p)}</p>`).join('')}
      </div>
      <button type="button" class="mm-read-more-btn" onclick="toggleKentMore('${uniqueId}', this)">
        <i class="fa-solid fa-angles-down"></i> Read More (${remainingParas.length} more paragraph${remainingParas.length > 1 ? 's' : ''})
      </button>
    `;
  }
  return out;
}

window.toggleKentMore = function(elementId, btn) {
  const el = document.getElementById(elementId);
  if (!el) return;
  if (el.style.display === 'none' || !el.style.display) {
    el.style.display = 'block';
    btn.innerHTML = '<i class="fa-solid fa-angles-up"></i> Show Less';
    btn.classList.add('expanded');
  } else {
    el.style.display = 'none';
    const remaining = el.querySelectorAll('p').length;
    btn.innerHTML = `<i class="fa-solid fa-angles-down"></i> Read More (${remaining} more paragraph${remaining > 1 ? 's' : ''})`;
    btn.classList.remove('expanded');
  }
};

function renderAllenContent(container, entry) {
  let text = entry.full_text || '';
  // Clean leading '>' or bullets and entities
  text = text.replace(/^\s*>\s*/, '').replace(/&#9472;/g, '—');

  // Extract Modalities and Relationships (support Relation or Relations)
  let aggText = '';
  let amelText = '';
  let relText = '';

  const aggMatch = text.match(/Aggravation\s*\.\s*-(.*?)(?=Amelioration|\Z)/is);
  if (aggMatch) aggText = aggMatch[1].trim();

  const amelMatch = text.match(/Amelioration\s*\.\s*-(.*?)(?=Relations?|Keynotes|\Z)/is);
  if (amelMatch) amelText = amelMatch[1].trim();

  const relMatch = text.match(/Relations?\s*\.\s*-(.*?)(?=Aggravation|Amelioration|Keynotes|\Z)/is);
  if (relMatch) relText = relMatch[1].trim();

  // Strip extracted sections from main keynote body
  let mainText = text
    .replace(/Aggravation\s*\.\s*-.*?(?=Amelioration|\Z)/is, '')
    .replace(/Amelioration\s*\.\s*-.*?(?=Relations?|Keynotes|\Z)/is, '')
    .replace(/Relations?\s*\.\s*-.*?(?=Aggravation|Amelioration|Keynotes|\Z)/is, '')
    .replace(/Keynotes\s+by\s+H\.C\.\s+Allen/gi, '')
    .trim();

  // Extract common name if in first line (e.g. "White Oxide of Arsenic (As2O3.)")
  let commonName = '';
  const firstSentenceMatch = mainText.match(/^([A-Za-z\s]+?\.\s*)([A-Z][^;:\.\n]+?\((?:[A-Za-z0-9_\s\.\+]+)\)\.?)/);
  if (firstSentenceMatch) {
    commonName = firstSentenceMatch[2];
    mainText = mainText.replace(firstSentenceMatch[0], '').trim();
  }

  let html = `
    <div class="mm-source-banner mm-banner-allen">
      <div class="mm-banner-title"><i class="fa-solid fa-bolt"></i> Allen's Keynotes & Characteristics</div>
      <div class="mm-banner-subtitle">${escapeHtml(entry.remedy_name || '')} ${commonName ? '— <span style="font-weight: normal; opacity: 0.9;">' + escapeHtml(commonName) + '</span>' : ''}</div>
    </div>
  `;

  // Render Modalities Grid if available
  if (aggText || amelText) {
    html += `<div class="mm-modalities-grid">`;
    if (aggText) {
      html += `
        <div class="mm-modality-card mm-agg-card">
          <div class="mm-modality-header"><i class="fa-solid fa-triangle-exclamation"></i> Aggravation (&lt;)</div>
          <div class="mm-modality-body">${formatMMText(aggText)}</div>
        </div>
      `;
    }
    if (amelText) {
      html += `
        <div class="mm-modality-card mm-amel-card">
          <div class="mm-modality-header"><i class="fa-solid fa-circle-check"></i> Amelioration (&gt;)</div>
          <div class="mm-modality-body">${formatMMText(amelText)}</div>
        </div>
      `;
    }
    html += `</div>`;
  }

  // Render Relationship Card if available
  if (relText) {
    html += `
      <div class="mm-organ-card mm-card-relation">
        <div class="mm-organ-header mm-header-relation"><i class="fa-solid fa-link"></i> Relationships, Complementary & Ailments From</div>
        <div class="mm-organ-body">${formatMMText(relText)}</div>
      </div>
    `;
  }

  // Split Keynotes into readable distinct bullet items
  const keynotes = mainText.split(/(?<=[;\.\n])\s+(?=[A-Z][a-z]+|Mental|Physical|Pains|Disposition|Great|Burning|Weakness|Anxiety|Restless|Thirst)/);

  html += `
    <div class="mm-organ-card">
      <div class="mm-organ-header"><i class="fa-solid fa-key"></i> Characteristic Keynote Symptoms</div>
      <div class="mm-organ-body" style="padding: 10px 14px;">
  `;

  let renderedCount = 0;
  keynotes.forEach(kn => {
    let cleanKn = kn.trim();
    if (!cleanKn || cleanKn.length < 5) return;
    renderedCount++;

    // Highlight the leading symptom keyword (up to first colon, semicolon, or dash)
    let leadMatch = cleanKn.match(/^([A-Za-z\s,\(\)]+?)([:;—–\-]|\s+is:|\s+with\s+)(.*)$/s);
    let itemFormatted = '';
    if (leadMatch && leadMatch[1].length < 45) {
      itemFormatted = `<strong class="mm-keynote-lead">${escapeHtml(leadMatch[1].trim())}${escapeHtml(leadMatch[2])}</strong> ${formatMMText(leadMatch[3].trim())}`;
    } else {
      itemFormatted = formatMMText(cleanKn);
    }

    html += `
      <div class="mm-keynote-item">
        <span class="mm-keynote-dot"></span>
        <div class="mm-keynote-text">${itemFormatted}</div>
      </div>
    `;
  });

  if (renderedCount === 0) {
    html += `<div class="mm-full-text-prose">${formatMMText(mainText)}</div>`;
  }

  html += `
      </div>
    </div>
  `;

  container.innerHTML = html;
}

function renderNashContent(container, entry) {
  let text = entry.therapeutics_text || '';
  text = text.replace(/^\s*>\s*/, '').replace(/&#9472;/g, '—');

  // Split Nash by asterisks (* * * * *)
  const parts = text.split(/\s*\*\s*\*\s*\*\s*\*\s*\*\s*/);
  const leadersPart = parts[0] || '';
  const clinicalPart = parts.slice(1).join('\n\n');

  let html = `
    <div class="mm-source-banner mm-banner-nash">
      <div class="mm-banner-title"><i class="fa-solid fa-trophy"></i> E.B. Nash — Leaders in Homoeopathic Therapeutics</div>
      <div class="mm-banner-subtitle">${escapeHtml(entry.remedy_name || '')}</div>
    </div>
  `;

  // Part 1: Leading Trio / Keynotes
  if (leadersPart.trim()) {
    html += `
      <div class="mm-organ-card mm-card-nash-leaders">
        <div class="mm-organ-header mm-header-nash"><i class="fa-solid fa-star"></i> Leading Indications & Trios (Nash's Core Pearls)</div>
        <div class="mm-organ-body">
    `;

    const leaderLines = leadersPart.trim().split(/(?<=[;\.\n])\s+(?=[A-Z])/);
    leaderLines.forEach(line => {
      let cl = line.trim();
      if (!cl) return;
      html += `
        <div class="mm-nash-pearl">
          <i class="fa-solid fa-circle-check" style="color: #9333ea; font-size: 13px; margin-top: 3px; flex-shrink: 0;"></i>
          <div>${formatMMText(cl)}</div>
        </div>
      `;
    });

    html += `
        </div>
      </div>
    `;
  }

  // Part 2: Clinical Comparative Analysis
  if (clinicalPart.trim()) {
    html += `
      <div class="mm-organ-card">
        <div class="mm-organ-header"><i class="fa-solid fa-stethoscope"></i> Comparative Clinical Analysis & Bedside Notes</div>
        <div class="mm-organ-body">
    `;

    const paras = splitIntoParagraphs(clinicalPart.trim(), 300);
    html += renderCollapsibleParas(paras, 2);

    html += `
        </div>
      </div>
    `;
  }

  container.innerHTML = html;
}

function renderKentContent(container, entry) {
  let text = entry.lecture_text || '';
  // Strip standard Kent Dr Robert Séror boilerplate
  text = text.replace(/^.*?Presented by Dr Robert S[ée]ror\s*/is, '').trim();
  text = text.replace(/&#9472;/g, '—');

  // Strip repeating title if at beginning
  text = text.replace(/^[A-Za-z\s]+?Generalities\s*:\s*/i, 'Generalities: ');

  let html = `
    <div class="mm-source-banner mm-banner-kent">
      <div class="mm-banner-title"><i class="fa-solid fa-graduation-cap"></i> J.T. Kent — Lectures on Homoeopathic Materia Medica</div>
      <div class="mm-banner-subtitle">${escapeHtml(entry.remedy_name || '')}</div>
    </div>
  `;

  // Segment Kent lectures by classic anatomy / section headers
  const sectionKeywords = [
    'Generalities', 'Mind', 'Periodicity', 'Headaches', 'Head', 'Eyes', 'Ears', 
    'Nose', 'Face', 'Mouth', 'Throat', 'Stomach', 'Abdomen', 'Bowels', 'Stool', 
    'Rectum', 'Urinary', 'Genitals', 'Respiratory', 'Cough', 'Chest', 'Heart', 
    'Back', 'Limbs', 'Sleep', 'Fever', 'Skin', 'Modalities'
  ];

  const pattern = new RegExp('(?:\\b|\\n)(' + sectionKeywords.join('|') + ')\\s*:', 'gi');
  const matches = [];
  let m;
  while ((m = pattern.exec(text)) !== null) {
    matches.push({ title: m[1], index: m.index, matchLen: m[0].length });
  }

  if (matches.length > 0) {
    // If text exists before first match
    if (matches[0].index > 50) {
      const intro = text.substring(0, matches[0].index).trim();
      const introParas = splitIntoParagraphs(intro, 320);
      html += `
        <div class="mm-organ-card">
          <div class="mm-organ-header"><i class="fa-solid fa-book-open"></i> Introduction & General Action</div>
          <div class="mm-organ-body">
            ${renderCollapsibleParas(introParas, 2)}
          </div>
        </div>
      `;
    }

    for (let i = 0; i < matches.length; i++) {
      const cur = matches[i];
      const startPos = cur.index + cur.matchLen;
      const endPos = (i + 1 < matches.length) ? matches[i + 1].index : text.length;
      const body = text.substring(startPos, endPos).trim();
      if (!body) continue;

      let icon = 'fa-circle-dot';
      let titleLower = cur.title.toLowerCase();
      if (titleLower.includes('mind')) icon = 'fa-brain';
      else if (titleLower.includes('head')) icon = 'fa-head-side-virus';
      else if (titleLower.includes('eye')) icon = 'fa-eye';
      else if (titleLower.includes('stomach') || titleLower.includes('abdomen') || titleLower.includes('bowel')) icon = 'fa-utensils';
      else if (titleLower.includes('resp') || titleLower.includes('cough') || titleLower.includes('chest')) icon = 'fa-lungs';
      else if (titleLower.includes('heart')) icon = 'fa-heart-pulse';
      else if (titleLower.includes('fever') || titleLower.includes('mod')) icon = 'fa-temperature-high';

      const sectionParas = splitIntoParagraphs(body, 320);

      html += `
        <div class="mm-organ-card">
          <div class="mm-organ-header"><i class="fa-solid ${icon}"></i> ${escapeHtml(cur.title.toUpperCase())}</div>
          <div class="mm-organ-body">
            ${renderCollapsibleParas(sectionParas, 2)}
          </div>
        </div>
      `;
    }
  } else {
    // Fallback: Format paragraphs nicely with collapsible
    const paras = splitIntoParagraphs(text, 320);
    html += `
      <div class="mm-organ-card">
        <div class="mm-organ-header"><i class="fa-solid fa-book-open"></i> Complete Lecture Transcript</div>
        <div class="mm-organ-body">
          ${renderCollapsibleParas(paras, 3)}
        </div>
      </div>
    `;
  }

  container.innerHTML = html;
}

function renderClarkeContent(container, entry) {
  let text = entry.text || '';
  // Strip Clarke Médi-T boilerplate
  text = text.replace(/^.*?Presented by M[ée]di-T\s*®?\s*/is, '').trim();
  text = text.replace(/&#9472;/g, '—');

  let html = `
    <div class="mm-source-banner mm-banner-clarke">
      <div class="mm-banner-title"><i class="fa-solid fa-book-atlas"></i> J.H. Clarke — Dictionary of Practical Materia Medica</div>
      <div class="mm-banner-subtitle">${escapeHtml(entry.remedy_name || '')}</div>
    </div>
  `;

  // 1. Extract Clinical Diseases Section
  const clinMatch = text.match(/Clinical\s*\.\s*(?:—|─|-)\s*(.*?)(?=(?:Characteristics|Relations|Causation|\d+\.\s+[A-Z])|\Z)/is);
  if (clinMatch) {
    const rawDiseases = clinMatch[1].trim();
    const diseaseList = rawDiseases.split(/\s*\.\s*|\s*;\s*/).map(d => d.trim()).filter(d => d.length > 1 && d.length < 50);

    html += `
      <div class="mm-organ-card mm-card-clinical">
        <div class="mm-organ-header mm-header-clinical"><i class="fa-solid fa-notes-medical"></i> Clinical Indications & Disease Affinities (${diseaseList.length} Pathologies)</div>
        <div class="mm-organ-body">
          <div class="mm-disease-pills-container">
            ${diseaseList.map(d => `<span class="mm-disease-pill">${escapeHtml(d)}</span>`).join('')}
          </div>
        </div>
      </div>
    `;
  }

  // 2. Extract Characteristics
  const charMatch = text.match(/Characteristics\s*\.\s*(?:—|─|-)\s*(.*?)(?=(?:Relations|Causation|\d+\.\s+[A-Z])|\Z)/is);
  if (charMatch) {
    const charText = charMatch[1].trim();
    const charParas = splitIntoParagraphs(charText, 320);
    html += `
      <div class="mm-organ-card">
        <div class="mm-organ-header"><i class="fa-solid fa-fingerprint"></i> Characteristics & Guiding Symptoms</div>
        <div class="mm-organ-body">
          ${renderCollapsibleParas(charParas, 2)}
        </div>
      </div>
    `;
  }

  // 3. Extract Relations & Causation
  const relMatch = text.match(/Relations\s*\.\s*(?:—|─|-)\s*(.*?)(?=(?:Causation|\d+\.\s+[A-Z])|\Z)/is);
  const causMatch = text.match(/Causation\s*\.\s*(?:—|─|-)\s*(.*?)(?=\d+\.\s+[A-Z]|\Z)/is);

  if (relMatch || causMatch) {
    html += `
      <div class="mm-organ-card mm-card-relation">
        <div class="mm-organ-header mm-header-relation"><i class="fa-solid fa-code-branch"></i> Relationships & Causation</div>
        <div class="mm-organ-body">
          ${relMatch ? `<div style="margin-bottom: 8px;"><strong>Relations:</strong> ${formatMMText(relMatch[1].trim())}</div>` : ''}
          ${causMatch ? `<div><strong>Causation:</strong> ${formatMMText(causMatch[1].trim())}</div>` : ''}
        </div>
      </div>
    `;
  }

  // 4. Extract Schema Sections (1. Mind, 2. Head, etc.)
  const schemaRegex = /(\d+\.\s+[A-Za-z\s]+?)\.\s*(?:—|─|-)\s*(.*?)(?=(?:\d+\.\s+[A-Za-z\s]+?\.\s*(?:—|─|-))|\Z)/gis;
  let sMatch;
  let schemaCount = 0;
  while ((sMatch = schemaRegex.exec(text)) !== null) {
    schemaCount++;
    const organName = sMatch[1].trim();
    const organBody = sMatch[2].trim();
    if (!organBody) continue;

    const organParas = splitIntoParagraphs(organBody, 320);

    html += `
      <div class="mm-organ-card">
        <div class="mm-organ-header"><i class="fa-solid fa-circle-nodes"></i> ${escapeHtml(organName)}</div>
        <div class="mm-organ-body">
          ${renderCollapsibleParas(organParas, 2)}
        </div>
      </div>
    `;
  }

  // If no schema found, render remaining text
  if (schemaCount === 0 && !charMatch && !clinMatch) {
    const rawParas = splitIntoParagraphs(text, 320);
    html += `
      <div class="mm-organ-card">
        <div class="mm-organ-header"><i class="fa-solid fa-book"></i> Materia Medica Entry</div>
        <div class="mm-organ-body">
          ${renderCollapsibleParas(rawParas, 3)}
        </div>
      </div>
    `;
  }

  container.innerHTML = html;
}
