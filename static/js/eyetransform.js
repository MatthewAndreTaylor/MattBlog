const anchor = document.getElementById('anchor');
const eyes = document.querySelectorAll('.eye');
document.addEventListener('mousemove', (e) => {
    const dim =  anchor.getBoundingClientRect();
    const anchorX = dim.left + dim.width / 2;
    const anchorY = dim.top + dim.height / 2;
    const angle = Math.atan2(anchorY - e.clientY,anchorX - e.clientX) * 180 / Math.PI;
    eyes.forEach(eye => eye.style.transform = `rotate(${100 + angle}deg)`);
});