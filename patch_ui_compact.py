import os

def update_ui_compactness(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Make .dropdown-item display compact inline items without wide empty gaps
    old_css = """.autocomplete-dropdown { position: absolute; top: calc(100% + 4px); left: 0; right: 0; background: white; border-radius: 8px; border: 1px solid var(--border); max-height: 420px; overflow-y: auto; z-index: 50; box-shadow: 0 10px 25px -3px rgba(0,0,0,0.15); display: none; }
    .dropdown-item { padding: 8px 12px; border-bottom: 1px solid #f1f5f9; cursor: pointer; display: flex; align-items: center; justify-content: space-between; gap: 10px; font-size: 13px; transition: background 0.15s; }"""

    new_css = """.autocomplete-dropdown { position: absolute; top: calc(100% + 4px); left: 0; right: 0; max-width: 850px; background: white; border-radius: 8px; border: 1px solid var(--border); max-height: 420px; overflow-y: auto; z-index: 50; box-shadow: 0 10px 25px -3px rgba(0,0,0,0.15); display: none; }
    .dropdown-item { padding: 8px 12px; border-bottom: 1px solid #f1f5f9; cursor: pointer; display: flex; align-items: center; justify-content: flex-start; gap: 14px; font-size: 13px; transition: background 0.15s; }
    .dropdown-item-content { flex: 0 1 auto; max-width: 65%; min-width: 0; }
    .dropdown-item-actions { display: inline-flex; align-items: center; gap: 8px; flex-shrink: 0; margin-left: 6px; }"""

    if old_css in content:
        content = content.replace(old_css, new_css)
        print(f"Updated CSS in {filepath}")

    old_div_inner = """div.innerHTML = `
              <div style="flex: 1; min-width: 0; padding-right: 10px;">
                <div style="font-weight: 700; color: #1e293b; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                  ${item.path} ${xrefBadge} ${semanticBadge}
                </div>
                <div style="font-size: 11px; color: var(--text-muted); display: flex; align-items: center; gap: 6px; margin-top: 2px;">
                  <span>Level ${item.level}</span>
                  <span>&bull;</span>
                  <span>Synthesis Repertory</span>
                </div>
              </div>
              <div style="display: flex; gap: 8px; align-items: center; flex-shrink: 0;">
                <span class="rem-badge">${item.remedy_count} remedies</span>
                <button class="btn btn-outline" style="padding: 3px 8px; font-size: 11px; font-weight: 600;" onclick="event.stopPropagation(); expandSubRubrics(${item.id}, '${escapeQuotes(item.path)}')">
                  <i class="fa-solid fa-folder-tree"></i> Sub-rubrics &rarr;
                </button>
              </div>
            `;"""

    new_div_inner = """div.innerHTML = `
              <div class="dropdown-item-content">
                <div style="font-weight: 700; color: #1e293b; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                  ${item.path} ${xrefBadge} ${semanticBadge}
                </div>
                <div style="font-size: 11px; color: var(--text-muted); display: flex; align-items: center; gap: 6px; margin-top: 2px;">
                  <span>Level ${item.level}</span>
                  <span>&bull;</span>
                  <span>Synthesis</span>
                </div>
              </div>
              <div class="dropdown-item-actions">
                <span class="rem-badge">${item.remedy_count} remedies</span>
                <button class="btn btn-outline" style="padding: 3px 8px; font-size: 11px; font-weight: 600;" onclick="event.stopPropagation(); expandSubRubrics(${item.id}, '${escapeQuotes(item.path)}')">
                  <i class="fa-solid fa-folder-tree"></i> Sub-rubrics &rarr;
                </button>
              </div>
            `;"""

    if old_div_inner in content:
        content = content.replace(old_div_inner, new_div_inner)
        print(f"Updated dropdown template in {filepath}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

update_ui_compactness('static/index.html')
update_ui_compactness('ai_repertory.html')
print("Completed UI compactness enhancements.")
