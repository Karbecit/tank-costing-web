export function renderDipTab(data) {
  if (!data?.rows?.length) {
    return `<section class="panel">
      <h2>Dip chart</h2>
      <p class="hint">Calculate the costing first, then click <strong>Generate dip chart</strong>.</p>
      <div class="field-grid">
        <label class="field"><span>Increment (mm)</span>
          <input id="dip-increment" type="number" min="1" max="100" value="10" /></label>
        <label class="field"><span>&nbsp;</span>
          <button type="button" id="btn-dip-gen" class="btn primary">Generate dip chart</button></label>
      </div>
    </section>`;
  }
  const rows = data.rows
    .map(
      (r) => `<tr>
        <td>${r.mm_from_top}</td>
        <td>${r.space_litres}</td>
        <td>${r.litres_in_tank}</td>
        <td>${r.section || ""}</td>
      </tr>`
    )
    .join("");
  return `<section class="panel">
    <h2>Dip chart (single tank)</h2>
    <p class="hint">Total volume: <strong>${data.total_volume_litres} L</strong> · Increment: ${data.increment_mm} mm</p>
    <div class="field-grid">
      <label class="field"><span>Increment (mm)</span>
        <input id="dip-increment" type="number" min="1" max="100" value="${data.increment_mm}" /></label>
      <label class="field"><span>&nbsp;</span>
        <button type="button" id="btn-dip-gen" class="btn secondary">Regenerate</button></label>
    </div>
    <div class="table-wrap" style="margin-top:1rem">
      <table class="data-table">
        <thead><tr><th>mm from top</th><th>Litres of space</th><th>Litres in tank</th><th>Section</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  </section>`;
}

export function bindDipTab(root, handlers) {
  root.querySelector("#btn-dip-gen")?.addEventListener("click", handlers.onGenerate);
}

export function readDipIncrement(root) {
  return parseInt(root.querySelector("#dip-increment")?.value || "10", 10);
}
