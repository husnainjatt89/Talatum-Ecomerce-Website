/**
 * Talatum E-Commerce — Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {

  /* ── Auto-dismiss toasts ── */
  const toastEls = document.querySelectorAll('.toast');
  toastEls.forEach(function (toastEl) {
    const bsToast = bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 4000 });
    bsToast.show();
    toastEl.addEventListener('hidden.bs.toast', function () {
      toastEl.remove();
    });
  });

  /* ── Back to Top ── */
  const backToTop = document.querySelector('.back-to-top');
  if (backToTop) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 300) {
        backToTop.classList.add('show');
      } else {
        backToTop.classList.remove('show');
      }
    });
    backToTop.addEventListener('click', function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ── Sticky Navbar Shadow ── */
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 10) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    });
  }

  /* ── Theme Toggle ── */
  const themeToggle = document.getElementById('themeToggle');
  const htmlEl = document.documentElement;

  function applyTheme(theme) {
    htmlEl.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    const icon = document.getElementById('themeIcon');
    if (icon) {
      icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
    if (themeToggle) {
      themeToggle.title = theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
    }
  }

  // Apply saved theme on load (icon sync — HTML attr already set by inline script)
  const savedTheme = localStorage.getItem('theme') || 'light';
  applyTheme(savedTheme);

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      const current = htmlEl.getAttribute('data-theme') || 'light';
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

  /* ── Search Suggestions ── */
  const searchInput = document.getElementById('searchInput');
  const searchSuggestions = document.getElementById('searchSuggestions');

  function debounce(fn, delay) {
    let timer;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  function renderSuggestions(items) {
    if (!searchSuggestions) return;
    if (!items || items.length === 0) {
      searchSuggestions.classList.remove('show');
      searchSuggestions.innerHTML = '';
      return;
    }
    searchSuggestions.innerHTML = items.map(function (item) {
      return `<div class="suggestion-item" data-url="${item.url || '/products/' + item.id}">
        <span>${item.name}</span>
        <span class="suggestion-price">${item.price ? item.price + ' TL' : ''}</span>
      </div>`;
    }).join('');
    searchSuggestions.classList.add('show');

    searchSuggestions.querySelectorAll('.suggestion-item').forEach(function (el) {
      el.addEventListener('click', function () {
        window.location.href = el.dataset.url;
      });
    });
  }

  if (searchInput && searchSuggestions) {
    const fetchSuggestions = debounce(function (q) {
      if (q.length < 2) {
        searchSuggestions.classList.remove('show');
        return;
      }
      fetch('/api/search/suggestions?q=' + encodeURIComponent(q))
        .then(function (res) { return res.json(); })
        .then(function (data) { renderSuggestions(data.results || data); })
        .catch(function () { searchSuggestions.classList.remove('show'); });
    }, 300);

    searchInput.addEventListener('input', function () {
      fetchSuggestions(this.value.trim());
    });

    document.addEventListener('click', function (e) {
      if (!searchInput.contains(e.target) && !searchSuggestions.contains(e.target)) {
        searchSuggestions.classList.remove('show');
      }
    });
  }

  /* ── Add to Cart AJAX ── */
  document.querySelectorAll('.add-cart-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(form);
      const url = form.action || '/cart/add';

      fetch(url, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
        .then(function (res) { return res.json(); })
        .then(function (data) {
          if (data.success || data.cart_count !== undefined) {
            // Update cart badge
            const cartBadges = document.querySelectorAll('.cart-badge-count, .badge-count[data-badge="cart"]');
            cartBadges.forEach(function (badge) {
              badge.textContent = data.cart_count || '';
              badge.style.display = data.cart_count ? 'flex' : 'none';
            });
            showToast(data.message || 'Added to cart!', 'success');
          } else {
            showToast(data.message || 'Could not add to cart.', 'danger');
          }
        })
        .catch(function () {
          showToast('An error occurred. Please try again.', 'danger');
        });
    });
  });

  /* ── Wishlist AJAX ── */
  document.querySelectorAll('.wishlist-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(form);
      const url = form.action || '/wishlist/toggle';
      const btn = form.querySelector('.wishlist-btn');

      fetch(url, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
        .then(function (res) { return res.json(); })
        .then(function (data) {
          // Update wish count badge
          const wishBadges = document.querySelectorAll('.wish-badge-count, .badge-count[data-badge="wish"]');
          wishBadges.forEach(function (badge) {
            badge.textContent = data.wish_count || '';
            badge.style.display = data.wish_count ? 'flex' : 'none';
          });
          // Toggle heart color
          if (btn) {
            if (data.in_wishlist) {
              btn.classList.add('active');
              const icon = btn.querySelector('i');
              if (icon) { icon.className = 'fas fa-heart'; }
            } else {
              btn.classList.remove('active');
              const icon = btn.querySelector('i');
              if (icon) { icon.className = 'far fa-heart'; }
            }
          }
          showToast(data.message || (data.in_wishlist ? 'Added to wishlist!' : 'Removed from wishlist.'), 'success');
        })
        .catch(function () {
          showToast('An error occurred.', 'danger');
        });
    });
  });

  /* ── Newsletter Forms ── */
  ['newsletterForm', 'footerNewsletter'].forEach(function (id) {
    const form = document.getElementById(id);
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(form);
      fetch('/newsletter/subscribe', {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
        .then(function (res) { return res.json(); })
        .then(function (data) {
          showToast(data.message || 'Subscribed successfully!', data.success ? 'success' : 'warning');
          if (data.success) { form.reset(); }
        })
        .catch(function () {
          showToast('Subscription failed. Please try again.', 'danger');
        });
    });
  });

  /* ── Smooth Scroll for Anchor Links ── */
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* ── Lazy Loading Images ── */
  if ('IntersectionObserver' in window) {
    const lazyImages = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          if (img.dataset.srcset) { img.srcset = img.dataset.srcset; }
          img.removeAttribute('data-src');
          imageObserver.unobserve(img);
        }
      });
    }, { rootMargin: '100px' });

    lazyImages.forEach(function (img) { imageObserver.observe(img); });
  }

  /* ── Mobile Search Toggle ── */
  const mobileSearchToggle = document.getElementById('mobileSearchToggle');
  const mobileSearchBar = document.getElementById('mobileSearchBar');
  if (mobileSearchToggle && mobileSearchBar) {
    mobileSearchToggle.addEventListener('click', function () {
      mobileSearchBar.classList.toggle('show');
      if (mobileSearchBar.classList.contains('show')) {
        const inp = mobileSearchBar.querySelector('input');
        if (inp) inp.focus();
      }
    });
  }

}); // end DOMContentLoaded

