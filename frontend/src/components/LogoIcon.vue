<template>
  <svg :width="size" :height="size" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="logo-bg" x1="0" y1="0" x2="100" y2="100">
        <stop offset="0%" stop-color="var(--color-white, #ffffff)"/>
        <stop offset="100%" stop-color="var(--color-hover, #eaf2e6)"/>
      </linearGradient>
    </defs>
    <rect width="100" height="100" rx="20" fill="url(#logo-bg)"/>
    <circle cx="50" cy="50" r="42" stroke="var(--color-primary, #7AA35A)" stroke-width="3" fill="none"/>
    <circle cx="50" cy="50" r="34" stroke="var(--color-border, #cddbc8)" stroke-width="1.5" stroke-dasharray="3 3" fill="none"/>
    <line x1="50" y1="6" x2="50" y2="14" stroke="var(--color-primary, #7AA35A)" stroke-width="3" stroke-linecap="round"/>
    <line x1="50" y1="86" x2="50" y2="94" stroke="var(--color-secondary, #9ABE7A)" stroke-width="2.5" stroke-linecap="round"/>
    <line x1="6" y1="50" x2="14" y2="50" stroke="var(--color-secondary, #9ABE7A)" stroke-width="2.5" stroke-linecap="round"/>
    <line x1="94" y1="50" x2="86" y2="50" stroke="var(--color-secondary, #9ABE7A)" stroke-width="2.5" stroke-linecap="round"/>
    <text x="50" y="22" text-anchor="middle" fill="var(--color-primary, #7AA35A)" font-size="9" font-weight="700" font-family="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">N</text>
    <polygon points="50,16 44,50 50,47 56,50" fill="var(--color-danger, #d85c5c)"/>
    <polygon points="50,84 44,50 50,53 56,50" fill="var(--color-text, #2d3b24)"/>
    <circle cx="50" cy="50" r="4.5" fill="var(--color-primary, #7AA35A)"/>
  </svg>
</template>

<script setup lang="ts">
defineProps<{
  size?: number
}>()
</script>
