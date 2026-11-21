/*
 * Baseball Graphics template engine
 * ---------------------------------
 * Renders JSON graphic templates into absolutely positioned HTML layers on a
 * 1920x1080 transparent stage and animates them in and out with the Web
 * Animations API. Shared by overlay.html (OBS browser sources) and
 * editor.html (visual editor), so what you design is exactly what airs.
 */
(function (root) {
  'use strict';

  var STAGE_W = 1920, STAGE_H = 1080;

  // ------------------------------------------------------------------ data
  function get(obj, path) {
    if (path == null || path === '') return undefined;
    var parts = String(path).split('.');
    var o = obj;
    for (var i = 0; i < parts.length; i++) {
      if (o == null) return undefined;
      o = o[parts[i]];
    }
    return o;
  }

  function blank(v) { return v === null || v === undefined || v === ''; }

  function rate(v, d) {
    if (blank(v)) return '';
    var n = Number(v);
    if (!isFinite(n)) return String(v);
    var s = n.toFixed(d);
    if (n >= 0 && n < 1) s = s.replace(/^0/, '');
    return s;
  }

  function ordinal(v) {
    var n = parseInt(v, 10);
    if (!isFinite(n)) return blank(v) ? '' : String(v);
    var s = (n % 100 >= 11 && n % 100 <= 13) ? 'th' : ({ 1: 'st', 2: 'nd', 3: 'rd' }[n % 10] || 'th');
    return n + s;
  }

  var FILTERS = {
    upper: function (v) { return blank(v) ? '' : String(v).toUpperCase(); },
    lower: function (v) { return blank(v) ? '' : String(v).toLowerCase(); },
    avg: function (v) { return rate(v, 3); },
    era: function (v) { if (blank(v)) return ''; var n = Number(v); return isFinite(n) ? n.toFixed(2) : String(v); },
    dec1: function (v) { if (blank(v)) return ''; var n = Number(v); return isFinite(n) ? n.toFixed(1) : String(v); },
    int: function (v) { if (blank(v)) return ''; var n = Number(v); return isFinite(n) ? String(Math.round(n)) : String(v); },
    last: function (v) { if (blank(v)) return ''; var p = String(v).trim().split(/\s+/); return p[p.length - 1]; },
    first: function (v) { if (blank(v)) return ''; return String(v).trim().split(/\s+/)[0]; },
    initial: function (v) { if (blank(v)) return ''; var p = String(v).trim().split(/\s+/); return p.length > 1 ? p[0][0] + '. ' + p.slice(1).join(' ') : p[0]; },
    ord: ordinal,
    dash: function (v) { return blank(v) ? '-' : v; },
    zero: function (v) { return blank(v) ? '0' : v; },
    num: function (v) { return blank(v) ? '' : '#' + v; },
    dot: function (v) { return blank(v) ? '' : v + '. '; },
    hand: function (v) { return v === 'L' ? 'LHP' : (v === 'R' ? 'RHP' : (blank(v) ? '' : v)); }
  };

  function fmt(tpl, ctx) {
    if (tpl == null) return '';
    return String(tpl).replace(/\{([^{}]+)\}/g, function (_, expr) {
      var bits = expr.split('|');
      var v = get(ctx, bits[0].trim());
      for (var i = 1; i < bits.length; i++) {
        var f = FILTERS[bits[i].trim()];
        if (f) v = f(v);
      }
      return blank(v) ? '' : String(v);
    });
  }

  function hexToRgba(hex, a) {
    var h = String(hex).replace('#', '');
    if (h.length === 3) h = h.split('').map(function (c) { return c + c; }).join('');
    if (!/^[0-9a-fA-F]{6}$/.test(h)) return hex;
    var n = parseInt(h, 16);
    return 'rgba(' + (n >> 16 & 255) + ',' + (n >> 8 & 255) + ',' + (n & 255) + ',' + a + ')';
  }

  // Colors: "#hex", "rgba(...)", "$primary" (theme token), "{home.color}" (data),
  // and any of those with "@0.8" appended for transparency.
  function color(v, ctx, theme) {
    if (blank(v)) return '';
    var s = String(v), alpha = null;
    var at = s.lastIndexOf('@');
    if (at > 0 && /^@\d*\.?\d+$/.test(s.slice(at))) { alpha = parseFloat(s.slice(at + 1)); s = s.slice(0, at); }
    if (s[0] === '$') s = (theme && theme[s.slice(1)]) || '';
    else if (s.indexOf('{') >= 0) { s = fmt(s, ctx); if (s[0] === '$') s = (theme && theme[s.slice(1)]) || ''; }
    if (alpha !== null && s) {
      if (s[0] === '#') s = hexToRgba(s, alpha);
      else s = 'color-mix(in srgb, ' + s + ' ' + Math.round(alpha * 100) + '%, transparent)';
    }
    return s;
  }

  function font(v, theme) {
    if (blank(v)) v = '$font';
    if (String(v)[0] === '$') return (theme && theme[String(v).slice(1)]) || (theme && theme.font) || 'sans-serif';
    return v;
  }

  // showIf: "path", "!path", "path>0", "half==top", "status!=FINAL"
  function cond(expr, ctx) {
    if (blank(expr)) return true;
    var sx = String(expr).trim();
    if (/^!\(.*\)$/.test(sx)) return !cond(sx.slice(2, -1), ctx);
    if (/^\(.*\)$/.test(sx)) return cond(sx.slice(1, -1), ctx);
    if (sx.indexOf('||') >= 0) return sx.split('||').some(function (p) { return cond(p, ctx); });
    if (sx.indexOf('&&') >= 0) return sx.split('&&').every(function (p) { return cond(p, ctx); });
    var m = sx.trim().match(/^(!)?\s*([\w.]+)\s*(==|!=|>=|<=|>|<)?\s*(.*)$/);
    if (!m) return true;
    var v = get(ctx, m[2]);
    var res;
    if (!m[3]) {
      res = !(blank(v) || v === false || v === 0 || (Array.isArray(v) && !v.length));
    } else {
      var rhs = m[4].trim().replace(/^['"]|['"]$/g, '');
      var a = isFinite(Number(v)) && !blank(v) ? Number(v) : String(v == null ? '' : v);
      var b = isFinite(Number(rhs)) && rhs !== '' ? Number(rhs) : rhs;
      switch (m[3]) {
        case '==': res = a == b; break;
        case '!=': res = a != b; break;
        case '>': res = a > b; break;
        case '<': res = a < b; break;
        case '>=': res = a >= b; break;
        case '<=': res = a <= b; break;
      }
    }
    return m[1] ? !res : res;
  }

  // Which sponsor a slot shows right now. Must match sponsor_for() in obs_baseball_graphics.py:
  // rotation is a pure function of the clock so every overlay and the exposure log agree.
  // A spec is one slot or a comma list tried in order, and may use {tokens}:
  //   "half_{halfKey}, scorebug"   "lineup_{batter.slot}, batter"   "lineup_{row.slot}"
  // The first slot that is switched on with a sponsor wins. Must match sponsor_for() in Python.
  function sponsorFor(ui, spec, now, ctx) {
    var off = { on: false, id: '', name: '', logo: '', label: '', slot: '' };
    var parts = String(spec || '').split(',');
    for (var i = 0; i < parts.length; i++) {
      var part = parts[i].trim();
      if (!part) continue;
      var missing = false;
      var name = part.replace(/\{([^{}]+)\}/g, function (_, k) {
        var v = get(ctx || {}, k.trim());
        if (blank(v)) { missing = true; return ''; }
        return String(v);
      });
      if (missing) continue;
      var r = sponsorSlot(ui, name, now);
      if (r.on) return r;
    }
    return off;
  }

  function sponsorSlot(ui, slot, now) {
    var off = { on: false, id: '', name: '', logo: '', label: '', slot: slot };
    if (!slot) return off;
    var sp = (ui && ui.sponsors) || {};
    var st = (sp.slots || {})[slot] || {};
    if (!st.enabled) return off;
    var lib = {};
    (sp.library || []).forEach(function (x) { if (x && x.id && x.active !== false) lib[x.id] = x; });
    var items = (st.ids || []).filter(function (i) { return lib[i]; }).map(function (i) { return lib[i]; });
    if (!items.length) return off;
    now = now == null ? Date.now() / 1000 : now;
    var rot = Number(st.rotate) || 0;
    var idx = rot > 0 && items.length > 1 ? Math.floor(now / rot) % items.length : 0;
    var it = items[idx];
    return { on: true, id: it.id, name: it.name || '', logo: it.logo || '', label: st.label || '', slot: slot };
  }

  function presetCtx(p, ctx) {
    var o = {};
    Object.keys(p).forEach(function (k) { o[k] = typeof p[k] === 'string' ? fmt(p[k], ctx) : p[k]; });
    var rows = String(o.text || '').split('\n').map(function (l) { return l.trim(); }).filter(Boolean).map(function (l) {
      var c = l.split('|').map(function (x) { return x.trim(); });
      return { a: c[0] || '', b: c[1] || '', c: c[2] || '', line: l };
    });
    o.rows = rows;
    o.count = rows.length;
    var i = rows.length ? ((Number(o.index) || 0) % rows.length + rows.length) % rows.length : 0;
    o.current = rows[i] || { a: '', b: '', c: '' };
    o.position = rows.length ? (i + 1) + ' / ' + rows.length : '';
    o.items = rows.map(function (r) { return { src: r.a, caption: r.b }; });
    o.interval = o.interval || 6;
    o.mode = o.mode || 'to';
    return o;
  }

  // Podcast fields (control panel > Podcast) with lists split into rows the graphics can show.
  function lines(t) {
    return String(t || '').split('\n').map(function (l) { return l.trim(); }).filter(Boolean)
      .map(function (l) { var c = l.split('|').map(function (x) { return x.trim(); }); return { a: c[0] || '', b: c[1] || '', c: c[2] || '', line: l }; });
  }
  function podcastCtx(p, ctx) {
    var o = {};
    p = p || {};
    Object.keys(p).forEach(function (k) { o[k] = typeof p[k] === 'string' ? fmt(p[k], ctx) : p[k]; });
    [1, 2, 3, 4].forEach(function (n) {
      o['p' + n] = { name: o['p' + n + 'n'] || '', role: o['p' + n + 'r'] || '', handle: o['p' + n + 'h'] || '', photo: o['p' + n + 'p'] || '', n: n };
    });
    o.count = [1, 2, 3, 4].filter(function (n) { return o['p' + n].name; }).length;
    o.guest = { name: o.gName || '', role: o.gTitle || '', handle: o.gHandle || '', photo: o.gPhoto || '', b1: o.gB1 || '', b2: o.gB2 || '', b3: o.gB3 || '' };
    var sp = String(o.speaker || '1');
    o.mic = sp === 'g' ? o.guest : (o['p' + sp] || o.p1);
    // Rundown: the current item is highlighted; the ones before it are done.
    var ag = lines(o.agenda), ai = Math.max(0, Math.min(ag.length - 1, Number(o.agendaIdx) || 0));
    o.agendaRows = ag.map(function (r, i) { return { n: String(i + 1), text: r.a, cur: i === ai, done: i < ai }; });
    o.agendaCur = (ag[ai] || {}).a || '';
    o.agendaNext = (ag[ai + 1] || {}).a || '';
    // Top list counts down: revealing shows the bottom entry first.
    var tp = lines(o.top), rv = Math.max(0, Math.min(tp.length, Number(o.topReveal) || 0));
    o.topRows = tp.map(function (r, i) { var rank = i + 1, shown = rank > tp.length - rv; return { n: String(rank), text: shown ? r.a : '', note: shown ? r.b : '', shown: shown }; });
    // Poll: "Option | percent". Results show when Reveal is on.
    var pl = lines(o.pollOpts);
    o.pollRows = pl.map(function (r, i) {
      var pct = Math.max(0, Math.min(100, parseFloat(r.b) || 0));
      return { n: String.fromCharCode(65 + i), text: r.a, pct: o.pollReveal ? pct : 0, pctText: o.pollReveal && r.b !== '' ? Math.round(pct) + '%' : '' };
    });
    [0, 1, 2, 3].forEach(function (i) { o['o' + (i + 1)] = o.pollRows[i] || { n: '', text: '', pct: 0, pctText: '' }; });
    o.cmpRows = lines(o.cmp).map(function (r) { return { label: r.a, l: r.b, r: r.c }; });
    o.pickRows = lines(o.picks).map(function (r) { return { who: r.a, pick: r.b, note: r.c }; });
    var soc = [['X', o.x], ['IG', o.ig], ['YT', o.yt], ['TT', o.tt], ['WEB', o.web]].filter(function (s2) { return s2[1]; });
    o.social = soc.map(function (s2) { return { icon: s2[0], handle: s2[1] }; });
    [0, 1, 2, 3, 4].forEach(function (i) { o['s' + (i + 1)] = o.social[i] || { icon: '', handle: '' }; });
    return o;
  }

  // GAME OPS (control panel): substitutions, pitch tracker, pitch clock, challenges, bullpen, hit data, storylines, breaks,
  // postgame and fan / sponsor features. Lists are one entry per line, columns split on "|".
  function opsCtx(p, ctx, game) {
    var o = {};
    p = p || {};
    Object.keys(p).forEach(function (k) { o[k] = typeof p[k] === 'string' ? fmt(p[k], ctx) : p[k]; });
    function cols(t) {
      return String(t || '').split('\n').map(function (l) { return l.trim(); }).filter(Boolean).map(function (l) { return l.split('|').map(function (x) { return x.trim(); }); });
    }
    function teamOf(k) {
      if (k === 'batting') k = game.battingSide || 'away';
      if (k === 'fielding') k = game.fieldingSide || 'home';
      return game[k === 'away' ? 'away' : 'home'] || {};
    }
    var st = teamOf(o.subTeam);
    o.sub = { label: o.subType || '', name: o.subIn || '', number: o.subInNum || '', pos: o.subPos || '', out: o.subOut || '', has: !!o.subIn,
      team: { abbr: st.abbr || '', name: st.name || '', logo: st.logo || '', color: st.color || '', color2: st.color2 || '' } };
    // Pitches of this at-bat: the ones entered on the pitch pad.
    var CALL = { b: ['Ball', 'ball'], s: ['Called strike', 'strike'], w: ['Swinging strike', 'strike'], f: ['Foul', 'strike'], x: ['In play', 'inplay'] };
    var feed = (game.abPitches || []).filter(function (r) { return r && r.x != null; });
    var rows = (o.pitchFeed !== false && feed.length) ? feed.map(function (r) { return { type: r.type || '', mph: r.mph || '', x: r.x, z: r.z, call: r.call || '', cls: r.cls || 'strike' }; })
      : cols(o.pitches).map(function (c) {
        var cl = CALL[String(c[4] || '').toLowerCase().charAt(0)] || [c[4] || '', 'strike'];
        return { type: c[0] || '', mph: c[1] || '', x: parseFloat(c[2]), z: parseFloat(c[3]), call: cl[0], cls: cl[1] };
      });
    rows.forEach(function (r, i) { r.n = String(i + 1); r.speed = r.mph ? r.mph + ' MPH' : ''; });
    o.pitchRows = rows;
    o.pitchCount = String(rows.length);
    var lp = rows[rows.length - 1] || {}, gp = game.pitch || {};
    o.lastPitch = { type: lp.type || gp.type || '', mph: lp.mph || gp.speed || '', call: lp.call || '' };
    o.lastPitch.has = !!(o.lastPitch.type || o.lastPitch.mph);
    // Challenges and replay review
    var REV = { review: 'Under review', stands: 'Call stands', overturned: 'Call overturned', confirmed: 'Call confirmed' };
    var rt = teamOf(o.revTeam);
    o.review = { status: REV[o.revStatus] || '', has: !!REV[o.revStatus], team: rt.abbr || '', call: o.revCall || '',
      done: o.revStatus === 'stands' || o.revStatus === 'overturned' || o.revStatus === 'confirmed' };
    o.chal = { away: Math.max(0, parseInt(o.chalAway, 10) || 0), home: Math.max(0, parseInt(o.chalHome, 10) || 0) };
    o.visits = { away: String(o.visitsAway == null ? '' : o.visitsAway), home: String(o.visitsHome == null ? '' : o.visitsHome) };
    // Bullpen: "Name | R | Warming | 0-25-0"; blank uses the roster's relievers.
    var STAT = { w: 'warm', h: 'warm', a: 'ready', r: 'ready', u: 'out', n: 'out', d: 'out', o: 'out' };
    o.bp = {};
    ['away', 'home'].forEach(function (sd) {
      var c = cols(o[sd === 'away' ? 'bpAway' : 'bpHome']);
      if (!c.length) c = ((game[sd] || {}).bullpen || []).map(function (p2) { return [p2.name || '', p2.throws || '', '', '']; });
      o.bp[sd] = c.map(function (r) { var cl = STAT[String(r[2] || '').toLowerCase().charAt(0)] || ''; return { name: r[0] || '', hand: r[1] || '', status: r[2] || '', last3: r[3] || '', cls: cl, warm: cl === 'warm' }; });
    });
    // Hit data: typed values win, then the feed's last batted ball.
    var gh = game.hit || {}, gl = game.lastPlay || {};
    o.hit = { ev: o.hitEv || gh.ev || gl.ev || '', la: o.hitLa || gh.la || gl.la || '', dist: o.hitDist || gh.dist || gl.distance || '' };
    o.hit.has = !!(o.hit.ev || o.hit.la || o.hit.dist);
    o.streakRows = cols(o.streaks).map(function (c) { return { player: c[0] || '', label: c[1] || '', value: c[2] || '' }; });
    o.msRows = cols(o.milestones).map(function (c) { return { player: c[0] || '', label: c[1] || '', value: c[2] || '' }; });
    o.cmpRows = cols(o.compare).map(function (c) { return { label: c[0] || '', away: c[1] || '', home: c[2] || '' }; });
    o.moveRows = cols(o.moves).map(function (c) { return { date: c[0] || '', player: c[1] || '', move: c[2] || '' }; });
    o.promoRows = cols(o.promos).map(function (c) { return { date: c[0] || '', opp: c[1] || '', promo: c[2] || '' }; });
    var sh = cols(o.shouts);
    o.shoutRows = sh.map(function (c) { return { text: c[0] || '', note: c[1] || '' }; });
    var si = Math.max(0, Math.min(sh.length - 1, parseInt(o.shoutIdx, 10) || 0));
    o.shout = o.shoutRows[si] || { text: '', note: '' };
    var gw = game.weather || {};
    o.wx = { temp: o.wxTemp || gw.temp || '', wind: o.wxWind || gw.wind || '', cond: o.wxCond || '', hum: o.wxHum || '' };
    o.series = { away: String(o.seriesAway || '0'), home: String(o.seriesHome || '0'), note: o.seriesNote || '', last: o.lastMeet || '', next: o.nextMeet || '' };
    o.delay = { title: o.delayTitle || '', msg: o.delayMsg || '', since: Number(o.delaySince) || 0, resume: o.delayResume || '' };
    o.delay.mode = o.delay.resume ? 'to' : 'up';
    o.stars = [o.star1, o.star2, o.star3].map(function (t, i) {
      var c = String(t || '').split('|').map(function (x) { return x.trim(); });
      return { n: String(i + 1), name: c[0] || '', team: c[1] || '', line: c[2] || '' };
    });
    o.hasStars = o.stars.some(function (r) { return r.name; });
    var kt = game[o.kTeam === 'away' ? 'away' : 'home'] || {};
    var kc = o.kMode === 'manual' ? (parseInt(o.kCount, 10) || 0) : (parseInt(kt.kTotal, 10) || 0);
    o.k = { count: String(kc), marks: new Array(Math.min(kc, 30) + 1).join('K'), team: kt.abbr || '', title: o.kTitle || '' };
    return o;
  }

  function makeCtx(game, ui, gid, def, theme) {
    game = game || {};
    ui = ui || {};
    var side = (ui.sides && ui.sides[gid]) || (def && def.side) || 'home';
    if (side === 'batting') side = game.battingSide || 'away';
    if (side === 'fielding') side = game.fieldingSide || 'home';
    var other = side === 'home' ? 'away' : 'home';
    var net = null;
    if (side === 'network') {
      // The broadcaster as a "team": its own colours (Custom > League & broadcaster), name and logo.
      var bb = (ui && ui.brand) || {};
      net = { name: bb.name || (theme && theme.brandName) || '', abbr: bb.short || (theme && theme.brandShort) || '', logo: bb.logo || (theme && theme.logo) || '',
        color: bb.color || (theme && theme.primary) || '#0A2240', color2: bb.color2 || (theme && theme.accent) || '#F5821F', isNetwork: true };
      other = 'home';
    }
    var ctx = Object.assign({}, game);
    ctx.custom = ui.custom || {};
    ctx.notes = ui.notes || {};
    ctx.show = ui.show || {};
    ctx.podcast = podcastCtx(ui.podcast, ctx);
    ctx.ops = opsCtx(ui.ops, ctx, game);
    // Manual home-run distance / exit velocity (control panel) when the feed has no Statcast.
    if (game.lastPlay && game.lastPlay.isHR) {
      var lp = Object.assign({}, game.lastPlay);
      if (blank(lp.distance) && !blank(ctx.notes.dist)) lp.distance = String(ctx.notes.dist);
      if (blank(lp.ev) && !blank(ctx.notes.ev)) lp.ev = String(ctx.notes.ev);
      ctx.lastPlay = lp;
    }
    ctx.team = net || game[side] || {};
    ctx.opp = game[other] || {};
    ctx.bullpen = (ctx.ops.bp || {})[side === 'away' ? 'away' : 'home'] || [];
    ctx.side = side;
    ctx.theme = theme || {};
    ctx.sponsor = (ui && ui.previewSponsor) || sponsorFor(ui, def && def.sponsorSlot, null, ctx);
    // Per-row sponsors (e.g. each lineup spot) for tables that show a sponsor column.
    if (def && def.rowSponsors) {
      ['away', 'home'].forEach(function (sd) {
        var t = game[sd];
        if (!t || !t.lineup) return;
        var copy = Object.assign({}, t);
        copy.lineup = t.lineup.map(function (r) {
          return Object.assign({}, r, { sponsor: (ui && ui.previewSponsor) || sponsorFor(ui, def.rowSponsors, null, Object.assign({}, ctx, { row: r })) });
        });
        ctx[sd] = copy;
        if (side === sd) ctx.team = copy;
      });
    }
    // Standings group chosen for this graphic (control panel), else the graphic's default.
    var groups = (game.standings && game.standings.groups) || [];
    var gi = ui && ui.groups && ui.groups[gid] != null ? ui.groups[gid] : ((def && def.groupIndex) || 0);
    ctx.standingsGroup = groups[Math.min(Math.max(0, gi | 0), Math.max(0, groups.length - 1))] || { name: '', teams: [] };
    // Brand: theme logo / name when set, otherwise the home team's.
    var home = game.home || {};
    var ub = (ui && ui.brand) || {};
    // Broadcaster (the network or stream brand), set in Custom > League & broadcaster. It no longer falls back to the
    // home team, so the home logo never appears twice; graphics hide the brand mark when none is set.
    ctx.brand = { logo: ub.logo || (theme && theme.logo) || '', name: ub.name || (theme && theme.brandName) || '', short: ub.short || (theme && theme.brandShort) || '',
      color: ub.color || (theme && theme.primary) || '#0A2240', color2: ub.color2 || (theme && theme.accent) || '#F5821F' };
    ctx.league = (ui && ui.league) || {};
    // Custom-panel preset graphics (p_<id>): ctx.preset with the text lines split on "|", the current line, and carousel items.
    if (def && def.presetId) ctx.preset = presetCtx(((ui && ui.presets) || {})[def.presetId] || {}, ctx);
    // Player picker: "pickable" graphics show the chosen player instead of the current batter / pitcher.
    var pk = game.picked;
    if (def && def.pickable && ui.pick && ui.pick.on && pk && pk.name) {
      var t = game[pk.side] || {};
      ctx.batter = pk.bat;
      ctx.pitcher = pk.pit;
      var sum = { abbr: t.abbr, name: t.name, color: t.color, color2: t.color2, logo: t.logo, runs: t.runs, city: t.city, nick: t.nick };
      ctx.batting = sum;
      ctx.fielding = sum;
      ctx.team = t;
      ctx.picked = pk;
    }
    return ctx;
  }

  // ------------------------------------------------------------ elements
  var ELEMENT_DEFAULTS = {
    box: { w: 400, h: 80, style: { fill: '$primary@0.9', radius: 0 } },
    text: { w: 400, h: 60, text: '{batter.name|upper}', style: { color: '$text', size: 36, weight: 700, align: 'left', valign: 'center', padX: 12, fit: true } },
    image: { w: 160, h: 160, src: '{batter.photo}', style: { fit: 'cover', radius: 0 } },
    video: { w: 1920, h: 1080, src: '{theme.openerVideo}', loop: false, sound: false, style: { fit: 'cover' } },
    bases: { w: 120, h: 80, style: { on: '$accent', off: '#FFFFFF@0.18', stroke: '#FFFFFF@0.7', strokeW: 2 } },
    dots: { w: 80, h: 24, bind: 'outs', style: { total: 2, size: 16, gap: 8, on: '$accent', off: '#FFFFFF@0.2', shape: 'circle', align: 'center' } },
    table: {
      w: 700, h: 600, bind: 'team.lineup',
      columns: [
        { label: '', field: 'slot', w: 0.6, align: 'center' },
        { label: 'PLAYER', field: '{row.name|upper}', w: 4, align: 'left' },
        { label: 'POS', field: 'pos', w: 1, align: 'center' },
        { label: 'AVG', field: '{row.avg|avg}', w: 1.2, align: 'right' }
      ],
      style: { rowH: 60, size: 28, weight: 700, color: '$text', rowFill: '$panel', altFill: '$panel2', header: true, headerH: 40, headerSize: 18, headerColor: '$accent', headerFill: '', padX: 16, gap: 2, highlight: 'isCurrent', highlightFill: '$accent@0.35', maxRows: 12 }
    },
    field: { w: 1000, h: 800, bind: 'team.defense', style: { grass: '#1F6B3A@0.55', dirt: '#B5835A@0.6', line: '#FFFFFF@0.8', labelFill: '$primary@0.92', nameColor: '$text', posColor: '$accent', size: 24, nameField: 'last' } },
    clock: { w: 400, h: 120, mode: '{preset.mode}', target: '{preset.time}', since: '{preset.since}', dur: '{preset.dur}', style: { color: '$text', size: 96, weight: 800, align: 'center' } },
    zone: { w: 300, h: 360, bind: 'ops.pitchRows', style: { ball: '#2FB463', strike: '#E5484D', inplay: '#3D8BFD', line: '#FFFFFF@0.85', fill: '#FFFFFF@0.06', r: 15 } },
    spray: { w: 520, h: 430, bind: 'batter.tm.spray', style: { grass: '#1F6B3A@0.55', dirt: '#B5835A@0.55', line: '#FFFFFF@0.85', hr: '$accent' } },
    flag: { w: 380, h: 220, src: '/art/us-flag.svg', style: { amp: 0.05, speed: 1, waves: 1.6, shade: 0.22 } },
    carousel: { w: 960, h: 540, bind: 'preset.items', interval: '{preset.interval}', style: { fit: 'cover', capSize: 40 } },
    qr: { w: 220, h: 220, text: '{show.qrUrl}', style: { color: '#000000', bg: '#FFFFFF', quiet: 2, ecc: 'M' } },
    ticker: { w: 1600, h: 60, bind: 'ticker.items', style: { size: 30, weight: 700, color: '$text', speed: 110, headFill: '$accent', headColor: '$primary' } },
    linescore: { w: 1100, h: 140, style: { size: 30, color: '$text', headColor: '$accent', headSize: 18, rowFill: '$panel', totalFill: '$primary', current: '$accent@0.3', minInnings: 9, teamW: 120 } }
  };

  function px(n) { return (Number(n) || 0) + 'px'; }

  function placeWrap(wrap, el) {
    var s = wrap.style;
    s.left = px(el.x); s.top = px(el.y); s.width = px(el.w); s.height = px(el.h);
    s.zIndex = el.z || 0;
  }

  function boxStyle(node, st, ctx, theme) {
    var bg = st.background ? fmt(st.background, ctx).replace(/\$(\w+)/g, function (_, k) { return (theme && theme[k]) || ''; }) : color(st.fill, ctx, theme);
    node.style.background = bg || 'transparent';
    node.style.borderRadius = st.radius ? (typeof st.radius === 'number' ? px(st.radius) : st.radius) : '';
    node.style.border = st.borderW ? px(st.borderW) + ' solid ' + (color(st.borderColor, ctx, theme) || '#fff') : '';
    node.style.boxShadow = st.shadow ? (st.shadow === true ? '0 8px 24px rgba(0,0,0,.45)' : st.shadow) : '';
    node.style.backdropFilter = st.blur ? 'blur(' + st.blur + 'px)' : '';
    node.style.webkitBackdropFilter = node.style.backdropFilter;
    var t = [];
    if (st.skew) t.push('skewX(' + st.skew + 'deg)');
    if (st.rotate) t.push('rotate(' + st.rotate + 'deg)');
    node.style.transform = t.join(' ');
    if (st.cut) {
      var c = st.cut;
      node.style.clipPath = 'polygon(' + c + 'px 0, 100% 0, calc(100% - ' + c + 'px) 100%, 0 100%)';
    } else node.style.clipPath = '';
  }

  function textStyle(node, st, theme, ctx) {
    var s = node.style;
    s.color = color(st.color || '$text', ctx, theme);
    s.fontFamily = font(st.font, theme);
    s.fontSize = px(st.size || 32);
    s.fontWeight = st.weight || 700;
    s.fontStyle = st.italic ? 'italic' : '';
    s.letterSpacing = st.tracking ? (st.tracking + 'px') : '';
    s.textTransform = st.upper ? 'uppercase' : '';
    s.textShadow = st.textShadow ? (st.textShadow === true ? '0 2px 6px rgba(0,0,0,.6)' : st.textShadow) : '';
    s.lineHeight = st.lineH || 1.05;
    s.writingMode = st.vertical ? 'vertical-rl' : '';
    // Outlined type: textStroke "2px #fff" (pair with color "transparent" for hollow letters)
    s.webkitTextStroke = st.textStroke ? fmt(String(st.textStroke), ctx).replace(/\$([a-zA-Z0-9]+)/g, function (_, k) { return (theme && theme[k]) || ''; }) : '';
  }

  function parseTarget(t) {
    var m = String(t || '').trim().match(/^(\d{1,2})(?::(\d{2}))?\s*([ap])?\.?m?\.?$/i);
    if (!m) return null;
    var h = +m[1], mi = +(m[2] || 0), ap = (m[3] || '').toLowerCase();
    if (ap === 'p' && h < 12) h += 12;
    if (ap === 'a' && h === 12) h = 0;
    var d = new Date(); d.setHours(h, mi, 0, 0);
    return d.getTime();
  }
  function clockText(ms) {
    var neg = ms < 0; ms = Math.abs(ms);
    var t = Math.floor(ms / 1000), h = Math.floor(t / 3600), m = Math.floor((t % 3600) / 60), sec = t % 60;
    return (neg ? '-' : '') + (h ? h + ':' + (m < 10 ? '0' : '') + m : m) + ':' + (sec < 10 ? '0' : '') + sec;
  }
  function tickClock(inner) {
    var c = inner._clock; if (!c) return;
    var now = Date.now(), txt;
    if (c.mode === 'game') {
      // Game / shot / penalty clock from the scoring panel: ms left at server time "at", counting down while running.
      var g = c.g || {}, srv = now + ((root.GFX && root.GFX.serverOffset) || 0);
      var ms = Math.max(0, (Number(g.ms) || 0) - (g.running && g.at ? Math.max(0, srv - g.at) : 0));
      txt = (c.secs ? (ms < 10000 && c.tenths ? (Math.floor(ms / 100) / 10).toFixed(1) : String(Math.ceil(ms / 1000)))
                    : (ms < 60000 && c.tenths ? (Math.floor(ms / 100) / 10).toFixed(1) : clockText(Math.ceil(ms / 1000) * 1000)));
      if (inner.textContent !== txt) inner.textContent = txt;
      return;
    }
    if (c.mode === 'up') txt = c.since ? clockText(now - c.since) : '0:00';
    else if (c.mode === 'dur') { var left = (c.since || now) + c.dur * 60000 - now; txt = left <= 0 && c.done ? c.done : clockText(Math.max(0, left)); }
    else { var tg = parseTarget(c.target); var l2 = tg == null ? 0 : tg - now; txt = tg == null ? '' : (l2 <= 0 && c.done ? c.done : clockText(Math.max(0, l2))); }
    if (inner.textContent !== txt) inner.textContent = txt;
  }
  function tickCarousel(inner) {
    var c = inner._car; if (!c || !c.n) return;
    var idx = Math.floor(Date.now() / (c.iv * 1000)) % c.n;
    if (inner._carIdx === idx) return;
    inner._carIdx = idx;
    Array.prototype.forEach.call(inner.children, function (ch, i) { ch.style.opacity = i === idx ? '1' : '0'; });
  }
  if (typeof setInterval === 'function' && typeof document !== 'undefined') {
    setInterval(function () {
      Array.prototype.forEach.call(document.querySelectorAll('.gx-clock'), tickClock);
      Array.prototype.forEach.call(document.querySelectorAll('.gx-carousel'), tickCarousel);
    }, 250);
  }

  var RENDER = {
    box: function (inner, el, ctx, theme) {
      var bst = el.style || {};
      boxStyle(inner, bst, ctx, theme);
      // pct: bar length as a percentage of the box (poll results). "{podcast.o1.pct}"
      if (bst.pct != null) {
        var pv = Math.max(0, Math.min(100, parseFloat(fmt(String(bst.pct), ctx)) || 0));
        inner.style.right = (100 - pv) + '%';
        inner.style.transition = 'right .7s cubic-bezier(.16,1,.3,1)';
      } else { inner.style.right = ''; inner.style.transition = ''; }
      // holes: see-through windows "x,y,w,h; ..." in the box's own pixels (remote guest frames)
      if (bst.holes) {
        var d = 'M0 0H' + el.w + 'V' + el.h + 'H0Z';
        String(bst.holes).split(';').forEach(function (h) {
          var q = h.split(',').map(Number);
          if (q.length === 4 && q.every(isFinite)) d += ' M' + q[0] + ' ' + q[1] + 'H' + (q[0] + q[2]) + 'V' + (q[1] + q[3]) + 'H' + q[0] + 'Z';
        });
        inner.style.clipPath = 'path(evenodd, "' + d + '")';
      }
      return 'box:' + inner.style.cssText;
    },

    text: function (inner, el, ctx, theme) {
      var st = el.style || {};
      var txt = fmt(el.text, ctx).replace(/\\n/g, '\n');
      var letters = ((el.anim || {})['in'] || {}).type === 'letters';
      var sig = txt + '|' + letters + '|' + JSON.stringify(st);
      if (inner._sig === sig) return sig;
      inner.innerHTML = '';
      var span = document.createElement('span');
      span.className = 'gx-txt';
      if (letters) {
        // One span per character so the "letters" animation can stagger them.
        txt.split('').forEach(function (ch) {
          if (ch === '\n') { span.appendChild(document.createElement('br')); return; }
          var c = document.createElement('span');
          c.className = 'gx-ch';
          c.textContent = ch === ' ' ? ' ' : ch;
          span.appendChild(c);
        });
      } else span.textContent = txt;
      if (st.wrap && !st.fit) {
        // Wrapped text as a full-width block: older OBS browser builds can collapse an
        // inline-block flex item with pre-line text to nothing.
        span.style.display = 'block';
        span.style.width = '100%';
        span.style.textAlign = st.align || 'left';
      }
      inner.appendChild(span);
      var s = inner.style;
      s.display = 'flex';
      s.justifyContent = { left: 'flex-start', center: 'center', right: 'flex-end' }[st.align || 'left'];
      s.alignItems = { top: 'flex-start', center: 'center', bottom: 'flex-end' }[st.valign || 'center'];
      s.padding = '0 ' + px(st.padX || 0);
      s.boxSizing = 'border-box';
      s.overflow = 'hidden';
      s.whiteSpace = st.wrap ? 'pre-line' : 'pre';
      s.textAlign = st.align || 'left';
      s.background = color(st.fill, ctx, theme) || '';
      textStyle(inner, st, theme, ctx);
      inner._fit = !!st.fit;
      inner._size = st.size || 32;
      return sig;
    },

    image: function (inner, el, ctx, theme) {
      var st = el.style || {};
      var src = fmt(el.src, ctx);
      var sig = src + '|' + JSON.stringify(st);
      if (inner._sig === sig) return sig;
      inner.innerHTML = '';
      if (src) {
        var img = document.createElement('img');
        img.src = src;
        img.style.cssText = 'width:100%;height:100%;display:block;object-fit:' + (st.fit || 'cover') + ';object-position:' + (st.focus || 'center top');
        img.onerror = function () { img.style.visibility = 'hidden'; };
        inner.appendChild(img);
      }
      inner.style.borderRadius = st.radius ? px(st.radius) : '';
      inner.style.overflow = 'hidden';
      inner.style.background = color(st.fill, ctx, theme) || '';
      // Soft edge so a player cutout or photo melts into a card.
      var mf = { left: 'to right', right: 'to left', top: 'to bottom', bottom: 'to top' }[st.maskFade];
      var m = mf ? 'linear-gradient(' + mf + ', transparent 0%, #000 ' + (st.maskSize || 35) + '%)' : '';
      inner.style.webkitMaskImage = m;
      inner.style.maskImage = m;
      inner.style.filter = st.grayscale ? 'grayscale(1)' : '';
      return sig;
    },

    video: function (inner, el, ctx, theme) {
      var st = el.style || {};
      var src = fmt(el.src, ctx);
      var sig = src + '|' + JSON.stringify(st) + '|' + !!el.loop;
      if (inner._sig === sig) return sig;
      inner.innerHTML = '';
      if (src) {
        var v = document.createElement('video');
        v.src = src;
        v.muted = !el.sound;
        v.loop = !!el.loop;
        v.playsInline = true;
        v.preload = 'auto';
        v.style.cssText = 'width:100%;height:100%;display:block;object-fit:' + (st.fit || 'cover');
        inner.appendChild(v);
      }
      inner.style.borderRadius = st.radius ? px(st.radius) : '';
      inner.style.overflow = 'hidden';
      return sig;
    },

    bases: function (inner, el, ctx, theme) {
      var st = el.style || {};
      var b = get(ctx, el.bind || 'bases') || {};
      var on = color(st.on || '$accent', ctx, theme), off = color(st.off, ctx, theme) || 'transparent';
      var stroke = color(st.stroke, ctx, theme) || 'none', sw = st.strokeW || 0;
      var tight = st.layout === 'tight';
      var sig = [b['1'], b['2'], b['3'], on, off, stroke, sw, st.layout].join('|');
      if (inner._sig === sig) return sig;
      var r = tight ? 22 : 19;
      function d(cx, cy, filled, n) {
        return '<polygon data-base="' + n + '" points="' + cx + ',' + (cy - r) + ' ' + (cx + r) + ',' + cy + ' ' + cx + ',' + (cy + r) + ' ' + (cx - r) + ',' + cy +
          '" fill="' + (filled ? on : off) + '" stroke="' + stroke + '" stroke-width="' + sw + '" stroke-linejoin="round"/>';
      }
      // "tight": the three bags nest edge to edge, as on most current network bugs.
      inner.innerHTML = '<svg viewBox="0 0 120 80" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">' +
        (tight ? d(60, 25, b['2'], 2) + d(85, 50, b['1'], 1) + d(35, 50, b['3'], 3)
               : d(60, 22, b['2'], 2) + d(88, 50, b['1'], 1) + d(32, 50, b['3'], 3)) + '</svg>';
      return sig;
    },

    // Strike zone (catcher's view): the zone split in nine, the plate, and each pitch of the at-bat numbered and coloured by
    // result. Rows {x, z, n, cls}: x -1..1 = plate edges, z 0..1 = bottom to top of the zone.
    zone: function (inner, el, ctx, theme) {
      var st = el.style || {};
      var rows = get(ctx, el.bind || 'ops.pitchRows') || [];
      if (!Array.isArray(rows)) rows = [];
      var cz = { ball: color(st.ball || '#2FB463', ctx, theme), strike: color(st.strike || '#E5484D', ctx, theme), inplay: color(st.inplay || '#3D8BFD', ctx, theme) };
      var line = color(st.line || '#FFFFFF@0.85', ctx, theme), fill = color(st.fill || '#FFFFFF@0.06', ctx, theme), txtc = color(st.text || '#FFFFFF', ctx, theme);
      var sig = 'zone|' + JSON.stringify(rows) + JSON.stringify(st) + line + fill;
      if (inner._sig === sig) return sig;
      // 300 x 360 canvas: the zone is 160 wide (plate edges) and 180 tall, centred
      var X0 = 70, X1 = 230, Z0 = 250, Z1 = 70, R = st.r || 15;
      var h = '<svg viewBox="0 0 300 360" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" style="overflow:visible">';
      h += '<rect x="' + X0 + '" y="' + Z1 + '" width="' + (X1 - X0) + '" height="' + (Z0 - Z1) + '" fill="' + fill + '" stroke="' + line + '" stroke-width="3"/>';
      for (var i = 1; i < 3; i++) {
        var gx = X0 + (X1 - X0) * i / 3, gz = Z1 + (Z0 - Z1) * i / 3;
        h += '<line x1="' + gx + '" y1="' + Z1 + '" x2="' + gx + '" y2="' + Z0 + '" stroke="' + line + '" stroke-opacity=".35" stroke-width="1.5"/>';
        h += '<line x1="' + X0 + '" y1="' + gz + '" x2="' + X1 + '" y2="' + gz + '" stroke="' + line + '" stroke-opacity=".35" stroke-width="1.5"/>';
      }
      h += '<polygon points="' + X0 + ',318 ' + X1 + ',318 ' + X1 + ',330 150,346 ' + X0 + ',330" fill="' + line + '" fill-opacity=".9"/>';
      rows.forEach(function (r) {
        var x = parseFloat(r.x), z = parseFloat(r.z);
        if (isNaN(x) || isNaN(z)) return;
        var cx = 150 + Math.max(-1.9, Math.min(1.9, x)) * (X1 - X0) / 2, cy = Z0 - Math.max(-0.9, Math.min(1.8, z)) * (Z0 - Z1);
        h += '<circle cx="' + cx.toFixed(1) + '" cy="' + cy.toFixed(1) + '" r="' + R + '" fill="' + (cz[r.cls] || cz.strike) + '" stroke="#000" stroke-opacity=".45" stroke-width="2"/>' +
          '<text x="' + cx.toFixed(1) + '" y="' + (cy + R * 0.36).toFixed(1) + '" text-anchor="middle" font-size="' + Math.round(R * 1.05) + '" font-weight="800" fill="' + txtc +
          '" font-family="' + esc(font(st.font || '$font2', theme)) + '">' + esc(String(r.n || '')) + '</text>';
      });
      inner.innerHTML = h + '</svg>';
      return sig;
    },

    // Spray chart: the field from home plate (fair lines, infield and an outfield arc) with each ball in play.
    // Points {d, f, k}: d = direction in degrees (negative toward left field), f = distance in feet, k = 1B / 2B / 3B / HR / OUT.
    spray: function (inner, el, ctx, theme) {
      var st = el.style || {};
      var pts = get(ctx, el.bind || 'batter.tm.spray') || [];
      if (!Array.isArray(pts)) pts = [];
      var grass = color(st.grass || '#1F6B3A@0.55', ctx, theme), dirt = color(st.dirt || '#B5835A@0.55', ctx, theme), line = color(st.line || '#FFFFFF@0.85', ctx, theme);
      var cz = { '1B': color(st.single || '#FFFFFF', ctx, theme), '2B': color(st.double || '#3D8BFD', ctx, theme), '3B': color(st.triple || '#B57CFF', ctx, theme),
        HR: color(st.hr || '$accent', ctx, theme), OUT: color(st.out || '#000000@0.45', ctx, theme) };
      var sig = 'spray|' + JSON.stringify(pts) + JSON.stringify(st) + grass + dirt;
      if (inner._sig === sig) return sig;
      // 400 x 330 canvas, home plate at (200, 320); 1 px = 1.05 ft
      var HX = 200, HY = 320, S = 0.72, M = 420 * S;
      function pt(d, f) { var a = d * Math.PI / 180; return [HX + Math.sin(a) * f * S, HY - Math.cos(a) * f * S]; }
      var l = pt(-45, 330), r = pt(45, 330), arc = pt(-45, 400), arc2 = pt(45, 400);
      var h = '<svg viewBox="0 0 400 330" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">';
      h += '<path d="M' + HX + ',' + HY + ' L' + arc[0].toFixed(1) + ',' + arc[1].toFixed(1) + ' A' + (400 * S) + ',' + (400 * S) + ' 0 0 1 ' + arc2[0].toFixed(1) + ',' + arc2[1].toFixed(1) + ' Z" fill="' + grass + '" stroke="' + line + '" stroke-width="2"/>';
      var i1 = pt(-45, 95), i2 = pt(45, 95), i3 = pt(0, 135);
      h += '<path d="M' + HX + ',' + HY + ' L' + i1[0].toFixed(1) + ',' + i1[1].toFixed(1) + ' Q' + i3[0].toFixed(1) + ',' + (i3[1] - 30).toFixed(1) + ' ' + i2[0].toFixed(1) + ',' + i2[1].toFixed(1) + ' Z" fill="' + dirt + '"/>';
      h += '<line x1="' + HX + '" y1="' + HY + '" x2="' + l[0].toFixed(1) + '" y2="' + l[1].toFixed(1) + '" stroke="' + line + '" stroke-width="2"/>' +
           '<line x1="' + HX + '" y1="' + HY + '" x2="' + r[0].toFixed(1) + '" y2="' + r[1].toFixed(1) + '" stroke="' + line + '" stroke-width="2"/>';
      pts.forEach(function (p2) {
        var d = parseFloat(p2.d), f = parseFloat(p2.f);
        if (isNaN(d) || isNaN(f)) return;
        var q = pt(Math.max(-60, Math.min(60, d)), Math.min(470, Math.max(0, f)));
        h += '<circle cx="' + q[0].toFixed(1) + '" cy="' + q[1].toFixed(1) + '" r="' + (p2.k === 'OUT' ? 4 : 6) + '" fill="' + (cz[p2.k] || cz.OUT) + '" stroke="#000" stroke-opacity=".5" stroke-width="1.2"/>';
      });
      inner.innerHTML = h + '</svg>';
      return sig;
    },

    dots: function (inner, el, ctx, theme) {
      var st = el.style || {};
      var val = parseInt(get(ctx, el.bind || 'outs'), 10) || 0;
      var total = st.total || 2;
      var on = color(st.on || '$accent', ctx, theme), off = color(st.off, ctx, theme) || 'transparent';
      var sig = [val, total, on, off, st.size, st.gap, st.shape, st.align, st.dir, st.border].join('|');
      if (inner._sig === sig) return sig;
      var html = '';
      for (var i = 0; i < total; i++) {
        html += '<i style="display:block;width:' + px(st.size || 16) + ';height:' + px(st.size || 16) + ';border-radius:' +
          (st.shape === 'square' ? '2px' : '50%') + ';background:' + (i < val ? on : off) +
          (st.border ? ';box-shadow:inset 0 0 0 2px ' + color(st.border, ctx, theme) : '') + '"></i>';
      }
      inner.innerHTML = html;
      var s = inner.style;
      s.display = 'flex';
      s.flexDirection = st.dir === 'col' ? 'column' : 'row';
      s.gap = px(st.gap || 8);
      s.alignItems = 'center';
      s.justifyContent = { left: 'flex-start', center: 'center', right: 'flex-end' }[st.align || 'center'];
      return sig;
    },

    table: function (inner, el, ctx, theme) {
      var st = el.style || {};
      var rows = get(ctx, el.bind) || [];
      if (!Array.isArray(rows)) rows = [];
      rows = rows.slice(0, st.maxRows || 12);
      var cols = el.columns || [];
      var tw = cols.reduce(function (a, c) { return a + (Number(c.w) || 1); }, 0) || 1;
      var parts = [];
      function cell(c, content, isHead, rctx, row) {
        var cx = rctx || ctx;
        var fillV = c.fill, colorV = c.color;
        if (row && c.fillIf && row[c.fillIf]) fillV = c.fillOn || fillV;
        if (row && c.colorIf && row[c.colorIf]) colorV = c.colorOn || colorV;
        var w = ((Number(c.w) || 1) / tw * 100).toFixed(3) + '%';
        if (c.image && !isHead) {
          return '<div class="gx-cell gx-imgcell" style="flex:0 0 ' + w + ';justify-content:' + ({ left: 'flex-start', center: 'center', right: 'flex-end' }[c.align || 'center']) +
            (fillV ? ';background:' + color(fillV, cx, theme) + ';align-self:stretch' : '') + '">' +
            (content ? '<img src="' + esc(content) + '" style="max-height:' + (c.imgH || 80) + '%;max-width:100%;object-fit:contain" onerror="this.style.display=\'none\'">' : '') + '</div>';
        }
        return '<div class="gx-cell" style="flex:0 0 ' + w + ';justify-content:' +
          ({ left: 'flex-start', center: 'center', right: 'flex-end' }[c.align || 'left']) +
          (colorV && !isHead ? ';color:' + color(colorV, cx, theme) : '') +
          (c.weight && !isHead ? ';font-weight:' + c.weight : '') +
          (c.size && !isHead ? ';font-size:' + px(c.size) : '') +
          (fillV && !isHead ? ';background:' + color(fillV, cx, theme) + ';align-self:stretch' : '') +
          (c.padX != null ? ';padding:0 ' + px(c.padX) : '') + '">' + esc(content) + '</div>';
      }
      if (st.header) {
        parts.push('<div class="gx-row gx-head" style="height:' + px(st.headerH || 40) + ';font-size:' + px(st.headerSize || 18) +
          (st.rowLine ? ';border-bottom:' + px(st.rowLineW || 1) + ' solid ' + color(st.rowLine, ctx, theme) : '') +
          ';color:' + color(st.headerColor || '$accent', ctx, theme) + ';background:' + (color(st.headerFill, ctx, theme) || 'transparent') +
          ';padding:0 ' + px(st.padX || 12) + '">' + cols.map(function (c) { return cell(c, fmt(c.label, ctx), true); }).join('') + '</div>');
      }
      rows.forEach(function (row, i) {
        var rctx = Object.assign({}, ctx, { row: row, i: i + 1 });
        var hl = st.highlight && row && row[st.highlight];
        var fill = hl ? color(st.highlightFill, ctx, theme) : color(i % 2 && st.altFill ? st.altFill : st.rowFill, ctx, theme);
        parts.push('<div class="gx-row" data-i="' + i + '" style="height:' + px(st.rowH || 56) + ';background:' + (fill || 'transparent') +
          (st.rowLine && i < rows.length - 1 ? ';border-bottom:' + px(st.rowLineW || 1) + ' solid ' + color(st.rowLine, ctx, theme) : '') +
          (st.radius ? ';border-radius:' + px(st.radius) : '') +
          ';margin-top:' + px(i || st.header ? (st.gap || 0) : 0) + ';padding:0 ' + px(st.padX || 12) + '">' +
          cols.map(function (c) {
            var f = c.field || '';
            var v = f.indexOf('{') >= 0 ? fmt(f, rctx) : get(row, f);
            if (c.filter && FILTERS[c.filter]) v = FILTERS[c.filter](v);
            return cell(c, blank(v) ? '' : v, false, rctx, row);
          }).join('') + '</div>');
      });
      var html = parts.join('');
      var sig = html + JSON.stringify(st);
      if (inner._sig === sig) return sig;
      inner.innerHTML = html;
      inner.style.display = 'flex';
      inner.style.flexDirection = 'column';
      inner.style.overflow = 'hidden';
      textStyle(inner, st, theme, ctx);
      return sig;
    },

    // QR code from text / a link (e.g. "{show.qrUrl}"), drawn as SVG. Uses the bundled qrcode-generator (MIT).
    qr: function (inner, el, ctx, theme) {
      var st = el.style || {};
      var text = String(fmt(el.text || '{show.qrUrl}', ctx) || '').trim();
      var sig = 'qr|' + text + '|' + JSON.stringify(st);
      if (inner._sig === sig) return sig;
      inner.className = 'gx-inner gx-qr';
      if (!text || !window.qrcode) { inner.innerHTML = ''; return sig; }
      var q;
      try { q = window.qrcode(0, st.ecc || 'M'); q.addData(unescape(encodeURIComponent(text))); q.make(); } catch (e) { inner.innerHTML = ''; return sig; }
      var n = q.getModuleCount(), qz = st.quiet == null ? 2 : st.quiet, size = n + qz * 2, d = '';
      for (var r = 0; r < n; r++) for (var c = 0; c < n; c++) if (q.isDark(r, c)) d += 'M' + (c + qz) + ' ' + (r + qz) + 'h1v1h-1z';
      inner.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + size + ' ' + size + '" width="100%" height="100%" shape-rendering="crispEdges" preserveAspectRatio="xMidYMid meet">' +
        '<rect width="' + size + '" height="' + size + '" fill="' + (color(st.bg || '#FFFFFF', ctx, theme) || '#FFFFFF') + '"/>' +
        '<path d="' + d + '" fill="' + (color(st.color || '#000000', ctx, theme) || '#000') + '"/></svg>';
      return sig;
    },

    // Clock: counts down to a time of day (mode "to", target "18:35" or "6:35 PM"), up from a moment (mode "up", since = ms),
    // or down over a duration from a moment (mode "dur", since + dur minutes). A shared timer repaints it every quarter second.
    clock: function (inner, el, ctx, theme) {
      var st = el.style || {};
      var spec = { mode: String(fmt(el.mode || 'to', ctx) || 'to'), target: String(fmt(el.target || '', ctx) || ''),
        since: Number(fmt(el.since || '', ctx)) || 0, dur: Number(fmt(el.dur || '', ctx)) || 0, done: String(fmt(el.done || '', ctx) || '') };
      if (spec.mode === 'game') { spec.g = get(ctx, el.src || 'sp.clock') || {}; spec.tenths = !!st.tenths; spec.secs = !!st.secs; }
      var sig = 'clock|' + JSON.stringify(spec) + JSON.stringify(st);
      if (inner._sig !== sig) {
        inner.className = 'gx-inner gx-clock';
        var s = inner.style;
        s.display = 'flex';
        s.justifyContent = { left: 'flex-start', center: 'center', right: 'flex-end' }[st.align || 'center'];
        s.alignItems = 'center';
        s.whiteSpace = 'pre';
        s.fontVariantNumeric = 'tabular-nums';
        textStyle(inner, st, theme, ctx);
      }
      inner._clock = spec;
      tickClock(inner);
      return sig;
    },

    // Carousel: items [{src, caption}] crossfade every "interval" seconds (images or .mp4 / .webm clips), caption along the bottom.
    carousel: function (inner, el, ctx, theme) {
      var st = el.style || {};
      var items = get(ctx, el.bind || 'preset.items') || [];
      if (!Array.isArray(items)) items = [];
      items = items.filter(function (it) { return it && it.src; });
      var iv = Math.max(2, Number(fmt(el.interval || '6', ctx)) || 6);
      var sig = 'car|' + iv + '|' + JSON.stringify(items) + JSON.stringify(st);
      if (inner._sig === sig) return sig;
      inner.className = 'gx-inner gx-carousel';
      inner.style.position = 'relative';
      inner.style.overflow = 'hidden';
      inner.style.borderRadius = st.radius ? px(st.radius) : '';
      var html = '';
      items.forEach(function (it, i) {
        var src = String(it.src).replace(/"/g, '&quot;');
        var media = /\.(mp4|webm|mov)(\?|$)/i.test(src)
          ? '<video src="' + src + '" muted autoplay loop playsinline style="width:100%;height:100%;object-fit:' + (st.fit || 'cover') + '"></video>'
          : '<img src="' + src + '" style="width:100%;height:100%;object-fit:' + (st.fit || 'cover') + '">';
        var cap = it.caption ? '<div class="gx-car-cap" style="position:absolute;left:0;right:0;bottom:0;padding:' + px(st.capPad || 18) + ' ' + px(st.capPad ? st.capPad * 1.4 : 26) +
          ';background:' + (color(st.capFill || '#000000@0.6', ctx, theme)) + ';color:' + (color(st.capColor || '$text', ctx, theme)) + ';font-size:' + px(st.capSize || 40) +
          ';font-weight:' + (st.capWeight || 800) + ';font-family:' + (font(st.font, theme) || 'inherit') + '">' + String(it.caption).replace(/</g, '&lt;') + '</div>' : '';
        html += '<div class="gx-car-item" style="position:absolute;inset:0;opacity:0;transition:opacity ' + (st.fade || 700) + 'ms ease">' + media + cap + '</div>';
      });
      inner.innerHTML = html;
      inner._car = { iv: iv, n: items.length };
      tickCarousel(inner);
      return sig;
    },

    // Waving flag: draws an image (default the US flag) on a canvas in 1-px columns, each lifted on a travelling
    // wave (still at the hoist, most motion at the fly) with light / shade bands. style: amp (px), speed, waves, shade.
    flag: function (inner, el, ctx, theme) {
      var st = el.style || {};
      var src = String(fmt(el.src || '/art/us-flag.svg', ctx) || '/art/us-flag.svg');
      var sig = 'flag|' + src + '|' + el.w + 'x' + el.h + '|' + JSON.stringify(st);
      if (inner._sig === sig) return sig;
      inner.className = 'gx-inner gx-flag';
      inner.innerHTML = '';
      var cv = document.createElement('canvas');
      var dpr = 1, W = Math.max(2, Math.round(el.w * dpr)), H = Math.max(2, Math.round(el.h * dpr));
      cv.width = W; cv.height = H;
      cv.style.width = '100%'; cv.style.height = '100%'; cv.style.display = 'block';
      inner.appendChild(cv);
      var g = cv.getContext('2d');
      var amp = (st.amp == null ? 0.05 : st.amp) * H, pad = amp + 2, fh = H - 2 * pad;
      var speed = st.speed || 1, waves = st.waves || 1.6, shade = st.shade == null ? 0.22 : st.shade;
      var img = new Image();
      var off = document.createElement('canvas'); off.width = W; off.height = Math.max(2, Math.round(fh));
      img.onload = function () { off.getContext('2d').drawImage(img, 0, 0, off.width, off.height); };
      img.src = src;
      var start = performance.now();
      function frame(now) {
        if (!inner.isConnected || inner._flagSrc !== sig) return;
        var t = (now - start) / 1000 * speed * 2 * Math.PI / 2.6;
        g.clearRect(0, 0, W, H);
        for (var x = 0; x < W; x++) {
          var f = x / W, a = amp * (0.15 + 0.85 * f);
          var ph = f * waves * 2 * Math.PI - t;
          var y = pad + a * Math.sin(ph);
          g.drawImage(off, x, 0, 1, off.height, x, y, 1, off.height);
          var l = Math.cos(ph) * shade * (0.3 + 0.7 * f);
          g.fillStyle = l > 0 ? 'rgba(255,255,255,' + (l * 0.7).toFixed(3) + ')' : 'rgba(0,0,0,' + (-l).toFixed(3) + ')';
          g.fillRect(x, y, 1, off.height);
        }
        requestAnimationFrame(frame);
      }
      inner._flagSrc = sig;
      requestAnimationFrame(frame);
      return sig;
    },

    // Continuous ticker: items [{head, text}] scroll right to left at style.speed px/s; content is doubled for a seamless loop.
    ticker: function (inner, el, ctx, theme) {
      var st = el.style || {};
      var items = get(ctx, el.bind || 'ticker.items') || [];
      if (!Array.isArray(items)) items = [];
      var headBg = color(st.headFill || '$accent', ctx, theme), headC = color(st.headColor || '$primary', ctx, theme);
      var sep = st.sep == null ? '\u25C6' : st.sep;
      var html = items.map(function (it) {
        if (it.head) return '<span class="gx-tk-head" style="background:' + headBg + ';color:' + headC + '">' + esc(it.text || '') + '</span>';
        return '<span class="gx-tk-item">' + (it.live ? '<i class="gx-tk-live"></i>' : '') + esc(it.text || '') + '</span><span class="gx-tk-sep" style="color:' +
          color(st.sepColor || '$accent', ctx, theme) + '">' + esc(sep) + '</span>';
      }).join('');
      var sig = html + JSON.stringify(st) + '|' + get(ctx, 'ticker.speed');
      if (inner._sig === sig) return sig;
      var prev = inner._tk, frac = 0;
      if (prev && prev.effect && prev.effect.getComputedTiming) {
        var tm = prev.effect.getComputedTiming();
        frac = tm.progress || 0;
        prev.cancel();
      }
      inner.innerHTML = items.length ? '<div class="gx-tk-strip">' + html + html + '</div>' : '';
      inner.className = 'gx-inner gx-ticker';
      textStyle(inner, st, theme, ctx);
      inner._tkSpeed = Number(get(ctx, 'ticker.speed')) || Number(st.speed) || 110;
      startTicker(inner, frac);
      return sig;
    },

    field: function (inner, el, ctx, theme) {
      var st = el.style || {};
      var def = get(ctx, el.bind || 'team.defense') || {};
      var spots = { CF: [50, 19], LF: [21, 33], RF: [79, 33], SS: [38, 50], '2B': [62, 50], '3B': [27, 66], '1B': [73, 66], P: [50, 69], C: [50, 92] };
      var nameField = st.nameField || 'last';
      var labels = Object.keys(spots).map(function (pos, i) {
        var p = def[pos] || {};
        var nm = p[nameField] || p.name || '';
        var xy = spots[pos];
        return '<div class="gx-fanchor" style="left:' + xy[0] + '%;top:' + xy[1] + '%"><div class="gx-row gx-fpos" data-i="' + i + '" style="background:' +
          color(st.labelFill, ctx, theme) + ';font-size:' + px(st.size || 24) + '">' +
          '<b style="color:' + color(st.posColor || '$accent', ctx, theme) + '">' + pos + '</b>' +
          '<span style="color:' + color(st.nameColor || '$text', ctx, theme) + '">' + esc(String(nm).toUpperCase()) + '</span></div></div>';
      }).join('');
      var svg = '<svg class="gx-fsvg" viewBox="0 0 1000 800" preserveAspectRatio="none">' +
        '<path d="M500 770 L40 320 Q500 -150 960 320 Z" fill="' + color(st.grass, ctx, theme) + '" stroke="' + color(st.line, ctx, theme) + '" stroke-width="3"/>' +
        '<path d="M500 770 L700 560 Q500 250 300 560 Z" fill="' + color(st.dirt, ctx, theme) + '"/>' +
        '<path d="M500 740 L660 580 L500 420 L340 580 Z" fill="' + color(st.grass, ctx, theme) + '" stroke="' + color(st.line, ctx, theme) + '" stroke-width="3"/>' +
        '<circle cx="500" cy="580" r="34" fill="' + color(st.dirt, ctx, theme) + '"/>' +
        ['500,740', '660,580', '500,420', '340,580'].map(function (pt) {
          var a = pt.split(','); return '<rect x="' + (a[0] - 10) + '" y="' + (a[1] - 10) + '" width="20" height="20" transform="rotate(45 ' + a[0] + ' ' + a[1] + ')" fill="' + color(st.line, ctx, theme) + '"/>';
        }).join('') + '</svg>';
      var html = svg + labels;
      var sig = html;
      if (inner._sig === sig) return sig;
      inner.innerHTML = html;
      textStyle(inner, st, theme, ctx);
      return sig;
    },

    linescore: function (inner, el, ctx, theme) {
      var st = el.style || {};
      var ls = ctx.linescore || { away: [], home: [] };
      var n = Math.max(st.minInnings || 9, ls.innings || 0, (ls.away || []).length);
      var cur = ctx.inning, live = ctx.isLive;
      var teamW = st.teamW || 120, statCols = 3;
      var cellW = 'calc((100% - ' + teamW + 'px) / ' + (n + statCols) + ')';
      var head = '<div class="gx-lc" style="flex:0 0 ' + teamW + 'px"></div>';
      for (var i = 1; i <= n; i++) {
        head += '<div class="gx-lc" style="flex:0 0 ' + cellW + (live && i === cur ? ';background:' + color(st.current, ctx, theme) : '') + '">' + i + '</div>';
      }
      ['R', 'H', 'E'].forEach(function (k) { head += '<div class="gx-lc gx-tot" style="flex:0 0 ' + cellW + ';background:' + color(st.totalFill, ctx, theme) + '">' + k + '</div>'; });
      var html = '<div class="gx-row gx-head" style="color:' + color(st.headColor || '$accent', ctx, theme) + ';font-size:' + px(st.headSize || 18) + '">' + head + '</div>';
      ['away', 'home'].forEach(function (side, ri) {
        var t = ctx[side] || {};
        var cells = '<div class="gx-lc gx-team" style="flex:0 0 ' + teamW + 'px"><i style="background:' + (t.color || '#888') + '"></i>' + esc(t.abbr || '') + '</div>';
        for (var j = 0; j < n; j++) {
          var v = (ls[side] || [])[j];
          cells += '<div class="gx-lc" style="flex:0 0 ' + cellW + (live && j + 1 === cur ? ';background:' + color(st.current, ctx, theme) : '') + '">' + (blank(v) ? '' : esc(v)) + '</div>';
        }
        [t.runs, t.hits, t.errors].forEach(function (v) { cells += '<div class="gx-lc gx-tot" style="flex:0 0 ' + cellW + ';background:' + color(st.totalFill, ctx, theme) + '">' + (blank(v) ? 0 : esc(v)) + '</div>'; });
        html += '<div class="gx-row" data-i="' + ri + '" style="background:' + color(st.rowFill, ctx, theme) + ';font-size:' + px(st.size || 30) + '">' + cells + '</div>';
      });
      var sig = html;
      if (inner._sig === sig) return sig;
      inner.innerHTML = html;
      inner.className = 'gx-inner gx-linescore';
      textStyle(inner, Object.assign({}, st, { size: st.size || 30 }), theme, ctx);
      return sig;
    }
  };

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; });
  }

  function buildElement(el, ctx, theme) {
    var wrap = document.createElement('div');
    wrap.className = 'gx-el gx-' + el.type;
    wrap.dataset.id = el.id;
    var inner = document.createElement('div');
    inner.className = 'gx-inner';
    wrap.appendChild(inner);
    wrap._inner = inner;
    paint(wrap, el, ctx, theme);
    return wrap;
  }

  // Returns true when the visible content changed.
  function paint(wrap, el, ctx, theme) {
    wrap._el = el;
    // growWith: {bind, base, per, max}. Height follows the number of rows (e.g. teams in a division).
    var gw = el.growWith;
    if (gw && gw.bind) {
      var rows = get(ctx, gw.bind);
      var n = Array.isArray(rows) ? Math.min(rows.length, gw.max || 99) : 0;
      placeWrap(wrap, Object.assign({}, el, { h: Math.max(gw.min || 0, (gw.base || 0) + n * (gw.per || 0)) }));
    } else placeWrap(wrap, el);
    var inner = wrap._inner;
    var vis = cond(el.showIf, ctx);
    wrap.style.display = vis ? '' : 'none';
    inner.style.opacity = el.opacity == null ? '' : el.opacity;
    inner.style.transform = '';
    var fn = RENDER[el.type];
    if (!fn) return false;
    var before = inner._sig;
    var sig = fn(inner, el, ctx, theme);
    var tf = el.type === 'box' ? inner.style.transform : '';
    if (el.rotate) tf += ' rotate(' + el.rotate + 'deg)';
    // 3D panel tilt, for virtual-set style boards angled toward the center.
    if (el.tiltY || el.tiltX) tf = 'perspective(' + (el.persp || 1600) + 'px) rotateY(' + (el.tiltY || 0) + 'deg) rotateX(' + (el.tiltX || 0) + 'deg) ' + tf;
    inner.style.transform = tf.trim();
    inner._sig = sig;
    if (inner._fit) fitText(inner);
    return before !== undefined && before !== sig;
  }

  function fitText(inner) {
    var span = inner.firstChild;
    if (!span || !inner.isConnected) return;
    var size = inner._size;
    inner.style.fontSize = px(size);
    var guard = 0;
    while (span.offsetWidth > inner.clientWidth - 2 && size > 8 && guard++ < 60) {
      size -= 1;
      inner.style.fontSize = px(size);
    }
  }

  // ----------------------------------------------------------- animation
  var EASE = {
    out: 'cubic-bezier(.16,1,.3,1)',
    'in': 'cubic-bezier(.7,0,.84,0)',
    'in-out': 'cubic-bezier(.65,0,.35,1)',
    back: 'cubic-bezier(.34,1.56,.64,1)',
    snap: 'cubic-bezier(.9,0,.1,1)',
    linear: 'linear'
  };
  var ANIM_TYPES = ['none', 'fade', 'slide-left', 'slide-right', 'slide-up', 'slide-down', 'wipe-right', 'wipe-left', 'wipe-down',
    'wipe-up', 'wipe-center', 'diamond', 'iris', 'reveal-up', 'reveal-down', 'reveal-left', 'reveal-right', 'letters',
    'grow-x', 'grow-y', 'scale', 'zoom-out', 'pop', 'flip-x', 'flip-y', 'blur', 'skew-in'];
  var LOOP_TYPES = ['none', 'drift', 'pulse', 'shine', 'breathe', 'spin', 'scroll-x', 'scroll-y', 'chase'];
  // Reveal types move the layer's content inside its own box, so the box acts as a mask.
  var REVEAL = { 'reveal-up': 'translateY(105%)', 'reveal-down': 'translateY(-105%)', 'reveal-left': 'translateX(105%)', 'reveal-right': 'translateX(-105%)' };

  function frames(type, dist) {
    var d = dist == null ? 60 : dist;
    var T = {
      none: [{ opacity: 1 }, { opacity: 1 }],
      fade: [{ opacity: 0 }, { opacity: 1 }],
      'slide-left': [{ transform: 'translateX(' + d + 'px)', opacity: 0 }, { transform: 'translateX(0)', opacity: 1 }],
      'slide-right': [{ transform: 'translateX(' + (-d) + 'px)', opacity: 0 }, { transform: 'translateX(0)', opacity: 1 }],
      'slide-up': [{ transform: 'translateY(' + d + 'px)', opacity: 0 }, { transform: 'translateY(0)', opacity: 1 }],
      'slide-down': [{ transform: 'translateY(' + (-d) + 'px)', opacity: 0 }, { transform: 'translateY(0)', opacity: 1 }],
      'wipe-right': [{ clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0% 0 0)' }],
      'wipe-left': [{ clipPath: 'inset(0 0 0 100%)' }, { clipPath: 'inset(0 0 0 0%)' }],
      'wipe-down': [{ clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0% 0)' }],
      'wipe-up': [{ clipPath: 'inset(100% 0 0 0)' }, { clipPath: 'inset(0% 0 0 0)' }],
      'wipe-center': [{ clipPath: 'inset(0 50% 0 50%)' }, { clipPath: 'inset(0 0% 0 0%)' }],
      diamond: [{ clipPath: 'polygon(50% 50%, 50% 50%, 50% 50%, 50% 50%)' }, { clipPath: 'polygon(50% -50%, 150% 50%, 50% 150%, -50% 50%)' }],
      iris: [{ clipPath: 'circle(0% at 50% 50%)' }, { clipPath: 'circle(75% at 50% 50%)' }],
      'zoom-out': [{ transform: 'scale(1.18)', opacity: 0 }, { transform: 'scale(1)', opacity: 1 }],
      letters: [{ opacity: 1 }, { opacity: 1 }],
      'grow-x': [{ transform: 'scaleX(0)' }, { transform: 'scaleX(1)' }],
      'grow-y': [{ transform: 'scaleY(0)' }, { transform: 'scaleY(1)' }],
      scale: [{ transform: 'scale(.7)', opacity: 0 }, { transform: 'scale(1)', opacity: 1 }],
      pop: [{ transform: 'scale(.3)', opacity: 0 }, { transform: 'scale(1.08)', opacity: 1, offset: 0.7 }, { transform: 'scale(1)', opacity: 1 }],
      'flip-x': [{ transform: 'perspective(900px) rotateX(-90deg)', opacity: 0 }, { transform: 'perspective(900px) rotateX(0deg)', opacity: 1 }],
      'flip-y': [{ transform: 'perspective(900px) rotateY(90deg)', opacity: 0 }, { transform: 'perspective(900px) rotateY(0deg)', opacity: 1 }],
      blur: [{ filter: 'blur(16px)', opacity: 0 }, { filter: 'blur(0px)', opacity: 1 }],
      'skew-in': [{ transform: 'translateX(' + (-d) + 'px) skewX(-20deg)', opacity: 0 }, { transform: 'translateX(0) skewX(0deg)', opacity: 1 }]
    };
    return (T[type] || T.fade).map(function (f) { return Object.assign({}, f); });
  }

  function reverseFrames(fr) {
    var out = fr.slice().reverse().map(function (f) { return Object.assign({}, f); });
    out.forEach(function (f) { if (f.offset != null) f.offset = 1 - f.offset; });
    return out;
  }

  var ANIM_IN_DEFAULT = { type: 'fade', dur: 400, delay: 0, ease: 'out', dist: 60 };
  var ANIM_OUT_DEFAULT = { type: 'auto', dur: 300, delay: 0, ease: 'in' };

  function specs(el) {
    var a = el.anim || {};
    var i = Object.assign({}, ANIM_IN_DEFAULT, a['in'] || {});
    var o = Object.assign({}, ANIM_OUT_DEFAULT, a.out || {});
    return { 'in': i, out: o, rows: a.rows || null, change: a.change || 'none',
      hold: Number(a.hold) || 0, loop: a.loop && a.loop.type && a.loop.type !== 'none' ? a.loop : null };
  }

  function originFor(type, origin) {
    if (origin) return origin;
    if (type === 'grow-x') return 'left center';
    if (type === 'grow-y') return 'center bottom';
    return 'center center';
  }

  // Plays one element in or out. Returns end time in ms.
  // opts.delay overrides the spec delay (used by "hold" exits).
  function animateEl(wrap, phase, speed, opts) {
    var el = wrap._el;
    var sp = specs(el);
    var spec = sp[phase];
    speed = speed || 1;
    opts = opts || {};
    var type = spec.type;
    if (phase === 'out' && (type === 'auto' || !type)) type = sp['in'].type;
    var dist = spec.dist == null ? sp['in'].dist : spec.dist;
    var dur = (spec.dur || 0) / speed;
    var delay = (opts.delay != null ? opts.delay : (spec.delay || 0)) / speed;
    var easing = EASE[spec.ease] || spec.ease || 'ease';
    var anims = [];
    var end = delay + dur;
    wrap.style.transformOrigin = originFor(type, spec.origin || sp['in'].origin);
    wrap.style.overflow = REVEAL[type] ? 'hidden' : '';

    if (REVEAL[type]) {
      // Content slides inside the layer's box; the box clips it.
      wrap.style.overflow = 'hidden';
      var rf = [{ transform: REVEAL[type] }, { transform: 'translate(0,0)' }];
      if (phase === 'out') rf.reverse();
      anims.push(wrap._inner.animate(rf, { duration: Math.max(1, dur), delay: delay, easing: easing, fill: 'both' }));
      anims.push(wrap.animate([{ opacity: 1 }, { opacity: 1 }], { duration: Math.max(1, dur), delay: delay, fill: 'both' }));
    } else if (type === 'letters') {
      var chars = wrap.querySelectorAll('.gx-ch');
      var stg = (spec.stagger == null ? 35 : spec.stagger) / speed;
      var lf = [{ transform: 'translateY(' + (dist == null ? 40 : dist) + 'px)', opacity: 0, filter: 'blur(6px)' }, { transform: 'translateY(0)', opacity: 1, filter: 'blur(0)' }];
      var n = chars.length;
      chars.forEach(function (c, i) {
        var idx = phase === 'out' ? n - 1 - i : i;
        var f = phase === 'out' ? reverseFrames(lf) : lf;
        anims.push(c.animate(f, { duration: Math.max(1, dur), delay: delay + idx * stg, easing: easing, fill: 'both' }));
      });
      end = delay + Math.max(0, n - 1) * stg + dur;
      anims.push(wrap.animate([{ opacity: 1 }, { opacity: 1 }], { duration: Math.max(1, end - delay), delay: delay, fill: 'both' }));
    } else {
      var fr = frames(type, dist);
      if (phase === 'out') fr = reverseFrames(fr);
      anims.push(wrap.animate(fr, { duration: Math.max(1, dur), delay: delay, easing: easing, fill: 'both' }));
    }
    if (sp.rows && phase === 'in') {
      var rs = sp.rows;
      var rowEls = wrap.querySelectorAll('.gx-row:not(.gx-head)');
      rowEls.forEach(function (r, idx) {
        var rd = delay + (rs.delay || 0) / speed + idx * (rs.stagger || 60) / speed;
        var rdur = (rs.dur || 300) / speed;
        r.style.transformOrigin = originFor(rs.type, rs.origin);
        anims.push(r.animate(frames(rs.type || 'slide-left', rs.dist == null ? 40 : rs.dist),
          { duration: rdur, delay: rd, easing: EASE[rs.ease || 'out'], fill: 'both' }));
        end = Math.max(end, rd + rdur);
      });
    }
    wrap._anims = anims;
    return { end: end, anims: anims };
  }

  function cancelAnims(wrap) {
    (wrap._anims || []).forEach(function (a) { try { a.cancel(); } catch (e) {} });
    try { wrap.getAnimations({ subtree: true }).forEach(function (a) { a.cancel(); }); } catch (e) {}
    clearTimeout(wrap._holdT);
    clearTimeout(wrap._loopT);
    clearTimeout(wrap._settleT);
    wrap._anims = [];
  }

  // (Re)start a ticker crawl; graphics cancel every animation inside them when they animate in.
  function startTicker(inner, frac) {
    var strip = inner && inner.firstChild;
    if (!strip || !strip.animate) return;
    var half = strip.scrollWidth / 2 || 1;
    var dur = Math.max(4000, half / (inner._tkSpeed || 110) * 1000);
    if (inner._tk) { try { inner._tk.cancel(); } catch (e) {} }
    inner._tk = strip.animate([{ transform: 'translateX(0)' }, { transform: 'translateX(' + (-half) + 'px)' }], { duration: dur, iterations: Infinity, easing: 'linear' });
    try { inner._tk.currentTime = (frac || 0) * dur; } catch (e) {}
  }

  function startLoop(wrap, speed) {
    if (wrap._el && wrap._el.type === 'ticker') startTicker(wrap._inner, 0);
    var lp = specs(wrap._el).loop;
    if (!lp) return;
    var t = wrap._inner, d = Math.max(200, (lp.dur || 4000) / (speed || 1)), a = lp.amount == null ? null : Number(lp.amount);
    var o = { duration: d, iterations: Infinity, direction: 'alternate', easing: 'ease-in-out' };
    var f;
    switch (lp.type) {
      case 'drift': f = [{ transform: 'translateX(' + -(a == null ? 20 : a) + 'px)' }, { transform: 'translateX(' + (a == null ? 20 : a) + 'px)' }]; break;
      case 'breathe': f = [{ transform: 'scale(1)' }, { transform: 'scale(' + (1 + (a == null ? 0.04 : a)) + ')' }]; break;
      case 'pulse': f = [{ opacity: 1 }, { opacity: a == null ? 0.5 : a }]; break;
      case 'spin': f = [{ transform: 'rotate(0deg)' }, { transform: 'rotate(360deg)' }]; o.direction = 'normal'; o.easing = 'linear'; break;
      // Continuous scroll by "amount" px (one repeat of tiled text), seamless when the text repeats.
      case 'scroll-x': f = [{ transform: 'translateX(0)' }, { transform: 'translateX(' + (a == null ? -400 : a) + 'px)' }]; o.direction = lp.pingpong ? 'alternate' : 'normal'; o.easing = lp.pingpong ? 'ease-in-out' : 'linear'; break;
      case 'scroll-y': f = [{ transform: 'translateY(0)' }, { transform: 'translateY(' + (a == null ? -400 : a) + 'px)' }]; o.direction = lp.pingpong ? 'alternate' : 'normal'; o.easing = lp.pingpong ? 'ease-in-out' : 'linear'; break;
      // Marquee bulbs: quick on / off flicker
      case 'chase': f = [{ opacity: 1 }, { opacity: 1, offset: 0.45 }, { opacity: a == null ? 0.25 : a, offset: 0.5 }, { opacity: a == null ? 0.25 : a }]; o.direction = 'normal'; o.easing = 'steps(1, end)'; break;
      case 'shine':
        t.style.backgroundSize = '250% 100%';
        f = [{ backgroundPosition: '100% 50%' }, { backgroundPosition: '-150% 50%' }]; o.direction = 'normal'; o.easing = 'linear'; break;
      default: return;
    }
    wrap._anims.push(t.animate(f, o));
  }

  function playVideo(wrap, on) {
    var v = wrap.querySelector('video');
    if (!v) return;
    if (on) { try { v.currentTime = 0; } catch (e) {} var p = v.play(); if (p && p.catch) p.catch(function () { v.muted = true; v.play(); }); }
    else v.pause();
  }

  function changeFx(wrap) {
    var sp = specs(wrap._el);
    var inner = wrap._inner;
    if (sp.change === 'pop') inner.animate([{ transform: 'scale(1.25)' }, { transform: 'scale(1)' }], { duration: 450, easing: EASE.back });
    else if (sp.change === 'flash') inner.animate([{ filter: 'brightness(2.2)' }, { filter: 'brightness(1)' }], { duration: 600, easing: 'ease-out' });
    else if (sp.change === 'fade') inner.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 500, easing: 'ease-out' });
    else if (sp.change === 'roll') inner.animate([{ transform: 'translateY(-60%)', opacity: 0 }, { transform: 'translateY(0)', opacity: 1 }], { duration: 380, easing: EASE.out });
  }

  // -------------------------------------------------------------- graphic
  function Graphic(container, gid, def, theme) {
    this.gid = gid;
    this.def = def;
    this.theme = theme || {};
    this.root = document.createElement('div');
    this.root.className = 'gx-graphic';
    this.root.dataset.g = gid;
    this.root.style.visibility = 'hidden';
    container.appendChild(this.root);
    this.nodes = [];
    this.state = 'out';
    this.token = 0;
  }

  Graphic.prototype.build = function (ctx) {
    this.root.innerHTML = '';
    var self = this;
    var els = (this.def.elements || []).slice();
    this.nodes = els.map(function (el) {
      var w = buildElement(el, ctx, self.theme);
      self.root.appendChild(w);
      return w;
    });
    // Re-run fit after attachment so measurements are real.
    this.nodes.forEach(function (w) { if (w._inner._fit) fitText(w._inner); });
    this.ctx = ctx;
  };

  Graphic.prototype.update = function (ctx) {
    var self = this;
    this.ctx = ctx;
    this.nodes.forEach(function (w) {
      var changed = paint(w, w._el, ctx, self.theme);
      if (changed && self.state === 'in') changeFx(w);
    });
  };

  Graphic.prototype.show = function (instant, speed) {
    var self = this;
    var tok = ++this.token;
    this.root.style.visibility = 'visible';
    this.state = 'in';
    this.nodes.forEach(function (w) {
      cancelAnims(w);
      w._holdDone = false;
      var sp = specs(w._el);
      playVideo(w, true);
      if (instant) {
        // Instant show (editor, reconnect). Layers with a hold stay visible so they can be edited.
        startLoop(w, speed);
        return;
      }
      var r = animateEl(w, 'in', speed);
      // Settle: once the in-animation is over, drop it so the layer rests in its natural (fully shown)
      // state. Some OBS browser builds stall or lose finished animations, which left text parked
      // off-screen on later takes; a timer still runs there, so this always lands.
      var inAnims = r.anims.slice();
      w._settleT = setTimeout(function () {
        if (self.token !== tok) return;
        inAnims.forEach(function (a) { try { a.cancel(); } catch (e) {} });
        w._anims = (w._anims || []).filter(function (a) { return inAnims.indexOf(a) < 0; });
      }, r.end + 120);
      if (w._el && w._el.type === 'ticker') startTicker(w._inner, 0);
      if (sp.loop) w._loopT = setTimeout(function () { if (self.token === tok) startLoop(w, speed); }, r.end);
      if (sp.hold > 0) {
        // Leave on its own after the hold, while the rest of the graphic stays up.
        w._holdT = setTimeout(function () {
          if (self.token !== tok) return;
          w._holdDone = true;
          w._anims = (w._anims || []).concat(animateEl(w, 'out', speed, { delay: 0 }).anims);
        }, r.end + sp.hold / (speed || 1));
      }
    });
    return tok;
  };

  Graphic.prototype.hide = function (instant, speed) {
    var self = this;
    var tok = ++this.token;
    this.state = 'out';
    if (instant) {
      this.nodes.forEach(function (w) { cancelAnims(w); w._holdDone = false; playVideo(w, false); });
      this.root.style.visibility = 'hidden';
      return Promise.resolve();
    }
    var ps = [], longest = 0;
    this.nodes.forEach(function (w) {
      // Layers that already left on a hold stay gone (keep their finished out state).
      if (w._holdDone) { clearTimeout(w._loopT); return; }
      cancelAnims(w);
      var r = animateEl(w, 'out', speed);
      longest = Math.max(longest, r.end);
      r.anims.forEach(function (a) { ps.push(a.finished.catch(function () {})); });
    });
    function done() {
      if (self.token === tok && self.state === 'out' && self.root.style.visibility !== 'hidden') {
        self.root.style.visibility = 'hidden';
        self.nodes.forEach(function (w) { cancelAnims(w); playVideo(w, false); });
      }
    }
    // Same safety as show(): finish the take-out on a timer even if the animations never report back.
    var safety = new Promise(function (res) { setTimeout(res, longest + 200); });
    return Promise.race([Promise.all(ps), safety]).then(done);
  };

  Graphic.prototype.destroy = function () {
    this.root.remove();
  };

  // Total in/out timeline length, useful for the editor.
  function timeline(def) {
    var tin = 0, tout = 0;
    (def.elements || []).forEach(function (el) {
      var sp = specs(el);
      var e = (sp['in'].delay || 0) + (sp['in'].dur || 0);
      if (sp['in'].type === 'letters') e += 12 * (sp['in'].stagger == null ? 35 : sp['in'].stagger);
      if (sp.rows) e += (sp.rows.delay || 0) + 8 * (sp.rows.stagger || 60) + (sp.rows.dur || 300);
      if (sp.hold) e += sp.hold + (sp.out.dur || 0);
      tin = Math.max(tin, e);
      if (!sp.hold) tout = Math.max(tout, (sp.out.delay || 0) + (sp.out.dur || 0));
    });
    return { 'in': tin, out: tout };
  }

  // ------------------------------------------------------- live connection
  // Live updates. WebSocket first: OBS shares one Chromium profile across all browser sources,
  // and Chromium allows only 6 HTTP connections per host, so a held-open EventSource per overlay
  // starves the rest. Falls back to EventSource only where WebSocket is unavailable.
  function connect(onMsg, onState, query) {
    var qs = query ? '?' + query : '';
    var sock, retry = 500, closed = false;
    function handle(data) {
      try { onMsg(JSON.parse(data)); } catch (err) { console.error(err); }
    }
    function again() {
      if (onState) onState(false);
      if (closed) return;
      setTimeout(open, retry);
      retry = Math.min(retry * 2, 8000);
    }
    function open() {
      if (typeof WebSocket === 'undefined') {
        sock = new EventSource('/events' + qs);
        sock.onopen = function () { retry = 500; if (onState) onState(true); };
        sock.onmessage = function (e) { handle(e.data); };
        sock.onerror = function () { sock.close(); again(); };
        return;
      }
      sock = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws' + qs);
      sock.onopen = function () { retry = 500; if (onState) onState(true); };
      sock.onmessage = function (e) { handle(e.data); };
      sock.onclose = again;
      sock.onerror = function () { try { sock.close(); } catch (e) {} };
    }
    open();
    return { close: function () { closed = true; try { sock.close(); } catch (e) {} } };
  }

  // Fonts uploaded to media/fonts become @font-face families named after the file.
  // Fonts installed on the computer can be used directly by name (OBS runs on the same machine).
  var fontSig = '';
  function loadFonts(list, onReady) {
    list = list || [];
    var sig = JSON.stringify(list);
    if (sig === fontSig) return;
    fontSig = sig;
    var el = document.getElementById('gx-fonts');
    if (!el) { el = document.createElement('style'); el.id = 'gx-fonts'; document.head.appendChild(el); }
    el.textContent = list.map(function (f) {
      return "@font-face{font-family:'" + String(f.family).replace(/'/g, '') + "';src:url('" + f.url + "') format('" + f.format + "');font-display:block;}";
    }).join('\n');
    if (document.fonts && onReady) {
      list.forEach(function (f) { try { document.fonts.load("40px '" + f.family + "'"); } catch (e) {} });
      document.fonts.ready.then(onReady);
    }
  }

  function api(path, body) {
    return fetch(path, body === undefined ? {} : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      .then(function (r) { return r.json(); });
  }

  // Data paths offered by the editor's binding picker.
  var BINDINGS = [
    ['Game', [['away.abbr', 'Away abbr'], ['away.name', 'Away name'], ['away.runs', 'Away runs'], ['away.hits', 'Away hits'], ['away.errors', 'Away errors'],
      ['away.record', 'Away record'], ['away.color', 'Away color'], ['away.logo', 'Away logo'],
      ['home.abbr', 'Home abbr'], ['home.name', 'Home name'], ['home.runs', 'Home runs'], ['home.hits', 'Home hits'], ['home.errors', 'Home errors'],
      ['home.record', 'Home record'], ['home.color', 'Home color'], ['home.logo', 'Home logo'],
      ['inning', 'Inning number'], ['inningOrd', 'Inning ordinal (7th)'], ['halfShort', 'TOP / BOT / MID / END'], ['arrow', 'Inning arrow'],
      ['inningLabel', 'Inning label (TOP 7)'], ['halfLong', 'TOP / BOTTOM / MIDDLE / END'], ['halfKey', 'Half-inning sponsor key (T3, B3, TX)'], ['nextHalfLabel', 'Next half (BOTTOM 3rd)'], ['statusText', 'Status text'], ['balls', 'Balls'], ['strikes', 'Strikes'], ['outs', 'Outs'],
      ['count', 'Count (2-1)'], ['batting.abbr', 'Batting team abbr'], ['batting.color', 'Batting team color'],
      ['fielding.abbr', 'Fielding team abbr'], ['fielding.color', 'Fielding team color']]],
    ['Batter', [['batter.name', 'Full name'], ['batter.first', 'First'], ['batter.last', 'Last'], ['batter.number', 'Number'],
      ['batter.pos', 'Position'], ['batter.bats', 'Bats'], ['batter.photo', 'Photo URL'], ['batter.today.line', 'Today line (2-3, HR)'],
      ['batter.season.avg|avg', 'AVG'], ['batter.season.obp|avg', 'OBP'], ['batter.season.slg|avg', 'SLG'], ['batter.season.ops|avg', 'OPS'],
      ['batter.season.hr', 'HR'], ['batter.season.rbi', 'RBI']]],
    ['Pitcher', [['pitcher.name', 'Full name'], ['pitcher.last', 'Last'], ['pitcher.number', 'Number'], ['pitcher.throws|hand', 'Throws (LHP/RHP)'],
      ['pitcher.photo', 'Photo URL'], ['pitcher.today.pc', 'Pitch count'], ['pitcher.today.st', 'Strikes'], ['pitcher.today.ip', 'IP today'],
      ['pitcher.today.h', 'H today'], ['pitcher.today.er', 'ER today'], ['pitcher.today.bb', 'BB today'], ['pitcher.today.k', 'K today'],
      ['pitcher.today.line', 'Today line'], ['pitcher.season.era|era', 'ERA'], ['pitcher.season.whip|era', 'WHIP'], ['pitcher.season.w', 'Wins'],
      ['pitcher.season.l', 'Losses'], ['pitcher.season.k', 'Season K']]],
    ['Selected team (side picker)', [['team.name', 'Team name'], ['team.abbr', 'Team abbr'], ['team.color', 'Team color'], ['team.color2', 'Team color 2'],
      ['team.logo', 'Team logo'], ['team.record', 'Record'], ['team.runs', 'Runs'], ['team.sp.name', 'Starting pitcher'], ['team.sp.era|era', 'SP ERA'],
      ['opp.abbr', 'Opponent abbr'], ['opp.name', 'Opponent name']]],
    ['Standings (group picked in the control panel)', [['standingsGroup.name', 'Group name'], ['standingsGroup.teams', 'Teams (rows)'], ['row.rank', 'Rank (row)'], ['row.record', 'W-L (row)'], ['row.w', 'Wins (row)'], ['row.l', 'Losses (row)'], ['row.pct', 'PCT (row)'], ['row.gb', 'GB (row)'], ['row.streak', 'Streak (row)'], ['row.logo', 'Logo URL (row)']]],
    ['Custom text', [['custom.line1', 'Line 1'], ['custom.line2', 'Line 2'], ['custom.line3', 'Line 3']]],
    ['Sponsor (from the graphic\'s sponsor slot)', [['sponsor.logo', 'Sponsor logo URL'], ['sponsor.name', 'Sponsor name'], ['sponsor.label', 'Sponsor label (Presented by)']]],
    ['Season / branding', [['seasonYear', 'Season year'], ['brand.logo', 'Brand logo (theme logo, else home logo)'], ['brand.name', 'Brand name (theme name, else home name)'], ['theme.logo', 'Brand logo URL'], ['theme.openerVideo', 'Opener video URL'],
      ['batter.first', 'Batter first'], ['pitcher.first', 'Pitcher first'], ['pitcher.season.g', 'P games'], ['pitcher.season.gs', 'P starts'],
      ['pitcher.season.h', 'P hits allowed'], ['pitcher.season.oppAvg|avg', 'P opp. AVG'], ['batter.season.g', 'B games'], ['batter.season.h', 'B hits'],
      ['batter.season.sb', 'B steals'], ['team.dueUp.0.name', 'Due up #1 name'], ['team.dueUp.0.photo', 'Due up #1 photo']]],
    ['Table rows', [['team.lineup', 'Lineup (rows)'], ['team.pitchers', 'Pitchers used (rows)'], ['team.dueUp', 'Due up (rows)'], ['team.defense', 'Defense (field)'],
      ['pitcher.card', 'Pitcher season card (label/value rows)'], ['batter.card', 'Batter season card (label/value rows)'], ['row.sponsor.logo', 'Row sponsor logo (lineup spot)']]],
    ['Row fields (inside tables)', [['row.label', 'Card label'], ['row.value', 'Card value'], ['row.slot', 'Slot'], ['row.name', 'Name'], ['row.last', 'Last'], ['row.number', 'Number'], ['row.pos', 'Position'],
      ['row.avg|avg', 'AVG'], ['row.ops|avg', 'OPS'], ['row.hr', 'HR'], ['row.rbi', 'RBI'], ['row.today', 'Today line'], ['row.ip', 'IP'],
      ['row.h', 'H'], ['row.r', 'R'], ['row.er', 'ER'], ['row.bb', 'BB'], ['row.k', 'K'], ['row.pc', 'Pitches'], ['row.era|era', 'ERA']]]
  ];

  root.GFX = {
    STAGE_W: STAGE_W, STAGE_H: STAGE_H, get: get, fmt: fmt, cond: cond, color: color, FILTERS: FILTERS,
    makeCtx: makeCtx, sponsorFor: sponsorFor, buildElement: buildElement, paint: paint, fitText: fitText, Graphic: Graphic,
    frames: frames, animateEl: animateEl, cancelAnims: cancelAnims, specs: specs, timeline: timeline,
    EASE: EASE, ANIM_TYPES: ANIM_TYPES, LOOP_TYPES: LOOP_TYPES, ELEMENT_DEFAULTS: ELEMENT_DEFAULTS, BINDINGS: BINDINGS,
    connect: connect, api: api, esc: esc, loadFonts: loadFonts
  };
})(window);
