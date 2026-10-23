export default function BrandLogo() {
  return (
    <a href="/" className="brand">
      <div className="brand-mark">
        <svg viewBox="0 0 20 20">
          <path d="M10 2L3 6.5V14l7 4.5 7-4.5V6.5z" opacity=".9" />
          <path d="M10 2v16.5M3 6.5l7 4 7-4" stroke="rgba(255,255,255,.45)" strokeWidth="1" fill="none" />
        </svg>
      </div>
      <div>
        <div className="brand-name">ContribIQ</div>
        <div className="brand-tag">Open-Source Onboarding</div>
      </div>
    </a>
  )
}
