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

// Основные цвета
const colors = [
  'rgb(0, 121, 193)',  // PANTONE 300C
  'rgb(0, 79, 109)',   // PANTONE 302C
  'rgb(82, 181, 224)'  // PANTONE 298C
];

function draw() {
  ctx.fillStyle = 'rgba(16,16,16,0.15)';
  ctx.fillRect(0, 0, w, h);
  ctx.font = fontSize + 'px Fira Mono, Consolas, monospace';
  
  for (let i = 0; i < drops.length; i++) {
    const text = letters[Math.floor(Math.random() * letters.length)];
    // Выбираем цвет в зависимости от позиции
    const colorIndex = Math.floor((i / columns) * colors.length);
    ctx.fillStyle = colors[colorIndex];
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