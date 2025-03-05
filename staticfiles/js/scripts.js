document.addEventListener('DOMContentLoaded', () => {
    const searchToggler = document.getElementById('search-toggler');
    const mobileSearch = document.getElementById('mobile-search');
  
    searchToggler.addEventListener('click', () => {
      const bsCollapse = new bootstrap.Collapse(mobileSearch, { toggle: true });
    });
  });