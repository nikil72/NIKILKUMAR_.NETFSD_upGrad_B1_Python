// Auto-hide toast after 3.5s
const toast = document.querySelector('.toast');
if (toast) setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateX(100%)'; toast.style.transition = 'all .4s'; setTimeout(() => toast.remove(), 400); }, 3500);

// Option select highlight (used in quiz)
document.querySelectorAll('.option-label').forEach(label => {
    label.addEventListener('click', function () {
        const group = this.closest('.options');
        if (group) group.querySelectorAll('.option-label').forEach(l => l.classList.remove('selected'));
        this.classList.add('selected');
    });
});

// Animate result ring on load
const fills = document.querySelectorAll('.score-ring circle[stroke-dasharray]');
fills.forEach(c => {
    const target = c.getAttribute('stroke-dasharray');
    c.setAttribute('stroke-dasharray', '0 314');
    requestAnimationFrame(() => {
        setTimeout(() => { c.style.transition = 'stroke-dasharray 1.2s ease'; c.setAttribute('stroke-dasharray', target); }, 100);
    });
});

// Animate history bars
document.querySelectorAll('.history-bar').forEach(bar => {
    const target = bar.style.width;
    bar.style.width = '0%';
    const obs = new IntersectionObserver(entries => {
        if (entries[0].isIntersecting) { setTimeout(() => { bar.style.width = target; }, 100); obs.disconnect(); }
    });
    obs.observe(bar);
});

// Confirm deletes
document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', e => { if (!confirm(el.dataset.confirm)) e.preventDefault(); });
});
