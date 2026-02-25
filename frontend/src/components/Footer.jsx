import { Link } from 'react-router-dom';
import { ShieldCheck, Github, Twitter, Linkedin, Mail, ArrowUpRight } from 'lucide-react';

export default function Footer() {
    const currentYear = new Date().getFullYear();

    const sections = [
        {
            title: 'Platform',
            links: [
                { label: 'Dashboard', path: '/dashboard' },
                { label: 'Upload', path: '/upload' },
                { label: 'History', path: '/history' },
                { label: 'API Docs', path: '#' },
            ]
        },
        {
            title: 'Resources',
            links: [
                { label: 'Authenticity Guide', path: '#' },
                { label: 'Security', path: '#' },
                { label: 'Privacy Policy', path: '#' },
                { label: 'Terms of Service', path: '#' },
            ]
        }
    ];

    const socialLinks = [
        { icon: Github, path: '#', label: 'GitHub' },
        { icon: Twitter, path: '#', label: 'Twitter' },
        { icon: Linkedin, path: '#', label: 'LinkedIn' },
        { icon: Mail, path: '#', label: 'Email' },
    ];

    return (
        <footer className="relative border-t border-surface-800/20 bg-surface-950/50 backdrop-blur-xl transition-colors duration-300">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 sm:gap-16">
                    {/* Brand Column */}
                    <div className="space-y-6">
                        <Link to="/" className="flex items-center gap-2.5 group w-fit">
                            <div className="w-9 h-9 bg-gradient-to-br from-brand-500 to-brand-700 rounded-xl flex items-center justify-center shadow-lg shadow-brand-500/20 group-hover:shadow-brand-500/40 transition-all duration-300">
                                <ShieldCheck className="text-white w-5 h-5" />
                            </div>
                            <span className="text-lg font-bold bg-gradient-to-r from-brand-400 to-brand-200 bg-clip-text text-transparent">
                                EduVerify AI
                            </span>
                        </Link>
                        <p className="text-sm text-surface-400 leading-relaxed font-medium">
                            Truth at the Core of Technology. Helping institutions maintain academic and professional integrity with AI-powered verification.
                        </p>
                        <div className="flex items-center gap-4">
                            {socialLinks.map(({ icon: Icon, path, label }) => (
                                <a
                                    key={label}
                                    href={path}
                                    className="p-2 rounded-lg bg-surface-900/50 text-surface-400 hover:text-brand-400 hover:bg-brand-500/10 transition-all duration-200 border border-surface-800/50"
                                    aria-label={label}
                                >
                                    <Icon size={18} />
                                </a>
                            ))}
                        </div>
                    </div>

                    {/* Links Columns */}
                    {sections.map(({ title, links }) => (
                        <div key={title} className="space-y-6">
                            <h3 className="text-sm font-black uppercase tracking-[0.2em] text-surface-500">{title}</h3>
                            <ul className="space-y-4">
                                {links.map(({ label, path }) => (
                                    <li key={label}>
                                        <Link
                                            to={path}
                                            className="text-sm font-medium text-surface-400 hover:text-brand-400 transition-colors flex items-center gap-1 group"
                                        >
                                            {label}
                                            {path === '#' && <ArrowUpRight size={12} className="opacity-0 group-hover:opacity-100 transition-opacity" />}
                                        </Link>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}

                    {/* Support Column */}
                    <div className="space-y-6">
                        <h3 className="text-sm font-black uppercase tracking-[0.2em] text-surface-500">Global Support</h3>
                        <div className="p-6 rounded-[2rem] bg-gradient-to-br from-brand-600/5 to-transparent border border-brand-500/10">
                            <p className="text-xs text-surface-400 font-medium leading-relaxed mb-4">
                                Need assistance? Our security experts are available 24/7 to help with complex verifications.
                            </p>
                            <a href="mailto:support@eduverify.ai" className="btn-primary w-full py-2.5 text-xs rounded-xl shadow-md shadow-brand-500/10 flex justify-center items-center gap-2">
                                <Mail size={14} />
                                Contact Support
                            </a>
                        </div>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div className="mt-16 pt-8 border-t border-surface-800/20 flex flex-col sm:flex-row items-center justify-between gap-6">
                    <p className="text-xs text-surface-500 font-medium">
                        © {currentYear} EduVerify AI. Built with integrity.
                    </p>
                    <div className="flex items-center gap-6">
                        <span className="flex items-center gap-1.5 text-xs text-success-500 font-bold bg-success-500/5 px-3 py-1.5 rounded-full border border-success-500/10">
                            <div className="w-1.5 h-1.5 bg-success-500 rounded-full animate-pulse" />
                            System Online
                        </span>
                        <div className="flex gap-4 text-xs font-bold text-surface-600 uppercase tracking-widest">
                            <span className="hover:text-surface-400 cursor-pointer transition-colors">v1.2.4</span>
                        </div>
                    </div>
                </div>
            </div>
        </footer>
    );
}
