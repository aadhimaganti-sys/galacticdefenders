const canvas = document.querySelector(".flight-scene");
const context = canvas.getContext("2d");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

async function recommendDownload() {
  const browserPlatform = navigator.userAgentData?.platform || navigator.platform || "";
  let architecture = "";
  try {
    architecture = (await navigator.userAgentData?.getHighEntropyValues?.(["architecture"]))?.architecture || "";
  } catch {
    // Platform choices remain available if the browser withholds architecture hints.
  }

  let target = "";
  if (/Win/i.test(browserPlatform) && !/arm/i.test(architecture)) target = "windows";
  else if (/Linux/i.test(browserPlatform) && /x86/i.test(`${architecture} ${navigator.platform}`)) target = "linux";
  else if (/Mac/i.test(browserPlatform)) {
    if (/arm/i.test(architecture)) target = "mac-arm";
    else if (/x86/i.test(architecture)) target = "mac-intel";
  }

  document.querySelector(`[data-platform="${target}"]`)?.classList.add("recommended");
}

function drawScene() {
  const bounds = canvas.getBoundingClientRect();
  const scale = window.devicePixelRatio || 1;
  canvas.width = Math.round(bounds.width * scale);
  canvas.height = Math.round(bounds.height * scale);
  context.setTransform(scale, 0, 0, scale, 0, 0);

  const width = bounds.width;
  const height = bounds.height;
  const stars = Array.from({ length: Math.floor(width / 4) }, (_, index) => ({
    x: (index * 127.1) % width,
    y: (index * 311.7) % height,
    r: index % 17 === 0 ? 1.5 : 0.7,
    a: 0.15 + (index % 7) * 0.1,
  }));

  function frame(time = 0) {
    context.clearRect(0, 0, width, height);
    const drift = reducedMotion ? 0 : (time / 80) % 40;
    for (const star of stars) {
      context.globalAlpha = star.a;
      context.fillStyle = "#d8ffef";
      context.fillRect((star.x - drift + width) % width, star.y, star.r, star.r);
    }
    context.globalAlpha = 1;

    const scaleShip = Math.min(width, height) / 550;
    context.save();
    context.translate(width * 0.76, height * 0.48);
    context.scale(scaleShip, scaleShip);
    context.rotate(-0.15);
    context.shadowBlur = 24;
    context.shadowColor = "#d7ff4f";
    context.fillStyle = "#d7ff4f";
    context.beginPath();
    context.moveTo(106, 0);
    context.lineTo(-64, -28);
    context.lineTo(-41, 0);
    context.lineTo(-64, 28);
    context.closePath();
    context.fill();
    context.shadowBlur = 0;
    context.fillStyle = "#ff7554";
    context.beginPath();
    context.moveTo(-44, -8);
    context.lineTo(-91 - (reducedMotion ? 0 : Math.sin(time / 90) * 9), 0);
    context.lineTo(-44, 8);
    context.closePath();
    context.fill();
    context.restore();

    context.strokeStyle = "rgba(255, 117, 84, .34)";
    context.beginPath();
    context.arc(width * .78, height * .48, Math.min(width, height) * .32, -1.05, .86);
    context.stroke();
    if (!reducedMotion) requestAnimationFrame(frame);
  }

  frame();
}

recommendDownload();
drawScene();
window.addEventListener("resize", drawScene);