import { Link } from 'react-router-dom';
import { Check, Zap, ShieldCheck, X } from 'lucide-react';
import Footer from '../../components/Footer';

export default function Pricing() {
    const plans = [
        {
            name: 'Free',
            price: '$0',
            period: 'forever',
            description: 'Get started with basic document verification',
            features: [
                { text: '10 document validations/month', included: true },
                { text: 'Basic authenticity scores', included: true },
                { text: 'OCR text extraction', included: true },
                { text: 'PDF & image support', included: true },
                { text: 'API access', included: false },
                { text: 'Priority support', included: false },
                { text: 'Advanced analytics', included: false },
            ],
            cta: 'Get Started Free',
            href: '/register',
            highlighted: false,
        },
        {
            name: 'Pro',
            price: '$29',
            period: '/month',
            description: 'For regular users and small institutions',
            features: [
                { text: 'Unlimited validations', included: true },
                { text: 'Advanced scoring & reports', included: true },
                { text: 'Database verification', included: true },
                { text: 'Multi-format support', included: true },
                { text: 'REST API access', included: true },
                { text: 'Email support', included: true },
                { text: 'Basic analytics', included: false },
            ],
            cta: 'Upgrade to Pro',
            href: '/dashboard',
            highlighted: true,
        },
        {
            name: 'Enterprise',
            price: 'Custom',
            period: 'pricing',
            description: 'For large institutions & organizations',
            features: [
                { text: 'Unlimited everything', included: true },
                { text: 'Custom integrations', included: true },
                { text: 'Dedicated support', included: true },
                { text: 'SLA guarantee', included: true },
                { text: 'Advanced API features', included: true },
                { text: '24/7 priority support', included: true },
                { text: 'Advanced analytics & insights', included: true },
            ],
            cta: 'Contact Sales',
            href: 'mailto:tukaramchate397@gmail.com',
            highlighted: false,
        }
    ];

    return (
        <div className="min-h-screen bg-surface-950 flex flex-col transition-colors duration-300">
            {/* Background */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-[500px] h-[500px] bg-brand-600/8 rounded-full blur-3xl" />
                <div className="absolute bottom-1/3 -left-40 w-[400px] h-[400px] bg-brand-500/6 rounded-full blur-3xl" />
            </div>

            <main className="flex-1 relative z-10">
                <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
                    {/* Header */}
                    <div className="text-center mb-16">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-600/10 border border-brand-500/20 text-brand-400 text-xs font-semibold mb-6">
                            <Zap size={14} />
                            <span>Simple, Transparent Pricing</span>
                        </div>
                        <h1 className="text-4xl sm:text-5xl font-black text-surface-100 tracking-tight mb-4">
                            Choose the right plan for you
                        </h1>
                        <p className="text-xl text-surface-400 max-w-2xl mx-auto font-medium">
                            Whether you're just getting started or need enterprise solutions, we have a plan that fits your needs.
                        </p>
                    </div>

                    {/* Pricing Cards */}
                    <div className="grid md:grid-cols-3 gap-8 mb-20">
                        {plans.map((plan, index) => (
                            <div
                                key={index}
                                className={`card rounded-[2rem] p-8 flex flex-col relative ${plan.highlighted
                                    ? 'ring-2 ring-brand-500 transform md:scale-105 bg-brand-600/5'
                                    : ''
                                    } transition-transform`}
                            >
                                {plan.highlighted && (
                                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                                        <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-brand-600 text-white text-xs font-bold shadow-lg shadow-brand-600/30">
                                            <Zap size={12} />
                                            Most Popular
                                        </span>
                                    </div>
                                )}

                                {/* Plan name */}
                                <h3 className="text-xl font-bold text-surface-100 mb-2">{plan.name}</h3>
                                <p className="text-sm text-surface-400 font-medium mb-6">{plan.description}</p>

                                {/* Price */}
                                <div className="mb-6">
                                    <div className="flex items-baseline">
                                        <span className="text-4xl font-black text-surface-100">{plan.price}</span>
                                        {plan.period !== 'forever' && plan.period !== 'pricing' && (
                                            <span className="text-surface-400 ml-2 font-medium">{plan.period}</span>
                                        )}
                                    </div>
                                </div>

                                {/* Features */}
                                <div className="space-y-3 mb-8 flex-1">
                                    {plan.features.map((feature, i) => (
                                        <div key={i} className="flex items-center gap-3">
                                            <div className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 ${feature.included
                                                ? 'bg-brand-500/20'
                                                : 'bg-surface-800/50'
                                                }`}>
                                                {feature.included ? (
                                                    <Check size={12} className="text-brand-400" strokeWidth={3} />
                                                ) : (
                                                    <X size={10} className="text-surface-600" strokeWidth={3} />
                                                )}
                                            </div>
                                            <span className={`text-sm ${feature.included
                                                ? 'text-surface-200 font-medium'
                                                : 'text-surface-600 line-through'
                                                }`}>
                                                {feature.text}
                                            </span>
                                        </div>
                                    ))}
                                </div>

                                {/* CTA */}
                                <Link
                                    to={plan.href}
                                    className={`w-full text-center py-3.5 rounded-xl font-bold transition-all ${plan.highlighted
                                        ? 'btn-primary shadow-lg shadow-brand-500/20'
                                        : 'btn-secondary'
                                        }`}
                                >
                                    {plan.cta}
                                </Link>
                            </div>
                        ))}
                    </div>

                    {/* FAQ Section */}
                    <div className="max-w-2xl mx-auto">
                        <h2 className="text-2xl font-bold text-surface-100 mb-8 text-center">
                            Frequently Asked Questions
                        </h2>

                        <div className="space-y-4">
                            {[
                                {
                                    q: 'Can I upgrade or downgrade my plan anytime?',
                                    a: 'Yes! You can change your plan at any time. Changes take effect immediately.'
                                },
                                {
                                    q: 'Do you offer refunds?',
                                    a: 'We offer a 30-day money-back guarantee if you\'re not satisfied with our service.'
                                },
                                {
                                    q: 'What payment methods do you accept?',
                                    a: 'We accept all major credit cards, bank transfers, and digital payment methods.'
                                }
                            ].map((faq, i) => (
                                <div key={i} className="card rounded-[2rem] p-6">
                                    <p className="font-bold text-surface-100 mb-2">{faq.q}</p>
                                    <p className="text-surface-400 text-sm font-medium">{faq.a}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>
            </main>

            <Footer />
        </div>
    );
}
