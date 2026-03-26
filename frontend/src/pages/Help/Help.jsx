import { useState } from 'react';
import { Search, MessageSquare, Mail, ChevronDown, ChevronUp, HelpCircle, ShieldCheck } from 'lucide-react';
import Footer from '../../components/Footer';

export default function Help() {
    const [searchTerm, setSearchTerm] = useState('');
    const [expandedCategory, setExpandedCategory] = useState(null);

    const categories = [
        {
            name: 'Getting Started',
            articles: [
                { title: 'How do I create an account?', content: 'Visit the registration page and fill in your details. You can register as a User or Institution.' },
                { title: 'How do I upload a document?', content: 'Go to the Upload page and drag-and-drop or select a file to begin verification.' },
                { title: 'What file formats are supported?', content: 'We support PDF, JPG, JPEG, and PNG formats up to 16MB.' },
            ]
        },
        {
            name: 'Verification Process',
            articles: [
                { title: 'How does the verification work?', content: 'Our system uses a 3-layer approach: AI forgery detection, OCR extraction, and database matching against institution records.' },
                { title: 'What do the verdict results mean?', content: 'AUTHENTIC: 90%+ confidence, SUSPICIOUS: 70-89% confidence, FAKE: below 70% confidence.' },
                { title: 'How accurate are the results?', content: 'Our system achieves high accuracy based on extensive testing across multiple document types.' },
            ]
        },
        {
            name: 'Billing & Pricing',
            articles: [
                { title: 'What\'s included with the free plan?', content: 'The free plan includes 10 document validations with basic verification scoring.' },
                { title: 'Can I cancel my subscription anytime?', content: 'Yes, you can cancel anytime without penalties from your account settings.' },
                { title: 'Do you offer refunds?', content: 'We offer a 30-day money-back guarantee if you\'re unsatisfied.' },
            ]
        },
        {
            name: 'Account & Security',
            articles: [
                { title: 'How is my data protected?', content: 'We use SSL encryption and comply with industry security standards. Your documents are encrypted at rest.' },
                { title: 'Can I change my password?', content: 'Yes, go to Settings > Security to change your password anytime.' },
                { title: 'Is two-factor authentication available?', content: 'Two-factor authentication is planned for a future release.' },
            ]
        }
    ];

    const filteredCategories = searchTerm.trim()
        ? categories.map(cat => ({
            ...cat,
            articles: cat.articles.filter(a =>
                a.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                a.content.toLowerCase().includes(searchTerm.toLowerCase())
            )
        })).filter(cat => cat.articles.length > 0)
        : categories;

    return (
        <div className="min-h-screen bg-surface-950 flex flex-col transition-colors duration-300">
            {/* Background */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 right-1/4 w-96 h-96 bg-brand-600/8 rounded-full blur-3xl" />
                <div className="absolute bottom-1/3 -left-40 w-80 h-80 bg-brand-500/6 rounded-full blur-3xl" />
            </div>

            <main className="flex-1 relative z-10">
                <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
                    {/* Header */}
                    <div className="text-center mb-12">
                        <div className="w-16 h-16 bg-brand-500/10 rounded-3xl flex items-center justify-center mx-auto mb-6">
                            <HelpCircle size={32} className="text-brand-400" />
                        </div>
                        <h1 className="text-4xl sm:text-5xl font-black text-surface-100 tracking-tight mb-4">
                            How can we help?
                        </h1>
                        <p className="text-xl text-surface-400 mb-8 font-medium">
                            Find answers to common questions or contact our support team
                        </p>

                        {/* Search */}
                        <div className="max-w-xl mx-auto relative">
                            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-surface-500" size={20} />
                            <input
                                type="text"
                                placeholder="Search for help..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="input-field pl-12 h-14 rounded-2xl text-base"
                            />
                        </div>
                    </div>

                    {/* Quick Links */}
                    <div className="grid md:grid-cols-3 gap-6 mb-16">
                        <div className="card rounded-[2rem] p-8 text-center group">
                            <div className="w-14 h-14 bg-brand-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 group-hover:bg-brand-500/20 transition-all duration-300">
                                <MessageSquare size={24} className="text-brand-400" />
                            </div>
                            <h3 className="font-bold text-surface-100 mb-2">Chat Support</h3>
                            <p className="text-sm text-surface-400 mb-4 font-medium">Get instant help from our support team</p>
                            <button className="btn-secondary px-6 py-2.5 rounded-xl text-sm font-bold">Start Chat</button>
                        </div>

                        <div className="card rounded-[2rem] p-8 text-center group">
                            <div className="w-14 h-14 bg-brand-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 group-hover:bg-brand-500/20 transition-all duration-300">
                                <Mail size={24} className="text-brand-400" />
                            </div>
                            <h3 className="font-bold text-surface-100 mb-2">Email Support</h3>
                            <p className="text-sm text-surface-400 mb-4 font-medium">Email us your questions</p>
                            <a href="mailto:tukaramchate397@gmail.com">
                                <button className="btn-secondary px-6 py-2.5 rounded-xl text-sm font-bold">Send Email</button>
                            </a>
                        </div>

                        <div className="card rounded-[2rem] p-8 text-center group">
                            <div className="w-14 h-14 bg-success-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 group-hover:bg-success-500/20 transition-all duration-300">
                                <ShieldCheck size={24} className="text-success-400" />
                            </div>
                            <h3 className="font-bold text-surface-100 mb-2">System Status</h3>
                            <p className="text-sm text-surface-400 mb-4 font-medium">All systems operational</p>
                            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-success-500/10 border border-success-500/20 rounded-xl text-success-400 text-[10px] font-black uppercase tracking-widest">
                                <div className="w-2 h-2 bg-success-400 rounded-full animate-pulse" />
                                Online
                            </span>
                        </div>
                    </div>

                    {/* FAQ Accordion */}
                    <div>
                        <h2 className="text-2xl font-bold text-surface-100 mb-8">Frequently Asked Questions</h2>

                        <div className="space-y-4">
                            {filteredCategories.map((cat, catIndex) => (
                                <div key={catIndex} className="card rounded-[2rem] overflow-hidden">
                                    <button
                                        onClick={() => setExpandedCategory(expandedCategory === catIndex ? null : catIndex)}
                                        className="w-full flex items-center justify-between p-6 text-left hover:bg-surface-800/30 transition-colors"
                                    >
                                        <h3 className="text-lg font-bold text-surface-100">{cat.name}</h3>
                                        {expandedCategory === catIndex
                                            ? <ChevronUp size={20} className="text-brand-400" />
                                            : <ChevronDown size={20} className="text-surface-500" />
                                        }
                                    </button>

                                    {expandedCategory === catIndex && (
                                        <div className="px-6 pb-6 space-y-4 animate-fade-in">
                                            {cat.articles.map((article, i) => (
                                                <div key={i} className="p-4 bg-surface-800/30 rounded-2xl border border-surface-700/30">
                                                    <h4 className="font-bold text-surface-200 text-sm mb-2">{article.title}</h4>
                                                    <p className="text-sm text-surface-400 font-medium leading-relaxed">{article.content}</p>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>

                        {filteredCategories.length === 0 && (
                            <div className="card rounded-[2rem] p-12 text-center">
                                <p className="text-surface-400 font-bold">No results found for "{searchTerm}"</p>
                                <button
                                    onClick={() => setSearchTerm('')}
                                    className="text-brand-400 font-bold text-sm mt-2 hover:underline"
                                >
                                    Clear search
                                </button>
                            </div>
                        )}
                    </div>
                </section>
            </main>

            <Footer />
        </div>
    );
}
