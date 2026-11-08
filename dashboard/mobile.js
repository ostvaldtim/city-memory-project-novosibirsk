/* Mobile-only navigation layer. Desktop behavior remains unchanged. */
(function () {
    'use strict';
    const mobileMedia = window.matchMedia('(max-width: 1200px)');
    const detailsPanel = document.getElementById('details-sidebar');
    const analyticsPanel = document.getElementById('analytics-sidebar');
    const analyticsButton = document.getElementById('mobile-analytics-btn');

    window.openMobileAnalytics = function () {
        if (!mobileMedia.matches || !analyticsPanel) return;
        closeMobileDetails();
        analyticsPanel.classList.add('is-open');
        if (analyticsButton) analyticsButton.setAttribute('aria-expanded', 'true');
    };
    window.closeMobileAnalytics = function () {
        if (!analyticsPanel) return;
        analyticsPanel.classList.remove('is-open');
        if (analyticsButton) analyticsButton.setAttribute('aria-expanded', 'false');
    };
    window.openMobileDetails = function () {
        if (!mobileMedia.matches || !detailsPanel) return;
        closeMobileAnalytics();
        detailsPanel.classList.add('is-open');
        document.body.classList.add('mobile-details-open');
        const card = detailsPanel.querySelector('#detail-panel');
        if (card) card.scrollTop = 0;
    };
    window.closeMobileDetails = function () {
        if (!detailsPanel) return;
        detailsPanel.classList.remove('is-open');
        document.body.classList.remove('mobile-details-open');
    };

    // Reuse existing map/search/gallery logic: only alter panel presentation.
    if (typeof window.showDetails === 'function') {
        const original = window.showDetails;
        window.showDetails = function (...args) {
            const result = original.apply(this, args);
            openMobileDetails();
            return result;
        };
    }
    if (typeof window.scrollToDetailPanel === 'function') {
        const originalScroll = window.scrollToDetailPanel;
        window.scrollToDetailPanel = function (...args) {
            if (mobileMedia.matches) return;
            return originalScroll.apply(this, args);
        };
    }
    if (typeof window.focusOnMapForDetail === 'function') {
        const originalFocus = window.focusOnMapForDetail;
        window.focusOnMapForDetail = function (...args) {
            closeMobileDetails();
            return originalFocus.apply(this, args);
        };
    }
    document.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape' || !mobileMedia.matches) return;
        if (analyticsPanel && analyticsPanel.classList.contains('is-open')) {
            closeMobileAnalytics(); event.stopPropagation();
        } else if (detailsPanel && detailsPanel.classList.contains('is-open')) {
            closeMobileDetails(); event.stopPropagation();
        }
    });
    window.addEventListener('resize', function () {
        if (!mobileMedia.matches) {
            closeMobileAnalytics();
            closeMobileDetails();
        }
        if (typeof map !== 'undefined' && map && typeof map.invalidateSize === 'function') {
            requestAnimationFrame(() => map.invalidateSize());
        }
    });
})();
