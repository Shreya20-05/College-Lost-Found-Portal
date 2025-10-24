document.addEventListener('DOMContentLoaded', function() {
    
    // --- Logic for Admin Dashboard Filtering ---
    const adminControls = document.querySelector('.admin-controls');
    if (adminControls) {
        const showAllBtn = document.getElementById('showAllBtn');
        const showLostBtn = document.getElementById('showLostBtn');
        const showFoundBtn = document.getElementById('showFoundBtn');
        const itemCards = document.querySelectorAll('.item-card');
        const filterButtons = adminControls.querySelectorAll('button');

        function filterAdminItems(type) {
            itemCards.forEach(card => {
                if (type === 'all' || card.dataset.type === type) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        }

        function setAdminActiveButton(activeBtn) {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            activeBtn.classList.add('active');
        }

        showAllBtn.addEventListener('click', () => {
            filterAdminItems('all');
            setAdminActiveButton(showAllBtn);
        });
        showLostBtn.addEventListener('click', () => {
            filterAdminItems('lost');
            setAdminActiveButton(showLostBtn);
        });
        showFoundBtn.addEventListener('click', () => {
            filterAdminItems('found');
            setAdminActiveButton(showFoundBtn);
        });
    }

    // --- Logic for Student Report Page Toggles ---
    const reportToggle = document.querySelector('.report-toggle-buttons');
    if (reportToggle) {
        const showLostFormBtn = document.getElementById('showLostFormBtn');
        const showFoundFormBtn = document.getElementById('showFoundFormBtn');
        const lostForm = document.getElementById('lostFormContainer');
        const foundForm = document.getElementById('foundFormContainer');

        showLostFormBtn.addEventListener('click', () => {
            lostForm.classList.remove('hidden');
            foundForm.classList.add('hidden');
            showLostFormBtn.classList.add('active');
            showFoundFormBtn.classList.remove('active');
        });

        showFoundFormBtn.addEventListener('click', () => {
            foundForm.classList.remove('hidden');
            lostForm.classList.add('hidden');
            showFoundFormBtn.classList.add('active');
            showLostFormBtn.classList.remove('active');
        });
    }
});

