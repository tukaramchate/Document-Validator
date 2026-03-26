import { Link } from 'react-router-dom';
import { ShieldCheck, Github, Twitter, Linkedin, Mail, Phone, MapPin } from 'lucide-react';

export default function Footer() {
    const currentYear = new Date().getFullYear();

    const sections = [
        {
            title: 'Quick Links',
            links: [
                { label: 'Home', path: '/' },
                { label: 'Verify Document', path: '/upload' },
                { label: 'Pricing', path: '/pricing' },
                { label: 'Help Center', path: '/help' },
            ]
        },
        {
            title: 'Resources',
            links: [
                { label: 'Documentation', path: '/help', external: false },
                { label: 'API Reference', path: '#', external: false },
                { label: 'Integration Guide', path: '#', external: false },
                { label: 'Status Page', path: '#', external: false },
            ]
        }
    ];

    const socialLinks = [
        { icon: Github, path: 'https://github.com', label: 'GitHub' },
        { icon: Twitter, path: 'https://x.com', label: 'Twitter' },
        { icon: Linkedin, path: 'https://linkedin.com', label: 'LinkedIn' },
    ];

    return (
        <footer className="relative border-t border-surface-800/20 bg-surface-950/50 backdrop-blur-xl transition-colors duration-300">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 sm:gap-16">
                    {/* Brand Column */}
                    <div className="space-y-4">
                        <Link to="/" className="flex items-center gap-2.5 group w-fit">
                            <div className="w-10 h-10 bg-gradient-to-br from-brand-500 to-brand-700 rounded-lg flex items-center justify-center shadow-lg shadow-brand-500/20">
                                <ShieldCheck className="text-white w-6 h-6" />
                            </div>
                            <div>
                            <div className="text-sm font-black text-white">VeriAcd</div>
                                <div className="text-xs text-surface-400">Team Error-404</div>
                            </div>
                        </Link>
                        <p className="text-sm text-surface-300 leading-relaxed max-w-xs">
                            Securing academic credentials with cutting-edge verification technology.
                        </p>
                        <div className="inline-block px-3 py-1.5 rounded-full bg-surface-800/50 text-xs font-bold text-surface-300 border border-surface-700/50">
                            Trusted Platform
                        </div>
                    </div>

                    {/* Quick Links & Resources Columns */}
                    {sections.map(({ title, links }) => (
                        <div key={title} className="space-y-4">
                            <h3 className="text-sm font-black uppercase tracking-[0.2em] text-surface-200">{title}</h3>
                            <ul className="space-y-3">
                                {links.map(({ label, path, external }) => (
                                    <li key={label}>
                                        {external ? (
                                            <a
                                                href={path}
                                                className="text-sm font-medium text-surface-400 hover:text-surface-200 transition-colors inline-flex items-center gap-1"
                                            >
                                                {label}
                                                <span className="text-xs">↗</span>
                                            </a>
                                        ) : (
                                            <Link
                                                to={path}
                                                className="text-sm font-medium text-surface-400 hover:text-surface-200 transition-colors"
                                            >
                                                {label}
                                            </Link>
                                        )}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}

                    {/* Contact Column */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-black uppercase tracking-[0.2em] text-surface-200">Contact</h3>
                        <div className="space-y-3 text-sm">
                            <div className="flex items-start gap-3">
                                <MapPin size={16} className="text-brand-400 shrink-0 mt-0.5" />
                                <div>
                                    <div className="font-semibold text-surface-200">Team Error-404</div>
                                    <div className="text-xs text-surface-400">Pune, MH</div>
                                </div>
                            </div>

                            <div className="flex items-center gap-3">
                                <Phone size={16} className="text-brand-400 shrink-0" />
                                <a href="tel:9322942240" className="text-surface-400 hover:text-surface-200 transition-colors">9322942240</a>
                            </div>

                            <div className="flex items-center gap-3">
                                <Mail size={16} className="text-brand-400 shrink-0" />
                                <a href="mailto:tukaramchate397@gmail.com" className="text-surface-400 hover:text-surface-200 transition-colors">tukaramchate397@gmail.com</a>
                            </div>

                            <div className="flex items-center gap-4 pt-2">
                                {socialLinks.map(({ icon: Icon, path, label }) => (
                                    <a key={label} href={path} className="text-surface-400 hover:text-surface-200 transition-colors" aria-label={label}>
                                        <Icon size={18} />
                                    </a>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div className="mt-12 pt-8 border-t border-surface-800/20 flex flex-col sm:flex-row items-center justify-between gap-6">
                    <p className="text-xs text-surface-500 font-medium">
                        © {currentYear} Team Firewall_Breakers. All rights reserved.
                    </p>
                    <div className="flex items-center gap-6 text-xs text-surface-400 flex-wrap justify-center sm:justify-end">
                        <a href="#" className="hover:text-surface-200 transition-colors">Privacy Policy</a>
                        <a href="#" className="hover:text-surface-200 transition-colors">Terms of Service</a>
                        <a href="#" className="hover:text-surface-200 transition-colors">Security Policy</a>
                        <a href="#" className="hover:text-surface-200 transition-colors">Cookie Policy</a>
                    </div>
                </div>
            </div>
        </footer>
    );
}
