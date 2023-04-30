document.addEventListener('mousemove', (event) => {
    const mouseX = event.clientX;
    const mouseY = event.clientY;
    const anchor = document.getElementById('anchor');
    const rekt = anchor.getBoundingClientRect();
    const anchorX = rekt.left + rekt.width / 2;
    const anchorY = rekt.top + rekt.height / 2;
    const eyes = document.querySelectorAll('.eye');
    const angleDeg =  angle(mouseX, mouseY, anchorX, anchorY);
    eyes.forEach(eye =>{
        eye.style.transform = `rotate(${100+angleDeg}deg)`
    })
})

function angle(cx, cy, ex, ey)
{
    const rad = Math.atan2(ey - cy, ex - cx);
    return rad * 180 / Math.PI;
}