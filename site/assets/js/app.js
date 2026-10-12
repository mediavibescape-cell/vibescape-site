(function () {
  'use strict';
  document.documentElement.classList.add('js');
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var FINE = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var isMob = function () { return innerWidth <= 900; };
  var VS = window.VS || {};
  var hasG = typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined';
  if (hasG) gsap.registerPlugin(ScrollTrigger);
  if (hasG) gsap.set('#pt', { y: 0, yPercent: 100 });

  /* ---------- smooth scroll ---------- */
  var lenis = null;
  if (hasG && !RM && typeof Lenis !== 'undefined') {
    lenis = new Lenis({ lerp: 0.1, wheelMultiplier: 1, smoothWheel: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
    gsap.ticker.lagSmoothing(0);
  }
  function scrollTo(target, opts) {
    opts = opts || {};
    if (lenis) lenis.scrollTo(target, { offset: opts.offset || 0, immediate: !!opts.immediate, duration: opts.duration || 1.4 });
    else {
      var y = typeof target === 'number' ? target : (target.getBoundingClientRect().top + scrollY + (opts.offset || 0));
      window.scrollTo({ top: y, behavior: opts.immediate ? 'auto' : 'smooth' });
    }
  }
  function lockScroll(on) { if (lenis) { on ? lenis.stop() : lenis.start(); } document.documentElement.style.overflow = on ? 'hidden' : ''; }

  /* ---------- split text ---------- */
  $$('[data-split]').forEach(function (el) {
    var i = 0;
    var walk = function (node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (w) {
            if (!w) return;
            if (/^\s+$/.test(w)) { frag.appendChild(document.createTextNode(' ')); return; }
            var o = document.createElement('span'); o.className = 'w';
            var inn = document.createElement('span'); inn.className = 'wi'; inn.style.setProperty('--i', i++); inn.textContent = w;
            o.appendChild(inn); frag.appendChild(o);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1 && n.tagName !== 'BR' && n.tagName !== 'SUP') walk(n);
      });
    };
    walk(el);
  });
  $$('[data-words]').forEach(function (p) {
    p.innerHTML = p.textContent.trim().split(/\s+/).map(function (w) { return '<span class="sw">' + w + '</span>'; }).join(' ');
  });

  /* ---------- reveals ---------- */
  var armed = false;
  var rio = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); rio.unobserve(e.target); } });
  }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
  function arm(scope) {
    if (!armed) return;
    $$('[data-split]:not(.in),[data-fade]:not(.in),[data-clip]:not(.in)', scope).forEach(function (el) {
      if (el.hasAttribute('data-hero')) return;
      rio.observe(el);
    });
  }

  /* ---------- lazy autoplay videos ---------- */
  var vio = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      var v = e.target;
      if (e.isIntersecting) {
        if (!v.src && v.dataset.src) { v.src = v.dataset.src; }
        var p = v.play(); if (p && p.catch) p.catch(function () {});
      } else if (!v.paused) v.pause();
    });
  }, { rootMargin: '150px 0px' });
  function autoVids(scope) { $$('video[data-auto]', scope).forEach(function (v) { vio.observe(v); }); }

  /* ---------- loader ---------- */
  var ldr = $('#ldr'), bar = $('#ldrBar'), pct = $('#ldrPct'), msg = $('#ldrMsg');
  var p = 0, t0 = Date.now(), finished = false;
  var lines = ['Chai ban rahi hai', 'Logo chhota kar rahe hain', 'Client ko samjha rahe hain', 'Almost. Promise.'], li = 0;
  function setP(v) { p = v; if (bar) bar.style.transform = 'scaleX(' + v / 100 + ')'; if (pct) pct.textContent = Math.round(v) + '%'; }
  var iv = setInterval(function () { if (p < 92) setP(p + (92 - p) * 0.07 + 0.4); }, 70);
  var mv = setInterval(function () { li = (li + 1) % lines.length; if (msg) msg.textContent = lines[li]; }, 1100);
  function finishLoad() {
    if (finished) return; finished = true; clearInterval(iv); clearInterval(mv); setP(100); if (msg) msg.textContent = 'Aa gayi.';
    setTimeout(function () {
      if (hasG) gsap.to(ldr, { yPercent: -100, duration: 1, ease: 'expo.inOut', onComplete: function () { ldr.remove(); } });
      else ldr.remove();
      setTimeout(function () {
        armed = true;
        $$('.page.on [data-hero]').forEach(function (el) { el.classList.add('in'); });
        arm($('.page.on'));
      }, hasG ? 450 : 0);
    }, 260);
  }
  function goLoad() { setTimeout(finishLoad, Math.max(0, 900 - (Date.now() - t0))); }
  var fr = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
  Promise.race([fr, new Promise(function (r) { setTimeout(r, 700); })]).then(goLoad, goLoad);
  setTimeout(finishLoad, 2600);

  /* ---------- cursor + magnet ---------- */
  var cur = $('#cur');
  if (FINE && hasG && cur) {
    var cx = gsap.quickTo(cur, 'x', { duration: 0.35, ease: 'power3' }), cy = gsap.quickTo(cur, 'y', { duration: 0.35, ease: 'power3' });
    addEventListener('mousemove', function (e) { cx(e.clientX); cy(e.clientY); }, { passive: true });
    document.addEventListener('mouseover', function (e) {
      var t = e.target.closest('[data-cursor]');
      if (t) { cur.classList.add('big'); cur.firstElementChild.textContent = t.dataset.cursor; }
      else cur.classList.remove('big');
    });
    document.addEventListener('mouseleave', function () { cur.classList.remove('big'); });
    $$('[data-magnet]').forEach(function (b) {
      var mx = gsap.quickTo(b, 'x', { duration: 0.6, ease: 'elastic.out(1,.4)' }), my = gsap.quickTo(b, 'y', { duration: 0.6, ease: 'elastic.out(1,.4)' });
      b.addEventListener('mousemove', function (e) { var r = b.getBoundingClientRect(); mx((e.clientX - r.left - r.width / 2) * 0.28); my((e.clientY - r.top - r.height / 2) * 0.35); });
      b.addEventListener('mouseleave', function () { mx(0); my(0); });
    });
  }

  /* ---------- header hide on scroll ---------- */
  var hdr = $('#hdr'), lastY = 0;
  function onScrollHdr() {
    var y = scrollY;
    if (y > 240 && y > lastY + 4 && !mmOpen) hdr.classList.add('hide');
    else if (y < lastY - 4 || y < 240) hdr.classList.remove('hide');
    lastY = y;
  }
  addEventListener('scroll', onScrollHdr, { passive: true });

  /* ---------- mobile menu ---------- */
  var burger = $('#burger'), mm = $('#mm'), mmOpen = false;
  function setMenu(o) { mmOpen = o; burger.classList.toggle('x', o); mm.classList.toggle('open', o); burger.setAttribute('aria-expanded', o); lockScroll(o); if (o) hdr.classList.remove('hide'); }
  burger.addEventListener('click', function () { setMenu(!mmOpen); });

  /* ---------- lightbox ---------- */
  var lb = $('#lb'), lbv = $('#lbv');
  function openFilm(id) {
    var f = VS.films[id]; if (!f) return;
    lbv.poster = f.p; lbv.src = '/assets/videos/' + id + '.mp4';
    $('#lbb').textContent = f.b; $('#lbt').textContent = f.t;
    lb.classList.add('open'); lb.setAttribute('aria-hidden', 'false'); lockScroll(true);
    var reel = $('#reel'); if (reel && !reel.paused) { reel.pause(); reel.dataset.wasPlaying = '1'; }
    lbv.muted = false; var pr = lbv.play(); if (pr && pr.catch) pr.catch(function () { lbv.muted = true; lbv.play().catch(function () {}); });
  }
  function closeFilm() {
    lb.classList.remove('open'); lb.setAttribute('aria-hidden', 'true'); lbv.pause(); lbv.removeAttribute('src'); lbv.load(); lockScroll(false);
    var reel = $('#reel'); if (reel && reel.dataset.wasPlaying) { reel.play().catch(function () {}); delete reel.dataset.wasPlaying; }
  }
  $('#lbx').addEventListener('click', closeFilm);
  lb.addEventListener('click', function (e) { if (e.target === lb) closeFilm(); });

  /* ---------- deck viewer ---------- */
  var viewer = $('#viewer'), vpages = $('#vpages');
  var pio = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); pio.unobserve(e.target); } }); }, { root: viewer, threshold: 0.02 });
  function openDeck(key) {
    var pj = VS.projects[key]; if (!pj) return;
    var d = document.getElementById('deck-' + pj[2]);
    var pages = [VS.covers[pj[2]]].concat(d ? JSON.parse(d.textContent) : []);
    $('#vtitle').innerHTML = pj[0] + ' <span>' + pj[1] + '</span>';
    vpages.innerHTML = '';
    pages.forEach(function (src, i) { var im = new Image(); im.decoding = 'async'; if (i > 1) im.loading = 'lazy'; im.alt = pj[0] + ' page ' + (i + 1); im.src = src; vpages.appendChild(im); });
    viewer.scrollTop = 0; viewer.classList.add('open'); viewer.setAttribute('aria-hidden', 'false'); lockScroll(true);
    setTimeout(function () { $$('img', vpages).forEach(function (i) { pio.observe(i); }); }, 80);
  }
  function flipOpen(card) {
    var im = card.querySelector('img');
    if (!hasG || RM || !im) { openDeck(card.dataset.project); return; }
    var r = im.getBoundingClientRect(), c = im.cloneNode();
    c.removeAttribute('loading'); c.className = 'flip';
    c.style.cssText = 'left:' + r.left + 'px;top:' + r.top + 'px;width:' + r.width + 'px;height:' + r.height + 'px;border-radius:22px';
    document.body.appendChild(c);
    gsap.timeline()
      .to(c, { left: 0, top: 0, width: innerWidth, height: innerHeight, borderRadius: 0, duration: 0.75, ease: 'expo.inOut' })
      .add(function () { openDeck(card.dataset.project); viewer.classList.add('nowipe'); })
      .to(c, { opacity: 0, duration: 0.35, ease: 'power1.out', onComplete: function () { c.remove(); viewer.classList.remove('nowipe'); } }, '+=0.05');
  }
  function closeDeck() { viewer.classList.remove('open'); viewer.setAttribute('aria-hidden', 'true'); lockScroll(false); }
  $('#vclose').addEventListener('click', closeDeck);
  addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (lb.classList.contains('open')) closeFilm();
    else if (viewer.classList.contains('open')) closeDeck();
    else if (mmOpen) setMenu(false);
  });

  /* ---------- contact ---------- */
  document.addEventListener('click', function (e) {
    var ob = e.target.closest('.opts button');
    if (ob) { $$('button', ob.parentNode).forEach(function (x) { x.classList.toggle('sel', x === ob); }); }
  });
  var fsend = $('#fsend');
  if (fsend) fsend.addEventListener('click', function () {
    var pick = function (g) { var x = $('.opts[data-g="' + g + '"] .sel'); return x ? x.textContent : 'n/a'; };
    var v = function (id) { return ($('#' + id).value || '').trim() || 'n/a'; };
    var body = ['Service needed: ' + pick('need'), 'Name: ' + v('fn'), 'Email / WhatsApp: ' + v('fr'), 'Budget: ' + pick('budget'), '', 'The brief:', v('fbr')].join('\n');
    location.href = 'mailto:mediavibescape@gmail.com?subject=' + encodeURIComponent('New brief: ' + (v('fn') === 'n/a' ? 'Website enquiry' : v('fn'))) + '&body=' + encodeURIComponent(body);
    var o = fsend.innerHTML; fsend.textContent = 'Mil gaya. Email khul rahi hai.'; setTimeout(function () { fsend.innerHTML = o; }, 2600);
  });

  /* ---------- global click delegation ---------- */
  document.addEventListener('click', function (e) {
    var f = e.target.closest('[data-film]'); if (f) { e.preventDefault(); openFilm(f.dataset.film); return; }
    var pr = e.target.closest('[data-project]'); if (pr) { e.preventDefault(); flipOpen(pr); return; }
    var j = e.target.closest('[data-jump]'); if (j) { e.preventDefault(); var t = document.getElementById(j.dataset.jump); if (t) scrollTo(t, { offset: -150 }); return; }
    var a = e.target.closest('a[data-link]');
    if (a && !e.metaKey && !e.ctrlKey && !e.shiftKey) {
      e.preventDefault();
      if (viewer.classList.contains('open')) closeDeck();
      if (mmOpen) setMenu(false);
      go(a.getAttribute('href'), true);
    }
  });

  /* ======================================================
     PAGE INITS
     ====================================================== */
  var ctx = null, pageTimers = [];
  var INIT = {};

  INIT.home = function (pg) {
    var hero = $('#hero', pg), hf = $('#heroF', pg), reel = $('#reel', pg), ht = $('.hero-t', pg);
    // choose reel source once
    if (reel && !reel.src) {
      reel.src = innerWidth < 700 ? reel.dataset.msrc : reel.dataset.hsrc;
      reel.addEventListener('playing', function () { var im = hf.querySelector('img'); if (im) im.style.opacity = 0; }, { once: true });
      reel.play().catch(function () {});
      new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { if (!reel.dataset.wasPlaying && reel.paused) reel.play().catch(function () {}); } else reel.pause(); }); }, { threshold: 0.05 }).observe(hf);
    }
    var snd = $('#snd', pg);
    if (snd && !snd.dataset.b) {
      snd.dataset.b = 1;
      var tog = function (e) { if (e) e.stopPropagation(); reel.muted = !reel.muted; if (!reel.muted) reel.play().catch(function () {}); snd.classList.toggle('on', !reel.muted); snd.setAttribute('aria-pressed', !reel.muted); snd.querySelector('.sl').textContent = reel.muted ? 'Sound off' : 'Sound on'; };
      snd.addEventListener('click', tog); hf.addEventListener('click', function () { tog(); });
    }
    autoVids(pg);
    if (!hasG) return;

    var mmq = gsap.matchMedia();
    mmq.add({ desk: '(min-width: 901px)', mob: '(max-width: 900px)' }, function (c) {
      var desk = c.conditions.desk;

      /* HERO: reel window grows to full bleed */
      var base = function () {
        gsap.set(hf, { clearProps: 'width,height,right,bottom,borderRadius' });
        var hr = hero.getBoundingClientRect(), fr = hf.getBoundingClientRect();
        return { w: fr.width, h: fr.height, r: hr.right - fr.right, b: hr.bottom - fr.bottom };
      };
      var B = base();
      var onRI = function () { B = base(); };
      ScrollTrigger.addEventListener('refreshInit', onRI);
      var tl = gsap.timeline({ scrollTrigger: { trigger: hero, start: 'top top', end: '+=130%', pin: true, scrub: 0.8, invalidateOnRefresh: true } });
      tl.fromTo(hf, { width: function () { return B.w; }, height: function () { return B.h; }, right: function () { return B.r; }, bottom: function () { return B.b; }, borderRadius: 22 },
        { width: function () { return hero.offsetWidth; }, height: function () { return hero.offsetHeight; }, right: 0, bottom: 0, borderRadius: 0, ease: 'power2.inOut', duration: 1 }, 0)
        .to(ht, { yPercent: -18, opacity: 0, scale: 0.94, transformOrigin: '0 0', ease: 'power1.in', duration: 0.6 }, 0)
        .to('.hero-tag', { opacity: 0, duration: 0.2 }, 0)
        .to(hf.querySelector('.scrim'), { opacity: 1, duration: 0.3 }, 0.7)
        .fromTo(hf.querySelector('.fl'), { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.3 }, 0.75)
        .to({}, { duration: 0.25 });

      /* STATEMENT words */
      $$('[data-words]', pg).forEach(function (p) {
        gsap.to($$('.sw', p), { opacity: 1, stagger: 0.1, ease: 'none', scrollTrigger: { trigger: p, start: 'top 82%', end: 'bottom 50%', scrub: true } });
      });

      /* STORY */
      var story = $('#story', pg);
      var ch = $$('.ch', story), fin = $('.fin', story), sc = $$('.sc', story), rail = $$('.rail i', story);
      var s1 = sc[0], s2 = sc[1], s3 = sc[2], s4 = sc[3];
      var vid2 = $('video', s2), ordN = $('#ordN', story), roasN = $('#roasN', story), fOrd = $('#fOrd', story), scr = $('#cScr', story);
      var fmtK = function (n) { return n >= 1000 ? (n / 1000).toFixed(n >= 100000 ? 0 : 1).replace(/\.0$/, '') + 'k' : String(Math.round(n)); };
      var cnt = { lk: 3, cm: 0, vw: 212, likedExtra: 0 };
      var paintC = function () { $('#cLk', story).textContent = fmtK(cnt.lk + cnt.likedExtra); $('#cCm', story).textContent = fmtK(cnt.cm); $('#cVw', story).textContent = fmtK(cnt.vw); };
      gsap.set(ch, { autoAlpha: 0, y: 34 }); gsap.set(ch[0], { autoAlpha: 1, y: 0 }); gsap.set(fin, { autoAlpha: 0, y: 34 });
      gsap.set(sc, { autoAlpha: 0 }); gsap.set(s1, { autoAlpha: 1 });
      gsap.set($('.good', s1), { clipPath: 'inset(100% 0% 0% 0%)' }); gsap.set($$('.pouch', s1), { y: 120, opacity: 0 }); gsap.set($('.seal', s1), { scale: 0, rotate: -120 }); gsap.set([$('.gtag', s1), $('.sws', s1)], { y: 30, opacity: 0 }); gsap.set($('.af', s1), { autoAlpha: 0, y: 10 });
      gsap.set(scr, { '--x': '100%' }); gsap.set($$('.cb', s2), { autoAlpha: 0, x: 30 }); paintC();
      gsap.set($('.af', s3), { autoAlpha: 0, y: 10 });
      gsap.set($('.af', s2), { autoAlpha: 0, y: 10 });
      gsap.set($('.aft', s3), { autoAlpha: 0 });
      gsap.set($('.shop', s4), { clipPath: 'inset(0% 0% 100% 0%)' }); gsap.set($('.speed', s4), { autoAlpha: 0, scale: 0.6 });
      gsap.set($('.stamp', s4), { autoAlpha: 0, scale: 2.4, rotate: 8 });
      var ord = { v: 0 }, bst = { n: 1 }, bstN = $('#bstN', story), ads = $$('.ad', s3), fnl = $('.fnl', s3), budI = $('#bud', story);
      var perf = function (b, k) { k = k == null ? 1 : k; var sh = b / 100, ro = 5.6 * sh + 0.8 * (1 - sh), o = Math.round(ro * 200000 / 650);
        ordN.textContent = Math.round(o * k).toLocaleString('en-US'); fOrd.textContent = Math.round(o * k).toLocaleString('en-US'); roasN.textContent = (ro * k).toFixed(1) + 'x'; $('#budV', story).textContent = b + '%'; };
      perf(70, 0);
      if (!budI.dataset.b) { budI.dataset.b = 1;
        budI.addEventListener('input', function () { perf(+budI.value, 1); ads[2].classList.toggle('won', +budI.value >= 40); });
        var bq = ['Still 0 orders.', 'Uncle liked it. Still 0 orders.', 'Rs 500 more. Same 3 likes.', 'Maybe try the funnel?'], bqi = 0;
        $('#bst', story).addEventListener('click', function () { bst.n = Math.round(bst.n) + 1; bstN.textContent = '×' + bst.n; $('#bstQ', story).textContent = bq[bqi++ % bq.length]; });
        // drag the split line
        var drag = false, setX = function (e) { var r = scr.getBoundingClientRect(); var x = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)); scr.style.setProperty('--x', (x * 100).toFixed(1) + '%'); };
        scr.addEventListener('pointerdown', function (e) { if (e.target.closest('.hrt')) return; drag = true; scr.setPointerCapture(e.pointerId); setX(e); });
        scr.addEventListener('pointermove', function (e) { if (drag) setX(e); });
        scr.addEventListener('pointerup', function () { drag = false; }); scr.addEventListener('pointercancel', function () { drag = false; });
        var hrt = $('#cHrt', story);
        hrt.addEventListener('click', function () { cnt.likedExtra++; paintC(); hrt.classList.remove('pop'); void hrt.offsetWidth; hrt.classList.add('pop', 'on');
          var f = document.createElement('i'); f.className = 'fh'; f.style.left = (40 + Math.random() * 30) + '%'; scr.appendChild(f); setTimeout(function () { f.remove(); }, 1200); });
      }
      var swapCh = function (tl, a, b, at) {
        tl.to(a, { autoAlpha: 0, y: -24, duration: 0.25, ease: 'power2.in' }, at)
          .fromTo(b, { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: 'power3.out', immediateRender: false }, at + 0.32);
      };
      var swapSc = function (tl, a, b, at) {
        tl.to(a, { autoAlpha: 0, scale: 0.9, duration: 0.45, ease: 'power2.in' }, at)
          .fromTo(b, { autoAlpha: 0, scale: 1.08 }, { autoAlpha: 1, scale: 1, duration: 0.55, ease: 'power3.out' }, at + 0.3);
      };
      var st = gsap.timeline({ defaults: { ease: 'none' }, scrollTrigger: { trigger: story, start: 'top top', end: function () { return '+=' + innerHeight * (desk ? 5 : 4.4); }, pin: true, scrub: 0.7, anticipatePin: 1,
        onToggle: function (s) { if (vid2) { if (s.isActive) { if (!vid2.src) vid2.src = vid2.dataset.src; vid2.play().catch(function () {}); } else vid2.pause(); } } } });
      // chapter 1
      st.to(rail[0], { scaleX: 1, duration: 2 }, 0)
        .to($('.t1', s1), { y: -80, rotate: -28, autoAlpha: 0, duration: 0.6, ease: 'power2.in' }, 0.35)
        .to($('.burst', s1), { x: 160, rotate: 120, autoAlpha: 0, duration: 0.6, ease: 'power2.in' }, 0.4)
        .to($('.t2', s1), { y: 90, autoAlpha: 0, duration: 0.5, ease: 'power2.in' }, 0.45)
        .to($('.wa', s1), { x: -140, rotate: -20, autoAlpha: 0, duration: 0.5, ease: 'power2.in' }, 0.5)
        .to($('.good', s1), { clipPath: 'inset(0% 0% 0% 0%)', duration: 0.7, ease: 'power3.inOut' }, 0.75)
        .to($('.pouch:not(.alt)', s1), { y: 0, opacity: 1, duration: 0.7, ease: 'power3.out' }, 0.95)
        .to($('.pouch.alt', s1), { y: 0, opacity: 1, duration: 0.7, ease: 'power3.out' }, 1.1)
        .to($('.seal', s1), { scale: 1, rotate: 0, duration: 0.6, ease: 'back.out(1.8)' }, 1.3)
        .to($('.gtag', s1), { y: 0, opacity: 1, duration: 0.4 }, 1.35)
        .to($('.sws', s1), { y: 0, opacity: 1, duration: 0.4 }, 1.5)
        .to($('.b4', s1), { autoAlpha: 0, y: -10, duration: 0.25 }, 0.8)
        .to($('.af', s1), { autoAlpha: 1, y: 0, duration: 0.3 }, 1.0);
      // chapter 2
      swapCh(st, ch[0], ch[1], 2); swapSc(st, s1, s2, 2);
      st.to(rail[1], { scaleX: 1, duration: 2 }, 2)
        .to(scr, { '--x': '0%', duration: 1, ease: 'power2.inOut' }, 2.6)
        .to(cnt, { lk: 18400, cm: 1120, vw: 184000, duration: 1, ease: 'power2.in', onUpdate: paintC }, 2.8)
        .to($$('.cb', s2), { autoAlpha: 1, x: 0, stagger: 0.15, duration: 0.3, ease: 'back.out(1.6)' }, 3.0)
        .to($('.b4', s2), { autoAlpha: 0, y: -10, duration: 0.3 }, 3.1)
        .to($('.af', s2), { autoAlpha: 1, y: 0, duration: 0.3 }, 3.3);
      // chapter 3
      swapCh(st, ch[1], ch[2], 4); swapSc(st, s2, s3, 4);
      st.to(rail[2], { scaleX: 1, duration: 2 }, 4)
        .to(bst, { n: 47, duration: 0.6, onUpdate: function () { bstN.textContent = '×' + Math.round(bst.n); } }, 4.2)
        .to($('.bef', s3), { autoAlpha: 0, y: -24, duration: 0.35 }, 4.9)
        .to($('.b4', s3), { autoAlpha: 0, y: -10, duration: 0.25 }, 4.9)
        .to($('.aft', s3), { autoAlpha: 1, duration: 0.35 }, 5.0)
        .to($('.af', s3), { autoAlpha: 1, y: 0, duration: 0.3 }, 5.1)
        .to({}, { duration: 0.6, onUpdate: function () { var p = this.progress(); ads[0].classList.toggle('dead', p > 0.25); ads[1].classList.toggle('dead', p > 0.55); ads[2].classList.toggle('won', p > 0.85); fnl.classList.toggle('on', p > 0.1); } }, 5.1)
        .to(ord, { v: 1, duration: 0.8, ease: 'power2.out', onUpdate: function () { perf(70, ord.v); } }, 5.2);
      // chapter 4
      swapCh(st, ch[2], ch[3], 6.2); swapSc(st, s3, s4, 6.2);
      st.to(rail[3], { scaleX: 1, duration: 1.8 }, 6.2)
        .to($('.shop', s4), { clipPath: 'inset(0% 0% 0% 0%)', duration: 0.8, ease: 'power3.inOut' }, 7)
        .to($('.speed', s4), { autoAlpha: 1, scale: 1, duration: 0.3, ease: 'back.out(2)' }, 7.6);
      // finale
      swapCh(st, ch[3], fin, 8.2);
      st.to($('.stamp', s4), { autoAlpha: 1, scale: 1, rotate: -12, duration: 0.35, ease: 'back.out(2.2)' }, 8.6)
        .to({}, { duration: 0.8 });

      /* SELECTED WORK horizontal */
      if (desk) {
        var hw = $('#hw', pg), track = $('.hw-track', hw);
        var dist = function () { return Math.max(0, track.scrollWidth - innerWidth); };
        gsap.to(track, { x: function () { return -dist(); }, ease: 'none', scrollTrigger: { trigger: $('.hw-pin', hw), start: 'center center', end: function () { return '+=' + dist(); }, pin: hw, scrub: 0.8, invalidateOnRefresh: true, anticipatePin: 1 } });
      }

      /* WALL rows drift */
      var wall = $('#wall', pg);
      $$('.wrow', wall).forEach(function (r) {
        var d = +r.dataset.dir;
        gsap.fromTo(r, { xPercent: d > 0 ? -28 : -2 }, { xPercent: d > 0 ? -2 : -28, ease: 'none', scrollTrigger: { trigger: wall, start: 'top bottom', end: 'bottom top', scrub: 0.6 } });
      });
      ScrollTrigger.create({ trigger: wall, start: 'top bottom', end: 'bottom top', onToggle: function (s) {
        $$('.wt video', wall).forEach(function (v) {
          if (!desk && !v.parentNode.dataset.mob) return;
          if (s.isActive) { if (!v.src) { v.src = v.dataset.src; v.addEventListener('playing', function () { v.classList.add('ok'); }, { once: true }); } v.play().catch(function () {}); }
          else v.pause();
        });
      } });

      /* QUOTES stack */
      var qs = $('#qs', pg), qc = $$('.qc', qs);
      var rots = [-4, 3, -2, 5, -1];
      gsap.set(qc, { y: function (i) { return i ? innerHeight : 0; }, rotate: function (i) { return rots[i % 5]; } });
      var qt = gsap.timeline({ defaults: { ease: 'power2.out' }, scrollTrigger: { trigger: qs, start: 'top top', end: '+=' + (qc.length - 1) * 70 + '%', pin: true, scrub: 0.7, invalidateOnRefresh: true } });
      qc.forEach(function (c, i) {
        if (!i) return;
        qt.to(c, { y: 0, duration: 1 }, i - 1).to(qc.slice(0, i), { scale: '-=0.04', y: '-=18', duration: 1 }, i - 1);
      });
      qt.to({}, { duration: 0.4 });

      return function () { ScrollTrigger.removeEventListener('refreshInit', onRI); gsap.set(hf, { clearProps: 'width,height,right,bottom,borderRadius' }); };
    });

    /* shoot list: floating preview (desktop) */
    var cats = $('.cats', pg), fl = $('#float', pg);
    if (FINE && cats && fl) {
      var fx = gsap.quickTo(fl, 'x', { duration: 0.6, ease: 'power3' }), fy = gsap.quickTo(fl, 'y', { duration: 0.6, ease: 'power3' });
      var cache = {}, cyc = null, curCat = null;
      var showCat = function (k) {
        curCat = k; clearInterval(cyc);
        if (!cache[k]) cache[k] = (VS.cats[k] || []).slice(0, 3).map(function (id) { var v = document.createElement('video'); v.muted = true; v.loop = true; v.playsInline = true; v.preload = 'auto'; v.src = '/assets/pv/' + id + '.mp4'; fl.appendChild(v); return v; });
        $$('video', fl).forEach(function (v) { v.classList.remove('on'); v.pause(); });
        var list = cache[k], i = 0;
        var on = function () { list.forEach(function (v, j) { v.classList.toggle('on', j === i); if (j === i) v.play().catch(function () {}); else v.pause(); }); };
        on(); if (list.length > 1) cyc = setInterval(function () { i = (i + 1) % list.length; on(); }, 2400);
      };
      cats.addEventListener('mousemove', function (e) { var w = fl.offsetWidth, h = fl.offsetHeight; fx(e.clientX - w / 2 + 40); fy(e.clientY - h / 2); });
      $$('.cat', cats).forEach(function (c) { c.addEventListener('mouseenter', function () { showCat(c.dataset.cat); }); });
      cats.addEventListener('mouseenter', function () { gsap.to(fl, { opacity: 1, scale: 1, duration: 0.5, ease: 'power3.out' }); });
      cats.addEventListener('mouseleave', function () { clearInterval(cyc); gsap.to(fl, { opacity: 0, scale: 0.6, duration: 0.4, ease: 'power3.in', onComplete: function () { $$('video', fl).forEach(function (v) { v.pause(); }); } }); });
    }
  };

  INIT.services = function (pg) {
    autoVids(pg);
    if (!hasG) return;
    var cards = isMob() ? [] : $$('.sv', pg);
    cards.forEach(function (c, i) {
      var nx = cards[i + 1]; if (!nx) return;
      gsap.to(c, { scale: 0.92, filter: 'brightness(0.4)', ease: 'none', scrollTrigger: { trigger: nx, start: 'top 85%', end: 'top 15%', scrub: true } });
    });
    var sio = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { scramble(e.target); sio.unobserve(e.target); } }); }, { threshold: 0.6 });
    $$('.sv h2', pg).forEach(function (h) { delete h.dataset.sc; sio.observe(h); });
    var fill = $('.pline .fill', pg);
    if (fill) gsap.to(fill, { scaleX: 1, ease: 'none', scrollTrigger: { trigger: fill.parentNode, start: 'top 80%', end: 'bottom 55%', scrub: true } });
  };

  INIT.work = function (pg) {
    autoVids(pg);
    // hover preview on film tiles
    if (FINE) $$('.ft1', pg).forEach(function (t) {
      if (t.dataset.hb) return; t.dataset.hb = 1;
      var v = null, tm = null;
      t.addEventListener('mouseenter', function () { tm = setTimeout(function () { if (!v) { v = document.createElement('video'); v.muted = true; v.loop = true; v.playsInline = true; v.src = '/assets/pv/' + t.dataset.film + '.mp4'; t.querySelector('.m').insertBefore(v, t.querySelector('.pb')); } v.play().catch(function () {}); t.classList.add('pl'); }, 120); });
      t.addEventListener('mouseleave', function () { clearTimeout(tm); if (v) v.pause(); t.classList.remove('pl'); });
    });
    if (!hasG) return;
    var links = $$('#subnav a', pg);
    links.forEach(function (a) {
      var sec = document.getElementById(a.dataset.jump); if (!sec) return;
      ScrollTrigger.create({ trigger: sec, start: 'top 55%', end: 'bottom 55%', onToggle: function (s) { if (s.isActive) { links.forEach(function (x) { x.classList.toggle('on', x === a); }); var sn = a.parentNode; if (sn.scrollWidth > sn.clientWidth) sn.scrollTo({ left: a.offsetLeft - sn.clientWidth / 2 + a.offsetWidth / 2, behavior: 'smooth' }); } } });
    });
  };

  INIT.desk = function (pg) {
    // tabs (bind once)
    $$('[data-tabs]', pg).forEach(function (tl) {
      if (tl.dataset.b) return; tl.dataset.b = 1;
      var btns = $$('button', tl);
      btns.forEach(function (b) { b.addEventListener('click', function () {
        btns.forEach(function (x) { var on = x === b; x.setAttribute('aria-selected', on); var p = document.getElementById(x.getAttribute('aria-controls')); if (p) p.hidden = !on; });
        if (hasG) ScrollTrigger.refresh();
      }); });
      tl.addEventListener('keydown', function (e) { var i = btns.indexOf(document.activeElement); if (e.key === 'ArrowRight' && i < btns.length - 1) { btns[i + 1].focus(); btns[i + 1].click(); } if (e.key === 'ArrowLeft' && i > 0) { btns[i - 1].focus(); btns[i - 1].click(); } });
    });
    // story: scroll drives six steps
    var story = $('#dk-story', pg), stage = $('#dk-stage', pg), steps = $$('.dk-step', pg), dots = $$('#dk-prog i', pg), pn = $('#dk-pn', pg), sw = $$('[data-on]', stage);
    var SIDES = ['portal', 'desk', 'desk', 'portal', 'portal', 'portal'], cur = -1;
    var setStep = function (n) {
      if (n === cur) return; cur = n; stage.dataset.step = n + 1; stage.dataset.side = SIDES[n];
      steps.forEach(function (s, i) { s.classList.toggle('dk-on', i === n); });
      dots.forEach(function (d, i) { d.classList.toggle('dk-on', i === n); }); pn.textContent = (n + 1) + ' of 6';
      sw.forEach(function (el) { el.classList.toggle('dk-on', el.dataset.on.split(',').indexOf(String(n + 1)) > -1); });
    };
    setStep(0);
    if (!dots[0].dataset.b) dots.forEach(function (d, i) { d.dataset.b = 1; d.addEventListener('click', function () { var h = story.offsetHeight - innerHeight; scrollTo(story.offsetTop + h * ((i + 0.5) / 6)); }); });
    // live timer
    var tEl = $('#dkTimer', pg), secs = 1 * 3600 + 42 * 60 + 18;
    var pad = function (n) { return (n < 10 ? '0' : '') + n; };
    pageTimers.push(setInterval(function () { secs++; tEl.textContent = pad(Math.floor(secs / 3600)) + ':' + pad(Math.floor(secs / 60) % 60) + ':' + pad(secs % 60); }, 1000));
    // subtasks tick over
    var subs = $$('#dkSub li', pg), si = 2;
    subs.forEach(function (l, i) { l.classList.toggle('done', i < 2); });
    pageTimers.push(setInterval(function () { if (si < subs.length) { subs[si].classList.add('done'); si++; } else { si = 2; subs.forEach(function (l, i) { l.classList.toggle('done', i < 2); }); } }, 5200));
    // live activity feed
    var feed = $('#dkFeed', pg);
    var EV = [['A', '<b>Ayesha</b> moved <b>Eid batch, reels</b> to In progress'], ['C', '<b>Bashir</b> approved 3 posts in his portal'], ['H', '<b>Hamza</b> logged 45m on <b>Boost test</b>'], ['S', '<b>Sana</b> uploaded <b>Nimko pack animation v2</b>'], ['C', '<b>Bashir</b> left a comment: "Logo thora bara?"'], ['A', '<b>Ayesha</b> replied: "Trust the process."'], ['B', '<b>Bilal</b> closed <b>Order page, mobile QA</b>'], ['L', 'New lead from Facebook, assigned to the CRO'], ['H', '<b>Hamza</b> paused the losing ad. Budget moved to the winner'], ['C', '<b>Gulmohar</b> booked a review, Thursday 11 am']];
    var ei = 0, stamps = [];
    var push = function (first) {
      var e = EV[ei++ % EV.length], li = document.createElement('li');
      li.innerHTML = '<i class="dkx-av">' + e[0] + '</i><span>' + e[1] + '</span><time>just now</time>';
      if (first) li.style.animation = 'none';
      feed.insertBefore(li, feed.firstChild); stamps.unshift(Date.now() - (first ? ((6 - ei) * 97000) : 0));
      while (feed.children.length > 7) { feed.removeChild(feed.lastChild); stamps.pop(); }
      $$('time', feed).forEach(function (t, i) { var m = Math.round((Date.now() - stamps[i]) / 60000); t.textContent = m < 1 ? 'just now' : m + 'm ago'; });
    };
    if (feed && !feed.children.length) { for (var k = 0; k < 5; k++) push(true); }
    pageTimers.push(setInterval(function () { push(false); }, 3600));
    if (!hasG) return;
    // team counters + bars
    $$('[data-count]', pg).forEach(function (b) { var o = { v: 0 }; gsap.to(o, { v: +b.dataset.count, duration: 1.6, ease: 'power2.out', scrollTrigger: { trigger: b, start: 'top 85%' }, onUpdate: function () { b.textContent = Math.round(o.v); } }); });
    ScrollTrigger.create({ trigger: $('.dkx-team', pg), start: 'top 80%', onEnter: function (s) { s.trigger.classList.add('in'); } });
    ScrollTrigger.create({ trigger: story, start: 'top top', end: 'bottom bottom', onUpdate: function (s) { setStep(Math.min(5, Math.floor(s.progress * 6))); } });
    $$('[data-words]', pg).forEach(function (p) {
      gsap.to($$('.sw', p), { opacity: 1, stagger: 0.1, ease: 'none', scrollTrigger: { trigger: p, start: 'top 82%', end: 'bottom 50%', scrub: true } });
    });
  };

  INIT.svc = function (pg) {
    if (!hasG) return;
    var fill = $('.pline .fill', pg);
    if (fill) gsap.to(fill, { scaleX: 1, ease: 'none', scrollTrigger: { trigger: fill.parentNode, start: 'top 80%', end: 'bottom 55%', scrub: true } });
  };

  INIT.studio = function (pg) {
    if (!hasG) return;
    $$('[data-words]', pg).forEach(function (p) {
      gsap.to($$('.sw', p), { opacity: 1, stagger: 0.1, ease: 'none', scrollTrigger: { trigger: p, start: 'top 82%', end: 'bottom 50%', scrub: true } });
    });
  };

  /* ======================================================
     ROUTER
     ====================================================== */
  var current = null;
  var PT = [['Chai break.', 'Point six seconds. We timed it.'], ['Ek minute, boss.', 'Literally less than one.'], ['Loading the vibe.', 'Vibe aani chahiye.'], ['Rendering.', 'Kidding. It is already here.'], ['Logo chhota kar rahe hain.', 'Just a little.']];
  var pti = Math.floor(Math.random() * PT.length);
  function resolve(path) {
    path = path.replace(/\.html$/, '').replace(/\/index$/, '').replace(/\/+$/, '') || '/';
    var m;
    if (path === '/' || path === '/index.html') return 'home';
    if ((m = path.match(/^\/(services|work|desk|journal|studio|careers|privacy|contact)$/))) return m[1];
    if (path === '/portfolio') return 'work';
    if (path === '/blog') return 'journal';
    if ((m = path.match(/^\/journal\/([\w-]+)$/)) && document.getElementById('p-post-' + m[1])) return 'post-' + m[1];
    if ((m = path.match(/^\/services\/([\w-]+)$/)) && document.getElementById('p-svc-' + m[1])) return 'svc-' + m[1];
    if (/^\/(dubai|global|for-agencies|for-ecommerce-brands)$/.test(path) && document.getElementById('p-' + path.slice(1))) return path.slice(1);
    return '404';
  }
  function swap(name, hash) {
    if (ctx) { ctx.revert(); ctx = null; }
    pageTimers.forEach(clearInterval); pageTimers = [];
    ScrollTrigger && ScrollTrigger.getAll().forEach(function (t) { t.kill(); });
    $$('.page').forEach(function (p) { p.classList.remove('on'); });
    var pg = document.getElementById('p-' + name) || document.getElementById('p-404');
    pg.classList.add('on');
    document.title = pg.dataset.title || 'Vibescape';
    $$('[data-nav]').forEach(function (a) { a.classList.toggle('on', a.dataset.nav === name || (name.indexOf('post-') === 0 && a.dataset.nav === 'journal') || (name.indexOf('svc-') === 0 && a.dataset.nav === 'services')); });
    if (lenis) lenis.scrollTo(0, { immediate: true, force: true }); window.scrollTo(0, 0);
    hdr.classList.remove('hide');
    current = name;
    var key = name.indexOf('post-') === 0 ? 'post' : (name.indexOf('svc-') === 0 || /^(dubai|global|for-agencies|for-ecommerce-brands)$/.test(name)) ? 'svc' : name;
    var run = function () { try { if (INIT[key]) INIT[key](pg); } catch (err) { if (window.console) console.error('init ' + key, err); } };
    if (hasG) ctx = gsap.context(run, pg); else run();
    if (armed) { $$('[data-hero]', pg).forEach(function (el) { el.classList.add('in'); }); arm(pg); }
    if (hasG) { ScrollTrigger.refresh(); }
    var top0 = function () { if (lenis) lenis.scrollTo(0, { immediate: true, force: true }); window.scrollTo(0, 0); };
    if (!hash) { top0(); requestAnimationFrame(top0); }
    if (hash) { var t = document.getElementById(hash.slice(1)); if (t) setTimeout(function () { scrollTo(t, { offset: -150, duration: 1.6 }); }, 250); }
  }
  var busy = false;
  function go(href, push) {
    var u = new URL(href, location.href);
    var name = resolve(u.pathname);
    if (push) { if (u.pathname + u.hash === location.pathname + location.hash && name === current) return; history.pushState({}, '', u.pathname + u.hash); }
    if (name === current) { if (u.hash) { var t = document.getElementById(u.hash.slice(1)); if (t) scrollTo(t, { offset: -150 }); } else scrollTo(0); return; }
    if (!hasG || RM || current === null) { swap(name, u.hash); return; }
    if (busy) return; busy = true;
    var pt = $('#pt'), s = PT[pti++ % PT.length];
    $('#ptl').textContent = s[0]; $('#pts').textContent = s[1];
    gsap.timeline({ onComplete: function () { busy = false; } })
      .set(pt, { y: 0, yPercent: 100 })
      .add(function () { if (lenis) lenis.stop(); })
      .to(pt, { yPercent: 0, duration: 0.55, ease: 'expo.inOut' })
      .add(function () { if (lenis) lenis.start(); swap(name, u.hash); })
      .to(pt, { yPercent: -100, duration: 0.65, ease: 'expo.inOut', delay: 0.18 });
  }
  addEventListener('popstate', function () { go(location.href, false); });

  // legacy hash links (#work etc) from old site
  if (location.hash && /^#(services|portfolio|work|blog|journal|studio|contact)$/.test(location.hash)) {
    history.replaceState({}, '', '/' + location.hash.slice(1).replace('portfolio', 'work').replace('blog', 'journal'));
  }
  go(location.href, false);

  // refresh on width changes only (mobile url bar safe)
  var lw = innerWidth, rt;
  addEventListener('resize', function () {
    if (Math.abs(innerWidth - lw) < 40) return; lw = innerWidth;
    clearTimeout(rt); rt = setTimeout(function () { var n = current; current = null; swap(n, ''); }, 250);
  });

  // footer wordmark: fit exactly inside the page gutters
  function fitWord() {
    var m = document.createElement('span'); m.className = 'fword-m'; m.textContent = 'Vibescape';
    var g = document.createElement('div'); g.style.cssText = 'position:absolute;visibility:hidden;width:0;padding-left:var(--g)';
    document.body.appendChild(m); document.body.appendChild(g);
    var r = m.getBoundingClientRect().width / 100, gp = parseFloat(getComputedStyle(g).paddingLeft) || 20; m.remove(); g.remove();
    var avail = Math.min(document.documentElement.clientWidth, 1600) - 2 * gp;
    if (r > 0) document.documentElement.style.setProperty('--fwpx', (avail / r).toFixed(2) + 'px');
  }
  // footer wordmark: letters rise in when the footer arrives; tap it to go back to the top
  $$('.fword').forEach(function (f) {
    f.innerHTML = f.textContent.split('').map(function (ch, i) { return '<span class="fl" style="--i:' + i + '">' + ch + '</span>'; }).join('');
    f.setAttribute('data-cursor', 'Top'); f.setAttribute('role', 'button'); f.setAttribute('tabindex', '0'); f.setAttribute('aria-label', 'Back to top');
    f.addEventListener('click', function () { scrollTo(0, { duration: 2 }); });
    f.addEventListener('keydown', function (e) { if (e.key === 'Enter') scrollTo(0, { duration: 2 }); });
  });
  var fio = new IntersectionObserver(function (es) { es.forEach(function (e) { e.target.classList.toggle('in', e.isIntersecting); }); }, { threshold: 0.35 });
  $$('.fword').forEach(function (f) { fio.observe(f); });

  // text scramble, used once per heading when it scrolls in
  var GLY = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&';
  function scramble(el) {
    if (RM || el.dataset.sc) return; el.dataset.sc = 1;
    var fin = el.textContent, n = 0, total = 22;
    el.style.minWidth = el.offsetWidth + 'px';
    var t = setInterval(function () {
      n++;
      el.textContent = fin.split('').map(function (ch, i) {
        if (ch === ' ' || i < (n / total) * fin.length) return ch;
        return GLY[(Math.random() * GLY.length) | 0];
      }).join('');
      if (n >= total) { clearInterval(t); el.textContent = fin; el.style.minWidth = ''; }
    }, 32);
  }
  window.__vsScramble = scramble;

  fitWord(); if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitWord);
  var fwT; addEventListener('resize', function () { clearTimeout(fwT); fwT = setTimeout(fitWord, 150); });

  try { console.log('%cCode dekh rahe ho? Designer ho toh baat karte hain: mediavibescape@gmail.com', 'font:500 13px/1.6 system-ui;color:#888'); } catch (e) {}
})();
