import { ArrowDownRight, ArrowRight, BarChart3, Check, ChevronRight, Link2, MousePointer2, ShieldCheck, Sparkles, Zap } from "lucide-react";
import { Link } from "react-router-dom";

const features = [
    { icon: Zap, title: "Links in a blink", copy: "Turn long URLs into clean, memorable links in seconds." },
    { icon: BarChart3, title: "Know what works", copy: "See every click and understand which campaigns connect." },
    { icon: ShieldCheck, title: "Always in control", copy: "Set custom aliases, expiration dates, and manage links in one place." },
];

export default function Home() {
    return (
        <main className="landing-page">
            <header className="landing-nav">
                <Link className="landing-brand" to="/"><img className="brand-image" src="/snipp-logo.png" alt="" />Snipp<span className="brand-period">.</span></Link>
                <nav className="landing-nav-links" aria-label="Main navigation">
                    <a href="#features">Features</a>
                    <a href="#how-it-works">How it works</a>
                </nav>
                <div className="landing-actions">
                    <Link className="nav-login" to="/login">Log in</Link>
                    <Link className="nav-signup" to="/register">Create account<ArrowRight size={15} /></Link>
                </div>
            </header>

            <section className="hero-section">
                <div className="hero-copy">
                    <div className="announcement"><Sparkles size={14} /> A little link goes a long way <ChevronRight size={14} /></div>
                    <h1>Make every link<br /> <span>go further.</span></h1>
                    <p className="hero-lede">Shorten, share, and understand your links. A simpler way to make every click count.</p>
                    <div className="hero-actions">
                        <Link className="hero-cta" to="/register">Create account <ArrowRight size={17} /></Link>
                        <a className="hero-secondary" href="#features">Explore features <ArrowDownRight size={16} /></a>
                    </div>
                    <div className="social-proof"><div className="avatar-stack"><span>J</span><span>M</span><span>A</span><span>+</span></div><p><strong>Made for the curious.</strong><br />Built for the links you share every day.</p></div>
                </div>

                <div className="hero-art" aria-label="Short link analytics preview">
                    <div className="orbit orbit-one" /><div className="orbit orbit-two" />
                    <div className="floating-chip chip-top"><span className="chip-dot" /> Link is live</div>
                    <div className="preview-card">
                    <div className="preview-head"><span className="preview-logo"><img src="/snipp-logo.png" alt="" /></span><span>Link overview</span><span className="preview-menu">•••</span></div>
                        <div className="preview-link"><span>Snipp.app/</span><strong>summer-notes</strong><button aria-label="Copy link"><Link2 size={15} /></button></div>
                        <div className="preview-summary"><div><span>Total clicks</span><strong>2,846 <small>↗ 18.6%</small></strong></div><span className="summary-icon"><MousePointer2 size={18} /></span></div>
                        <div className="chart-label"><span>Click activity</span><span>Last 7 days⌄</span></div>
                        <div className="mini-chart" aria-hidden="true"><div className="chart-gridline" /><svg viewBox="0 0 420 116" preserveAspectRatio="none"><defs><linearGradient id="chartFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="#fe8b64" stopOpacity=".28" /><stop offset="1" stopColor="#fe8b64" stopOpacity="0" /></linearGradient></defs><path d="M0 95 C25 90 31 72 58 79 S90 85 112 55 S151 67 174 48 S206 54 231 36 S264 53 286 29 S315 42 342 18 S372 38 397 10 S411 18 420 6 V116 H0Z" fill="url(#chartFill)"/><path d="M0 95 C25 90 31 72 58 79 S90 85 112 55 S151 67 174 48 S206 54 231 36 S264 53 286 29 S315 42 342 18 S372 38 397 10 S411 18 420 6" fill="none" stroke="#ef7954" strokeWidth="3" strokeLinecap="round" /></svg></div>
                        <div className="chart-days"><span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span></div>
                    </div>
                    <div className="floating-chip chip-bottom"><span className="chip-check"><Check size={13} /></span> Your next great link</div>
                    <div className="hero-spark spark-one">✳</div><div className="hero-spark spark-two">✳</div>
                </div>
                <a className="scroll-cue" href="#features">Scroll to explore <span /></a>
            </section>

            <section className="features-section" id="features">
                <div className="features-intro"><p className="landing-kicker">A better way to share</p><h2>Everything clicks<br /><em>into place.</em></h2><p>All the little things that make sharing links feel a lot less complicated.</p></div>
                <div className="feature-grid">{features.map(({ icon: Icon, title, copy }, index) => <article className="feature-card" key={title}><span className={`feature-icon feature-icon-${index}`}><Icon size={20} /></span><span className="feature-number">0{index + 1}</span><h3>{title}</h3><p>{copy}</p></article>)}</div>
            </section>

            <section className="how-section" id="how-it-works"><div><p className="landing-kicker">Less fuss, more focus</p><h2>From long link<br />to <em>look at that.</em></h2></div><div className="how-steps"><div><span>01</span><p><strong>Paste your link</strong><br />Start with any URL you want to share.</p></div><div><span>02</span><p><strong>Make it yours</strong><br />Choose a short alias and set it up your way.</p></div><div><span>03</span><p><strong>Share & learn</strong><br />Send it out, then see how it performs.</p></div></div></section>

            <section className="closing-cta"><div><p className="landing-kicker">Your next link starts here</p><h2>Ready to make a<br />little link magic?</h2></div><Link className="hero-cta" to="/register">Create account <ArrowRight size={17} /></Link><span className="cta-doodle">✳</span></section>

            <footer className="site-footer"><div className="footer-main"><div className="footer-brand-col"><Link className="landing-brand" to="/"><img className="brand-image" src="/snipp-logo.png" alt="" />Snipp<span className="brand-period">.</span></Link><p>Small links. Big possibilities.</p></div><div className="footer-links"><div><strong>Explore</strong><a href="#features">Features</a><a href="#how-it-works">How it works</a></div><div><strong>Get started</strong><Link to="/login">Log in</Link><Link to="/register">Create account</Link></div><div><strong>Say hello</strong><a href="mailto:hello@snipp.app">hello@snipp.app</a><span>Made with care, everywhere.</span></div></div></div><div className="footer-bottom"><span>© {new Date().getFullYear()} Snipp. All rights reserved.</span><div><a href="mailto:hello@snipp.app?subject=Privacy">Privacy</a><a href="mailto:hello@snipp.app?subject=Terms">Terms</a><span>Built for better sharing <span className="footer-heart">♥</span></span></div></div></footer>
        </main>
    );
}
