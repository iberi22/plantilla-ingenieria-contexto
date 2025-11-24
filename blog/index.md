---
layout: default
---

<div class="home">

  <div style="text-align: center; margin-bottom: 60px;">
    <h1 style="font-size: 3rem; margin-bottom: 10px; background: linear-gradient(to right, #3b82f6, #a855f7); -webkit-background-clip: text; color: transparent;">
      Discover Open Source Gems
    </h1>
    <p style="font-size: 1.2rem; color: #94a3b8;">
      AI-generated summaries and video reels of the hottest GitHub repositories.
    </p>
  </div>

  <ul class="post-list">
    {% for post in site.posts %}
      <li>
        <a class="post-card" href="{{ post.url | relative_url }}" style="display: block; text-decoration: none;">
          <span class="post-meta">{{ post.date | date: "%b %-d, %Y" }}</span>
          <h2 class="post-title">{{ post.title | escape }}</h2>
          <p class="post-excerpt">{{ post.excerpt | strip_html | truncatewords: 30 }}</p>
          <span style="color: var(--accent-color); font-weight: 500; margin-top: 10px; display: block;">Read Analysis &rarr;</span>
        </a>
      </li>
    {% endfor %}
  </ul>

</div>
