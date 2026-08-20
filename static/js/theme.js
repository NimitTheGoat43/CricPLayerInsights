(function () {
    const saved = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
})();

document.addEventListener('DOMContentLoaded', () => {
    const current = document.documentElement.getAttribute('data-theme');
    updateToggleIcons(current);
    setupThemeToggle();
    setupMobileSidebar();
    updateWinnerBadges();
});

function getPlayerColor(name) {
    if (!name) return { bg: 'rgba(52,211,153,0.18)', color: '#34d399', border: 'rgba(52,211,153,0.4)' };
    const n = name.toLowerCase().trim();
    
    // Explicit player color mapping requested by user & IPL traditions:
    if (n.includes('dhoni') || n.includes('msd')) {
        // MS Dhoni -> Yellow
        return { bg: 'rgba(234, 179, 8, 0.25)', color: '#facc15', border: 'rgba(234, 179, 8, 0.6)' };
    }
    if (n.includes('kohli') || n.includes('virat')) {
        // V Kohli -> Red
        return { bg: 'rgba(239, 68, 68, 0.25)', color: '#f87171', border: 'rgba(239, 68, 68, 0.6)' };
    }
    if (n.includes('rohit') || n.includes('sharma')) {
        // Rohit Sharma -> Blue
        return { bg: 'rgba(59, 130, 246, 0.25)', color: '#60a5fa', border: 'rgba(59, 130, 246, 0.6)' };
    }
    if (n.includes('rahul')) {
        // KL Rahul -> Cyan
        return { bg: 'rgba(6, 182, 212, 0.25)', color: '#22d3ee', border: 'rgba(6, 182, 212, 0.6)' };
    }
    if (n.includes('pant')) {
        // Rishabh Pant -> Sky Blue
        return { bg: 'rgba(14, 165, 233, 0.25)', color: '#38bdf8', border: 'rgba(14, 165, 233, 0.6)' };
    }
    if (n.includes('samson')) {
        // Sanju Samson -> Pink
        return { bg: 'rgba(236, 72, 153, 0.25)', color: '#f472b6', border: 'rgba(236, 72, 153, 0.6)' };
    }
    if (n.includes('gill')) {
        // Shubman Gill -> Teal
        return { bg: 'rgba(20, 184, 166, 0.25)', color: '#2dd4bf', border: 'rgba(20, 184, 166, 0.6)' };
    }
    if (n.includes('narine') || n.includes('russell') || n.includes('iyer')) {
        // KKR -> Purple
        return { bg: 'rgba(168, 85, 247, 0.25)', color: '#c084fc', border: 'rgba(168, 85, 247, 0.6)' };
    }
    if (n.includes('cummins') || n.includes('head') || n.includes('abhishek') || n.includes('klaasen')) {
        // SRH -> Orange
        return { bg: 'rgba(249, 115, 22, 0.25)', color: '#fb923c', border: 'rgba(249, 115, 22, 0.6)' };
    }

    // Dynamic HSL hash for any other player
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    const h = Math.abs(hash) % 360;
    return {
        bg: `hsla(${h}, 85%, 50%, 0.22)`,
        color: `hsl(${h}, 95%, 68%)`,
        border: `hsla(${h}, 85%, 50%, 0.5)`
    };
}

function updateWinnerBadges() {
    document.querySelectorAll('.badge-win, [data-player-badge], [data-player]').forEach(el => {
        const playerName = el.getAttribute('data-player') || el.textContent.trim();
        if (playerName && playerName !== 'Tie' && playerName !== '—' && !playerName.includes('vs')) {
            const styles = getPlayerColor(playerName);
            el.style.backgroundColor = styles.bg;
            el.style.color = styles.color;
            el.style.borderColor = styles.border;
        }
    });
}

function setupThemeToggle() {
    ['theme-toggle', 'theme-toggle-topbar'].forEach(id => {
        const btn = document.getElementById(id);
        if (!btn) return;

        btn.addEventListener('click', () => {
            const cur = document.documentElement.getAttribute('data-theme');
            const next = cur === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            updateToggleIcons(next);
            updateWinnerBadges();
        });
    });
}

function updateToggleIcons(theme) {
    const icon = document.getElementById('theme-toggle-icon');
    if (icon) {
        icon.textContent = theme === 'dark' ? 'Light' : 'Dark';
    }
    const topbarBtn = document.getElementById('theme-toggle-topbar');
    if (topbarBtn) {
        topbarBtn.textContent = theme === 'dark' ? '☀︎' : '☾';
    }
}

function setupMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    const menuBtn = document.getElementById('mobile-menu-btn');
    const backdrop = document.getElementById('sidebar-backdrop');
    if (!sidebar || !menuBtn || !backdrop) return;

    const setOpen = (isOpen) => {
        sidebar.classList.toggle('open', isOpen);
        backdrop.classList.toggle('show', isOpen);
        menuBtn.classList.toggle('is-open', isOpen);
        menuBtn.setAttribute('aria-expanded', String(isOpen));
        document.body.classList.toggle('nav-open', isOpen);
    };

    menuBtn.addEventListener('click', () => setOpen(!sidebar.classList.contains('open')));
    backdrop.addEventListener('click', () => setOpen(false));
    sidebar.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            if (window.matchMedia('(max-width: 1100px)').matches) setOpen(false);
        });
    });
    window.addEventListener('keydown', event => {
        if (event.key === 'Escape') setOpen(false);
    });
}

