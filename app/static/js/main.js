// GlobeTrotter - Main JavaScript Utilities

document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            alert.style.transition = 'all 0.4s ease';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });

    // Alert close button handlers
    document.querySelectorAll('.alert-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const alert = e.target.closest('.alert');
            if (alert) alert.remove();
        });
    });

    // Modal helpers
    window.openModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    };

    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    };

    // Close modal on clicking backdrop
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });

    // Destination Wishlist Save / Bookmark Toggle
    document.querySelectorAll('.btn-save-destination').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const cityId = btn.getAttribute('data-city-id');
            if (!cityId) return;

            try {
                const res = await fetch(`/api/save-destination/${cityId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                if (res.redirected) {
                    window.location.href = res.url;
                    return;
                }
                const data = await res.json();
                if (data.saved) {
                    btn.classList.add('btn-saved');
                    btn.innerHTML = '<i class="fa-solid fa-heart text-rose"></i> Saved';
                    showToast(data.message, 'success');
                } else {
                    btn.classList.remove('btn-saved');
                    btn.innerHTML = '<i class="fa-regular fa-heart"></i> Save';
                    showToast(data.message, 'info');
                }
            } catch (err) {
                console.error('Error saving destination:', err);
            }
        });
    });

    // Trip Like / Bookmark Toggle in Community
    document.querySelectorAll('.btn-like-trip').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const tripId = btn.getAttribute('data-trip-id');
            if (!tripId) return;

            try {
                const res = await fetch(`/community/trips/${tripId}/like`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                if (res.redirected) {
                    window.location.href = res.url;
                    return;
                }
                const data = await res.json();
                if (data.success) {
                    const icon = btn.querySelector('i');
                    const countSpan = btn.querySelector('.like-count');
                    if (data.liked) {
                        icon.className = 'fa-solid fa-heart text-rose';
                    } else {
                        icon.className = 'fa-regular fa-heart';
                    }
                    if (countSpan) countSpan.textContent = data.like_count;
                }
            } catch (err) {
                console.error('Error liking trip:', err);
            }
        });
    });

    // Copy to clipboard helper
    window.copyToClipboard = function(text, successMessage = 'Copied to clipboard!') {
        navigator.clipboard.writeText(text).then(() => {
            showToast(successMessage, 'success');
        }).catch(err => {
            console.error('Could not copy text: ', err);
        });
    };

    // Toast notification generator
    window.showToast = function(message, type = 'info') {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.position = 'fixed';
            container.style.bottom = '20px';
            container.style.right = '20px';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `alert alert-${type}`;
        toast.style.boxShadow = '0 10px 15px -3px rgba(0,0,0,0.1)';
        toast.innerHTML = `
            <span>${message}</span>
            <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
        `;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    };
});
