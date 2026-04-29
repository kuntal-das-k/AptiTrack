/* AptiTrack Global JS */
document.addEventListener('DOMContentLoaded', function() {
  // Mobile menu toggle
  const hamburger = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-links');
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => navLinks.classList.toggle('open'));
  }

  // Auto-dismiss messages after 5s
  document.querySelectorAll('.messages li').forEach(msg => {
    setTimeout(() => {
      msg.style.opacity = '0';
      msg.style.transform = 'translateX(100%)';
      setTimeout(() => msg.remove(), 300);
    }, 5000);
  });

  // Bookmark toggle (AJAX)
  document.querySelectorAll('.bookmark-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      const qid = this.dataset.questionId;
      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content
        || document.querySelector('[name=csrfmiddlewaretoken]')?.value 
        || getCookie('csrftoken');
      
      fetch(`/bookmark/${qid}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json',
        },
      })
      .then(r => r.json())
      .then(data => {
        this.classList.toggle('active', data.bookmarked);
        this.textContent = data.bookmarked ? '★' : '☆';
      });
    });
  });
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