/* ── Toggle Password Visibility ── */
function togglePassword(inputId, iconEl) {
  const input = document.getElementById(inputId);
  if (!input) return;
  if (input.type === 'password') {
    input.type = 'text';
    if (iconEl) { iconEl.className = iconEl.className.replace('fa-eye', 'fa-eye-slash'); }
  } else {
    input.type = 'password';
    if (iconEl) { iconEl.className = iconEl.className.replace('fa-eye-slash', 'fa-eye'); }
  }
}

/* ── Toast Helper ── */
function showToast(message, type) {
  type = type || 'success';
  const container = document.getElementById('toastContainer') || createToastContainer();
  const id = 'toast-' + Date.now();
  const bgClass = {
    success: 'bg-success',
    danger:  'bg-danger',
    warning: 'bg-warning text-dark',
    info:    'bg-info text-dark'
  }[type] || 'bg-secondary';

  const html = `<div id="${id}" class="toast align-items-center text-white ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  </div>`;
  container.insertAdjacentHTML('beforeend', html);
  const toastEl = document.getElementById(id);
  const bsToast = new bootstrap.Toast(toastEl, { delay: 4000 });
  bsToast.show();
  toastEl.addEventListener('hidden.bs.toast', function () { toastEl.remove(); });
}

function createToastContainer() {
  const div = document.createElement('div');
  div.id = 'toastContainer';
  div.className = 'toast-container position-fixed bottom-0 end-0 p-3';
  div.style.zIndex = '9999';
  document.body.appendChild(div);
  return div;
}
