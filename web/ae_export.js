/*
 * Adobe export: turns graphics drawn by the live engine into a description After Effects can rebuild
 * (web/ae_runtime.jsx), and packs it with the pictures into a .zip download.
 *
 * It reads the graphic as the engine actually drew it (positions, fitted font sizes, table rows, colours), so the
 * After Effects version lines up with what goes on air. Text that comes from data (names, numbers, stats) becomes an
 * editable field in the Essential Graphics panel; team colours, runners on base and outs become controls.
 */
(function (root) {
  var TEAMS = ['away', 'home', 'team', 'batting', 'fielding', 'scorer'];
  var TEAM_LABEL = { away: 'Away color', home: 'Home color', team: 'Team color', batting: 'Batting team color', fielding: 'Fielding team color',
                     scorer: 'Scoring team color' };

  // ---------------------------------------------------------------- colours
  function parseColor(s) {
    if (!s) return null;
    s = String(s).trim();
    if (s === 'transparent') return [0, 0, 0, 0];
    var m = s.match(/^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+%?))?\s*\)$/);
    if (m) return [+m[1] / 255, +m[2] / 255, +m[3] / 255, alpha(m[4])];
    m = s.match(/^color\(srgb\s+([\d.e-]+)\s+([\d.e-]+)\s+([\d.e-]+)(?:\s*\/\s*([\d.]+%?))?\s*\)$/);
    if (m) return [clamp(+m[1]), clamp(+m[2]), clamp(+m[3]), alpha(m[4])];
    m = s.match(/^#([0-9a-f]{3,8})$/i);
    if (m) {
      var h = m[1];
      if (h.length <= 4) h = h.split('').map(function (c) { return c + c; }).join('');
      return [parseInt(h.slice(0, 2), 16) / 255, parseInt(h.slice(2, 4), 16) / 255, parseInt(h.slice(4, 6), 16) / 255,
        h.length >= 8 ? parseInt(h.slice(6, 8), 16) / 255 : 1];
    }
    return null;
  }
  function alpha(a) {
    if (a == null || a === '') return 1;
    return String(a).slice(-1) === '%' ? parseFloat(a) / 100 : +a;
  }
  function clamp(v) { return Math.max(0, Math.min(1, v)); }
  function r3(v) { return Math.round(v * 1000) / 1000; }
  function col(c) { return [r3(c[0]), r3(c[1]), r3(c[2]), r3(c[3] == null ? 1 : c[3])]; }
  var COLOR_RE = /(rgba?\([^)]*\)|color\(srgb[^)]*\)|#[0-9a-fA-F]{3,8}\b|transparent)/g;

  function splitTop(s) {
    var out = [], depth = 0, cur = '';
    for (var i = 0; i < s.length; i++) {
      var ch = s[i];
      if (ch === '(') depth++;
      if (ch === ')') depth--;
      if (ch === ',' && depth === 0) { out.push(cur.trim()); cur = ''; } else cur += ch;
    }
    if (cur.trim()) out.push(cur.trim());
    return out;
  }

  // Background of a node as one flat colour or a two-colour ramp (After Effects' Gradient Ramp).
  function background(cs) {
    var img = cs.backgroundImage || 'none';
    if (img !== 'none' && img.indexOf('gradient') >= 0) {
      var layers = splitTop(img).filter(function (l) { return l.indexOf('gradient(') >= 0; });
      // The last layer is the base; layers above it are highlights or patterns.
      var base = layers[layers.length - 1];
      var cols = (base.match(COLOR_RE) || []).map(parseColor).filter(Boolean);
      if (cols.length) {
        var maxA = Math.max.apply(null, cols.map(function (c) { return c[3]; }));
        if (maxA <= 0.01) return null;
        var opaque = cols.filter(function (c) { return c[3] > 0.01; });
        if (/^repeating-/.test(base) || /conic-gradient/.test(base)) {
          // Stripes and patterns: their average colour.
          var avg = [0, 0, 0];
          opaque.forEach(function (c) { avg[0] += c[0]; avg[1] += c[1]; avg[2] += c[2]; });
          return { kind: 'flat', c0: col([avg[0] / opaque.length, avg[1] / opaque.length, avg[2] / opaque.length, 1]), alpha: maxA };
        }
        var c0 = opaque[0], c1 = opaque[opaque.length - 1];
        var radial = /radial-gradient/.test(base);
        var p0, p1;
        if (radial) {
          var at = base.match(/at\s+([\d.]+)%\s+([\d.]+)%/);
          p0 = at ? [+at[1] / 100, +at[2] / 100] : [0.5, 0.5];
          p1 = [p0[0] + 0.6, p0[1]];
        } else {
          var ang = 180, m = base.match(/^linear-gradient\(\s*(-?[\d.]+)deg/), t = base.match(/^linear-gradient\(\s*to ([a-z ]+),/);
          if (m) ang = +m[1];
          else if (t) ang = { top: 0, right: 90, bottom: 180, left: 270, 'top right': 45, 'right top': 45, 'bottom right': 135, 'right bottom': 135,
                              'bottom left': 225, 'left bottom': 225, 'top left': 315, 'left top': 315 }[t[1].trim()] || 180;
          var rad = ang * Math.PI / 180, dx = Math.sin(rad) / 2, dy = -Math.cos(rad) / 2;
          p0 = [0.5 - dx, 0.5 - dy]; p1 = [0.5 + dx, 0.5 + dy];
        }
        if (c0.join() === c1.join()) return { kind: 'flat', c0: col(c0), alpha: maxA };
        return { kind: 'ramp', c0: col(c0), c1: col(c1), p0: p0.map(r3), p1: p1.map(r3), radial: radial, alpha: maxA };
      }
    }
    var bc = parseColor(cs.backgroundColor);
    if (bc && bc[3] > 0.01) return { kind: 'flat', c0: col(bc), alpha: bc[3] };
    return null;
  }

  function shadowOf(s) {
    if (!s || s === 'none') return null;
    var first = splitTop(s)[0];
    var c = parseColor((first.match(COLOR_RE) || [])[0]);
    var nums = first.replace(COLOR_RE, '').trim().split(/\s+/).map(parseFloat).filter(function (n) { return !isNaN(n); });
    if (!c || nums.length < 2 || c[3] <= 0.01) return null;
    var x = nums[0], y = nums[1], blur = nums[2] || 0;
    var dir = (Math.atan2(x, -y) * 180 / Math.PI + 360) % 360;
    return { color: col(c), dir: Math.round(dir), dist: Math.round(Math.sqrt(x * x + y * y)), blur: Math.round(blur) };
  }

  // ---------------------------------------------------------------- fonts
  // Fonts are named by PostScript name in After Effects. The first one installed is used.
  function weightName(w) {
    w = +w || 400;
    if (w >= 900) return ['Black', 'Heavy', 'ExtraBold', 'Bold'];
    if (w >= 800) return ['ExtraBold', 'Heavy', 'Bold'];
    if (w >= 700) return ['Bold'];
    if (w >= 600) return ['SemiBold', 'Semibold', 'Bold'];
    if (w >= 500) return ['Medium', 'Regular'];
    return ['Regular'];
  }
  function fontList(family, weight, italic) {
    var fams = String(family || '').split(',').map(function (f) { return f.trim().replace(/^['"]|['"]$/g, ''); }).filter(Boolean);
    var out = [], w = +weight || 400, it = italic ? 'Italic' : '';
    function add(x) { if (out.indexOf(x) < 0) out.push(x); }
    fams.forEach(function (f) {
      var key = f.toLowerCase();
      if (key === 'inter var' || key === 'inter') weightName(w).forEach(function (n) { add('Inter-' + n + it); add('Inter' + (n === 'Regular' ? '' : '-' + n)); });
      else if (key.indexOf('bahnschrift') === 0) {
        add(w >= 700 ? 'Bahnschrift-BoldSemiCondensed' : 'Bahnschrift-SemiBoldSemiCondensed');
        add('Bahnschrift-SemiBoldSemiCondensed'); add('Bahnschrift-BoldCondensed'); add('Bahnschrift-Bold'); add('Bahnschrift');
      } else if (key === 'din condensed') add('DINCondensed-Bold');
      else if (key === 'roboto condensed') weightName(w).forEach(function (n) { add('RobotoCondensed-' + n + it); });
      else if (key === 'arial narrow') { add(w >= 600 ? 'ArialNarrow-Bold' + it : 'ArialNarrow' + (it ? '-Italic' : '')); add('ArialNarrow-Bold'); }
      else if (key === 'helvetica neue') add(w >= 600 ? 'HelveticaNeue-Bold' + it : 'HelveticaNeue');
      else if (key === 'sf pro display') weightName(w).forEach(function (n) { add('SFProDisplay-' + n + it); });
      else if (key === 'bbg fredoka' || key === 'fredoka') { add('Fredoka-Bold'); add('Fredoka-SemiBold'); add('FredokaOne-Regular'); }
      else if (key === 'bbg archivo' || key === 'archivo') { add(w >= 900 ? 'Archivo-BlackItalic' : 'Archivo-ExtraBoldItalic'); add('Archivo-BlackItalic'); }
      else if (key === 'bbg vt323' || key === 'vt323') add('VT323-Regular');
      // Theme-package faces (bundled in web/fonts; install them on the editing machine for After Effects to match)
      else if (key === 'bbg orbitron') add(w >= 900 ? 'Orbitron-Black' : 'Orbitron-Bold');
      else if (key === 'bbg mountains of christmas') add('MountainsofChristmas-Bold');
      else if (key.indexOf('bbg ') === 0) add(f.slice(4).replace(/\s+/g, '') + '-Regular');
      else if (key === 'arial black') add('Arial-Black');
      else if (key === 'impact') add('Impact');
      else if (key === 'courier new') add(w >= 600 ? 'CourierNewPS-BoldMT' : 'CourierNewPSMT');
      else if (key === 'arial') add(w >= 600 ? 'Arial-BoldMT' : 'ArialMT');
      else if (['sans-serif', 'serif', 'monospace', 'system-ui'].indexOf(key) < 0)
        weightName(w).forEach(function (n) { add(f.replace(/\s+/g, '') + '-' + n + it); });
    });
    add(w >= 600 ? 'Arial-BoldMT' : 'ArialMT'); add('Helvetica-Bold'); add('ArialMT');
    return out;
  }

  // ---------------------------------------------------------------- animation
  function chan(type, dist, w, h) {
    // Start state of an "in" animation, as offsets from the resting state.
    var d = dist == null ? 60 : dist;
    switch (type) {
      case 'none': return {};
      case 'fade': return { o: 0 };
      case 'slide-left': return { o: 0, p: [d, 0] };
      case 'slide-right': case 'skew-in': return { o: 0, p: [-d, 0] };
      case 'slide-up': return { o: 0, p: [0, d] };
      case 'slide-down': return { o: 0, p: [0, -d] };
      case 'wipe-right': return { w: 270 };
      case 'wipe-left': return { w: 90 };
      case 'wipe-down': return { w: 0 };
      case 'wipe-up': return { w: 180 };
      case 'reveal-up': return { w: 180, p: [0, Math.min(40, h / 2)] };
      case 'reveal-down': return { w: 0, p: [0, -Math.min(40, h / 2)] };
      case 'reveal-left': return { w: 90, p: [Math.min(40, w / 2), 0] };
      case 'reveal-right': return { w: 270, p: [-Math.min(40, w / 2), 0] };
      case 'wipe-center': return { s: [0, 100] };
      case 'grow-x': return { s: [0, 100] };
      case 'grow-y': return { s: [100, 0] };
      case 'zoom-out': return { o: 0, s: [118, 118] };
      case 'scale': return { o: 0, s: [70, 70] };
      case 'pop': return { o: 0, s: [30, 30], pop: true };
      case 'diamond': case 'iris': return { o: 0, s: [0, 0] };
      case 'letters': return { o: 0, p: [0, dist == null ? 40 : dist] };
      default: return { o: 0 };
    }
  }
  function anim(sp, t, box, rowOverride) {
    // t: {inStart, inEnd, outStart, outEnd} in seconds. Returns keys for opacity, position offset, scale and wipe.
    var A = { o: [], p: [], s: [], w: null };
    var inT = rowOverride || sp['in'];
    var outType = sp.out.type === 'auto' || !sp.out.type ? sp['in'].type : sp.out.type;
    var a = chan(inT.type || 'fade', inT.dist, box.w, box.h);
    var b = chan(outType, sp.out.dist == null ? inT.dist : sp.out.dist, box.w, box.h);
    function seg(c, t0, t1, enter) {
      if (c.o != null) { A.o.push([enter ? t0 : t0, enter ? 0 : 100]); A.o.push([t1, enter ? 100 : 0]); }
      if (c.p) { A.p.push([t0, enter ? c.p : [0, 0]]); A.p.push([t1, enter ? [0, 0] : c.p]); }
      if (c.s) {
        if (c.pop && enter) { A.s.push([t0, c.s]); A.s.push([t0 + (t1 - t0) * 0.7, [108, 108]]); A.s.push([t1, [100, 100]]); }
        else { A.s.push([t0, enter ? c.s : [100, 100]]); A.s.push([t1, enter ? [100, 100] : c.s]); }
      }
      if (c.w != null) {
        A.w = A.w || { angle: c.w, k: [] };
        A.w.k.push([t0, enter ? 100 : 0]); A.w.k.push([t1, enter ? 0 : 100]);
      }
    }
    seg(a, t.inStart, Math.max(t.inStart + 1 / 30, t.inEnd), true);
    if (b.w != null && a.w != null && b.w !== a.w) b.w = a.w;   // one wipe effect per layer
    seg(b, t.outStart, Math.max(t.outStart + 1 / 30, t.outEnd), false);
    var out = {};
    ['o', 'p', 's'].forEach(function (k) { if (A[k].length) out[k] = A[k].map(function (x) { return [r3(x[0]), x[1]]; }); });
    if (A.w) out.w = { angle: A.w.angle, k: A.w.k.map(function (x) { return [r3(x[0]), x[1]]; }) };
    return out;
  }

  // ---------------------------------------------------------------- reading a drawn graphic
  function rectIn(node, stageRect, k) {
    var r = node.getBoundingClientRect();
    return { x: (r.left - stageRect.left) / k, y: (r.top - stageRect.top) / k, w: r.width / k, h: r.height / k };
  }
  function textRect(node, stageRect, k) {
    var rg = document.createRange();
    rg.selectNodeContents(node);
    var r = rg.getBoundingClientRect();
    return { x: (r.left - stageRect.left) / k, y: (r.top - stageRect.top) / k, w: r.width / k, h: r.height / k };
  }
  var MEASURE = null;
  function inkCenter(text, cs, tr, size) {
    if (/\n/.test(text)) return null;
    try {
      MEASURE = MEASURE || document.createElement('canvas').getContext('2d');
      MEASURE.font = (cs.fontStyle === 'italic' ? 'italic ' : '') + cs.fontWeight + ' ' + size + 'px ' + cs.fontFamily;
      var m = MEASURE.measureText(text);
      if (m.fontBoundingBoxAscent == null || m.actualBoundingBoxAscent == null) return null;
      var lineTop = tr.y + (tr.h - (m.fontBoundingBoxAscent + m.fontBoundingBoxDescent)) / 2;
      var baseline = lineTop + m.fontBoundingBoxAscent;
      return baseline - (m.actualBoundingBoxAscent - m.actualBoundingBoxDescent) / 2;
    } catch (e) { return null; }
  }
  function teamOf(str) {
    var m = String(str || '').match(/\{(away|home|team|batting|fielding|scorer)\.color\}/);
    return m ? m[1] : null;
  }
  function nice(s) {
    s = String(s || '').replace(/[_-]+/g, ' ').trim();
    return s.charAt(0).toUpperCase() + s.slice(1);
  }

  /*
   * gr: a GFX.Graphic built and shown (instant) on a 1920x1080 stage element; ctx: the data it was drawn with.
   * Returns {name, layers, controls, inEnd, outStart, duration, images: {src: file}}.
   */
  function extract(gr, ctx, stage, opts) {
    opts = opts || {};
    var k = stage.getBoundingClientRect().width / 1920;
    var sr = stage.getBoundingClientRect();
    var layers = [], controls = [], teams = {}, images = opts.images || {}, used = {};
    var holdS = opts.hold == null ? 4 : opts.hold;
    var nodes = gr.nodes.slice().sort(function (a, b) { return (a._el.z || 0) - (b._el.z || 0); });
    // timing: when everything is in, and how long the way out takes
    var inEnd = 0, outLen = 0;
    nodes.forEach(function (w) {
      if (w.style.display === 'none') return;
      var sp = GFX.specs(w._el);
      var e = (sp['in'].delay || 0) + (sp['in'].dur || 0);
      if (sp['in'].type === 'letters') e += 12 * (sp['in'].stagger == null ? 35 : sp['in'].stagger);
      if (sp.rows) e += (sp.rows.delay || 0) + 6 * (sp.rows.stagger || 60) + (sp.rows.dur || 300);
      if (!sp.hold) { inEnd = Math.max(inEnd, e); outLen = Math.max(outLen, (sp.out.delay || 0) + (sp.out.dur || 0)); }
      else inEnd = Math.max(inEnd, Math.min(e, 1500));
    });
    inEnd = inEnd / 1000;
    var outStart = Math.round((inEnd + holdS) * 30) / 30;
    var duration = Math.round((outStart + outLen / 1000 + 0.2) * 30) / 30;

    function editName(base) {
      var n = nice(base), i = 2;
      while (used[n]) n = nice(base) + ' ' + i++;
      used[n] = true;
      return n;
    }
    function timing(sp, rowIdx) {
      var i = sp['in'], o = sp.out;
      var d = i.delay || 0, dur = i.dur || 0;
      if (rowIdx != null && sp.rows) { d = d + (sp.rows.delay || 0) + rowIdx * (sp.rows.stagger || 60); dur = sp.rows.dur || 300; }
      var t = { inStart: d / 1000, inEnd: (d + dur) / 1000 };
      if (sp.hold) { t.outStart = (d + dur + sp.hold) / 1000; }
      else t.outStart = outStart + (o.delay || 0) / 1000;
      t.outEnd = t.outStart + (o.dur || 300) / 1000;
      return t;
    }
    function teamControl(team) {
      if (!teams[team]) {
        var c = parseColor(GFX.color('{' + team + '.color}', ctx, gr.theme)) || [0.5, 0.5, 0.5, 1];
        teams[team] = { label: TEAM_LABEL[team] };
        controls.push({ kind: 'color', label: TEAM_LABEL[team], value: col(c) });
      }
      return teams[team];
    }

    nodes.forEach(function (w) {
      if (w.style.display === 'none') return;
      var el = w._el, st = el.style || {}, sp = GFX.specs(el), inner = w._inner;
      var rot = (el.rotate || 0) + (st.rotate || 0);
      var op = el.opacity == null ? 1 : +el.opacity;
      var wr = { x: +el.x, y: +el.y, w: +el.w, h: +el.h };
      var useRows = sp.rows && (sp['in'].type === 'none' || !sp['in'].type);
      var base = el.name || el.type;

      function boxFrom(node, rect, name, team, aSpec) {
        var cs = getComputedStyle(node);
        var bg = background(cs);
        var bw = parseFloat(cs.borderTopWidth) || 0;
        var bc = bw ? parseColor(cs.borderTopColor) : null;
        if (!bg && !(bc && bc[3] > 0.01)) return;
        var rad = cs.borderTopLeftRadius || '0px';
        var L = { t: 'box', name: name, x: r3(rect.x), y: r3(rect.y), w: r3(rect.w), h: r3(rect.h), rot: node === inner ? rot : 0,
                  r: /%/.test(rad) ? 0 : Math.round(parseFloat(rad) || 0), anim: aSpec };
        if (/%/.test(rad) && parseFloat(rad) >= 50) L.round = 'ellipse';
        if (L.r >= Math.min(rect.w, rect.h) / 2 - 0.5 && Math.abs(rect.w - rect.h) < 1 && L.r > 0) L.round = 'ellipse';
        if (bg) {
          L.fill = bg;
          L.alpha = r3(bg.alpha * op);
        } else { L.fill = { kind: 'flat', c0: [0, 0, 0, 1] }; L.alpha = 0; }
        if (bc && bc[3] > 0.01) L.border = { w: bw, c: col(bc) };
        var sh = shadowOf(cs.boxShadow);
        if (sh) L.shadow = sh;
        if (team && bg) L.team = teamControl(team);
        if (!bg && L.border) { L.fill = { kind: 'flat', c0: [0, 0, 0, 1] }; L.alpha = 0; }
        layers.push(L);
      }
      function textFrom(node, txtNode, name, editable, aSpec, align, maxW, wrap) {
        var cs = getComputedStyle(node);
        var raw = (txtNode.textContent || '').replace(/ /g, ' ');
        if (!raw.trim()) return;
        if (cs.textTransform === 'uppercase') raw = raw.toUpperCase();
        var c = parseColor(cs.color) || [1, 1, 1, 1];
        if (c[3] <= 0.01) {
          // hollow outlined type: keep the outline only
          if (!(parseFloat(cs.webkitTextStrokeWidth) > 0)) return;
        }
        var tr = textRect(txtNode, sr, k);
        if (tr.w <= 0 || tr.h <= 0) return;
        var size = parseFloat(cs.fontSize) || 32;
        var L = { t: 'text', name: name, text: raw.replace(/\n/g, '\r'), size: r3(size), fonts: fontList(cs.fontFamily, cs.fontWeight, cs.fontStyle === 'italic'),
                  css: [cs.fontFamily, cs.fontWeight, cs.fontStyle], color: col(c), align: align || 'left', tracking: Math.round((parseFloat(cs.letterSpacing) || 0) / size * 1000),
                  cy: r3(tr.y + tr.h / 2), rot: node === inner ? rot : 0, anim: aSpec, alpha: r3((c[3] > 0.01 ? c[3] : 1) * op) };
        L.ax = r3(align === 'center' ? tr.x + tr.w / 2 : (align === 'right' ? tr.x + tr.w : tr.x));
        // After Effects centres on the letters themselves (their ink), not the line box: find where the ink sits.
        var ink = inkCenter(raw, cs, tr, size);
        if (ink != null) L.cy = r3(ink);
        if (maxW) L.maxW = Math.round(maxW);
        if (wrap) { L.wrap = true; L.x = wr.x; L.y = wr.y; L.w = wr.w; L.h = wr.h; }
        var sw = parseFloat(cs.webkitTextStrokeWidth) || 0;
        if (sw > 0) L.stroke = { w: sw, c: col(parseColor(cs.webkitTextStrokeColor) || [0, 0, 0, 1]) };
        if (c[3] <= 0.01) L.color = col(L.stroke.c);
        var sh = shadowOf(cs.textShadow);
        if (sh) L.shadow = sh;
        var tm = teamOf(st.color);
        if (tm && node === inner) L.team = teamControl(tm);
        if (editable) L.edit = editName(name);
        layers.push(L);
      }
      function imageFrom(img, name, aSpec) {
        if (!img.src || img.style.visibility === 'hidden' || img.style.display === 'none' || !img.naturalWidth) return;
        var cs = getComputedStyle(img);
        var rect = rectIn(img, sr, k);
        if (rect.w < 1 || rect.h < 1) return;
        var src = img.currentSrc || img.src;
        if (!images[src]) images[src] = 'img' + (Object.keys(images).length + 1);
        layers.push({ t: 'image', name: name, file: images[src], src: src, x: r3(rect.x), y: r3(rect.y), w: r3(rect.w), h: r3(rect.h),
                      fit: cs.objectFit === 'cover' ? 'cover' : 'contain', focusTop: /top/.test(cs.objectPosition) && cs.objectFit === 'cover',
                      r: Math.round(parseFloat(getComputedStyle(img.parentNode).borderTopLeftRadius) || 0), rot: rot, anim: aSpec, alpha: r3(op) });
      }

      var whole = anim(sp, timing(sp), wr);
      if (el.type === 'box') return boxFrom(inner, wr, base, teamOf(st.background || st.fill), whole);
      if (el.type === 'text') {
        var span = inner.querySelector('.gx-txt');
        var bg = background(getComputedStyle(inner));
        if (bg) boxFrom(inner, wr, base + ' bg', null, whole);
        if (!span) return;
        var pad = parseFloat(getComputedStyle(inner).paddingLeft) || 0;
        var editable = String(el.text || '').indexOf('{') >= 0;
        return textFrom(inner, span, base, editable, whole, st.align || 'left', st.wrap && !st.fit ? 0 : wr.w - 2 * pad, st.wrap && !st.fit);
      }
      if (el.type === 'image') {
        var im = inner.querySelector('img');
        if (im) imageFrom(im, base, whole);
        return;
      }
      if (el.type === 'bases') {
        var on = parseColor(GFX.color(st.on || '$accent', ctx, gr.theme)) || [1, 1, 1, 1];
        var off = parseColor(GFX.color(st.off, ctx, gr.theme) || 'transparent') || [0, 0, 0, 0];
        var stroke = st.stroke ? parseColor(GFX.color(st.stroke, ctx, gr.theme)) : null;
        var b = GFX.get(ctx, el.bind || 'bases') || {};
        Array.prototype.forEach.call(inner.querySelectorAll('polygon[data-base]'), function (pg) {
          var n = pg.getAttribute('data-base');
          var label = { '1': 'Runner on 1st', '2': 'Runner on 2nd', '3': 'Runner on 3rd' }[n];
          if (!controls.some(function (c) { return c.label === label; })) controls.push({ kind: 'check', label: label, value: b[n] ? 1 : 0 });
          var rr = rectIn(pg, sr, k), side = rr.w / Math.SQRT2;
          layers.push({ t: 'base', name: 'Base ' + n, x: r3(rr.x + (rr.w - side) / 2), y: r3(rr.y + (rr.h - side) / 2), w: r3(side), h: r3(side),
                        on: col(on), off: col(off), ctl: label, border: stroke && st.strokeW ? { w: +st.strokeW, c: col(stroke) } : null, anim: whole });
        });
        return;
      }
      if (el.type === 'dots') {
        var don = parseColor(GFX.color(st.on || '$accent', ctx, gr.theme)) || [1, 1, 1, 1];
        var doff = parseColor(GFX.color(st.off, ctx, gr.theme) || 'transparent') || [0, 0, 0, 0];
        var label = el.bind === 'outs' || !el.bind ? 'Outs' : nice(el.bind.split('.').pop());
        if (!controls.some(function (c) { return c.label === label; }))
          controls.push({ kind: 'slider', label: label, value: parseInt(GFX.get(ctx, el.bind || 'outs'), 10) || 0 });
        Array.prototype.forEach.call(inner.children, function (dot, i) {
          var rr = rectIn(dot, sr, k);
          layers.push({ t: 'dot', name: label + ' ' + (i + 1), x: r3(rr.x), y: r3(rr.y), w: r3(rr.w), h: r3(rr.h), n: i + 1, on: col(don), off: col(doff),
                        ctl: label, round: st.shape !== 'square', anim: whole });
        });
        return;
      }
      // Everything else (tables, linescore, ticker, clocks, QR...): walk what was drawn.
      var bgIn = background(getComputedStyle(inner));
      if (bgIn) boxFrom(inner, wr, base + ' bg', null, whole);
      var rows = Array.prototype.slice.call(inner.querySelectorAll('.gx-row:not(.gx-head)'));
      (function walk(node, rowIdx, depth) {
        Array.prototype.forEach.call(node.children, function (ch) {
          if (getComputedStyle(ch).display === 'none') return;
          var ri = rowIdx;
          if (ch.classList.contains('gx-row') && !ch.classList.contains('gx-head')) ri = rows.indexOf(ch);
          var a = useRows && ri != null && ri >= 0 ? anim(sp, timing(sp, ri), wr, sp.rows) : whole;
          var head = !!(ch.closest && ch.closest('.gx-head'));
          var tag = ch.tagName.toLowerCase();
          if (tag === 'img') return imageFrom(ch, base + ' image', a);
          if (tag === 'svg' || tag === 'canvas') return;
          var rect = rectIn(ch, sr, k);
          if (rect.w < 1 || rect.h < 1) return;
          boxFrom(ch, rect, base + (ri != null && ri >= 0 ? ' row ' + (ri + 1) : '') + ' fill', null, a);
          var direct = Array.prototype.some.call(ch.childNodes, function (n) { return n.nodeType === 3 && n.textContent.trim(); });
          if (direct) {
            var cs = getComputedStyle(ch);
            var jc = cs.justifyContent, ta = cs.textAlign;
            var al = /flex-end|right|end/.test(jc) ? 'right' : (/center/.test(jc) ? 'center' : (cs.display.indexOf('flex') < 0 && ta === 'center' ? 'center' :
                     (cs.display.indexOf('flex') < 0 && ta === 'right' ? 'right' : 'left')));
            var cellName = base + (ri != null && ri >= 0 ? ' row ' + (ri + 1) : (head ? ' header' : '')) + ' text';
            textFrom(ch, ch, cellName, !head && ri != null && ri >= 0 || el.type === 'linescore' && !head, a, al, rect.w, false);
            return;
          }
          if (depth < 6) walk(ch, ri, depth + 1);
        });
      })(inner, null, 0);
    });
    return { layers: layers, controls: controls, inEnd: r3(Math.max(inEnd, 0.1)), outStart: r3(outStart), duration: r3(duration), images: images };
  }

  // ---------------------------------------------------------------- script + zip
  function asciiJs(s) {
    // ExtendScript reads files in the system encoding; escape everything outside ASCII.
    return s.replace(/[\u0080-￿]/g, function (c) { return '\\u' + ('000' + c.charCodeAt(0).toString(16)).slice(-4); });
  }
  function script(runtime, data) {
    var clean = JSON.parse(JSON.stringify(data, function (k, v) { return k === 'src' || k === 'css' ? undefined : v; }));
    return '#target aftereffects\n' + asciiJs('var BBG_DATA = ' + JSON.stringify(clean) + ';\n') + asciiJs(runtime);
  }

  var CRC = (function () {
    var t = [];
    for (var n = 0; n < 256; n++) {
      var c = n;
      for (var i = 0; i < 8; i++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
      t[n] = c >>> 0;
    }
    return t;
  })();
  function crc32(u8) {
    var c = 0xFFFFFFFF;
    for (var i = 0; i < u8.length; i++) c = CRC[(c ^ u8[i]) & 0xFF] ^ (c >>> 8);
    return (c ^ 0xFFFFFFFF) >>> 0;
  }
  // files: [{name, data: Uint8Array}] -> Blob (stored, no compression)
  function zip(files) {
    var enc = new TextEncoder(), parts = [], central = [], offset = 0;
    function u16(v) { return [v & 255, (v >>> 8) & 255]; }
    function u32(v) { return [v & 255, (v >>> 8) & 255, (v >>> 16) & 255, (v >>> 24) & 255]; }
    files.forEach(function (f) {
      var name = enc.encode(f.name), data = f.data, crc = crc32(data);
      var head = [].concat([0x50, 0x4b, 0x03, 0x04], u16(20), u16(0x0800), u16(0), u16(0), u16(0x21), u32(crc), u32(data.length), u32(data.length),
        u16(name.length), u16(0));
      parts.push(new Uint8Array(head), name, data);
      central.push(new Uint8Array([].concat([0x50, 0x4b, 0x01, 0x02], u16(20), u16(20), u16(0x0800), u16(0), u16(0), u16(0x21), u32(crc),
        u32(data.length), u32(data.length), u16(name.length), u16(0), u16(0), u16(0), u16(0), u32(0), u32(offset))), name);
      offset += head.length + name.length + data.length;
    });
    var csize = central.reduce(function (a, p) { return a + p.length; }, 0);
    var end = new Uint8Array([].concat([0x50, 0x4b, 0x05, 0x06], u16(0), u16(0), u16(files.length), u16(files.length), u32(csize), u32(offset), u16(0)));
    return new Blob(parts.concat(central, [end]), { type: 'application/zip' });
  }

  root.AEX = { extract: extract, script: script, zip: zip, crc32: crc32, parseColor: parseColor, background: background, fontList: fontList, anim: anim };
})(window);
