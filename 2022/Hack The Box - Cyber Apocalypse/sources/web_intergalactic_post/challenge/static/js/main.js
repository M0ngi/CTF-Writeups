const color = {
    teal2: '#00ffc3',
    teal: '#59b29e',
    dark: '#0f0026',
    red: '#f63b4c',
    light: '#afe3d7' };
  
  
  const $ = sel => document.querySelector(sel);
  const $$ = sel => document.querySelectorAll(sel);
  
  function introAnimation() {
    const duration = 4;
    // const { chars } = new SplitText('#header h1 span', {
    //   type: 'lines, words, chars',
    //   linesClass: 'line line++',
    //   wordsClass: 'word word++',
    //   charsClass: 'char' });
  
  
    const easeOutElastic = Elastic.easeOut.config(1, 1);
    const section = this.$refs.header;
    const button = this.$el.querySelector('#header button');
  
    // Set the section opacity low, so that it doenst visully load with a hop/skip
    TweenMax.set([section, '#header', '.gui'], { autoAlpha: 0 });
  
    // Sort tics from the middle -> to outside
    const sortTics = selector => {
      const tics = Array.from(document.querySelectorAll(selector));
      return {
        left: tics.filter((tic, i) => i < tics.length / 2).reverse(),
        right: tics.filter((tic, i) => i > (tics.length - 1) / 2) };
  
    };
    const ticsT = sortTics('.ui-tics.t .tic');
    const ticsB = sortTics('.ui-tics.b .tic');
    const borderXF = $('.gui .border-x.f');
    const borderXL = $('.gui .border-x.l');
    const textBox = $$('.ui-text .t-o');
    const textBoxTitleL = $$('.ui-text.l h5');
    const textBoxTitleR = $$('.ui-text.r h5');
    const curvedBorder = $('.ui-border-v2.t');
  
    new TimelineMax({
      onComplete: () => document.body.classList.add('intro-anim-complete') }).
  
    delay(1).
    set('body', { opacity: 1 })
    // Turn the opacity back up
    .add(_ => TweenMax.set([section, '#header', '.gui'], { autoAlpha: 1 })).
    set('.gui .border-vert .dot', { autoAlpha: 0 }, 0).
  
    from('.gui .border-horz', duration, {
      scaleX: 0,
      ease: easeOutElastic },
    0).
    from(borderXF, duration, {
      rotation: '90deg',
      scaleX: 0,
      ease: easeOutElastic,
      onComplete() {
        borderXF.style = null;
      } },
    0).
    from(borderXL, duration, {
      rotation: '-90deg',
      scaleX: 0,
      ease: easeOutElastic,
      onComplete() {
        borderXL.style = null;
      } },
    0).
  
    from('.gui .border-vert', duration, {
      scaleY: 0,
      ease: easeOutElastic },
    0).
    fromTo('#header .ui-box', duration * 0.1, {
      autoAlpha: 0 },
    {
      autoAlpha: 1,
      ease: easeOutElastic },
    0).
    staggerFromTo(ticsT.left, duration, {
      visibility: 'hidden' },
    {
      visibility: 'visible',
      ease: easeOutElastic },
    0.05, 0).
    staggerFromTo(ticsT.right, duration, {
      visibility: 'hidden' },
    {
      visibility: 'visible',
      ease: easeOutElastic },
    0.05, 0).
  
    staggerFromTo(ticsB.left, duration, {
      visibility: 'hidden' },
    {
      visibility: 'visible',
      ease: easeOutElastic },
    0.05, 0).
    staggerFromTo(ticsB.right, duration, {
      visibility: 'hidden' },
    {
      visibility: 'visible',
      ease: easeOutElastic },
    0.05, 0).
  
    fromTo('#header .ui-fx', duration, {
      top: '40%',
      right: '40%',
      bottom: '40%',
      left: '40%' },
    {
      top: '0%',
      right: '0%',
      bottom: '0%',
      left: '0%',
      ease: easeOutElastic },
    0).
    set('.gui .ui-border', { transition: 'none' }, 0).
    fromTo('.gui .ui-border', duration, {
      height: 0 },
    {
      height: '80vh',
      ease: easeOutElastic,
      onComplete() {
        resetStyle('.gui .ui-border');
      } },
    0).
  
    from('.ui-inner-border', duration / 4, {
      autoAlpha: 0,
      ease: easeOutElastic },
    0).
  
    fromTo('.ui-fx .ui-inner-border', duration, {
      height: 0 },
    {
      height: '80%',
      ease: easeOutElastic },
    0).
  
    fromTo(['#header .ui-inner-border.t', '#header .ui-inner-border.b'], duration, {
      width: 0,
      borderWidth: '0px' },
    {
      width: '40vw',
      borderWidth: '3px',
      ease: easeOutElastic },
    0).
  
    from(curvedBorder, duration, {
      y: -40 },
    0.4)
  
    // Caps, Borders, Details
    .to('.gui .border-vert .dot', duration / 2, {
      autoAlpha: 1,
      ease: RoughEase.ease.config({
        points: 200,
        strength: 4,
        clamp: true,
        randomize: true }) },
  
    duration * 0.66).
    fromTo(['.gui .cap'], duration, {
      opacity: 0 },
    {
      opacity: 1,
      ease: RoughEase.ease.config({
        points: 200,
        strength: 4,
        clamp: true,
        randomize: true }) },
  
    duration * 0.66).
    fromTo(['.gui .batt'], duration, {
      opacity: 0 },
    {
      opacity: 1,
      ease: RoughEase.ease.config({
        points: 100,
        strength: 3,
        clamp: true,
        randomize: true }) },
  
    duration * 0.66).
    fromTo(['#header .ui-corner'], duration, {
      opacity: 0 },
    {
      opacity: 1,
      ease: RoughEase.ease.config({
        points: 100,
        strength: 2,
        clamp: true,
        randomize: true }) },
  
    duration * 0.66)
  
    // Left and Right, Top, Bottom Batts in Header
    .from(['.ui-batts.l .batt', '.ui-batts.r .batt'], duration / 2, {
      width: 0,
      ease: easeOutElastic },
    duration / 2).
    from(['.ui-batts.t .batt', '.ui-batts.b .batt'], duration / 2, {
      height: 0,
      ease: easeOutElastic },
    duration / 2)
  
    // Circles
    .staggerFromTo('.gui .ui-circles.l .circle', duration / 2, {
      visibility: 'hidden',
      ease: Power4.easeInOut },
    {
      visibility: 'visible',
      ease: Power4.easeOut,
      onComplete() {
        resetStyle('.gui .ui-circles.l .circle');
      } },
    0.1, duration * 0.66).
    staggerFromTo('.gui .ui-circles.r .circle', duration / 2, {
      visibility: 'hidden',
      ease: Power4.easeInOut },
    {
      visibility: 'visible',
      ease: Power4.easeOut,
      onComplete() {
        resetStyle('.gui .ui-circles.r .circle');
      } },
    0.1, duration * 0.66)
  
    // Title
    // .staggerFromTo(chars, 0.5, {
    //   visibility: 'hidden',
    //   background: 'rgba(0, 255, 195, 0.3)',
    //   textShadow: `0 0 0 ${color.teal2}`,
    //   ease: Sine.easeIn },
    // {
    //   visibility: 'visible',
    //   background: 'rgba(0, 255, 195, 0)',
    //   textShadow: `0 0 60px ${color.teal2}`,
    //   ease: Sine.easeOut },
    // 0.05, duration * 0.33)
  
    // UI-Text 
    .add('textBox', duration * 0.66).
    staggerFromTo(textBox, 5, {
      height: 0 },
    {
      height: 100,
      repeat: -1,
      repeatDelay: 3,
      yoyo: true,
      ease: Sine.easeOut },
    4, 'textBox').
    fromTo([textBoxTitleL, textBoxTitleR], 1, {
      autoAlpha: 0 },
    {
      autoAlpha: 1,
      ease: Sine.easeOut },
    'textBox').
    to(textBoxTitleL, 2, {
      text: 'Status: Ready',
      repeat: -1,
      repeatDelay: 5,
      yoyo: true,
      ease: Sine.easeOut },
    'textBox').
    to(textBoxTitleR, 2.4, {
      text: 'LETS GO',
      repeat: -1,
      repeatDelay: 5,
      yoyo: true,
      ease: Sine.easeOut },
    'textBox')
  
    //button
    .from(button, 0.3, {
      autoAlpha: 0 },
    2).
    from(button, 1, {
      scale: 1.5,
      autoAlpha: 0,
      ease: easeOutElastic,
      onComplete() {
        button.style = null;
      } },
    2);
  }
  
  function resetStyle(selector, callback) {
    if (typeof selector === 'string') {
      Array.from(document.querySelectorAll(selector)).forEach((c, i) => c.style = null);
    } else
    {
      if (callback) {
        Array.from(selector).forEach(callback);
      } else
      {
        Array.from(selector).forEach((c, i) => c.style = null);
      }
  
    }
  }
  
  function colorHex(color) {
    return parseInt('0x' + color.replace(/#/g, '').toUpperCase());
  }
  
  function spaceStars(scene, farPlane = 1000) {
    const geometry = new THREE.SphereGeometry(1, 1, 1);
    const material = new THREE.PointsMaterial({
      size: 5,
      opacity: 1,
      color: color.teal,
      transparent: true });
  
  
    let starQty = 1000;
    for (let i = 0; i < starQty; i++) {
      const starVertex = new THREE.Vector3();
      starVertex.x = Math.random() * farPlane - farPlane * 0.5;
      starVertex.y = Math.random() * farPlane - farPlane * 0.5;
      starVertex.z = Math.random() * farPlane - farPlane * 0.5;
      geometry.vertices.push(starVertex);
    }
  
    const stars = new THREE.Points(geometry, material);
  
    scene.add(stars);
  
    return stars;
  }
  
  function spaceWorld(targetElement) {
  
    let HEIGHT = window.innerHeight;
    let WIDTH = window.innerWidth;
    let aspectRatio = WIDTH / HEIGHT;
    let fieldOfView = 75;
    let nearPlane = 1;
    let farPlane = 5000;
    let mouseX = 0;
    let mouseY = 0;
  
    const scene = new THREE.Scene({ antialias: true });
    const camera = new THREE.PerspectiveCamera(fieldOfView, aspectRatio, nearPlane, farPlane);
    const renderer = webGLSupport() ? new THREE.WebGLRenderer() : new THREE.CanvasRenderer();
  
    // Add objects to the scene
    // -------------------------------------------------------
  
    const stars = spaceStars(scene, farPlane);
  
    init();
  
    return {
      stars };
  
  
    // Initialize and Animate, Functions Hoisted
    // --------------------------------------
  
    function render(t) {
      stars.rotation.x += (mouseX - stars.rotation.x) * 0.000015;
      stars.rotation.y += (mouseY - stars.rotation.y) * 0.000015;
      camera.lookAt(scene.position);
      renderer.render(scene, camera);
    }
  
    function init() {
      targetElement.appendChild(renderer.domElement);
  
      camera.position.z = 1070 * 3.5;
  
      renderer.setClearColor(new THREE.Color(colorHex(color.dark)), 1);
      renderer.setPixelRatio(window.devicePixelRatio);
      renderer.setSize(WIDTH, HEIGHT);
  
      window.addEventListener('resize', onWindowResize, false);
      document.addEventListener('mousemove', onMouseMove, false);
  
      animate();
    }
  
    function animate(t) {
      requestAnimationFrame(animate);
      render(t);
    }
  
    function webGLSupport() {
      try {
        const canvas = document.createElement('canvas');
        return !!(window.WebGLRenderingContext && (
        canvas.getContext('webgl') ||
        canvas.getContext('experimental-webgl')));
  
      } catch (e) {
        return false;
      }
    }
  
    function onWindowResize() {
      const w = window.innerWidth;
      const h = window.innerHeight;
      camera.aspect = aspectRatio;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
      renderer.domElement.style.width = w + 'px';
      renderer.domElement.style.height = h + 'px';
    }
  
    function onMouseMove(e) {
      let windowHalfX = WIDTH / 2;
      let windowHalfY = HEIGHT / 2;
      mouseX = e.clientX - windowHalfX;
      mouseY = e.clientY - windowHalfY;
    }
  
  }
  
  new Vue({
    el: "#app",
    mounted() {
      introAnimation.call(this);
      spaceWorld(document.getElementById('starfield'));
    } });


const htmlEncode = (str) => {
    return String(str).replace(/[^\w. ]/gi, function(c) {
        return '&#' + c.charCodeAt(0) + ';';
    });
}


var url = new URL(document.location.href);
var msg = url.searchParams.get("msg");
if(msg){
    $('.alert').innerHTML = htmlEncode(msg);
    $('.alert').style.display = 'block';
}

