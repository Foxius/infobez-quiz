const canvas = document.getElementById('matrix-bg');
const ctx = canvas.getContext('2d');

let w = window.innerWidth;
let h = window.innerHeight;
canvas.width = w;
canvas.height = h;

const letters = 'АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*';
const fontSize = 18;
const columns = Math.floor(w / fontSize);
const drops = Array(columns).fill(1);

function draw() {
  ctx.fillStyle = 'rgba(16,16,16,0.15)';
  ctx.fillRect(0, 0, w, h);
  ctx.font = fontSize + 'px Fira Mono, Consolas, monospace';
  ctx.fillStyle = '#00ff41';
  for (let i = 0; i < drops.length; i++) {
    const text = letters[Math.floor(Math.random() * letters.length)];
    ctx.fillText(text, i * fontSize, drops[i] * fontSize);
    if (drops[i] * fontSize > h && Math.random() > 0.975) {
      drops[i] = 0;
    }
    drops[i]++;
  }
}
setInterval(draw, 40);
window.addEventListener('resize', () => {
  w = window.innerWidth;
  h = window.innerHeight;
  canvas.width = w;
  canvas.height = h;
}); 