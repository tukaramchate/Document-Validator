import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
    ShieldCheck,
    Zap,
    Search,
    Database,
    AlertTriangle,
    FileText,
    Cpu,
    FileUp,
    CheckCircle,
    ArrowRight,
    MousePointerClick,
    Activity,
    CloudUpload
} from 'lucide-react';

export default function Landing() {
    const { isAuthenticated } = useAuth();
    const ctaPath = isAuthenticated ? '/dashboard' : '/register';
    const ctaLabel = isAuthenticated ? 'Go to Dashboard' : 'Get Started Free';

    const features = [
        {
            icon: Cpu,
            title: 'AI-Powered Analysis',
            desc: 'Deep learning CNN model analyzes visual patterns and detects forgery with high accuracy.',
        },
        {
            icon: FileText,
            title: 'OCR Verification',
            desc: 'Extracts text from documents and cross-references it against database records.',
        },
        {
            icon: Database,
            title: 'Database Matching',
            desc: 'Every field is verified against trusted records for comprehensive validation.',
        },
        {
            icon: Zap,
            title: 'Instant Results',
            desc: 'Get a detailed authenticity score with breakdown in seconds, not hours.',
        },
        {
            icon: ShieldCheck,
            title: 'Three-Tier Verdict',
            desc: 'Clear Authentic, Suspicious, or Fake verdicts based on combined scoring.',
        },
        {
            icon: Activity,
            title: 'Detailed Reports',
            desc: 'Visual score breakdowns, extracted data, and field-by-field match reports.',
        },
    ];

    const steps = [
        {
            num: '01',
            title: 'Upload Document',
            desc: 'Drag and drop or browse to upload your PDF, JPG, or PNG document.',
            icon: FileUp,
        },
        {
            num: '02',
            title: 'AI Analysis',
            desc: 'Our CNN model, OCR engine, and database work together to analyze your document.',
            icon: Cpu,
        },
        {
            num: '03',
            title: 'Get Verdict',
            desc: 'Receive a detailed report with authenticity score, breakdown, and verification results.',
            icon: CheckCircle,
        },
    ];

    return (
        <div className="min-h-screen bg-surface-950 transition-colors duration-300">
            {/* Background */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-[500px] h-[500px] bg-brand-600/8 rounded-full blur-3xl" />
                <div className="absolute top-1/2 -left-40 w-[400px] h-[400px] bg-brand-500/6 rounded-full blur-3xl" />
                <div className="absolute -bottom-40 right-1/3 w-[350px] h-[350px] bg-brand-400/5 rounded-full blur-3xl" />
            </div>

            {/* Nav */}
            <nav className="relative z-20 border-b border-surface-800/20 backdrop-blur-xl bg-surface-950/60">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                    <Link to="/" className="flex items-center gap-2.5 group">
                        <div className="w-9 h-9 bg-gradient-to-br from-brand-500 to-brand-700 rounded-xl flex items-center justify-center shadow-lg shadow-brand-500/20 group-hover:shadow-brand-500/40 transition-all duration-300">
                            <ShieldCheck className="text-white w-5 h-5" />
                        </div>
                        <span className="text-lg font-bold bg-gradient-to-r from-brand-400 to-brand-200 bg-clip-text text-transparent">
                            EduVerify AI
                        </span>
                    </Link>
                    <div className="flex items-center gap-2 sm:gap-4">
                        {isAuthenticated ? (
                            <Link to="/dashboard" className="btn-primary text-sm px-4 py-2 rounded-xl">Dashboard</Link>
                        ) : (
                            <>
                                <Link to="/login" className="text-sm font-medium text-surface-400 hover:text-surface-100 px-3 py-2 transition-colors">
                                    Sign In
                                </Link>
                                <Link to="/register" className="btn-primary text-sm px-5 py-2.5 rounded-xl shadow-lg shadow-brand-500/20">
                                    Get Started
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </nav>

            <div className="relative z-10">
                {/* ─── Hero ─── */}
                <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24 sm:pt-28 sm:pb-32 text-center">
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-600/10 border border-brand-500/20 text-brand-400 text-xs font-semibold mb-8 animate-fade-in">
                        <Activity size={14} className="animate-pulse" />
                        <span>AI-Powered Document Verification</span>
                    </div>

                    <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black text-surface-100 leading-[1.1] tracking-tight animate-fade-in">
                        Truth at the Core
                        <br />
                        <span className="bg-gradient-to-r from-brand-400 via-brand-300 to-brand-500 bg-clip-text text-transparent">
                            of Technology
                        </span>
                    </h1>

                    <p className="mt-8 text-lg sm:text-xl text-surface-400 max-w-2xl mx-auto leading-relaxed animate-fade-in font-medium">
                        EduVerify AI provides instant, AI-powered document verification for academic and professional credentials. Fast, secure, and built for maximum integrity.
                    </p>

                    <div className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in">
                        <Link to={ctaPath} className="btn-primary text-base px-10 py-4 rounded-2xl shadow-xl shadow-brand-500/25 hover:shadow-brand-500/40 hover:-translate-y-0.5 transition-all flex items-center gap-2">
                            <span>{ctaLabel}</span>
                            <ArrowRight size={20} />
                        </Link>
                        <a href="#how-it-works" className="text-surface-400 hover:text-surface-100 font-semibold text-base px-8 py-4 transition-all flex items-center gap-2 group">
                            <span>See how it works</span>
                            <MousePointerClick size={18} className="group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                        </a>
                    </div>

                    {/* Stats */}
                    <div className="mt-20 grid grid-cols-3 max-w-xl mx-auto gap-8 sm:gap-12 animate-fade-in bg-surface-900/40 backdrop-blur-md border border-surface-800/50 p-6 sm:p-8 rounded-[2.5rem]">
                        {[
                            { value: '3-Layer', label: 'AI Analysis', icon: Cpu },
                            { value: '<10s', label: 'Avg. Time', icon: Zap },
                            { value: '99%', label: 'Accuracy', icon: ShieldCheck },
                        ].map(({ value, label, icon: Icon }) => (
                            <div key={label} className="flex flex-col items-center">
                                <Icon className="text-brand-500/40 mb-3" size={24} />
                                <div className="text-2xl sm:text-3xl font-black text-surface-100 tracking-tight">{value}</div>
                                <div className="text-[10px] uppercase tracking-widest text-surface-500 font-bold mt-1">{label}</div>
                            </div>
                        ))}
                    </div>
                </section>

                {/* ─── Features ─── */}
                <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-24" id="features">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl sm:text-5xl font-black text-surface-100 tracking-tight">
                            Detect fraud with
                            <span className="bg-gradient-to-r from-brand-400 to-brand-300 bg-clip-text text-transparent"> confidence</span>
                        </h2>
                        <p className="mt-4 text-surface-400 max-w-xl mx-auto font-medium">
                            A multi-layered approach to document verification that leaves no room for doubt.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {features.map(({ icon: Icon, title, desc }, i) => (
                            <div
                                key={title}
                                className="group p-8 rounded-[2rem] bg-surface-900/40 border border-surface-800/40 hover:border-brand-500/30 hover:bg-surface-800/40 transition-all duration-300 animate-slide-up relative overflow-hidden"
                                style={{ animationDelay: `${i * 80}ms` }}
                            >
                                <div className="absolute top-0 right-0 p-8 text-brand-500/5 group-hover:text-brand-500/10 transition-colors">
                                    <Icon size={80} />
                                </div>
                                <div className="w-14 h-14 bg-brand-500/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 group-hover:bg-brand-500/20 transition-all duration-300">
                                    <Icon className="text-brand-400" size={28} />
                                </div>
                                <h3 className="text-xl font-bold text-surface-100 mb-3">{title}</h3>
                                <p className="text-surface-400 text-sm leading-relaxed font-medium">{desc}</p>
                            </div>
                        ))}
                    </div>
                </section>

                {/* ─── How It Works ─── */}
                <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-24" id="how-it-works">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl sm:text-5xl font-black text-surface-100 tracking-tight">
                            Simple
                            <span className="bg-gradient-to-r from-brand-400 to-brand-300 bg-clip-text text-transparent"> workflow</span>
                        </h2>
                        <p className="mt-4 text-surface-400 max-w-xl mx-auto font-medium">
                            Three steps from upload to verified result.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                        {steps.map(({ num, title, desc, icon: Icon }, i) => (
                            <div key={num} className="relative text-center animate-slide-up" style={{ animationDelay: `${i * 120}ms` }}>
                                {/* Connector line */}
                                {i < steps.length - 1 && (
                                    <div className="hidden md:block absolute top-[4.5rem] left-[60%] w-[80%] h-px bg-gradient-to-r from-brand-500/30 via-brand-500/10 to-transparent" />
                                )}

                                <div className="inline-flex items-center justify-center w-20 h-20 bg-surface-900/60 border border-surface-800/50 rounded-3xl mb-8 relative group">
                                    <div className="absolute inset-0 bg-brand-500/5 rounded-3xl group-hover:bg-brand-500/10 transition-colors" />
                                    <Icon className="text-brand-400 relative z-10" size={36} />
                                    <span className="absolute -top-3 -right-3 w-8 h-8 bg-brand-600 text-white text-xs font-black rounded-full flex items-center justify-center shadow-lg shadow-brand-600/20 border-2 border-surface-950">
                                        {num}
                                    </span>
                                </div>

                                <h3 className="text-2xl font-bold text-surface-100 mb-4">{title}</h3>
                                <p className="text-surface-400 text-sm leading-relaxed max-w-[280px] mx-auto font-medium">{desc}</p>
                            </div>
                        ))}
                    </div>

                    <div className="text-center mt-20">
                        <Link to={ctaPath} className="btn-primary text-lg px-12 py-4.5 rounded-2xl shadow-xl shadow-brand-500/25 flex items-center gap-3 mx-auto w-fit">
                            <span>{ctaLabel}</span>
                            <ArrowRight size={22} />
                        </Link>
                    </div>
                </section>

                {/* ─── Footer ─── */}
                <footer className="border-t border-surface-800/20 mt-12 bg-surface-950/50 backdrop-blur-sm">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex flex-col sm:flex-row items-center justify-between gap-6">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-gradient-to-br from-brand-500 to-brand-700 rounded-lg flex items-center justify-center shadow-md">
                                <ShieldCheck className="text-white w-4.5 h-4.5" />
                            </div>
                            <span className="font-bold text-surface-200">EduVerify AI</span>
                        </div>
                        <div className="text-xs text-surface-500 font-medium tracking-wide">
                            © {new Date().getFullYear()} EduVerify AI. Built for maximum trust.
                        </div>
                    </div>
                </footer>
            </div>
        </div>
    );
}
